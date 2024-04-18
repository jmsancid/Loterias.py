#!/usr/bin/env python3
# -*- coding: cp1252 -*-
import sys

from loterias_tools.loteriasdb import lotoparams, PrimiComb, EuroComb, sql_connection, sql_find, sql_recordcount
from loterias_tools.loteriasdb import sql_insert, sql_getcolumnname, sql_checkifexists
from loterias_tools.loteriasdb import Error
from loterias_tools.get_primi_comb_from_web import get_primi_latest_results
from loterias_tools.get_euro_comb_from_web import get_euro_latest_results
from datetime import datetime, timedelta
from typing import List
from dataclasses import asdict


def sql_update(con, tipoloto):
    """
    rutina para añadir a la base de datos los últimos resultados leídos en la web
    :param con: objeto base de datos sqlite3
    :param tipoloto: tabla a actualizar
    :return:
    """
    if tipoloto == lotoparams.PRIMITIVA:
        resultados = get_primi_latest_results()
        campos = lotoparams.PRIMIFIELDS
    elif tipoloto == lotoparams.EUROMILLONES:
        resultados = get_euro_latest_results()
        campos = lotoparams.EUROFIELDS
    else:
        raise NameError

    resultados = {clave: resultados[clave] for clave in sorted(resultados)}
    # print(resultados)
    for fecha in resultados:  # la clave del diccionario resultados es la fecha
        found = sql_find(con, tipoloto, 'fecha', fecha)
        if not found:
            current_recordcount = sql_recordcount(con, tipoloto)
            valtoinsert = [current_recordcount + 1] + [fecha] + resultados[fecha]
            print('Insertada:', [current_recordcount + 1] + [fecha] + resultados[fecha])
            sql_insert(con, tipoloto, campos, valtoinsert)


def sql_savecomb(combinaciones: dict = None):
    """
    Guarda las combinaciones calculadas en las tablas SelEuro o SelPrimi según sea Euromillones o primitiva,
    identificando el día de la semana del sorteo.
    Las combinaciones calculadas considerando todos los sorteos, sin separar unos días de otros, se guardan en
    SelPrimiTot y en SelEuroTot
    :param combinaciones:combinaciones a añadir. Es un diccionario con un entero como clave que representa
    el día del sorteo:
    2=martes(Euromillón), 4=jueves(Primitiva), 5=viernes(Euromillón), 6=sábado(Primitiva)
    :return:
    """

    if not combinaciones:
        exit()

    tabla = lotoparams.SELPRIMI if list(combinaciones.keys())[0] in [46, 4, 6] else lotoparams.SELEURO

    # Obtengo el número de la semana actual
    def getcurrentweek(anno: int = int(datetime.now().year),
                       mes: int = int(datetime.now().month),
                       dia: int = int(datetime.now().day)):
        currentweek = str(datetime(anno, mes, dia).isocalendar().week)
        return currentweek

    currentweek = getcurrentweek()

    # Busco fechas de la semana siguiente a la actual, correspondientes a martes, jueves, viernes y sábado
    # dependiendo del valor de x
    # currentweeklotodays: 2 martes euro, 4 jueves primi, 5 viernes euro, 6 sábado primi
    def getnextweekdate(x: int, offset: int = 1) -> str:
        nextweek = (datetime.now() + timedelta(weeks=offset)).isocalendar()
        nextweekdate = str(datetime.fromisocalendar(nextweek.year, nextweek.week, x).date())
        return nextweekdate

    con = None
    try:
        con = sql_connection()
        cursorObj = con.cursor()

        # Compruebo si las bases de datos de Primitiva o Euromillones tienen las estimaciones de la semana actual
        qregs = sql_recordcount(con, tabla)
        sqlorder = f'SELECT fecha FROM {tabla}'
        cursorObj.execute(sqlorder)
        registro = cursorObj.fetchall()
        fechalastreg = registro[qregs - 1][0]  # Fecha del último registro
        datetimefecha = fechalastreg.split('-')
        anno = int(datetimefecha[0])
        mes = int(datetimefecha[1])
        dia = int(datetimefecha[2])
        weeklastreg = str(datetime(anno, mes, dia).isocalendar().week)  # Semana del último registro
        # db combinaciones seleccionadas

        # Si todavía no se han guardado las combinaciones de la semana actual, se guardan las combinaciones
        # asociándolas a la semana actual
        ordendiasemana = datetime.now().isoweekday()  # Lunes= 1; Domingo = 7
        weekoffset = 0 if ((weeklastreg == currentweek and ordendiasemana != 7) or
                           weeklastreg != currentweek) else 1  # Sólo guardo pronósticos a
        # partir del domingo, siempre y cuando haya ya alguna previsión en la semana actual
        # nextlotodays: 2 martes euro, 4 jueves primi, 5 viernes euro, 6 sábado primi
        nextlotodays = {dia: getnextweekdate(dia, weekoffset) for dia in [2, 4, 5, 6]}
        week4total = f'{datetime.strptime(nextlotodays.get(2), "%Y-%m-%d").isocalendar().year}.{currentweek}'

        for dia in combinaciones:
            for combinacion in combinaciones.get(dia):
                # Los días 46 de primitiva y 25 de euromillones son combinaciones calculadas con la totalidad
                # de sorteos y dichas combinaciones se almacenan por año y número de semana en lugar de por fecha
                fecha = nextlotodays.get(dia)  # Si devuelve None es porque la combinación es 46 de Primitiva o 25
                # de Euromillones
                if not fecha:
                    fecha = week4total  # Semana expresada en formato AAAA.ss, 2021.48

                if dia == 46:  # Combinaciones calculadas a partir del total de sorteos de PRIMITIVA,
                    # jueves+sábado
                    tabla = lotoparams.SELPRIMITOT
                elif dia in [4, 6]:  # Combinaciones de PRIMITIVA calculadas por separado para jueves o sábados
                    tabla = lotoparams.SELPRIMI
                elif dia == 25:  # Combinaciones calculadas a partir del total de sorteos de EUROMILLONES,
                    # martes+viernes
                    tabla = lotoparams.SELEUROTOT
                elif dia in [2, 5]:  # Combinaciones de EUROMILLONES calculadas por separado para martes o viernes
                    tabla = lotoparams.SELEURO

                campos = sql_getcolumnname(con, tabla)
                vals = '?' + ', ?' * (len(campos) - 1)
                campos2insert = ', '.join(x for x in campos)
                vals2insert = [fecha, combinacion] + combinaciones[dia][combinacion]
                # Si es primitiva, borramos el complementario
                if dia in [46, 4, 6]:
                    del (vals2insert[8])

                existe, valor = sql_checkifexists(con, tabla, [fecha, combinacion], [campos[0], campos[1]])
                # existe, valor = sql_checkifexists(con, tabla, [fecha,], [campos[0],])

                if not existe:
                    sql_command = f'INSERT INTO {tabla}({campos2insert}) VALUES({vals})'
                    # print('sql_savecomb: \n', sql_command)
                    cursorObj.execute(sql_command, vals2insert)
                con.commit()

    except Error:
        print('sql_savecomb: Error módulo guardado base de datos', Error)

    con.close()


