#!/usr/bin/env python3
# -*- coding: cp1252 -*-

import constants as cte
from dbMgnt import sqlConnection, Error

from datetime import datetime
from dataclasses import dataclass, field, fields
from typing import List, Union

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
    combDate    : datetime.date = field(init=False)
    n1          : int = field(init=False)
    n2          : int = field(init=False)
    n3          : int = field(init=False)
    n4          : int = field(init=False)
    n5          : int = field(init=False)
    n6          : int = field(init=False)
    comp        : int = field(init=False, repr=False)
    re          : Union[int, None] = field(init=False)
    
    def __eq__(self, other):
        """
        devuelve True si 2 combinaciones son iguales sin tener en cuenta el complementario
        :param other: combinación de primitiva  
        :return: True si todos los campos excepto comp coinciden. False en cualquier otro caso
        """
        # como de momento no tengo los campos ordenados, los tengo que ordenar aquí
        numself = sorted(n for n in (self.n1, self.n2, self.n3, self.n4, self.n5, self.n6))
        numother = sorted(n for n in (other.n1, other.n2, other.n3, other.n4, other.n5, other.n6))
        iguales = self.combDate == other.combDate and \
                  numself == numother and \
                  self.re == other.re
        return iguales

    def compara_sin_fecha(self, otra_comb):
        """
        devuelve True si 2 combinaciones son iguales sin tener en cuenta la fecha ni el complementario
        :param otra_comb: combinación de primitiva  
        :return: True si todos los campos excepto combDate y comp coinciden. False en cualquier otro caso
        """
        # como los campos podrían no estar ordenados, los tengo que ordenar aquí
        numself = sorted((self.n1, self.n2, self.n3, self.n4, self.n5, self.n6))
        numother = sorted((otra_comb.n1, otra_comb.n2, otra_comb.n3, otra_comb.n4, otra_comb.n5, otra_comb.n6))
        iguales = [*numself, self.re] == [*numother, otra_comb.re]
        return iguales


    def ordena(self):
        """
        ordena de menor a mayor los números de primitiva
        :return: 0 no hay problemas en la ordenación
        """
        num_ordenados  = sorted((self.n1, self.n2, self.n3, self.n4, self.n5, self.n6))
        self.n1, self.n2, self.n3, self.n4, self.n5, self.n6  = num_ordenados
        return 0


def makePrimitivaDbClass():
    """Construye la lista con todas las combinaciones de primitiva
    :returns objeto PrimiDB todas las combinaciones de primitiva
    """

    # db_fields = ', '.join(cte.PRIMIFIELDS[2:])    # sólo números
    db_fields = ', '.join(cte.PRIMIFIELDS[1:])      # números y fecha de la combinación
    sqlstmt = f'SELECT {db_fields} FROM {cte.PRIMITIVA}'

    con = None
    try:
        con = sqlConnection(cte.DBDIR + cte.DBFILE)
        cursor = con.cursor()
        cursor.execute(sqlstmt)

        combinations = list(cursor.fetchall())
        primiCombs = []
        strfmt  = "%Y-%m-%d"
        for comb in combinations:
            auxComb = PrimiComb()
            auxComb.combDate    = datetime.strptime(comb[0], strfmt).date()
            auxComb.n1          = comb[1]
            auxComb.n2          = comb[2]
            auxComb.n3          = comb[3]
            auxComb.n4          = comb[4]
            auxComb.n5          = comb[5]
            auxComb.n6          = comb[6]
            auxComb.comp        = comb[7]
            auxComb.re          = comb[8]

            try:
                auxComb.ordena()
                primiCombs.append(auxComb)
            except Exception as e:
                print(f"Error: {e}\n{auxComb}")
        # return [PrimiComb(*cmb) for cmb in combinations]
        return primiCombs

    except Error:
        print('makePrimitivaDbClass: Error creando la base de datos con todos los PrimiCombs', Error)

    con.close()


@dataclass
class PrimiDB:
    combs: List[PrimiComb] = field(default_factory=makePrimitivaDbClass)  # todas las combinaciones


