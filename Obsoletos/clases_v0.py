#!/usr/bin/env python3
# -*- coding: cp1252 -*-

from collections import Counter
from dataclasses import dataclass, field, fields
from typing import List, Union
from bisect import bisect_left
import constants as cte
from db_mgnt import sql_connection

'''
07/02/2024  Versión 0 del módulo Clases.
Lo sustituye el módulo 1
'''
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

    db_fields = ', '.join(cte.PRIMIFIELDS[2:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.PRIMITIVA}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [PrimiComb(*cmb) for cmb in combinations]


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


@dataclass()
class PrimiDB:
    combs: List[PrimiComb] = field(default_factory=make_primitiva_dbclass)  # todas las combinaciones
    combsmon: List[PrimiComb] = field(default_factory=make_primilunes_dbclass)  # combinaciones de los lunes
    combsthr: List[PrimiComb] = field(default_factory=make_primijueves_dbclass)  # combinaciones de los jueves
    combssat: List[PrimiComb] = field(default_factory=make_primisabado_dbclass)  # combinaciones de los sábados

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
                    v[n] = round(q / q_sorteos * 100, 2)
                    valfreqfiltered[k][n] = v[n]

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

    def evenodd(self, combgrp: Union[None, int] = None) -> dict:
        """
        :return: diccionario con las combinaciones de números pares e impares por orden de extracción,
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
        eo_count = Counter(e_o_list)
        return eo_count

    def selcombs(self, combgrp: Union[None, int] = None) -> dict:
        """
        selecciona todas las combinaciones de forma que:
        - los números se ajustan a las combinaciones par-impar más frecuentes, respetando el orden de pares e impares.
        procede de evenodd
        - para cada orden de extracción, se saca la frecuencia más habitual que tenía el número extraído en el momento
        de la extracción. Procede de freq_evolution
        - se busca esa frecuencia para cada orden de extracción a partir de cuentafreq
        :param combgrp se utiliza para identificar si se analizan todos los sorteos (combgrp=None), o los del lunes,
        jueves o sabado, en los que combgrp vale 1, 4 o 6 respectivamente
        :return: diccionario con el nº de apuesta (0 a 4) como clave, y objeto PrimiComb como valor
        """
        if combgrp not in [None, *cte.PRIMIDAYS[1:]]:
            print(f'PrimiDb.selcombs: {combgrp} no es válido. Debe ser None, 1, 4 ó 6')
            return {}
        # Obtengo la última combinación extraída
        comboptions = {1: self.combsmon, 4: self.combsthr, 6: self.combssat}  # 1, lunes; 4, jueves; 6, sábados
        combgrpsel = self.combs if not combgrp else comboptions.get(combgrp)
        last_extracted_comb = list(combgrpsel[-1].__dict__.values())[0:cte.PRIMINUMBERS]  # Números de la última
        # extracción

        # obtengo par-impar. eveodd devuelve un diccionario y la clave es la combinación de pares e impares
        # tomo tantas claves como apuestas se vayan a hacer
        e_o_combs = list(self.evenodd(combgrp))
        frqev = self.freq_evolution(combgrp)  # diccionario con la evolución de la frecuencia de extracción
        qfrq = self.cuentafreq(combgrp)  # diccionario todos los números extraídos en cada orden de extracción y
        # su frecuencia de aparición
        combsel = {}
        allbetnumbers = []
        for apuesta in range(cte.PRIMI_Q_BETS):
            # primera apuesta -> primera combinación de par-impar
            eo = e_o_combs[apuesta]
            # construyo diccionario con los candidatos por orden de extracción, dependiendo de si son par o impar
            candidatos = {}
            bet = []
            for idx, tiponum in enumerate(eo):
                # fieldidx = eo.index(tiponum)
                extorderfield = list(qfrq.keys())[idx]  # n1...n6, comp, reint, None
                fld2anal = qfrq.get(extorderfield)
                # freq2find = list(frqev.get(extorderfield).keys())[idx]
                freq2find = list(frqev.get(extorderfield).keys())[0]
                candidatos[extorderfield] = {k: v for k, v in fld2anal.items()
                                             if ((tiponum == cte.EVEN and
                                                  k and k % 2 == 0) or
                                                 (tiponum == cte.ODD and
                                                  # k and k % 2 != 0)) and
                                                  k and k % 2 != 0) or
                                                 # (idx in [6, 7] or
                                                 idx in [6, 7]) and
                                                  (k not in allbetnumbers and k not in last_extracted_comb)
                                             }
                freqs = sorted(list(candidatos[extorderfield].values()))  # Ordena la frecuenca de candidatos de
                # menor a mayor
                candidate_position = bisect_left(freqs, freq2find)
                if freqs and candidate_position >= len(freqs):
                    # Si la frecuencia buscada es superior a la máxima disponible, se toma la máxima disponible
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

    db_fields = ', '.join(cte.EUROFIELDS[2:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.EUROMILLONES}'

    con = sql_connection(cte.DBDIR + cte.DBFILE)
    cursor = con.cursor()
    cursor.execute(sqlstmt)
    combinations = list(cursor.fetchall())
    return [EuroComb(*cmb) for cmb in combinations]


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

    def evenodd(self, combgrp: Union[None, int] = None) -> dict:
        """
        :return: diccionario con las combinaciones de números pares e impares por orden de extracción,
        ordenado por frecuencia de combinación par-impar
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
        eo_count = Counter(e_o_list)
        return eo_count

    def selcombs(self, combgrp: Union[None, int] = None) -> dict:
        """
        selecciona todas las combinaciones de forma que:
        - los números se ajustan a las combinaciones par-impar más frecuentes, respetando el orden de pares e impares.
        procede de evenodd
        - para cada orden de extracción, se saca la frecuencia más habitual que tenía el número extraído en el momento
        de la extracción. Procede de freq_evolution
        - se busca esa frecuencia para cada orden de extracción a partir de cuentafreq
        :return: diccionario con el nº de apuesta (0 a 1) como clave, y objeto EuroComb como valor
        """
        if combgrp not in [None, *cte.EURODAYS[1:]]:
            print(f'EuroDB.selcombs: {combgrp} no es válido. Debe ser None, 2 ó 5')
            return {}
        # obtengo par-impar. eveodd devuelve un diccionario y la clave es la combinación de pares e impares
        # tomo tantas claves como apuestas se vayan a hacer
        e_o_combs = list(self.evenodd(combgrp))
        frqev = self.freq_evolution(combgrp)  # diccionario con la evolución de la frecuencia de extracción
        qfrq = self.cuentafreq(combgrp)  # diccionario todos los números extraídos en cada orden de extracción y
        # su frecuencia de aparición
        # Obtengo la última combinación extraída
        comboptions = {2: self.combstue, 5: self.combsfri}  # 2 para los partes, 5 para los viernes
        combgrpsel = self.combs if combgrp is None else comboptions.get(combgrp)
        last_extracted_comb = list(combgrpsel[-1].__dict__.values())[0:cte.EURONUMBERS]  # Números de la última
        # extracción
        combsel = {}
        allbetnumbers = []
        allbetstars = []
        for apuesta in range(cte.EURO_Q_BETS):
            # primera apuesta -> primera combinación de par-impar
            eo = e_o_combs[apuesta]
            # construyo diccionario con los candidatos por orden de extracción, dependiendo de si son par o impar
            candidatos = {}
            bet = []
            for idx, tiponum in enumerate(eo):
                extorderfield = list(qfrq.keys())[idx]
                fld2anal = qfrq.get(extorderfield)
                freq2find = list(frqev.get(extorderfield).keys())[0]
                # candidatos[extorderfield] = {k: v for k, v in fld2anal.items() \
                #                              if (tiponum == cte.EVEN and k and k % 2 == 0 and k not in bet) or \
                #                              tiponum == cte.ODD and k and k % 2 != 0 and k not in bet}
                candidatos[extorderfield] = {k: v for k, v in fld2anal.items()
                                             if ((tiponum == cte.EVEN and
                                                  k and k % 2 == 0) or
                                                 (tiponum == cte.ODD and
                                                  # k and k % 2 != 0)) or
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
                #     # Si la frecuencia buscada es superior a la máxima disponible, se toma la máxima disponible
                #     val = freqs[-1]
                # else:
                #     # val = freqs[min(candidate_position, len(freqs) - 1)]
                #     val = freqs[candidate_position] \
                #         if (freqs[candidate_position] - freq2find) < freqs[candidate_position - 1] - freq2find \
                #         else freqs[candidate_position - 1]
                if freqs and candidate_position >= len(freqs):
                    # Si la frecuencia buscada es superior a la máxima disponible, se toma la máxima disponible
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
                        else:  # para que no se repitan los números
                            allbetnumbers.append(k)
                        bet.append(k)
                        break
                else:
                    val2append = list(qfrq[extorderfield].keys())[apuesta]
                    # allbetnumbers.append(val2append)
                    if idx in [5, 6]:  # para que no se repitan las estrellas
                        allbetstars.append(val2append)
                    else:  # para que no se repitan los números
                        allbetnumbers.append(val2append)
                    bet.append(val2append)

            # print(f'selcombs: {candidatos}')
            combsel[apuesta] = EuroComb(*bet)

            # print(f'selcombs:{combsel}')
        return combsel