def sql_savecomb2(combinaciones=None):
    """
    Guarda las combinaciones calculadas en las tablas SelEuro o SelPrimi según sea Euromillones o primitiva,
    identificando el día de la semana del sorteo.
    Las combinaciones calculadas considerando todos los sorteos, sin separar unos días de otros, se guardan en
    SelPrimiTot y en SelEuroTot
    :param combinaciones:combinaciones a añadir. Es una tupla con 3 diccionarios. Cada diccionario contiene las
     combinaciones seleccionadas. 5 combinaciones para primitiva y 2 para euromillones. Las combinaciones son
     instancias de PrimiComb o EuroComb.
     El primero de los 3 diccionarios contiene las combinaciones calculadas con el total de los datos, el segundo
     las combinaciones calculadas con los datos de los martes para euromillones o jueves para primitiva y el tercer
     diccionario las combinaciones calculadas para viernes de euromillones o sábado de primitiva.
    :return:
    """

    if combinaciones is None:
        combinaciones = []
    if not combinaciones:
        exit()

    primitiva = isinstance(list(combinaciones[0].values())[0], PrimiComb)  # Si True, las combinaciones son de
    # Primitiva. Si False, de Euromillones

    tabla = lotoparams.SELPRIMI if primitiva else lotoparams.SELEURO

    # Obtengo el número de la semana actual
    def getcurrentweek(anno: int = int(datetime.now().year),
                       mes: int = int(datetime.now().month),
                       dia: int = int(datetime.now().day)):
        currentweek = "%2.2d" % (datetime(anno, mes, dia).isocalendar().week)
        return currentweek

    currentweek = getcurrentweek()

    # Busco fechas de la semana siguiente a la actual, correspondientes a martes, jueves, viernes y sábado
    # dependiendo del valor de x
    # currentweeklotodays: 2 martes euro, 4 jueves primi, 5 viernes euro, 6 sábado primi
    def getnextweekdate(x: int, offset: int = 1) -> str:
        nextweek = (datetime.now() + timedelta(weeks=offset)).isocalendar()
        nextweekdate = str(datetime.fromisocalendar(nextweek.year, nextweek.week, x).date())
        return nextweekdate

    con = None
    try:
        con = sql_connection()
        cursorObj = con.cursor()

        # Compruebo si las bases de datos de Primitiva o Euromillones tienen las estimaciones de la semana actual
        qregs = sql_recordcount(con, tabla)
        sqlorder = f'SELECT fecha FROM {tabla}'
        cursorObj.execute(sqlorder)
        registro = cursorObj.fetchall()
        fechalastreg = registro[qregs - 1][0]  # Fecha del último registro
        datetimefecha = fechalastreg.split('-')
        anno = int(datetimefecha[0])
        mes = int(datetimefecha[1])
        dia = int(datetimefecha[2])
        weeklastreg = str(datetime(anno, mes, dia).isocalendar().week)  # Semana del último registro
        # db combinaciones seleccionadas

        # Si todavía no se han guardado las combinaciones de la semana actual, se guardan las combinaciones
        # asociándolas a la semana actual
        ordendiasemana = datetime.now().isoweekday()  # Lunes= 1; Domingo = 7
        weekoffset = 0 if ((weeklastreg == currentweek and ordendiasemana != 7) or
                           weeklastreg != currentweek) else 1  # Sólo guardo pronósticos a
        # partir del domingo, siempre y cuando haya ya alguna previsión en la semana actual
        # nextlotodays: 2 martes euro, 4 jueves primi, 5 viernes euro, 6 sábado primi
        nextlotodays = {dia: getnextweekdate(dia, weekoffset) for dia in [1, 2, 4, 5, 6]}
        week4total = f'{datetime.strptime(nextlotodays.get(2), "%Y-%m-%d").isocalendar().year}.{currentweek}'

        tablanames = {lotoparams.SELPRIMITOT: 'PRIMITIVA TOTALES',
                      lotoparams.SELEUROTOT: 'EUROMILLONES TOTALES',
                      1: 'PRIMITIVA LUNES',
                      2: 'EUROMILLONES MARTES',
                      4: 'PRIMITIVA JUEVES',
                      5: 'EUROMILLONES VIERNES',
                      6: 'PRIMITIVA SÁBADO'}

        for grp in combinaciones:  # el primer grupo de combinaciones es el calculado con valores totales, el
            # segundo corresponde al primer día de sorteo y el tercero al segundo día de sorteo
            print(f'savecomb2 - Grupo de combinaciones: {combinaciones.index(grp)}')
            if combinaciones.index(grp) == 0:  # La primera es la combinación calculada con todas las combinaciones
                fecha = week4total
                tabla = lotoparams.SELPRIMITOT if primitiva else lotoparams.SELEUROTOT
            elif primitiva:
                fecha = nextlotodays.get(lotoparams.PRIMIDAYS[combinaciones.index(grp)])  # lunes, jueves y sábado
                tabla = lotoparams.SELPRIMI
            else:
                fecha = nextlotodays.get(lotoparams.EURODAYS[combinaciones.index(grp)])  # martes y viernes
                tabla = lotoparams.SELEURO

            for k, v in grp.items():
                if combinaciones.index(grp) == 0:
                    print(f'sql_savecomb2: Seleccionada {tablanames.get(tabla)}\tFecha: {fecha}')
                elif primitiva:
                    print(f'sql_savecomb2: Seleccionada '
                          f'{tablanames.get(lotoparams.PRIMIDAYS[combinaciones.index(grp)])}\tFecha: {fecha}')
                else:
                    print(f'sql_savecomb2: Seleccionada '
                          f'{tablanames.get(lotoparams.EURODAYS[combinaciones.index(grp)])}\tFecha: {fecha}')

                combinacion = [k] + \
                              sorted([j for i, j in asdict(v).items() if i not in ['comp', 'reint', 'e1', 'e2']])

                if primitiva:
                    # Si es primitiva, añado el reintegro
                    reint = asdict(v).get('reint')  # Reintegro en el caso de primitiva
                    combinacion += [reint]
                    print(f'\tReintegro: {reint}')
                else:  # Es Euromillón
                    e1 = asdict(v).get('e1')  # e1 en el caso de euromillones
                    e2 = asdict(v).get('e2')  # e2 en el caso de euromillones
                    combinacion += [e1, e2]
                print(*combinacion[1:])
                # print(f'Combinación {combinacion[0]}: {combinacion[1:]}')
                # print(f'sql_savecomb2: Combinaciones {grp}')

                campos = sql_getcolumnname(con, tabla)
                vals = '?' + ', ?' * (len(campos) - 1)
                campos2insert = ', '.join(x for x in campos)
                vals2insert = [fecha, *combinacion]
                # print(f'SQL: Valores a insertar {vals2insert}')

                existe, valor = sql_checkifexists(con, tabla, [fecha, k], [campos[0], campos[1]])

                if not existe:
                    sql_command = f'INSERT INTO {tabla}({campos2insert}) VALUES({vals})'
                    # print('sql_savecomb: \n', sql_command)
                    cursorObj.execute(sql_command, vals2insert)
                con.commit()

    except Error:
        print('sql_savecomb: Error módulo guardado base de datos', Error)

    con.close()


# sql_savecomb()
# exit()

def actualiza_loteriasdb():
    con = None
    try:
        con = sql_connection()
        sql_update(con, lotoparams.PRIMITIVA)
        sql_update(con, lotoparams.EUROMILLONES)
    except Error:
        print('No ha sido posible actualizar la base de datos de loterías')
        print(Error)
    finally:
        con.close()
    print('Bases de datos actualizadas')

# def main():
#     actualiza_loteriasdb()
#
#
# if __name__ == '__main__':
#     main()
