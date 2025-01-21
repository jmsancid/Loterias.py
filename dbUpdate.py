#!/usr/bin/env python3
# -*- coding: cp1252 -*-

import constants as cte
from clases import PrimiComb
from getPrimiCombFromWeb import getPrimiLatestResults
from getEuroCombFromWeb import getEuroLatestResults
from dbMgnt import sqlConnection, sqlFind, sqlRecordCount, sqlInsert, sqlGetColumnName, sqlCheckIfExists, \
    Error
from datetime import datetime, timedelta
from dataclasses import asdict


def sqlUpdate(con, tipoloto):
    """
    rutina para añadir a la base de datos los últimos resultados leídos en la web
    :param con: objeto base de datos sqlite3
    :param tipoloto: tabla a actualizar
    :return:
    """
    if tipoloto == cte.PRIMITIVA:
        resultados = getPrimiLatestResults()
        campos = cte.PRIMIFIELDS
    elif tipoloto == cte.EUROMILLONES:
        resultados = getEuroLatestResults()
        campos = cte.EUROFIELDS
    else:
        raise NameError

    resultados = {clave: resultados[clave] for clave in sorted(resultados)}
    # print(resultados)
    for fecha in resultados:  # la clave del diccionario resultados es la fecha
        found = sqlFind(con, tipoloto, 'fecha', fecha)
        if not found:
            current_recordcount = sqlRecordCount(con, tipoloto)
            valtoinsert = [current_recordcount + 1] + [fecha] + resultados[fecha]
            print('Insertada:', [current_recordcount + 1] + [fecha] + resultados[fecha])
            sqlInsert(con, tipoloto, campos, valtoinsert)


