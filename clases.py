#!/usr/bin/env python3
# -*- coding: cp1252 -*-
import datetime
import operator
from collections import Counter
from dataclasses import dataclass, field, fields
from typing import List, Union
import constants as cte
from db_mgnt import sql_connection, get_last_comb

'''
07/02/2024  Versión 1 del módulo Clases.
Sustituye al módulo Clases_old0.py (almacenado en obsoletos)
NOTAS:
En esta versión se vuelven a seleccionar los números más frecuentes en cada posición.
Posteriormente, tras seleccionar los 36 números, se mezclarán aleatoriamente.
Se deja de tener en cuenta la evolución de la frecuencia (freqevolution)
'''

# @dataclass()
@dataclass
class PrimiComb:
    combDate    : None      = field(init=False)
    n1          : int       = field(init=False)
    n2          : int       = field(init=False)
    n3          : int       = field(init=False)
    n4          : int       = field(init=False)
    n5          : int       = field(init=False)
    n6          : int       = field(init=False)
    comp        : int       = field(init=False, repr=False)
    re          : Union[int, None]       = field(init=False)


def make_primitiva_dbclass():
    """Construye la lista con todas las combinaciones de primitiva
    :returns objeto PrimiDB todas las combinaciones de primitiva
    """

    # db_fields = ', '.join(cte.PRIMIFIELDS[2:])    # sólo números
    db_fields = ', '.join(cte.PRIMIFIELDS[1:])      # números y fecha de la combinación
    sqlstmt = f'SELECT {db_fields} FROM {cte.PRIMITIVA}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)

    combinations = list(cursor.fetchall())
    primiCombs = []
    strfmt  = "%Y-%m-%d"
    for comb in combinations:
        # auxComb = PrimiComb(
        #     combDate    = datetime.datetime.strptime(comb[0], strfmt),
        #     n1          = comb[1],
        #     n2          = comb[2],
        #     n3          = comb[3],
        #     n4          = comb[4],
        #     n5          = comb[5],
        #     n6          = comb[6],
        #     comp        = comb[7],
        #     re          = comb[8]
        #     )
        auxComb = PrimiComb()
        auxComb.combDate    = datetime.datetime.strptime(comb[0], strfmt)
        auxComb.n1          = comb[1]
        auxComb.n2          = comb[2]
        auxComb.n3          = comb[3]
        auxComb.n4          = comb[4]
        auxComb.n5          = comb[5]
        auxComb.n6          = comb[6]
        auxComb.comp        = comb[7]
        auxComb.re          = comb[8]

        primiCombs.append(auxComb)
    # return [PrimiComb(*cmb) for cmb in combinations]
    return primiCombs


