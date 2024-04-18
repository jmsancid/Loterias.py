#!
# -*- coding: cp1252 -*-

import os
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass, field, fields
from datetime import datetime
from sqlite3 import Error
from typing import List, Union
from bisect import bisect_left, bisect_right

cur_year = str(datetime.now().year)  # A�o actual para descargar las combinaciones de primitiva
class lotoparams:
    PRIMIFIELDS = ('idx', 'fecha', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'compl', 're')
    EUROFIELDS = ('idx', 'fecha', 'n1', 'n2', 'n3', 'n4', 'n5', 'e1', 'e2')
    PRIMITIVA = 'Primitiva'  # Nombre de la db con todas las combinaciones hist�ricas de Primitiva
    SELPRIMI = 'SelPrimi'  # Nombre de la db con todas las apuestas de Primitiva, identificadas por jueves y s�bado
    SELPRIMITOT = 'SelPrimiTot'  # Nombre de la db con todas las apuestas de Primitiva considerando todos los n�meros,
    # sin separar jueves y s�bados y ordenados por semanas
    PREMIADOSPRIMI = 'PremiadosPrimi'  # Nombre de la db con todas las apuestas de Primitiva que coinciden
    # con alguna premiada anteriormente
    EUROMILLONES = 'Euromillones'  # Nombre de la db con todas las combinaciones hist�ricas de Euromillones,
    # identificados par martes y viernes
    SELEURO = 'SelEuro'  # Nombre de la db con todas las apuestas de Euromillones considerando todos los n�meros,
    # sin separar martes y viernes y ordenados por semanas
    SELEUROTOT = 'SelEuroTot'  # Nombre de la db con todas las apuestas de Euromillones
    PREMIADOSEURO = 'PremiadosEuro'  # Nombre de la db con todas las apuestas de Euromillones que coinciden
    # con alguna premiada anteriormente
    primifile = r'primitiva.xlsx'
    primidir = r'C:/Users/josemanuel.santiago/OneDrive - Uponor Corporation/Documents/JSC/Loterias/Primitiva/'
    eurofile = r'euromillones.xlsx'
    eurodir = r'C:/Users/josemanuel.santiago/OneDrive - Uponor Corporation/Documents/JSC/Loterias/Euromillones/'
    dbfile = r'loterias.db'
    dbdir = r'/home/chema/PycharmProjects/loterias/'
    EUROWEB = 'https://www.euromillones.com.es/resultados-anteriores.html'
    #PRIMIWEB = 'https://www.loterias.com/la-primitiva/resultados/2023'
    PRIMIWEB = 'https://www.loterias.com/la-primitiva/resultados/' + cur_year
    PRIMIDAYS = (46, 1, 4, 6)  # Dias de primitiva. Domingo es d�a 0. Primitiva es lunes, jueves y s�bado: 1, 4 y 6. El 46
    # representa el total de sorteos de primitiva de jueves y s�bado
    EURODAYS = (25, 2, 5)  # Dias de euromillones. Domingo es d�a 0. Euromilones es martes y viernes: 2 y 5. El 25
    # representa el total de sorteos de euromillones de martes y viernes
    PRIMINUMBERS = 6  # Cantidad de numeros que forman una apuesta de primitiva, sin contar complementario y reintegro
    EURONUMBERS = 5  # Cantidad de numeros que forman una apuesta de euromillones, sin contar las estrellas
    primibets = 5  # N� de apuestas de primitiva
    eurobets = 2  # N� de apuestas de euromillones
    Q_NUM_MAS_FREQ = 10  # Cantidad de n�meros seleccionados en la lista de m�s frecuentes
    EVEN = 'e'
    ODD = 'o'


@dataclass()
class PrimiComb:
    n1: int
    n2: int
    n3: int
    n4: int
    n5: int
    n6: int
    comp: int = field(repr=False)
    reint: Union[int, None]


def make_primitiva_dbclass():
    """Construye la lista con todas las combinaciones de primitiva
    :returns objeto PrimiDB todas las combinaciones de primitiva
    """

    fields = ', '.join(lotoparams.PRIMIFIELDS[2:])
    sqlstmt = f'SELECT {fields} FROM {lotoparams.PRIMITIVA}'

    con = sql_connection()
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [PrimiComb(*cmb) for cmb in combinations]