def sqlSaveCombinations(combinaciones=None):
    """
    Guarda las combinaciones calculadas en las tablas SelEuro o SelPrimi según sea Euromillones o primitiva,
    identificando el día de la semana del sorteo.
    Las combinaciones calculadas considerando todos los sorteos, sin separar unos días de otros, se guardan en
    SelPrimiTot y en SelEuroTot
    :param combinaciones:combinaciones a añadir. Es una tupla con 3 o 4 diccionarios según sea euromillones
    (totales, martes o viernes) o primitiva (totales, lunes, jueves o sábado.
    Cada diccionario contiene las combinaciones seleccionadas. 5 combinaciones para primitiva y 2
     para euromillones. Las combinaciones son instancias de PrimiComb o EuroComb.
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

    tabla = cte.SELPRIMI if primitiva else cte.SELEURO

    # Obtengo el número de la semana actual
    currentweek   = datetime.now().isocalendar().week  # obtengo el número de la semana actual

    # Busco fechas de la semana siguiente a la actual, correspondientes a martes, jueves, viernes y sábado
    # dependiendo del valor de x
    # currentweeklotodays: 2 martes euro, 4 jueves primi, 5 viernes euro, 6 sábado primi
    def getnextweekdate(x: int, offset: int = 1) -> str:
        nextweek = (datetime.now() + timedelta(weeks=offset)).isocalendar()
        nextweekdate = str(datetime.fromisocalendar(nextweek.year, nextweek.week, x).date())
        return nextweekdate

    con = None
    try:
        con = sqlConnection(cte.DBDIR + cte.DBFILE)
        cur = con.cursor()

        # Compruebo si las bases de datos de Primitiva o Euromillones tienen las estimaciones de la semana actual
        qregs = sqlRecordCount(con, tabla)
        sqlorder = f'SELECT fecha FROM {tabla}'
        cur.execute(sqlorder)
        registro = cur.fetchall()
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

        tablanames = {cte.SELPRIMITOT: 'PRIMITIVA TOTALES',
                      cte.SELEUROTOT: 'EUROMILLONES TOTALES',
                      1: 'PRIMITIVA LUNES',
                      2: 'EUROMILLONES MARTES',
                      4: 'PRIMITIVA JUEVES',
                      5: 'EUROMILLONES VIERNES',
                      6: 'PRIMITIVA SÁBADO'}

        for idx, grp in enumerate(combinaciones):  # el primer grupo de combinaciones es el calculado con
            # valores totales, el segundo corresponde al primer día de sorteo y el tercero al segundo día de sorteo
            # print(f'savecomb - Grupo de combinaciones: {combinaciones.index(grp)}')
            # if combinaciones.index(grp) == 0:  # La primera es la combinación calculada con todas las combinaciones
            # print(f"DEBUGGING (primitiva, idx, grp) - {primitiva} - {idx} - {grp}")
            if idx == 0:  # La primera es la combinación calculada con todas las combinaciones
                fecha = week4total
                tabla = cte.SELPRIMITOT if primitiva else cte.SELEUROTOT
                sorteo = tabla
            elif primitiva:
                fecha = nextlotodays.get(cte.PRIMIDAYS[combinaciones.index(grp)])  # lunes, jueves y sábado
                tabla = cte.SELPRIMI
                # print(f"Clave de tablenames: {cte.PRIMIDAYS[idx]}")
                sorteo = cte.PRIMIDAYS[idx]
            else:
                fecha = nextlotodays.get(cte.EURODAYS[combinaciones.index(grp)])  # martes y viernes
                tabla = cte.SELEURO
                sorteo = cte.EURODAYS[idx]

            print(f'\nSeleccionada {tablanames.get(sorteo)}\tFecha: {fecha}')
            first_combi = True
            for k, v in grp.items():
                combinacion = [k] + sorted([j for i, j in asdict(v).items()
                                            if i not in ['comp', 're', 'e1', 'e2']])
                if primitiva:
                    # Si es primitiva, añado el reintegro
                    reint = asdict(v).get('re')  # Reintegro en el caso de primitiva
                    if first_combi:
                        print(f'\tReintegro: {reint}')
                        first_combi = False
                    print(", ".join([str(i) for i in combinacion[1:]]))
                    combinacion += [reint]
                else:  # Es Euromillón
                    e1 = asdict(v).get('e1')  # e1 en el caso de euromillones
                    e2 = asdict(v).get('e2')  # e2 en el caso de euromillones
                    stars = [str(i) for i in (e1, e2)]
                    print(", ".join([str(i) for i in combinacion[1:]]) + " Estrellas: " + ", ".join(stars))
                    combinacion += [e1, e2]
                # print(*combinacion[1:])
                # print(f'Combinación {combinacion[0]}: {combinacion[1:]}')
                # print(f'sql_savecomb2: Combinaciones {grp}')

                campos = sqlGetColumnName(con, tabla)
                vals = '?' + ', ?' * (len(campos) - 1)
                campos2insert = ', '.join(x for x in campos)
                vals2insert = [fecha, *combinacion]

                existe, valor = sqlCheckIfExists(con, tabla, [fecha, k], [campos[0], campos[1]])

                if not existe:
                    print(f'SQL: Valores a insertar {vals2insert}')
                    sql_command = f'INSERT INTO {tabla}({campos2insert}) VALUES({vals})'
                    # print('sql_savecomb: \n', sql_command)
                    cur.execute(sql_command, vals2insert)
                    con.commit()
                # else:
                #     print(f'checkifexists: el registro ({valor}) ya existe')


    except Error:
        print('sqlSaveCombinations: Error módulo guardado base de datos', Error)

    con.close()


# sql_savecomb()
# exit()

def dbUpdate():
    con = None
    try:
        con = sqlConnection(cte.DBDIR + cte.DBFILE)
        sqlUpdate(con, cte.PRIMITIVA)
        sqlUpdate(con, cte.EUROMILLONES)
    except Error:
        print('No ha sido posible actualizar la base de datos de loterías')
        print(Error)
    finally:
        con.close()
    print('Bases de datos actualizadas')
