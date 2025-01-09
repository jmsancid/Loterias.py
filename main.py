#!/usr/bin/env python3
# -*- coding: cp1252 -*-

from estadisticas import analiza
from myFunctions import seleccionaCombinaciones, printCombinaciones, getEstacion
import constants as cte
from clases import PrimiDB, EuroDB
from db_update import db_update, sql_savecomb

import datetime


def main():
    """
    Descarga las �ltimas combinaciones de los sorteos de Primitiva y Euromillones y los almacena
    en la base de datos loterias.db.

    Obtiene las frecuencias con las que salen los n�meros en cada posici�n n1, n2... en base a 3 posibles criterios:
    - con el total de los sorteos realizados
    - en funci�n de la estaci�n del a�o: primavera, verano, etc (criterios de 1 a 4)
    - en base a la semana del a�o actual (criterio 5)

    En funci�n de esa frecuencia, selecciona los n�meros que m�s han salido, sin que se repita ninguno en las
    combinaciones seleccionadas.

    :return: 0 si sale todo ok
    """
    print('... Actualizando bases de datos')
    db_update()

    currentStation = getEstacion(datetime.datetime.now())  # obtengo la estaci�n actual

    # Extraigo todas las primitivas sorteadas
    combPrimiTodas = PrimiDB().combs

    # Selecciono las combinaciones en funci�n de la frecuencia hist�rica de los n�meros
    primiTotales = analiza(combPrimiTodas)  # lista con todas los resultados de primitiva en formato PrimiComb
    combinacionesSeleccionadas = seleccionaCombinaciones(primiTotales)
    printCombinaciones("primitiva totales", combinacionesSeleccionadas)

    # Selecciono del total de combinaciones, las que coinciden con la semana actual (criterio 5)
    primiNumWeek = analiza(combPrimiTodas, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    printCombinaciones("primitiva totales seg�n semana anual", combinacionesSeleccionadas)

    # Selecciono del total de combinaciones de primitiva, las que coinciden con la estaci�n actual
    primiStation = analiza(combPrimiTodas, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    printCombinaciones(f"primitivas totales seg�n estaci�n actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en lunes
    combPrimiLunes = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.LUNES]

    # Selecciono las combinaciones de primitiva en funci�n de la frecuencia hist�rica de los n�meros extra�dos en lunes
    primiLunes = analiza(combPrimiLunes)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiLunes)
    printCombinaciones("primitiva lunes", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de primitiva de los lunes, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiLunes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    printCombinaciones("primitiva de lunes seg�n semana anual", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los lunes, las que coinciden con la estaci�n actual
    primiStation = analiza(combPrimiLunes, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    printCombinaciones(f"primitivas de lunes seg�n estaci�n actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en jueves
    combPrimiJueves = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.JUEVES]

    # Selecciono las combinaciones en funci�n de la frecuencia hist�rica de los n�meros extra�dos en jueves
    primiJueves = analiza(combPrimiJueves)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiJueves)
    printCombinaciones("primitiva jueves", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de primitiva de los jueves, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiJueves, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    printCombinaciones("primitiva de jueves seg�n semana anual", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los jueves, las que coinciden con la estaci�n actual
    primiStation = analiza(combPrimiJueves, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    printCombinaciones(f"primitivas de jueves seg�n estaci�n actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en s�bado
    combPrimiSabado = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.SABADO]

    # Selecciono las combinaciones de primitiva en funci�n de la frecuencia hist�rica de los n�meros extra�dos en s�bado
    primiSabados = analiza(combPrimiSabado)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiSabados)
    printCombinaciones("primitiva s�bados", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de primitiva de los sabados, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiSabado, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    printCombinaciones("primitiva de s�bados seg�n semana anual", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los s�bados, las que coinciden con la estaci�n actual
    primiStation = analiza(combPrimiSabado, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    printCombinaciones(f"primitivas de s�bados seg�n estaci�n actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Extraigo todos los euromillones sorteadas
    combEuroTodas = EuroDB().combs

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros
    euroTotales = analiza(combEuroTodas)  # lista con todas los resultados de euromillones en formato PrimiComb
    combinacionesSeleccionadas = seleccionaCombinaciones(euroTotales)
    printCombinaciones("euromillones totales", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones, las que coinciden con la semana actual (criterio 5)
    euroNumWeek = analiza(combEuroTodas, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    printCombinaciones("euromillones totales seg�n semana anual", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones, las que coinciden con la estaci�n actual
    euroStation = analiza(combEuroTodas, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    printCombinaciones(f"euromillones totales seg�n estaci�n actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros extra�dos
    # en martes
    combEuroMartes = [comb for comb in combEuroTodas if comb.combDate.isoweekday() == cte.MARTES]

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros extra�dos
    # en martes
    euroMartes = analiza(combEuroMartes)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroMartes)
    printCombinaciones("euromillones martes", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de euromillones de los martes, las que coinciden con la semana actual
    # (criterio 5)
    euroNumWeek = analiza(combEuroMartes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    printCombinaciones("euromillones de martes seg�n semana anual", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones de los martes, las que coinciden con la
    # estaci�n actual
    euroStation = analiza(combEuroMartes, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    printCombinaciones(f"euromillones de los martes seg�n estaci�n actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros extra�dos
    # en viernes
    combEuroviernes = [comb for comb in combEuroTodas if comb.combDate.isoweekday() == cte.VIERNES]

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros extra�dos
    # en viernes
    euroViernes = analiza(combEuroviernes)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroViernes)
    printCombinaciones("euromillones viernes", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de euromillones de los viernes, las que coinciden con la semana actual
    # (criterio 5)
    euroNumWeek = analiza(combEuroviernes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    printCombinaciones("euromillones de viernes seg�n semana anual", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones de los martes, las que coinciden con la
    # estaci�n actual
    euroStation = analiza(combEuroviernes, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    printCombinaciones(f"euromillones de los viernes seg�n estaci�n actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # sql_savecomb(primicomb)
    # sql_savecomb(eurocomb)

    return 0

if __name__ == '__main__':
    main()