def make_primilunes_dbclass():
    """Construye la lista con todas las combinaciones de primitiva extra�das los lunes
    :returns objeto PrimiDB todas las combinaciones de primitiva de los lunes
    """

    fields = ', '.join(lotoparams.PRIMIFIELDS[2:])
    sqlstmt = f'SELECT {fields} FROM {lotoparams.PRIMITIVA} WHERE CAST (strftime("%w", fecha) AS Integer) = {1}'

    con = sql_connection()
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [PrimiComb(*cmb) for cmb in combinations]


def make_primijueves_dbclass():
    """Construye la lista con todas las combinaciones de primitiva extra�das los jueves
    :returns objeto PrimiDB todas las combinaciones de primitiva de los jueves
    """

    fields = ', '.join(lotoparams.PRIMIFIELDS[2:])
    sqlstmt = f'SELECT {fields} FROM {lotoparams.PRIMITIVA} WHERE CAST (strftime("%w", fecha) AS Integer) = {4}'

    con = sql_connection()
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [PrimiComb(*cmb) for cmb in combinations]


def make_primisabado_dbclass():
    """Construye la lista con todas las combinaciones de primitiva
    :returns objeto PrimiDB todas las combinaciones de primitiva
    """

    fields = ', '.join(lotoparams.PRIMIFIELDS[2:])
    sqlstmt = f'SELECT {fields} FROM {lotoparams.PRIMITIVA} WHERE CAST (strftime("%w", fecha) AS Integer) = {6}'

    con = sql_connection()
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [PrimiComb(*cmb) for cmb in combinations]