def make_primilunes_dbclass():
    """Construye la lista con todas las combinaciones de primitiva extraídas los lunes
    :returns objeto PrimiDB todas las combinaciones de primitiva de los lunes
    """

    db_fields = ', '.join(cte.PRIMIFIELDS[2:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.PRIMITIVA} WHERE CAST (strftime("%w", fecha) AS Integer) = {1}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [PrimiComb(*cmb) for cmb in combinations]


def make_primijueves_dbclass():
    """Construye la lista con todas las combinaciones de primitiva extraídas los jueves
    :returns objeto PrimiDB todas las combinaciones de primitiva de los jueves
    """

    db_fields = ', '.join(cte.PRIMIFIELDS[2:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.PRIMITIVA} WHERE CAST (strftime("%w", fecha) AS Integer) = {4}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [PrimiComb(*cmb) for cmb in combinations]


def make_primisabado_dbclass():
    """Construye la lista con todas las combinaciones de primitiva
    :returns objeto PrimiDB todas las combinaciones de primitiva
    """

    db_fields = ', '.join(cte.PRIMIFIELDS[2:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.PRIMITIVA} WHERE CAST (strftime("%w", fecha) AS Integer) = {6}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [PrimiComb(*cmb) for cmb in combinations]


@dataclass
class PrimiDB:
    combs: List[PrimiComb] = field(default_factory=make_primitiva_dbclass)  # todas las combinaciones
    # combsmon: List[PrimiComb] = field(default_factory=make_primilunes_dbclass)  # combinaciones de los lunes
    # combsthr: List[PrimiComb] = field(default_factory=make_primijueves_dbclass)  # combinaciones de los jueves
    # combssat: List[PrimiComb] = field(default_factory=make_primisabado_dbclass)  # combinaciones de los sábados

    def contador(self, combgrp: Union[None, int] = None) -> dict:
        """
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        1 .- combinaciones de los lunes
        4 .- combinaciones de los jueves
        6 .- combinaciones de los sábados
        :return: diccionario con clave el número de orden en la combinación y valor un diccionario con clave
        número extraído y valor la cantidad de veces que ha salido ordenado por nº de veces extraído
        """
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, sábados
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        valfreq = {x.name: dict(Counter(getattr(y, x.name) for y in combgrpsel).most_common())
                   for x in fields(PrimiComb)}
        return valfreq

    def cuentafreq(self, combgrp: Union[None, int] = None) -> dict:
        """
        Devuelve un diccionario con clave el número de orden en la combinación y valor otro diccionario con claves
        los números extraídos en esa posición y el porcentaje de apariciones
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        1 .- combinaciones de los lunes
        4 .- combinaciones de los jueves
        6 .- combinaciones de los sábados
        :return: diccionario con clave el número de orden en la combinación y valor otro diccionario con claves
        los números extraídos en esa posición y el porcentaje de apariciones
        """
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, sábados
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        q_sorteos = len(combgrpsel)
        valfreq = {x.name: dict(Counter(getattr(y, x.name) for y in combgrpsel).most_common())
                   for x in fields(PrimiComb)}
        valfreqfiltered = {}
        for k, v in valfreq.items():
            valfreqfiltered[k] = {}
            for n, q in v.items():
                if n is not None:  # Para excluir los sorteos en los que no había reintegro
                    valfreqfiltered[k][n] = {}
                    # v[n] = round(q / q_sorteos * 100, 2)
                    freqTmp = round(q / q_sorteos * 100, 2)
                    valfreqfiltered[k][n] = freqTmp
                    # valfreqfiltered[k][n] = v[n]

        return valfreqfiltered

    def freq_evolution(self, combgrp: Union[None, int] = None) -> dict:
        """
        Analisis de cómo evoluciona la frecuencia de aparición de los números extraídos, sorteo tras sorteo
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        1 .- combinaciones de los lunes
        4 .- combinaciones de los jueves
        6 .- combinaciones de los sábados
        :return: para cada orden de extracción, lista con el porcentaje de apariciones hasta esa fecha
        """
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, sábados
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        freq_evo = {}
        for fld in fields(PrimiComb):
            fldname = fld.name
            freq_evo[fldname] = []
            extracted = []
            idx = 0
            for cmb in combgrpsel:
                idx += 1
                last_extracted = getattr(cmb, fldname)
                if last_extracted:
                    extracted.append(last_extracted)
                    freq_evo[fldname].append(round(Counter(extracted).get(last_extracted) / idx * 100, 2))
                else:
                    continue
            freq_evo[fldname] = dict(Counter(freq_evo[fldname]).most_common())
        return freq_evo

    def evenodd(self, combgrp: Union[None, int] = None) -> list:
        """
        :return: lista de tuplas con las combinaciones de números pares e impares por orden de extracción,
        ordenado por frecuencia de combinación par-impar y según el sorteo: todos, lunes, jueves o sábado
        """
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, sábados
        combgrpsel = self.combs if not combgrp else comboptions.get(combgrp)
        combfields = fields(PrimiComb)
        e_o_list = []
        for cmb in combgrpsel:
            extraidos = [getattr(cmb, fld.name) for fld in combfields]
            parimpar = []
            for extnum in extraidos:
                if not extnum or extnum % 2 == 0:
                    parimpar.append(cte.EVEN)
                else:
                    parimpar.append(cte.ODD)
            e_o_list.append(tuple(parimpar))
        eo_count = sorted(Counter(e_o_list).items(),
                          key=operator.itemgetter(1),
                          reverse=True)
        return eo_count

    def selcombs(self, combgrp: Union[None, int] = None) -> dict:
        """
        selecciona todas las combinaciones de Primitiva de forma que:
        - los números se ajustan a las combinaciones par-impar más frecuentes, respetando el orden de pares e impares.
        procede de evenodd
        :param combgrp se utiliza para identificar si se analizan todos los sorteos (combgrp=None), o los del lunes,
        jueves o sabado, en los que combgrp vale 1, 4 o 6 respectivamente
        :return: diccionario con el nº de apuesta (0 a 4) como clave, y objeto PrimiComb como valor
        """
        if combgrp not in [None, *cte.PRIMIDAYS[1:]]:
            print(f'PrimiDb.selcombs: {combgrp} no es válido. Debe ser None, 1, 4 ó 6')
            return {}
        # Obtengo la última combinación extraída
        con = sql_connection(cte.DBDIR + cte.DBFILE)  # conexion a la base de datos de loterias
        last_combs = get_last_comb(con, cte.PRIMITIVA)  # Devuelve las ultimas 5 combinaciones guardadas en
        # db loterias

        #cambio la fecha de cada combinacion extraida por el dia de la semana al que corresponde. lunes=1 y asi
        # hasta domingo 7
        last_comb = []
        if combgrp is None:  # Para el analisis de todas las combinaciones se toma la ultima combinacion extraida
            last_comb = last_combs[0]
        else:
            for i in range(len(last_combs)):  # se toma la ultima combinacion del dia analizado, L, J o S
                dayOfTheWeek = datetime.datetime.strptime(last_combs[i][1], '%Y-%m-%d').isoweekday()
                if dayOfTheWeek == combgrp:
                    last_comb = last_combs[i]
                    break

        # obtengo par-impar. eveodd devuelve una lista de tuplas con la combinación de pares e impares y la
        # cantidad de veces que se dan, ordenados por dichas cantidades
        e_o_combs = self.evenodd(combgrp)

        distribApariciones = self.contador(combgrp)  # cantidad de veces que sale cada numero cada dia de la semana
        valPrimiCombInit = (100, 100, 100, 100, 100, 100, 100, 100)
        combsel = {c:PrimiComb(*valPrimiCombInit) for c in range(cte.PRIMI_Q_BETS)}
        allBetNumbers = []  # guarda todos los numeros seleccionados para las apuestas
        allReintNumbers = []  # guarda todos los reintegros
        for posic, nums in distribApariciones.items():
            # el complementario no se evalua
            esComp = True if posic in cte.PRIMIFIELDS[8] else False
            if esComp:
                continue

            esReint = True if posic in cte.PRIMIFIELDS[9] else False  # compruebo si estamos evaluando el reintegro

            # posicType = 0 si posic esta entre n1 a n6 y vale 1 si es el reintegro
            posicType = 1 if esReint else 0

            # ordeno por cantidad de apariciones los numeros que han salido historicamente en cada posicion
            lst_tmp = sorted(nums.items(), key=operator.itemgetter(1), reverse=True)

            for i in range(cte.PRIMI_Q_BETS):
                # combinacion de pares e impares
                e_o_comb = e_o_combs[i]  # combinacion de pares e impare a aplicar segun el numero de apuesta
                tipo_e_o = e_o_comb[0][cte.PRIMIFIELDS.index(posic) - 2]  # resto 2 porque los 2 primeros elementos de
                # PRIMIFIELDS son el idx y la fecha del sorteo

                for j in lst_tmp:
                    addNumber = False
                    candidato = j[0]
                    if candidato is None:
                        continue
                    esPar = True if candidato % 2 == 0 else False  # para ver si el candidato es par o impar
                    esValido = (candidato is not None) and (
                            (esPar and tipo_e_o == 'e') or (not esPar and tipo_e_o == 'o'))
                    match posicType:
                        case 0:  # numero que forma parte de la combinacion
                            if (not candidato in last_comb[2:7] and
                                    not candidato in allBetNumbers and
                                    esValido):
                                addNumber = True
                                allBetNumbers.append(candidato)
                        case 1:  # reintegro
                            if (candidato != last_comb[9] and
                                    not candidato in allReintNumbers and
                                    esValido):
                                addNumber = True
                                allReintNumbers.append(candidato)
                    if addNumber:
                        setattr(combsel[i], posic, candidato)
                        break

        return combsel


@dataclass
class EuroComb:
    combDate    : None  = field(init=False)
    n1          : int   = field(init=False)
    n2          : int   = field(init=False)
    n3          : int   = field(init=False)
    n4          : int   = field(init=False)
    n5          : int   = field(init=False)
    e1          : int   = field(init=False)
    e2          : int   = field(init=False)


def make_euromillones_dbclass():
    """Construye la lista con todas las combinaciones de Euromillones
    :returns objeto EuroDB todas las combinaciones de Euromillones
    """

    db_fields = ', '.join(cte.EUROFIELDS[1:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.EUROMILLONES}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    euroCombs = []
    strfmt  = "%Y-%m-%d"
    for comb in combinations:
        auxComb = EuroComb()
        auxComb.combDate    = datetime.datetime.strptime(comb[0], strfmt)
        auxComb.n1          = comb[1]
        auxComb.n2          = comb[2]
        auxComb.n3          = comb[3]
        auxComb.n4          = comb[4]
        auxComb.n5          = comb[5]
        auxComb.e1          = comb[6]
        auxComb.e2          = comb[7]
        euroCombs.append(auxComb)
    # return [PrimiComb(*cmb) for cmb in combinations]
    return euroCombs
    # return [EuroComb(*cmb) for cmb in combinations]


def make_euromartes_dbclass():
    """Construye la lista con todas las combinaciones de euromillones extraídas los martes
    :returns objeto EuroDB todas las combinaciones de euromillones de los martes
    """

    db_fields = ', '.join(cte.EUROFIELDS[2:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.EUROMILLONES} WHERE CAST (strftime("%w", fecha) AS Integer) = {2}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [EuroComb(*cmb) for cmb in combinations]


def make_euroviernes_dbclass():
    """Construye la lista con todas las combinaciones de euromillones extraídas los viernes
    :returns objeto EuroDB todas las combinaciones de euromillones de los viernes
    """

    db_fields = ', '.join(cte.EUROFIELDS[2:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.EUROMILLONES} WHERE CAST (strftime("%w", fecha) AS Integer) = {5}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [EuroComb(*cmb) for cmb in combinations]


@dataclass
class EuroDB:
    combs: List[EuroComb] = field(default_factory=make_euromillones_dbclass)
    # combstue: List[EuroComb] = field(default_factory=make_euromartes_dbclass)
    # combsfri: List[EuroComb] = field(default_factory=make_euroviernes_dbclass)

    def contador(self, combgrp: Union[None, int] = None) -> dict:
        """
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        2 .- combinaciones de los martes
        5 .- combinaciones de los viernes
        :return: diccionario con clave el número de orden en la combinación y valor un diccionario con clave
        número extraído y valor la cantidad de veces que ha salido
        """
        comboptions = {2: self.combstue, 5: self.combsfri}
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        valfreq = {x.name: dict(Counter(getattr(y, x.name) for y in combgrpsel).most_common())
                   for x in fields(EuroComb)}
        return valfreq

    def cuentafreq(self, combgrp: Union[None, int] = None) -> dict:
        """
        Devuelve un diccionario con clave el número de orden en la combinación y valor otro diccionario con claves
        los números extraídos en esa posición y el porcentaje de apariciones
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        2 .- combinaciones de los martes
        5 .- combinaciones de los viernes
        :return: diccionario con clave el número de orden en la combinación y valor otro diccionario con claves
        los números extraídos en esa posición y el porcentaje de apariciones
        """
        comboptions = {cte.EURODAYS[1]: self.combstue, cte.EURODAYS[2]: self.combsfri}
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        q_sorteos = len(combgrpsel)
        valfreq = {x.name: dict(Counter(getattr(y, x.name) for y in combgrpsel).most_common())
                   for x in fields(EuroComb)}
        for k, v in valfreq.items():
            for n, q in v.items():
                # TODO corregir el tipo de dato v[n] para que sea float en lugar de int, que es lo que devuelve
                #  most_common
                v[n] = round(q / q_sorteos * 100, 2)
        return valfreq

    def freq_evolution(self, combgrp: Union[None, int] = None) -> dict:
        """
        analisis de cómo evoluciona la frecuencia de aparición de los números extraídos, sorteo tras sorteo
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        2 .- combinaciones de los martes
        5 .- combinaciones de los viernes
        :return: para cada orden de extracción, lista con el porcentaje de apariciones hasta esa fecha
        """
        comboptions = {2: self.combstue, 5: self.combsfri}
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        freq_evo = {}
        for fld in fields(EuroComb):
            fldname = fld.name
            freq_evo[fldname] = []
            extracted = []
            # Evolución, sorteo a sorteo, de la frecuencia de los números extraídos
            for cmbidx, cmb in enumerate(combgrpsel):
                last_extracted = getattr(cmb, fldname)
                extracted.append(last_extracted)
                freq_evo[fldname].append(round(Counter(extracted).get(last_extracted) / (cmbidx + 1) * 100, 2))
            freq_evo[fldname] = dict(Counter(freq_evo[fldname]).most_common())
        return freq_evo

    def evenodd(self, combgrp: Union[None, int] = None) -> list:
        """
        :return: lista de tuplas con las combinaciones de números pares e impares por orden de extracción,
        ordenado por frecuencia de combinación par-impar y según el sorteo: todos, lunes, jueves o sábado
        """
        comboptions = {2: self.combstue, 5: self.combsfri}  # 2 para los partes, 5 para los viernes
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        combfields = fields(EuroComb)
        e_o_list = []
        for cmb in combgrpsel:
            extraidos = [getattr(cmb, fld.name) for fld in combfields]
            parimpar = []
            for extnum in extraidos:
                if not extnum or extnum % 2 == 0:
                    parimpar.append(cte.EVEN)
                else:
                    parimpar.append(cte.ODD)
            e_o_list.append(tuple(parimpar))
        # eo_count = Counter(e_o_list)
        eo_count = sorted(Counter(e_o_list).items(),
                          key=operator.itemgetter(1),
                          reverse=True)
        return eo_count

    def selcombs(self, combgrp: Union[None, int] = None) -> dict:
        """
        selecciona todas las combinaciones de Euromillones de forma que:
        - los números se ajustan a las combinaciones par-impar más frecuentes, respetando el orden de pares e impares.
        procede de evenodd
        :param combgrp se utiliza para identificar si se analizan todos los sorteos (combgrp=None), o los de M y V
        en los que combgrp vale 2 o 5 respectivamente
        :return: diccionario con el nº de apuesta (0 a 1) como clave, y objeto EuroComb como valor
        """
        if combgrp not in [None, *cte.EURODAYS[1:]]:
            print(f'EuroDB.selcombs: {combgrp} no es válido. Debe ser None, 2 ó 5')
            return {}
        # Obtengo la última combinación extraída
        con = sql_connection(cte.DBDIR + cte.DBFILE)  # conexion a la base de datos de loterias
        last_combs = get_last_comb(con, cte.EUROMILLONES)  # Devuelve las ultimas 5 combinaciones guardadas en
        # db loterias

        #cambio la fecha de cada combinacion extraida por el dia de la semana al que corresponde. lunes=1 y asi
        # hasta domingo 7
        last_comb = []
        if combgrp is None:  # Para el analisis de todas las combinaciones se toma la ultima combinacion extraida
            last_comb = last_combs[0]
        else:
            for i in range(len(last_combs)):  # se toma la ultima combinacion del dia analizado, M o V
                dayOfTheWeek = datetime.datetime.strptime(last_combs[i][1], '%Y-%m-%d').isoweekday()
                if dayOfTheWeek == combgrp:
                    last_comb = last_combs[i]
                    break

        # extraigo el orden par-impar de la ultima combinacion extraida TODO: No lo utilizo
        lastComb_e_o = tuple(map(lambda x: 'e' if x%2 == 0 else 'o', last_comb[2:]))

        # obtengo par-impar. eveodd devuelve un diccionario y la clave es la combinación de pares e impares
        # tomo tantas claves como apuestas se vayan a hacer
        e_o_combs = self.evenodd(combgrp)
        e_o_comb_found = True if lastComb_e_o in [x[0] for x in e_o_combs] else False
        distribApariciones = self.contador(combgrp)  # cantidad de veces que sale cada numero cada dia de la semana
        valEuroCombInit = (100, 100, 100, 100, 100, 100, 100)
        combsel = {c:EuroComb(*valEuroCombInit) for c in range(cte.EURO_Q_BETS)}
        allBetNumbers = []  # guarda todos los numeros seleccionados para las apuestas
        allStarNumbers = []  # guarda todas las estrellas

        for posic, nums in distribApariciones.items():
            isStar = True if posic in cte.EUROFIELDS[7:9] else False  # compruebo si estamos evaluando las estrellas

            # posicType = 0 si posic esta entre n1 a n5 y vale 1 si es una estrella
            posicType = 1 if isStar else 0

            # ordeno por cantidad de apariciones los numeros que han salido historicamente en cada posicion
            lst_tmp = sorted(nums.items(), key=operator.itemgetter(1), reverse=True)

            for i in range(cte.EURO_Q_BETS):
                # combinacion de pares e impares
                e_o_comb = e_o_combs[i]  # combinacion de pares e impares a aplicar segun el numero de apuesta
                tipo_e_o = e_o_comb[0][cte.EUROFIELDS.index(posic) - 2]  # resto 2 porque los 2 primeros elementos de
                # PRIMIFIELDS son el idx y la fecha del sorteo

                for j in lst_tmp:
                    addNumber = False
                    candidato = j[0]
                    if candidato is None:
                        continue
                    esPar = True if candidato % 2 == 0 else False  # para ver si el candidato es par o impar
                    esValido = (candidato is not None) and (
                            (esPar and tipo_e_o == 'e') or (not esPar and tipo_e_o == 'o'))
                    match posicType:
                        case 0:  # numero que forma parte de la combinacion
                            if (not candidato in last_comb[2:6] and
                                    not candidato in allBetNumbers and
                                    esValido):
                                addNumber = True
                                allBetNumbers.append(candidato)
                        case 1:  # reintegro
                            if (not candidato in last_comb[7:8] and
                                    not candidato in allStarNumbers and
                                    esValido):
                                addNumber = True
                                allStarNumbers.append(j[0])
                    if addNumber:
                        setattr(combsel[i], posic, candidato)
                        break
                    elif j == lst_tmp[-1]:  # Se han recorrido todas las opciones y ningún candidato es válido
                        print("OJO, no había ningún número válido. Se toma el candidato")
                        setattr(combsel[i], posic, candidato)
                        print(f"Apuesta: {i} - {posic} = {getattr(combsel[i], posic)} ")
                        # Si el candidato es menor que la posición anterior, intercambio posiciones
                        if candidato < getattr(combsel[i], cte.EUROFIELDS[cte.EUROFIELDS.index(posic)-1]):
                            setattr(combsel[i],
                                    cte.EUROFIELDS[cte.EUROFIELDS.index(posic)],
                                    getattr(combsel[i], cte.EUROFIELDS[cte.EUROFIELDS.index(posic)-1]))
                            setattr(combsel[i],
                                    cte.EUROFIELDS[cte.EUROFIELDS.index(posic)-1],
                                    candidato)
        return combsel
