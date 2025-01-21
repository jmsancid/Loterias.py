#!/usr/bin/env python3
# -*- coding: cp1252 -*-

from estadisticas import analiza
from myFunctions import seleccionaCombinaciones, printCombinaciones, getSeason, combinacionExistente, check_to_add
import constants as cte
from clases import PrimiDB, EuroDB
from dbUpdate import dbUpdate, sqlSaveCombinations

from datetime import datetime, timedelta
import pickle



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

    """
    # Nombre del archivo donde se guardará la lista
archivo_pickle = "primi_comb.pkl"

# Guardar la lista de objetos con pickle
with open(archivo_pickle, "wb") as archivo:
    pickle.dump(objetos, archivo)
    print(f"Lista de objetos guardada en {archivo_pickle}")

# Leer la lista de objetos desde el archivo pickle
with open(archivo_pickle, "rb") as archivo:
    objetos_cargados = pickle.load(archivo)
    print("Lista de objetos cargada desde el archivo:")
    print(objetos_cargados)

"""

    pickleLotoDb = {
        "primiResults": [],
        "allPrimi": [],
        "allPrimiSeason": [],
        "allPrimiWeek": [],
        "primiLunes": [],
        "primiLunesSeason": [],
        "primiLunesWeek": [],
        "primiJueves": [],
        "primiJuevesSeason": [],
        "primiJuevesWeek": [],
        "primiSabado": [],
        "primiSabadoSeason": [],
        "primiSabadoWeek": [],
        "euroResults": [],
        "allEuro": [],
        "allEuroSeason": [],
        "allEuroWeek": [],
        "euroMartes": [],
        "euroMartesSeason": [],
        "euroMartesWeek": [],
        "euroViernes": [],
        "euroViernesSeason": [],
        "euroViernesWeek": []
    }

    archivo_pickle = cte.PICKLEDIR + cte.LOTOPICKERFILE
    currentSeason = getSeason(datetime.now())  # obtengo la estación actual
    semana_actual = datetime.now().isocalendar().week
    semana_siguiente = (datetime.now() + timedelta(weeks=1)).isocalendar().week
    semana_actual = semana_actual if datetime.now().isoweekday() < 7 else semana_siguiente  # los domingos considero
    # ya el número de semana siguiente

    # Obtengo las fechas de los días de sorteo de la semana actual para asignárselo a las combinaciones
    # correspondientes. Si el sorteo ya ha pasado, se asigna la fecha a la de la semana siguiente. Por ejemplo, si
    # ejecuto el programa un martes, la fecha del lunes será la del lunes de la semana siguiente, no la del lunes de
    # la semana actual.
    # A las combinaciones con todos los números históricos se les asigna el domingo y a las del número de semana del
    # año se les asigna el miércoles
    # A estas combinaciones se les asigna la fecha del lunes de la semana actual
    hoy = datetime.now().isoweekday()
    next_monday = (datetime.now() + timedelta(days=8-hoy)).date()

    lunes = datetime.now().date() if hoy == 1 else next_monday
    martes = datetime.now().date() if hoy == 2 else next_monday + timedelta(days=1)
    miercoles = datetime.now().date() if hoy == 3 else next_monday + timedelta(days=3)
    jueves = datetime.now().date() if hoy == 4 else next_monday + timedelta(days=4)
    viernes = datetime.now().date() if hoy == 5 else next_monday + timedelta(days=5)
    sabado = datetime.now().date() if hoy == 6 else next_monday + timedelta(days=6)
    domingo = datetime.now().date() if hoy == 7 else next_monday + timedelta(days=7)
    # lunes = datetime.now() - timedelta(days=datetime.now().weekday())
    # lunes = lunes.date()
    # martes = lunes + timedelta(days=1)
    # miercoles = lunes + timedelta(days=2)
    # jueves = lunes + timedelta(days=3)
    # viernes = lunes + timedelta(days=4)
    # sabado = lunes + timedelta(days=5)
    # domingo = lunes + timedelta(days=6)

    print('... Actualizando bases de datos')
    dbUpdate()

    # Leer la lista de objetos desde el archivo pickle
    with open(archivo_pickle, "rb") as f:
        objetos_cargados = pickle.load(f)
        print("Lista de objetos cargada desde el archivo:")
        # print(objetos_cargados)

    # Extraigo todas las primitivas sorteadas
    combPrimiTodas = PrimiDB().combs
    pickleLotoDb["primiResults"] = combPrimiTodas

    # Selecciono las combinaciones en función de la frecuencia histórica de los números
    primiTotales = analiza(combPrimiTodas)  # lista con todas los resultados de primitiva en formato PrimiComb
    combinacionesSeleccionadas = seleccionaCombinaciones(primiTotales)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas totales,
    # hay que asignar a las combinaciones la fecha del domingo de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', domingo) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allPrimi"])
    printCombinaciones("primitiva totales", combinacionesSeleccionadas)

    # Selecciono del total de combinaciones, las que coinciden con la semana actual (criterio 5)
    primiNumWeek = analiza(combPrimiTodas, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas por
    # nº de semana hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', miercoles) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allPrimiWeek"])
    printCombinaciones(f"primitiva totales según número de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono del total de combinaciones de primitiva, las que coinciden con la estación actual
    primiStation = analiza(combPrimiTodas, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas
    # por estación del año, hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', miercoles) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allPrimiSeason"])
    printCombinaciones(f"primitivas totales según estación actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en lunes
    combPrimiLunes = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.LUNES]
    pickleLotoDb["primiLunes"] = combPrimiLunes

    # Selecciono las combinaciones de primitiva en función de la frecuencia histórica de los números extraídos en lunes
    primiLunes = analiza(combPrimiLunes)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiLunes)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas de los lunes,
    # hay que asignar a las combinaciones la fecha del lunes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', lunes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiLunes"])
    printCombinaciones(f"primitiva lunes ({lunes})", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los lunes, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiLunes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas por
    # nº de semana anual, hay que asignar a las combinaciones la fecha del lunes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', lunes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiLunesWeek"])
    printCombinaciones(f"primitiva de lunes según número de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los lunes, las que coinciden con la estación actual
    primiStation = analiza(combPrimiLunes, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas de los lunes
    # por estación del año, hay que asignar a las combinaciones la fecha del lunes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', lunes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiLunesSeason"])
    printCombinaciones(f"primitivas de lunes según estación actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en jueves
    combPrimiJueves = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.JUEVES]
    pickleLotoDb["primiJueves"] = combPrimiJueves

    # Selecciono las combinaciones en función de la frecuencia histórica de los números extraídos en jueves
    primiJueves = analiza(combPrimiJueves)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiJueves)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas de los jueves,
    # hay que asignar a las combinaciones la fecha del jueves de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', jueves) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiJueves"])
    printCombinaciones(f"primitiva jueves ({jueves})", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los jueves, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiJueves, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas de los jueves
    # en función del nº de semana anual, hay que asignar a las combinaciones la fecha del jueves de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', jueves) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiJuevesWeek"])
    printCombinaciones(f"primitiva de jueves según número de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los jueves, las que coinciden con la estación actual
    primiStation = analiza(combPrimiJueves, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas de los jueves
    # en función de la estación del año, hay que asignar a las combinaciones la fecha del jueves de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', jueves) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiJuevesSeason"])
    printCombinaciones(f"primitivas de jueves según estación actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en sábado
    combPrimiSabado = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.SABADO]
    pickleLotoDb["primiSabado"] = combPrimiSabado

    # Selecciono las combinaciones de primitiva en función de la frecuencia histórica de los números extraídos en sábado
    primiSabados = analiza(combPrimiSabado)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiSabados)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas de los sábados,
    # hay que asignar a las combinaciones la fecha del sábado de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', sabado) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiSabado"])
    printCombinaciones(f"primitiva sábados ({sabado})", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de primitiva de los sabados, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiSabado, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas de los sábados
    # en función del nº de semana anual, hay que asignar a las combinaciones la fecha del sábado de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', sabado) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiSabadoWeek"])
    printCombinaciones(f"primitiva de sábados según número de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los sábados, las que coinciden con la estación actual
    primiStation = analiza(combPrimiSabado, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de primitivas de los sábados,
    # en función de la estación del año, hay que asignar a las combinaciones la fecha del sábado de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', sabado) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiSabadoSeason"])
    printCombinaciones(f"primitivas de sábados según estación actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Extraigo todos los euromillones sorteadas
    combEuroTodas = EuroDB().combs
    pickleLotoDb["euroResults"] = combEuroTodas

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números
    euroTotales = analiza(combEuroTodas)  # lista con todas los resultados de euromillones en formato EuroComb
    combinacionesSeleccionadas = seleccionaCombinaciones(euroTotales)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones totales,
    # hay que asignar a las combinaciones la fecha del domingo de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', domingo) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allEuro"])
    printCombinaciones("euromillones totales", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones, las que coinciden con la semana actual (criterio 5)
    euroNumWeek = analiza(combEuroTodas, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones en función del
    # nº de semana anual, hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', miercoles) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allEuroWeek"])
    printCombinaciones(f"euromillones totales según semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones, las que coinciden con la estación actual
    euroStation = analiza(combEuroTodas, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones
    # por estación del año, hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', miercoles) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allEuroSeason"])
    printCombinaciones(f"euromillones totales según estación actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números extraídos
    # en martes
    combEuroMartes = [comb for comb in combEuroTodas if comb.combDate.isoweekday() == cte.MARTES]
    pickleLotoDb["euroMartes"] = combEuroMartes

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números extraídos
    # en martes
    euroMartes = analiza(combEuroMartes)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroMartes)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones de los martes,
    # hay que asignar a las combinaciones la fecha del martes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', martes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroMartes"])
    printCombinaciones(f"euromillones martes ({martes})", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de euromillones de los martes, las que coinciden con la semana actual
    # (criterio 5)
    euroNumWeek = analiza(combEuroMartes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones de los martes
    # en función del nº de semana anual, hay que asignar a las combinaciones la fecha del martes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', martes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroMartesWeek"])
    printCombinaciones(f"euromillones de martes según número de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones de los martes, las que coinciden con la
    # estación actual
    euroStation = analiza(combEuroMartes, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones de los martes
    # por estación del año, hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', martes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroMartesSeason"])
    printCombinaciones(f"euromillones de los martes según estación actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números extraídos
    # en viernes
    combEuroviernes = [comb for comb in combEuroTodas if comb.combDate.isoweekday() == cte.VIERNES]
    pickleLotoDb["euroViernes"] = combEuroviernes

    # Selecciono las combinaciones de euromillones en función de la frecuencia histórica de los números extraídos
    # en viernes
    euroViernes = analiza(combEuroviernes)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroViernes)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones de los viernes,
    # hay que asignar a las combinaciones la fecha del viernes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', viernes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroViernes"])
    printCombinaciones(f"euromillones viernes ({viernes})", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de euromillones de los viernes, las que coinciden con la semana actual
    # (criterio 5)
    euroNumWeek = analiza(combEuroviernes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones de los viernes
    # en función del nº de semana anual, hay que asignar a las combinaciones la fecha del viernes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', viernes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroViernesWeek"])
    printCombinaciones(f"euromillones de viernes según semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones de los martes, las que coinciden con la
    # estación actual
    euroStation = analiza(combEuroviernes, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    # Antes de comprobar si se añaden las combinaciones seleccionadas al histórico de euromillones de los viernes
    # por estación del año, hay que asignar a las combinaciones la fecha del viernes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', viernes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroViernesSeason"])
    printCombinaciones(f"euromillones de los viernes según estación actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # sql_savecomb(primicomb)
    # sql_savecomb(eurocomb)

    # Guardar la lista de objetos con pickle
    with open(archivo_pickle, "wb") as f:
        # noinspection PyTypeChecker
        pickle.dump(pickleLotoDb, f, pickle.HIGHEST_PROTOCOL)
        print(f"\nLista de objetos guardada en {archivo_pickle}")

    return 0

if __name__ == '__main__':
    main()