@dataclass()
class PrimiDB:
    combs: List[PrimiComb] = field(default_factory=make_primitiva_dbclass)  # todas las combinaciones
    combsmon: List[PrimiComb] = field(default_factory=make_primilunes_dbclass)  # combinaciones de los lunes
    combsthr: List[PrimiComb] = field(default_factory=make_primijueves_dbclass)  # combinaciones de los jueves
    combssat: List[PrimiComb] = field(default_factory=make_primisabado_dbclass)  # combinaciones de los s�bados

    def contador(self, combgrp: Union[None, int] = None) -> dict:
        """
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        1 .- combinaciones de los lunes
        4 .- combinaciones de los jueves
        6 .- combinaciones de los s�bados
        :return: diccionario con clave el n�mero de orden en la combinaci�n y valor un diccionario con clave
        n�mero extra�do y valor la cantidad de veces que ha salido ordenado por n� de veces extra�do
        """
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, s�bados
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        valfreq = {x.name: dict(Counter(getattr(y, x.name) for y in combgrpsel).most_common())
                   for x in fields(PrimiComb)}
        return valfreq


    def cuentafreq(self, combgrp: Union[None, int] = None) -> dict:
        """
        Devuelve un diccionario con clave el n�mero de orden en la combinaci�n y valor otro diccionario con claves
        los n�meros extra�dos en esa posici�n y el porcentaje de apariciones
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        1 .- combinaciones de los lunes
        4 .- combinaciones de los jueves
        6 .- combinaciones de los s�bados
        :return: diccionario con clave el n�mero de orden en la combinaci�n y valor otro diccionario con claves
        los n�meros extra�dos en esa posici�n y el porcentaje de apariciones
        """
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, s�bados
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        q_sorteos = len(combgrpsel)
        valfreq = {x.name: dict(Counter(getattr(y, x.name) for y in combgrpsel).most_common())
                   for x in fields(PrimiComb)}
        valfreqfiltered={}
        for k, v in valfreq.items():
            valfreqfiltered[k] = {}
            for n, q in v.items():
                if not n is None:  # Para excluir los sorteos en los que no hab�a reintegro
                    valfreqfiltered[k][n] = {}
                    v[n] = round(q / q_sorteos * 100, 2)
                    valfreqfiltered[k][n] = v[n]

        return valfreqfiltered

    def freq_evolution(self, combgrp: Union[None, int] = None) -> dict:
        """
        Analisis de c�mo evoluciona la frecuencia de aparici�n de los n�meros extra�dos, sorteo tras sorteo
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        1 .- combinaciones de los lunes
        4 .- combinaciones de los jueves
        6 .- combinaciones de los s�bados
        :return: para cada orden de extracci�n, lista con el porcentaje de apariciones hasta esa fecha
        """
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, s�bados
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

    def evenodd(self, combgrp: Union[None, int] = None) -> dict:
        """
        :return: diccionario con las combinaciones de n�meros pares e impares por orden de extracci�n,
        ordenado por frecuencia de combinaci�n par-impar y seg�n el sorteo: todos, lunes, jueves o s�bado
        """
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, s�bados
        combgrpsel = self.combs if not combgrp else comboptions.get(combgrp)
        combfields = fields(PrimiComb)
        e_o_list = []
        for cmb in combgrpsel:
            extraidos = [getattr(cmb, fld.name) for fld in combfields]
            parimpar = []
            for extnum in extraidos:
                if not extnum or extnum % 2 == 0:
                    parimpar.append(lotoparams.EVEN)
                else:
                    parimpar.append(lotoparams.ODD)
            e_o_list.append(tuple(parimpar))
        eo_count = Counter(e_o_list)
        return eo_count

    def selcombs(self, combgrp: Union[None, int] = None) -> dict:
        """
        selecciona todas las combinaciones de forma que:
        - los n�meros se ajustan a las combinaciones par-impar m�s frecuentes, respetando el orden de pares e impares.
        procede de evenodd
        - para cada orden de extracci�n, se saca la frecuencia m�s habitual que ten�a el n�mero extra�do en el momento
        de la extracci�n. Procede de freq_evolution
        - se busca esa frecuencia para cada orden de extracci�n a partir de cuentafreq
        :return: diccionario con el n� de apuesta (0 a 4) como clave, y objeto PrimiComb como valor
        """
        if combgrp not in [None, *lotoparams.PRIMIDAYS[1:]]:
            print(f'PrimiDb.selcombs: {combgrp} no es v�lido. Debe ser None, 1, 4 � 6')
            return {}
        # Obtengo la �ltima combinaci�n extra�da
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, s�bados
        combgrpsel = self.combs if not combgrp else comboptions.get(combgrp)
        last_extracted_comb = list(combgrpsel[-1].__dict__.values())[0:lotoparams.PRIMINUMBERS]  # N�meros de la �ltima
        # extracci�n

        # obtengo par-impar. eveodd devuelve un diccionario y la clave es la combinaci�n de pares e impares
        # tomo tantas claves como apuestas se vayan a hacer
        e_o_combs = list(self.evenodd(combgrp))
        frqev = self.freq_evolution(combgrp)  # diccionario con la evoluci�n de la frecuencia de extracci�n
        qfrq = self.cuentafreq(combgrp)  # diccionario todos los n�meros extra�dos en cada orden de extracci�n y
        # su frecuencia de aparici�n
        combsel = {}
        allbetnumbers = []
        for apuesta in range(lotoparams.primibets):
            # primera apuesta -> primera combinaci�n de par-impar
            eo = e_o_combs[apuesta]
            # construyo diccionario con los candidatos por orden de extracci�n, dependiendo de si son par o impar
            candidatos = {}
            bet = []
            for idx, tiponum in enumerate(eo):
                # fieldidx = eo.index(tiponum)
                extorderfield = list(qfrq.keys())[idx]  # n1...n6, comp, reint, None
                fld2anal = qfrq.get(extorderfield)
                # freq2find = list(frqev.get(extorderfield).keys())[idx]
                freq2find = list(frqev.get(extorderfield).keys())[0]
                candidatos[extorderfield] = {k: v for k, v in fld2anal.items() \
                                             if ((tiponum == lotoparams.EVEN and
                                                 k and k % 2 == 0) or
                                             (tiponum == lotoparams.ODD and
                                              k and k % 2 != 0)) and
                                             (idx in [6, 7] or
                                              (k not in allbetnumbers and k not in last_extracted_comb))
                                             }
                freqs = sorted(list(candidatos[extorderfield].values()))  # Ordena la frecuenca de candidatos de
                # menor a mayor
                candidate_position = bisect_left(freqs, freq2find)
                if freqs and candidate_position >= len(freqs):
                    # Si la frecuencia buscada es superior a la m�xima disponible, se toma la m�xima disponible
                    val = freqs[-1]
                elif not freqs:
                    # val = freqs[0]
                    val = list(frqev[extorderfield].keys())[0]
                else:
                    # val = freqs[min(candidate_position, len(freqs) - 1)]
                    val = freqs[candidate_position] \
                        if (freqs[candidate_position] - freq2find) < freqs[candidate_position - 1] - freq2find \
                        else freqs[candidate_position - 1]
                if candidatos[extorderfield]:
                    for k, v in candidatos[extorderfield].items():
                        allbetnumbers.append(k)
                        bet.append(k)
                        break
                else:
                    val2append = list(qfrq[extorderfield].keys())[apuesta]
                    allbetnumbers.append(val2append)
                    bet.append(val2append)
            # print(f'selcombs: {candidatos}')
            combsel[apuesta] = PrimiComb(*bet)

            # print(f'selcombs:{combsel}')
        return combsel


