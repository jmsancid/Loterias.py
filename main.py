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
    Descarga las últimas combinaciones de los sorteos de Primitiva y Euromillones y los almacena
    en la base de datos loterias.db.

    Obtiene las frecuencias con las que salen los números en cada posición n1, n2... en base a 3 posibles criterios:
    - con el total de los sorteos realizados
    - en función de la estación del año: primavera, verano, etc (criterios de 1 a 4)
    - en base a la semana del año actual (criterio 5)

    En función de esa frecuencia, selecciona los números que más han salido, sin que se repita ninguno en las
    combinaciones seleccionadas.

    :return: 0 si sale todo ok
    """
    print('... Actualizando bases de datos')
    db_update()

    currentStation = getEstacion(datetime.datetime.now())  # obtengo la estación actual

    # Extraigo todas las primitivas sorteadas
    combPrimiTodas = PrimiDB().combs

    # Selecciono las combinaciones en función de la frecuencia histórica de los números
    primiTotales = analiza(combPrimiTodas)  # lista con todas los resultados de primitiva en formato PrimiComb
    combinacionesSeleccionadas = seleccionaCombinaciones(primiTotales)
    printCombinaciones("primitiva totales", combinacionesSeleccionadas)

    # Selecciono del total de combinaciones, las que coinciden con la semana actual (criterio 5)
    primiNumWeek = analiza(combPrimiTodas, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    printCombinaciones("primitiva totales según semana anual", combinacionesSeleccionadas)

    # Selecciono del total de combinaciones de primitiva, las que coinciden con la estación actual
    primiStation = analiza(combPrimiTodas, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    printCombinaciones(f"primitivas totales según estación actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en lunes
    combPrimiLunes = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.LUNES]

    # Selecciono las combinaciones de primitiva en función de la frecuencia histórica de los números extraídos en lunes
    primiLunes = analiza(combPrimiLunes)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiLunes)
    printCombinaciones("primitiva lunes", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de primitiva de los lunes, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiLunes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    printCombinaciones("primitiva de lunes según semana anual", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los lunes, las que coinciden con la estación actual
    primiStation = analiza(combPrimiLunes, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    printCombinaciones(f"primitivas de lunes según estación actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en jueves
    combPrimiJueves = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.JUEVES]

    # Selecciono las combinaciones en función de la frecuencia histórica de los números extraídos en jueves
    primiJueves = analiza(combPrimiJueves)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiJueves)
    printCombinaciones("primitiva jueves", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de primitiva de los jueves, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiJueves, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    printCombinaciones("primitiva de jueves según semana anual", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los jueves, las que coinciden con la estación actual
    primiStation = analiza(combPrimiJueves, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    printCombinaciones(f"primitivas de jueves según estación actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en sábado
    combPrimiSabado = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.SABADO]

    # Selecciono las combinaciones de primitiva en función de la frecuencia histórica de los números extraídos en sábado
    primiSabados = analiza(combPrimiSabado)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiSabados)
    printCombinaciones("primitiva sábados", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de primitiva de los sabados, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiSabado, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    printCombinaciones("primitiva de sábados según semana anual", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los sábados, las que coinciden con la estación actual
    primiStation = analiza(combPrimiSabado, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    printCombinaciones(f"primitivas de sábados según estación actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Extraigo todos los euromillones sorteadas
    combEuroTodas = EuroDB().combs

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números
    euroTotales = analiza(combEuroTodas)  # lista con todas los resultados de euromillones en formato PrimiComb
    combinacionesSeleccionadas = seleccionaCombinaciones(euroTotales)
    printCombinaciones("euromillones totales", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones, las que coinciden con la semana actual (criterio 5)
    euroNumWeek = analiza(combEuroTodas, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    printCombinaciones("euromillones totales según semana anual", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones, las que coinciden con la estación actual
    euroStation = analiza(combEuroTodas, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    printCombinaciones(f"euromillones totales según estación actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números extraídos
    # en martes
    combEuroMartes = [comb for comb in combEuroTodas if comb.combDate.isoweekday() == cte.MARTES]

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números extraídos
    # en martes
    euroMartes = analiza(combEuroMartes)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroMartes)
    printCombinaciones("euromillones martes", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de euromillones de los martes, las que coinciden con la semana actual
    # (criterio 5)
    euroNumWeek = analiza(combEuroMartes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    printCombinaciones("euromillones de martes según semana anual", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones de los martes, las que coinciden con la
    # estación actual
    euroStation = analiza(combEuroMartes, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    printCombinaciones(f"euromillones de los martes según estación actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números extraídos
    # en viernes
    combEuroviernes = [comb for comb in combEuroTodas if comb.combDate.isoweekday() == cte.VIERNES]

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números extraídos
    # en viernes
    euroViernes = analiza(combEuroviernes)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroViernes)
    printCombinaciones("euromillones viernes", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de euromillones de los viernes, las que coinciden con la semana actual
    # (criterio 5)
    euroNumWeek = analiza(combEuroviernes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    printCombinaciones("euromillones de viernes según semana anual", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones de los martes, las que coinciden con la
    # estación actual
    euroStation = analiza(combEuroviernes, currentStation)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    printCombinaciones(f"euromillones de los viernes según estación actual: {cte.ESTACIONES.get(currentStation)}",
                       combinacionesSeleccionadas)

    # sql_savecomb(primicomb)
    # sql_savecomb(eurocomb)

    return 0

if __name__ == '__main__':
    main()