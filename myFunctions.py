#!/usr/bin/env python3
# -*- coding: cp1252 -*-

import constants as cte
from clases import PrimiComb, EuroComb

from typing import Union, Dict, List


def getSeason(fecha) -> int:
    """
    Devuelve la estaci�n del a�o a la que pertenece 'fecha'

    :param fecha: objeto datetime que necesita al menos mes y d�a del mes
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
    salido cada n�mero en cada posici�n
    :param estadisticas: diccionario con la frecuencia con la que han salido los n�meros en los sorteos.
    Las claves son los identificadores de las posiciones de los n�meros: n1, n2,,, re / e1, e2
    :param numerosExluidos: lista con n�meros que no queremos usar, por ejemplo, los del �ltimo sorteo
    :param qCombinaciones: cantidad de combinaciones a devolver en la lista
    :return: lista con las combinaciones seleccionadas. Los elementos de la lista son objetos del tipo
    PrimiComb o EuroComb
    """
    esPrimitiva = True if "re" in estadisticas.keys() else False
    if numerosExcluidos is None:    # numerosExcluidos se utiliza para no repetir n�meros y no incluir los de la
        # semana anterior (en desarrollo). No afecta ni a reintegros de primitiva ni a estrellas 1 y 2 de euromill�n
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
            # posici�n n1, n2.. ordenados por frecuencia
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

            if not added:   # no se ha utilizado ning�n candidato
                # tomo un candidato que no est� en la combinaci�n actual
                numCombActual = comb.__dict__.values()
                for candidato in candidatos:
                    # utilizo un candidato no usado en la combinaci�n actual en otra posici�n
                    if not candidato in numCombActual:
                        setattr(comb, numId, candidato)
            added = False

        comb.ordena()
        combinaciones.append(comb)
    return combinaciones


def printCombinaciones(titulo:str, combinaciones:List) -> int:
    """
    imprime a consola las combinaciones seleccionadas seg�n el m�todo __repr__ de
    las dataclasses PrimiComb y EuroComb.

    :param titulo: descripci�n del sorteo al que corresponden las combinaciones
    :param combinaciones: lista con las combinaciones en forma de objeto PrimiComb o EuroComb
    :return: 0 si la operaci�n termina correctamente
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


def combinacionExistente(comb: Union[PrimiComb, EuroComb], listaComb: List[Union[PrimiComb, EuroComb]],
                         conFecha: bool = True) -> bool:
    """
    si la combinaci�n 'comb' est� en la lista de combinaciones devuelve true. si no, devuelve false
    :param comb: combinaci�n a verificar si est� en la lista de combinaciones
    :param listaComb: lista de combinaciones en la que se comprueba la existencia de 'comb'
    :param conFecha: indica si se tiene en cuenta la fecha o no.
    La fecha se tiene en cuenta a la hora de comprobar si hay que a�adir una combinaci�n a la lista de
    combinaciones seleccionadas y no se tiene en cuenta al comprobar si una determinada combinaci�n ha sido premiada
    :return: True si 'comb' est� en 'listaComb'. False si no est� o los elementos de 'listaComb' son de un tipo
    diferente a 'comb'
    """
    comb_en_listaComb = False

    # compruebo si hay algo que comparar
    nothing_to_search = True if comb is None or listaComb == [] or listaComb is None else False
    if nothing_to_search:
        return comb_en_listaComb

    types_match = all([type(comb) == type(c) for c in listaComb])
    if not types_match:
        return comb_en_listaComb

    if conFecha:    # hay que comprobar tambi�n la fecha
        comb_en_listaComb = any(comb.__eq__(c) for c in listaComb)
    else:
        comb_en_listaComb = any(comb.compara_sin_fecha(c) for c in listaComb)

    return comb_en_listaComb


def check_to_add(comb_sel: List[Union[PrimiComb, EuroComb]], comb_list: List) -> List:
    """
    Comprueba si las combinaciones de comb_sel ya existen en comb_list y si no existen, las a�ade.
    IMPORTANTE: antes de llamar a esta funci�n hay que asignarle fecha a la combinaci�n
    :param comb_sel: lista de combinaciones a comprobar si se a�aden o no al hist�rico
    :param comb_list: lista de combinaciones hist�rica
    :return: lista de combinaciones hist�rica actualizada
    """
    for comb in comb_sel:
            if not any([comb.compara_sin_fecha(allcomb) for allcomb in comb_list]):
                comb_list.append(comb)
            else:
                print(f"{__name__}. La combinaci�n {comb} ya se hab�a guardado anteriormente")
    return comb_list