@dataclass()
class EuroComb:
    n1: int
    n2: int
    n3: int
    n4: int
    n5: int
    e1: int
    e2: int


def make_euromillones_dbclass():
    """Construye la lista con todas las combinaciones de Euromillones
    :returns objeto EuroDB todas las combinaciones de Euromillones
    """

    fields = ', '.join(lotoparams.EUROFIELDS[2:])
    sqlstmt = f'SELECT {fields} FROM {lotoparams.EUROMILLONES}'

    con = sql_connection()
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [EuroComb(*cmb) for cmb in combinations]


def make_euromartes_dbclass():
    """Construye la lista con todas las combinaciones de euromillones extra�das los martes
    :returns objeto EuroDB todas las combinaciones de euromillones de los martes
    """

    fields = ', '.join(lotoparams.EUROFIELDS[2:])
    sqlstmt = f'SELECT {fields} FROM {lotoparams.EUROMILLONES} WHERE CAST (strftime("%w", fecha) AS Integer) = {2}'

    con = sql_connection()
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [EuroComb(*cmb) for cmb in combinations]


def make_euroviernes_dbclass():
    """Construye la lista con todas las combinaciones de euromillones extra�das los viernes
    :returns objeto EuroDB todas las combinaciones de euromillones de los viernes
    """

    fields = ', '.join(lotoparams.EUROFIELDS[2:])
    sqlstmt = f'SELECT {fields} FROM {lotoparams.EUROMILLONES} WHERE CAST (strftime("%w", fecha) AS Integer) = {5}'

    con = sql_connection()
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [EuroComb(*cmb) for cmb in combinations]


