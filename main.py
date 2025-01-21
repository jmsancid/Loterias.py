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

    """
    # Nombre del archivo donde se guardar� la lista
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
    currentSeason = getSeason(datetime.now())  # obtengo la estaci�n actual
    semana_actual = datetime.now().isocalendar().week
    semana_siguiente = (datetime.now() + timedelta(weeks=1)).isocalendar().week
    semana_actual = semana_actual if datetime.now().isoweekday() < 7 else semana_siguiente  # los domingos considero
    # ya el n�mero de semana siguiente

    # Obtengo las fechas de los d�as de sorteo de la semana actual para asign�rselo a las combinaciones
    # correspondientes. Si el sorteo ya ha pasado, se asigna la fecha a la de la semana siguiente. Por ejemplo, si
    # ejecuto el programa un martes, la fecha del lunes ser� la del lunes de la semana siguiente, no la del lunes de
    # la semana actual.
    # A las combinaciones con todos los n�meros hist�ricos se les asigna el domingo y a las del n�mero de semana del
    # a�o se les asigna el mi�rcoles
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

    # Selecciono las combinaciones en funci�n de la frecuencia hist�rica de los n�meros
    primiTotales = analiza(combPrimiTodas)  # lista con todas los resultados de primitiva en formato PrimiComb
    combinacionesSeleccionadas = seleccionaCombinaciones(primiTotales)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas totales,
    # hay que asignar a las combinaciones la fecha del domingo de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', domingo) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allPrimi"])
    printCombinaciones("primitiva totales", combinacionesSeleccionadas)

    # Selecciono del total de combinaciones, las que coinciden con la semana actual (criterio 5)
    primiNumWeek = analiza(combPrimiTodas, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas por
    # n� de semana hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', miercoles) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allPrimiWeek"])
    printCombinaciones(f"primitiva totales seg�n n�mero de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono del total de combinaciones de primitiva, las que coinciden con la estaci�n actual
    primiStation = analiza(combPrimiTodas, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas
    # por estaci�n del a�o, hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', miercoles) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allPrimiSeason"])
    printCombinaciones(f"primitivas totales seg�n estaci�n actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en lunes
    combPrimiLunes = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.LUNES]
    pickleLotoDb["primiLunes"] = combPrimiLunes

    # Selecciono las combinaciones de primitiva en funci�n de la frecuencia hist�rica de los n�meros extra�dos en lunes
    primiLunes = analiza(combPrimiLunes)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiLunes)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas de los lunes,
    # hay que asignar a las combinaciones la fecha del lunes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', lunes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiLunes"])
    printCombinaciones(f"primitiva lunes ({lunes})", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los lunes, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiLunes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas por
    # n� de semana anual, hay que asignar a las combinaciones la fecha del lunes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', lunes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiLunesWeek"])
    printCombinaciones(f"primitiva de lunes seg�n n�mero de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los lunes, las que coinciden con la estaci�n actual
    primiStation = analiza(combPrimiLunes, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas de los lunes
    # por estaci�n del a�o, hay que asignar a las combinaciones la fecha del lunes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', lunes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiLunesSeason"])
    printCombinaciones(f"primitivas de lunes seg�n estaci�n actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en jueves
    combPrimiJueves = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.JUEVES]
    pickleLotoDb["primiJueves"] = combPrimiJueves

    # Selecciono las combinaciones en funci�n de la frecuencia hist�rica de los n�meros extra�dos en jueves
    primiJueves = analiza(combPrimiJueves)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiJueves)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas de los jueves,
    # hay que asignar a las combinaciones la fecha del jueves de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', jueves) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiJueves"])
    printCombinaciones(f"primitiva jueves ({jueves})", combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los jueves, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiJueves, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas de los jueves
    # en funci�n del n� de semana anual, hay que asignar a las combinaciones la fecha del jueves de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', jueves) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiJuevesWeek"])
    printCombinaciones(f"primitiva de jueves seg�n n�mero de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los jueves, las que coinciden con la estaci�n actual
    primiStation = analiza(combPrimiJueves, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas de los jueves
    # en funci�n de la estaci�n del a�o, hay que asignar a las combinaciones la fecha del jueves de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', jueves) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiJuevesSeason"])
    printCombinaciones(f"primitivas de jueves seg�n estaci�n actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Extraigo todas las primitivas sorteadas en s�bado
    combPrimiSabado = [comb for comb in combPrimiTodas if comb.combDate.isoweekday() == cte.SABADO]
    pickleLotoDb["primiSabado"] = combPrimiSabado

    # Selecciono las combinaciones de primitiva en funci�n de la frecuencia hist�rica de los n�meros extra�dos en s�bado
    primiSabados = analiza(combPrimiSabado)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiSabados)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas de los s�bados,
    # hay que asignar a las combinaciones la fecha del s�bado de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', sabado) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiSabado"])
    printCombinaciones(f"primitiva s�bados ({sabado})", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de primitiva de los sabados, las que coinciden con la semana actual
    # (criterio 5)
    primiNumWeek = analiza(combPrimiSabado, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiNumWeek)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas de los s�bados
    # en funci�n del n� de semana anual, hay que asignar a las combinaciones la fecha del s�bado de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', sabado) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiSabadoWeek"])
    printCombinaciones(f"primitiva de s�bados seg�n n�mero de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre las combinaciones de primitiva de los s�bados, las que coinciden con la estaci�n actual
    primiStation = analiza(combPrimiSabado, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(primiStation)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de primitivas de los s�bados,
    # en funci�n de la estaci�n del a�o, hay que asignar a las combinaciones la fecha del s�bado de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', sabado) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["primiSabadoSeason"])
    printCombinaciones(f"primitivas de s�bados seg�n estaci�n actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Extraigo todos los euromillones sorteadas
    combEuroTodas = EuroDB().combs
    pickleLotoDb["euroResults"] = combEuroTodas

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros
    euroTotales = analiza(combEuroTodas)  # lista con todas los resultados de euromillones en formato EuroComb
    combinacionesSeleccionadas = seleccionaCombinaciones(euroTotales)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones totales,
    # hay que asignar a las combinaciones la fecha del domingo de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', domingo) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allEuro"])
    printCombinaciones("euromillones totales", combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones, las que coinciden con la semana actual (criterio 5)
    euroNumWeek = analiza(combEuroTodas, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones en funci�n del
    # n� de semana anual, hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', miercoles) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allEuroWeek"])
    printCombinaciones(f"euromillones totales seg�n semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones, las que coinciden con la estaci�n actual
    euroStation = analiza(combEuroTodas, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones
    # por estaci�n del a�o, hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', miercoles) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["allEuroSeason"])
    printCombinaciones(f"euromillones totales seg�n estaci�n actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros extra�dos
    # en martes
    combEuroMartes = [comb for comb in combEuroTodas if comb.combDate.isoweekday() == cte.MARTES]
    pickleLotoDb["euroMartes"] = combEuroMartes

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros extra�dos
    # en martes
    euroMartes = analiza(combEuroMartes)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroMartes)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones de los martes,
    # hay que asignar a las combinaciones la fecha del martes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', martes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroMartes"])
    printCombinaciones(f"euromillones martes ({martes})", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de euromillones de los martes, las que coinciden con la semana actual
    # (criterio 5)
    euroNumWeek = analiza(combEuroMartes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones de los martes
    # en funci�n del n� de semana anual, hay que asignar a las combinaciones la fecha del martes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', martes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroMartesWeek"])
    printCombinaciones(f"euromillones de martes seg�n n�mero de semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones de los martes, las que coinciden con la
    # estaci�n actual
    euroStation = analiza(combEuroMartes, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones de los martes
    # por estaci�n del a�o, hay que asignar a las combinaciones la fecha del miercoles de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', martes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroMartesSeason"])
    printCombinaciones(f"euromillones de los martes seg�n estaci�n actual: {cte.ESTACIONES.get(currentSeason)}",
                       combinacionesSeleccionadas)

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros extra�dos
    # en viernes
    combEuroviernes = [comb for comb in combEuroTodas if comb.combDate.isoweekday() == cte.VIERNES]
    pickleLotoDb["euroViernes"] = combEuroviernes

    # Selecciono las combinaciones de euromillones en funci�n de la frecuencia hist�rica de los n�meros extra�dos
    # en viernes
    euroViernes = analiza(combEuroviernes)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroViernes)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones de los viernes,
    # hay que asignar a las combinaciones la fecha del viernes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', viernes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroViernes"])
    printCombinaciones(f"euromillones viernes ({viernes})", combinacionesSeleccionadas)

    # Selecciono del entre las combinaciones de euromillones de los viernes, las que coinciden con la semana actual
    # (criterio 5)
    euroNumWeek = analiza(combEuroviernes, 5)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroNumWeek)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones de los viernes
    # en funci�n del n� de semana anual, hay que asignar a las combinaciones la fecha del viernes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', viernes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroViernesWeek"])
    printCombinaciones(f"euromillones de viernes seg�n semana anual ({semana_actual})",
                       combinacionesSeleccionadas)

    # Selecciono de entre todas las combinaciones de euromillones de los martes, las que coinciden con la
    # estaci�n actual
    euroStation = analiza(combEuroviernes, currentSeason)
    combinacionesSeleccionadas = seleccionaCombinaciones(euroStation)
    # Antes de comprobar si se a�aden las combinaciones seleccionadas al hist�rico de euromillones de los viernes
    # por estaci�n del a�o, hay que asignar a las combinaciones la fecha del viernes de la semana actual
    combinacionesSeleccionadas = list(map(lambda obj: setattr(obj, 'combDate', viernes) or obj,
                                          combinacionesSeleccionadas))
    check_to_add(combinacionesSeleccionadas, pickleLotoDb["euroViernesSeason"])
    printCombinaciones(f"euromillones de los viernes seg�n estaci�n actual: {cte.ESTACIONES.get(currentSeason)}",
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