@dataclass
class EuroComb:
    combDate    : datetime.date  = field(init=False)
    n1          : int   = field(init=False)
    n2          : int   = field(init=False)
    n3          : int   = field(init=False)
    n4          : int   = field(init=False)
    n5          : int   = field(init=False)
    e1          : int   = field(init=False)
    e2          : int   = field(init=False)

    def __eq__(self, other):
        """
        devuelve True si 2 combinaciones son iguales sin tener en cuenta el complementario
        :param other: combinación de primitiva  
        :return: True si todos los campos excepto comp coinciden. False en cualquier otro caso
        """
        
        # como de momento no tengo los campos ordenados, los tengo que ordenar aquí
        numself = sorted(n for n in (self.n1, self.n2, self.n3, self.n4, self.n5))
        numother = sorted(n for n in (other.n1, other.n2, other.n3, other.n4, other.n5))
        starself = sorted(n for n in (self.e1, self.e2))
        starother = sorted(n for n in (other.e1, other.e2))
        iguales = self.combDate == other.combDate and \
                  numself == numother and \
                  starself == starother
        return iguales

    def compara_sin_fecha(self, otra_comb):
        """
        devuelve True si 2 combinaciones son iguales sin tener en cuenta la fecha
        :param otra_comb: combinación de euromillón
        :return: True si todos los campos excepto combDate coinciden. False en cualquier otro caso
        """
        # como los campos podrían no estar ordenados, los tengo que ordenar aquí
        numself = sorted((self.n1, self.n2, self.n3, self.n4, self.n5))
        starself = sorted((self.e1, self.e2))
        numother = sorted((otra_comb.n1, otra_comb.n2, otra_comb.n3, otra_comb.n4, otra_comb.n5))
        starother = sorted((otra_comb.e1, otra_comb.e2))
        iguales = [*numself, *starself] == [*numother, *starother]
        return iguales


    def ordena(self):
        """
        ordena de menor a mayor los números de euromillón y las estrellas
        :return: 0 no hay problemas en la ordenación
        """
        num_ordenados  = sorted((self.n1, self.n2, self.n3, self.n4, self.n5))
        self.n1, self.n2, self.n3, self.n4, self.n5  = num_ordenados
        estrellas_ordenadas = sorted((self.e1, self.e2))
        self.e1, self.e2 = estrellas_ordenadas
        return 0


def makeEuromillonesDbClass():
    """Construye la lista con todas las combinaciones de Euromillones
    :returns objeto EuroDB todas las combinaciones de Euromillones
    """

    db_fields = ', '.join(cte.EUROFIELDS[1:])
    sqlstmt = f'SELECT {db_fields} FROM {cte.EUROMILLONES}'

    con = None
    try:
        con = sqlConnection(cte.DBDIR + cte.DBFILE)
        cursor = con.cursor()
        cursor.execute(sqlstmt)
        combinations = list(cursor.fetchall())
        euroCombs = []
        strfmt  = "%Y-%m-%d"
        for comb in combinations:
            auxComb = EuroComb()
            auxComb.combDate    = datetime.strptime(comb[0], strfmt).date()
            auxComb.n1          = comb[1]
            auxComb.n2          = comb[2]
            auxComb.n3          = comb[3]
            auxComb.n4          = comb[4]
            auxComb.n5          = comb[5]
            auxComb.e1          = comb[6]
            auxComb.e2          = comb[7]

            auxComb.ordena()
            euroCombs.append(auxComb)
        # return [PrimiComb(*cmb) for cmb in combinations]
        return euroCombs
        # return [EuroComb(*cmb) for cmb in combinations]
    except Error:
        print('makeEuromillonesDbClass: Error creando la base de datos con todos los EuroCombs', Error)

    con.close()


@dataclass
class EuroDB:
    combs: List[EuroComb] = field(default_factory=makeEuromillonesDbClass)
    # combstue: List[EuroComb] = field(default_factory=make_euromartes_dbclass)
    # combsfri: List[EuroComb] = field(default_factory=make_euroviernes_dbclass)

