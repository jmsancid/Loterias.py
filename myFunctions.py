#!/usr/bin/env python3
# -*- coding: cp1252 -*-

import constants as cte
from clases import PrimiComb, EuroComb

from typing import Union, Dict, List


def getEstacion(fecha) -> int:
    """
    Devuelve la estación del año a la que pertenece 'fecha'

    :param fecha: objeto datetime que necesita al menos mes y día del mes
    :return: valor entero
        PRIMAVERA = 1 desde 0321 a 0620
        VERANO = 2 desde 0621 a 0920
        OTOCHO = 3 desde 0921 a 1220
        INVIERNO = 4 resto de fechas
    """
    mesDia = fecha.month * 100 + fecha.day
    match mesDia:
        case intervalo if 321 <= intervalo < 620:
            estacion = cte.PRIMAVERA
        case intervalo if 621 <= intervalo < 920:
            estacion = cte.VERANO
        case intervalo if 921 <= intervalo < 1220:
            estacion = cte.OTONO
        case _:
            estacion = cte.INVIERNO
    return estacion


def seleccionaCombinaciones(estadisticas:Dict, numerosExcluidos:Union[List,None]=None, qCombinaciones:int=5) -> List:
    """
    Selecciona qCombinaciones a partir del diccionario con la frecuencia con la que ha
    salido cada número en cada posición
    :param estadisticas: diccionario con la frecuencia con la que han salido los números en los sorteos.
    Las claves son los identificadores de las posiciones de los números: n1, n2,,, re / e1, e2
    :param numerosExluidos: lista con números que no queremos usar, por ejemplo, los del último sorteo
    :param qCombinaciones: cantidad de combinaciones a devolver en la lista
    :return: lista con las combinaciones seleccionadas. Los elementos de la lista son objetos del tipo
    PrimiComb o EuroComb
    """
    esPrimitiva = True if "re" in estadisticas.keys() else False
    if numerosExcluidos is None:    # numerosExcluidos se utiliza para no repetir números y no incluir los de la
        # semana anterior (en desarrollo). No afecta ni a reintegros de primitiva ni a estrellas 1 y 2 de euromillón
        numerosExcluidos = []
    reintegrosExcluidos = [None]
    estrellasExcluidas = []
    combinaciones = []
    added = False
    qValores = len(estadisticas.get(tuple(estadisticas.keys())[0]))
    rango = min(qValores, qCombinaciones)
    for combinacionId in range(rango):
        comb = PrimiComb() if esPrimitiva else EuroComb()
        for numId, num in estadisticas.items():
            candidatos = [n[0] for n in estadisticas.get(numId)]    # lista con los candidatos de una determinada
            # posición n1, n2.. ordenados por frecuencia
            for i in range(len(candidatos)):
                if not (candidatos[i] in numerosExcluidos) and not numId in ['re', 'e1', 'e2']:
                    setattr(comb, numId, candidatos[i])
                    numerosExcluidos.append(candidatos[i])
                    added = True
                    break
                elif not (candidatos[i] in reintegrosExcluidos) and numId == 're':
                    setattr(comb, numId, candidatos[i])
                    reintegrosExcluidos.append(candidatos[i])
                    added = True
                    break
                elif not (candidatos[i] in estrellasExcluidas) and numId in ['e1', 'e2']:
                    setattr(comb, numId, candidatos[i])
                    estrellasExcluidas.append(candidatos[i])
                    added = True
                    break

            if not added:   # no se ha utilizado ningún candidato
                # tomo un candidato que no esté en la combinación actual
                numCombActual = comb.__dict__.values()
                for candidato in candidatos:
                    # utilizo un candidato no usado en la combinación actual en otra posición
                    if not candidato in numCombActual:
                        setattr(comb, numId, candidato)
            added = False

        combinaciones.append(comb)
    return combinaciones


def printCombinaciones(titulo:str, combinaciones:List) -> int:
    """
    imprime a consola las combinaciones seleccionadas según el método __repr__ de
    las dataclasses PrimiComb y EuroComb.

    :param titulo: descripción del sorteo al que corresponden las combinaciones
    :param combinaciones: lista con las combinaciones en forma de objeto PrimiComb o EuroComb
    :return: 0 si la operación termina correctamente
    """
    print(f"\n{titulo.upper()}")
    esPrimitiva = True if isinstance(combinaciones[0], PrimiComb) else False
    if esPrimitiva:
        for comb in combinaciones:
            print(f"{comb.n1:<2} {comb.n2:<2} {comb.n3:<2} {comb.n4:<2} {comb.n5:<2} {comb.n6:<2}\tRe-{comb.re}")
    else:
        for comb in combinaciones:
            print(f"{comb.n1:<2} {comb.n2:<2} {comb.n3:<2} {comb.n4:<2} {comb.n5:<2}\te1-{comb.e1:<2} e2-{comb.e2}")
    print("___________________")
    return 0