@dataclass()
class EuroDB:
    combs: List[EuroComb] = field(default_factory=make_euromillones_dbclass)
    combstue: List[EuroComb] = field(default_factory=make_euromartes_dbclass)
    combsfri: List[EuroComb] = field(default_factory=make_euroviernes_dbclass)

    def contador(self, combgrp: Union[None, int] = None) -> dict:
        """
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        2 .- combinaciones de los martes
        5 .- combinaciones de los viernes
        :return: diccionario con clave el n�mero de orden en la combinaci�n y valor un diccionario con clave
        n�mero extra�do y valor la cantidad de veces que ha salido
        """
        comboptions = {2: self.combstue, 5: self.combsfri}
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        valfreq = {x.name: dict(Counter(getattr(y, x.name) for y in combgrpsel).most_common())
                   for x in fields(EuroComb)}
        return valfreq


    def cuentafreq(self, combgrp: Union[None, int] = None) -> dict:
        """
        Devuelve un diccionario con clave el n�mero de orden en la combinaci�n y valor otro diccionario con claves
        los n�meros extra�dos en esa posici�n y el porcentaje de apariciones
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        2 .- combinaciones de los martes
        5 .- combinaciones de los viernes
        :return: diccionario con clave el n�mero de orden en la combinaci�n y valor otro diccionario con claves
        los n�meros extra�dos en esa posici�n y el porcentaje de apariciones
        """
        comboptions = {lotoparams.EURODAYS[1]: self.combstue, lotoparams.EURODAYS[2]: self.combsfri}
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        q_sorteos = len(combgrpsel)
        valfreq = {x.name: dict(Counter(getattr(y, x.name) for y in combgrpsel).most_common())
                   for x in fields(EuroComb)}
        for k, v in valfreq.items():
            for n, q in v.items():
                v[n] = round(q / q_sorteos * 100, 2)
        return valfreq


    def freq_evolution(self, combgrp: Union[None, int] = None) -> dict:
        """
        analisis de c�mo evoluciona la frecuencia de aparici�n de los n�meros extra�dos, sorteo tras sorteo
        :type combgrp: Valores posibles:
        None .- todas las combinaciones,
        2 .- combinaciones de los martes
        5 .- combinaciones de los viernes
        :return: para cada orden de extracci�n, lista con el porcentaje de apariciones hasta esa fecha
        """
        comboptions = {2: self.combstue, 5: self.combsfri}
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        freq_evo = {}
        for fld in fields(EuroComb):
            fldname = fld.name
            freq_evo[fldname] = []
            extracted = []
            # Evoluci�n, sorteo a sorteo, de la frecuencia de los n�meros extra�dos
            for cmbidx, cmb in enumerate(combgrpsel):
                last_extracted = getattr(cmb, fldname)
                extracted.append(last_extracted)
                freq_evo[fldname].append(round(Counter(extracted).get(last_extracted) / (cmbidx+1) * 100, 2))
            freq_evo[fldname] = dict(Counter(freq_evo[fldname]).most_common())
        return freq_evo


    def evenodd(self, combgrp: Union[None, int] = None) -> dict:
        """
        :return: diccionario con las combinaciones de n�meros pares e impares por orden de extracci�n,
        ordenado por frecuencia de combinaci�n par-impar
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
                    parimpar.append(lotoparams.EVEN)
                else:
                    parimpar.append(lotoparams.ODD)
            e_o_list.append(tuple(parimpar))
        eo_count = Counter(e_o_list)
        return eo_count


    def selcombs(self, combgrp: Union[None, int] = None) -> dict:
        """
        selecciona todas las combinaciones de forma que:
        - los n�meros se ajustan a las combinaciones par-impar m�s frecuentes, respetando el orden de pares e impares.
        procede de evenodd
        - para cada orden de extracci�n, se saca la frecuencia m�s habitual que ten�a el n�mero extra�do en el momento
        de la extracci�n. Procede de freq_evolution
        - se busca esa frecuencia para cada orden de extracci�n a partir de cuentafreq
        :return: diccionario con el n� de apuesta (0 a 1) como clave, y objeto EuroComb como valor
        """
        if combgrp not in [None, *lotoparams.EURODAYS[1:]]:
            print(f'EuroDB.selcombs: {combgrp} no es v�lido. Debe ser None, 2 � 5')
            return {}
        # obtengo par-impar. eveodd devuelve un diccionario y la clave es la combinaci�n de pares e impares
        # tomo tantas claves como apuestas se vayan a hacer
        e_o_combs = list(self.evenodd(combgrp))
        frqev = self.freq_evolution(combgrp)  # diccionario con la evoluci�n de la frecuencia de extracci�n
        qfrq = self.cuentafreq(combgrp)  # diccionario todos los n�meros extra�dos en cada orden de extracci�n y
        # su frecuencia de aparici�n
        # Obtengo la �ltima combinaci�n extra�da
        comboptions = {2: self.combstue, 5: self.combsfri}  # 2 para los partes, 5 para los viernes
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        last_extracted_comb = list(combgrpsel[-1].__dict__.values())[0:lotoparams.EURONUMBERS]  # N�meros de la �ltima
        # extracci�n
        combsel = {}
        allbetnumbers = []
        allbetstars = []
        for apuesta in range(lotoparams.eurobets):
            # primera apuesta -> primera combinaci�n de par-impar
            eo = e_o_combs[apuesta]
            # construyo diccionario con los candidatos por orden de extracci�n, dependiendo de si son par o impar
            candidatos = {}
            bet = []
            for idx, tiponum in enumerate(eo):
                extorderfield = list(qfrq.keys())[idx]
                fld2anal = qfrq.get(extorderfield)
                freq2find = list(frqev.get(extorderfield).keys())[0]
                # candidatos[extorderfield] = {k: v for k, v in fld2anal.items() \
                #                              if (tiponum == lotoparams.EVEN and k and k % 2 == 0 and k not in bet) or \
                #                              tiponum == lotoparams.ODD and k and k % 2 != 0 and k not in bet}
                candidatos[extorderfield] = {k: v for k, v in fld2anal.items() \
                                             if ((tiponum == lotoparams.EVEN and
                                                 k and k % 2 == 0) or
                                             (tiponum == lotoparams.ODD and
                                              k and k % 2 != 0)) and
                                             ((idx not in [5, 6] and
                                               k not in allbetnumbers and
                                               k not in last_extracted_comb) or
                                             (idx in [5, 6] and k not in allbetstars))
                                             }
                freqs = sorted(list(candidatos[extorderfield].values()))  # Ordena la frecuenca de candidatos de
                # menor a mayor

                candidate_position = bisect_left(freqs, freq2find)
                # if candidate_position >= len(freqs):
                #     # Si la frecuencia buscada es superior a la m�xima disponible, se toma la m�xima disponible
                #     val = freqs[-1]
                # else:
                #     # val = freqs[min(candidate_position, len(freqs) - 1)]
                #     val = freqs[candidate_position] \
                #         if (freqs[candidate_position] - freq2find) < freqs[candidate_position - 1] - freq2find \
                #         else freqs[candidate_position - 1]
                if freqs and candidate_position >= len(freqs):
                    # Si la frecuencia buscada es superior a la m�xima disponible, se toma la m�xima disponible
                    val = freqs[-1]
                elif not freqs:
                    # val = freqs[0]
                    val = list(frqev[extorderfield].keys())[0]
                else:
                    # val = freqs[min(candidate_position, len(freqs) - 1)]
                    val = freqs[candidate_position] \
                        if (freqs[candidate_position] - freq2find) < freqs[candidate_position - 1] - freq2find \
                        else freqs[candidate_position - 1]


                # val = freqs[min(len(freqs)-1, bisect_left(freqs, freq2find))]
                # for k, v in candidatos[extorderfield].items():
                #     if v == val:
                #         bet.append(k)
                #         break
                if candidatos[extorderfield]:
                    for k, v in candidatos[extorderfield].items():
                        if idx in [5, 6]:  # para que no se repitan las estrellas
                            allbetstars.append(k)
                        else:  # para que no se repitan los n�meros
                            allbetnumbers.append(k)
                        bet.append(k)
                        break
                else:
                    val2append = list(qfrq[extorderfield].keys())[apuesta]
                    # allbetnumbers.append(val2append)
                    if idx in [5, 6]:  # para que no se repitan las estrellas
                        allbetstars.append(val2append)
                    else:  # para que no se repitan los n�meros
                        allbetnumbers.append(val2append)
                    bet.append(val2append)


            # print(f'selcombs: {candidatos}')
            combsel[apuesta] = EuroComb(*bet)

            # print(f'selcombs:{combsel}')
        return combsel


def sql_connection():
    """
    Conexi�n a la base de datos de loter�as
    :return: conexi�n a la base de datos
    """
    con = None
    try:
        con = sqlite3.connect(lotoparams.dbdir + lotoparams.dbfile)
        return con
    except Error:
        con.close()
        print('Error abriendo base de datos en sql_connection')
        print(Error)


def sql_table(con, tabla):
    """
    funci�n para insertar tablas en la db de loterias
    :param con: conexi�n a base de datos
    :param tabla: tabla a crear
    :return:
    """
    campos = None  # Inicializo los campos
    if tabla == lotoparams.PRIMITIVA:
        campos = list(zip(lotoparams.PRIMIFIELDS,
                          list(map(lambda x: 'date' if x == 'fecha' else 'integer', lotoparams.PRIMIFIELDS))))
    elif tabla == lotoparams.EUROMILLONES:
        campos = list(zip(lotoparams.EUROFIELDS,
                          list(map(lambda x: 'date' if x == 'fecha' else 'integer', lotoparams.EUROFIELDS))))

    sqlorder = f'CREATE TABLE if not exists {tabla}('
    primercampo = True
    # construimos la tabla con sus campos
    for campo in campos:
        print('sql_table', campo)
        if primercampo:
            sqlorder += f'{campo[0]} {campo[1]} PRIMARY KEY'
            primercampo = False
        else:
            sqlorder += f', {campo[0]} {campo[1]}'
    sqlorder += ')'
    cursorObj = con.cursor()  # objeto cursor sqlite3
    # print('sql_table: ', sqlorder)
    cursorObj.execute(sqlorder)
    con.commit()


def sql_insert(con, tabla, campos, valores):
    cursorObj = con.cursor()
    vals = '?' + ', ?' * (len(campos) - 1)
    campos2insert = ', '.join(campos)
    sqlstmt = f'INSERT INTO {tabla}({campos2insert}) VALUES({vals})'
    # for campo in campos:
    #     if campos.index(campo) < len(campos) - 1:
    #         sqlstmt += f'{campo}, '
    #     else:
    #         sqlstmt += f'{campo}) VALUES({vals})'

    # print('sql_insert', sqlstmt, valores)
    try:
        cursorObj.execute(sqlstmt, valores)
        con.commit()
        print('Registro insertado (sql_insert)')
    except Error:
        print('Error insertando registro en sql_insert')


def sql_find(con, tabla, campo, valor):
    cursorObj = con.cursor()
    sqlorder = f'SELECT * FROM {tabla} WHERE {campo}="{valor}"'

    # print('sql_find', sqlorder)
    cursorObj.execute(sqlorder)
    registro = cursorObj.fetchall()
    return registro


def sql_recordcount(con, tabla):
    """
    devuelve el n�mero de registros de una tabla
    :param con:
    :param tabla:
    :return:
    """
    cursorObj = con.cursor()
    cursorObj.execute(f'SELECT * FROM {tabla}')
    q_registros = len(cursorObj.fetchall())
    return q_registros


def sql_getcolumn(con, tabla, campos, dias=(x for x in range(7)), ):
    """
    devuelve los valores de las campos seleccionados en las fechas seleccionadas
    en el campo dias. dia 0 es domingo, dia 6 es s�bado. Ojo, domingo puede ser 0 � 7, pero no afecta.
    :param con: conexi�n a base de datos sqlite3
    :param tabla: datos de las loterias
    :param dias: dias seleccionados para el sorteo
    :param campos: campos de la base de datos
    :return: diccionario con el campo como clave y una lista con los datos selecconados como valor
    """

    cursorObj = con.cursor()
    if isinstance(campos, (list, tuple)):
        sqlcampos = ', '.join(campos)
    else:
        sqlcampos = campos
        campos = [campos, ]

    if not isinstance(dias, (list, tuple)):
        sqlcommand = f'SELECT {sqlcampos} FROM {tabla} WHERE CAST (strftime("%w", fecha) AS Integer) = {dias}'
    else:
        sqlcommand = f'SELECT {sqlcampos} FROM {tabla} WHERE CAST (strftime("%w", fecha) AS Integer) in {dias}'

    try:
        cursorObj.execute(sqlcommand)
        valores = cursorObj.fetchall()
        valores = {campo: [val[campos.index(campo)] for val in valores] for campo in campos}
        # print(f'{len(valores)} valores encontrados', valores)
        return valores
    except Error:
        print(f'Error recuperando datos de campo {campos}')


def sql_get_value_in_column(con, tabla, campo1, campo2, valor_campo1, dias=(x for x in range(7)), ):
    """
    devuelve los valores de las campos seleccionados en las fechas seleccionadas
    en el campo dias. dia 0 es domingo, dia 6 es s�bado
    :param con: conexi�n a base de datos sqlite3
    :param tabla: datos de las loterias
    :param campo1: campo de la base de datos en el que buscar valor_campo1
    :param campo2: campo de la base de datos de registros con campo1 = valor_campo1
    :param valor_campo1: valor a buscar en campo1
    :param dias: dias seleccionados para el sorteo
    :return: lista con los datos selecconados
    """

    if tabla == lotoparams.PRIMITIVA:
        campos = lotoparams.PRIMIFIELDS
    elif tabla == lotoparams.EUROMILLONES:
        campos = lotoparams.EUROFIELDS
    else:
        print('Analiza: Base de datos no encontrada')
        raise FileNotFoundError

    # Compruebo si los campos son v�lidos
    campovalido = True
    if campo1 not in campos:
        print(f'{campo1} no es un campo v�lido en {tabla}')
        campovalido = False
    if campo2 not in campos:
        print(f'{campo2} no es un campo v�lido en {tabla}')
        campovalido = False
    if not campovalido:
        print('sql_get_value_in_column: Saliendo de la aplicaci�n por campos inv�lidos')
        sys.exit()

    # campoidx = campos.index(campo1)
    # nextcampo = campoidx + 1
    # if nextcampo > len(campos) - 1:
    #     print(f'sql_get_value_in_column: Superado el n�mero de campos, {nextcampo} debe ser <= {len(campos)}')
    #     nextcampo = campoidx

    cursorObj = con.cursor()
    sqlcommand = f'SELECT {campo2} FROM {tabla} WHERE ' \
                 + f'(CAST (strftime("%w", fecha) AS Integer) = {dias} AND ' \
                 + f'{campo1} = {valor_campo1})'

    cursorObj.execute(sqlcommand)
    valores = cursorObj.fetchall()
    valores = {campo2: [val[0] for val in valores]}
    # print(f'{len(valores)} valores encontrados', valores)
    return valores


def sql_getcolumnname(con, tabla):
    cur = con.cursor()
    cursor = cur.execute(f"SELECT * FROM {tabla};")
    names = list(map(lambda x: x[0], cursor.description))
    return names


def sql_checkifexists(con, tabla, valores, campos=None):
    """
    comprueba si en la tabla "tabla" existe alg�n registro con la combinaci�n de valores "valores"
    :param con: conexi�n de base de datos de sqlite3
    :param tabla: tabla en la que buscar
    :param valores: combinaci�n de valores de campos a buscar
    :param campos: lista de campos en los que buscar los valores
    :return: tupla con valor True y el valor encontrado si existe
            False si no existe
    """
    if not campos:
        campos = sql_getcolumnname(con, tabla)

    if len(campos) != len(valores):
        print(f'{sys.modules[__name__]}: El n� de campos de {tabla} no coincide con la cantidad de valores')
        return False, None

    sql_command = f'SELECT * FROM {tabla} WHERE {campos[0]}="{valores[0]}" '
    for campo in campos[1:]:
        idx = campos.index(campo)
        sql_command += f'AND {campo}={valores[idx]} '
    # print('checkifexists: ', sql_command)
    cursor = con.cursor()
    cursor.execute(sql_command)
    exist = cursor.fetchone()
    if not exist:
        return False, None
    else:
        print(f'checkifexists: el registro ({valores}) ya existe')
        return True, exist


def get_most_freq(tabla: dict, q_num: int = lotoparams.Q_NUM_MAS_FREQ):
    """
    lista ordenada en funci�n de la frecuencia de aparici�n de los n�meros que componen las listas de valores
    de cada campo clave
    :param tabla: diccionario con los campos de los sorteos como clave y las listas con los n�meros que han salido
    :param q_num: cantidad de n�meros a tomar en la lista de m�s frecuentes
    :return: diccionario con las mismas claves que la tabla y los valores ser�n una lista de n�meros, ordenados por su
    frecuencia de aparici�n
    """
    tabla_by_freq = {}
    for clave in tabla:
        # len_clave = len(list(Counter(tabla[clave])))
        clave_by_freq = Counter(tabla[clave]).most_common(q_num)
        clave_by_freq = [num[0] for num in clave_by_freq if num[0]][:q_num]
        tabla_by_freq[clave] = clave_by_freq

    return tabla_by_freq


if __name__ == '__main__':
    con = sql_connection()
    # Creando estructura de las base de datos de primitiva y euromillones
    sql_table(con, lotoparams.PRIMITIVA)
    sql_table(con, lotoparams.EUROMILLONES)
    con.close()
