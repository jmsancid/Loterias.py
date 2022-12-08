#!usr/bin/env
# -*- coding: cp1252 -*-

from loterias_tools.loteriasdb import *
from functools import wraps
from bisect import bisect_left


def measure(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t = datetime.now()
        result = func(*args, **kwargs)
        print(func.__name__, 'tardó ', str(datetime.now() - t))
        return result
    return wrapper


def imprimecombinacion(func, *args):
    """
    Decorador
    func es una función que analiza combinaciones de primitiva o euromillones y devuelve unas combinaciones
    dichas combinaciones son un diccionario que tiene como clave un entero que representa el día de la semana
    en el que se celebró el sorteo (domingo = 0) y como valores otro diccionario que tiene como clave
    una identificación de la apuesta y como valor la propia combinación
    :param func:
    :return:
    """
    combinaciones = func(*args)
    diassemana = {0: 'Domingo', 1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado',
                  25: 'Martes + Viernes', 46: 'Jueves + Sábado'}
    reintegro = None
    for dia in combinaciones:
        print(f'Combinaciones del {diassemana[dia]}')
        for numcomb, combinacion in combinaciones[dia].items():
            if dia in [4, 6, 46]:  # Si es combinación de Primitiva
                if numcomb == 0:
                    reintegro = combinacion[7]
                del combinacion[6:8]  # Eliminamos el número complementario y el reintegro
            print(f'Combinación {numcomb}: {combinacion}')
        if dia in [4, 6, 46]:
            print(f'\tReintegro: {reintegro}')


def analiza(lototype):
    """
    rutina para seleccionar 5 combinaciones de primitiva y 2 de euromillones.
    :param lototype: tipo de lotería PRIMITIVA o EUROMILLONES
    :return: diccionario con la fecha, el número de orden de la apuesta (del 0 al 4 en primitiva y
    del 0 al 1 en euromillones) y la apuesta correspondiente, sin complementario en el caso de la primitiva.
    """
    if lototype == lotoparams.PRIMITIVA:
        dias = lotoparams.PRIMIDAYS[1:]  # días 1, lunes, 4, jueves, y 6, sábado
        Sorteo = PrimiDB()
    else:
        dias = lotoparams.EURODAYS[1:]  # días 2, martes, y 5, viernes
        Sorteo = EuroDB()

    # Prueba 3: Con DataClasses
    # totalsorteos = sorteo().contador()
    # freqevoltotsorteos = Sorteo.freq_evolution()
    # parimpartotsorteos = Sorteo.evenodd()
    # qfreqtotsorteos = Sorteo.cuentafreq()
    qselcombtotsorteos = Sorteo.selcombs()

    # sorteodia1 = PrimiDB().contador(dias[0])
    # freqevoldia1 = Sorteo.freq_evolution(dias[0])
    # parimpardia1 = Sorteo.evenodd(dias[0])
    # qfreqdia1 = Sorteo.cuentafreq(dias[0])
    qselcombdia1 = Sorteo.selcombs(dias[0])

    # sorteodia2 = PrimiDB().contador(dias[1])
    # freqevoldia2 = Sorteo.freq_evolution(dias[1])
    # parimpardia2 = Sorteo.evenodd(dias[1])
    # qfreqdia2 = Sorteo.cuentafreq(dias[1])
    qselcombdia2 = Sorteo.selcombs(dias[1])

    # con.close()

    if len(dias) > 2:
        qselcombdia3 = Sorteo.selcombs(dias[2])
        return qselcombtotsorteos, qselcombdia1, qselcombdia2, qselcombdia3
    else:
        return qselcombtotsorteos, qselcombdia1, qselcombdia2


def siblinged(comb: list[tuple[int]], qcomb: int = 10) -> dict[int:list]:
    """
    siblinged es un alias de la estrategia hermanada, definida para mis Hermanos
    Primero se ordena la lista de combinaciones por aquellos números que salen más en primer lugar, luego por los
    que más salen en segundo lugar cuando el primer número es el más frecuente, luego el tercero más frecuente con
    el primero más frecuentey así sucesivamente.

    La primera combinación empieza por el más frecuente, la segunda por el segundo más frecuente y así sucesivamente
    TODO: Rechazar los números que ya han sido seleccionados y los que salieron la semana anterior
    :param comb: lista formada por las listas de números que componen todas las combinaciones
    :param qcomb: cantidad de combinaciones que se quieren devolver
    :return: Lista con qcomb combinaciones (listas) de números
    """
    # Convierto la lista de combinaciones en un diccionario. La clave será el nº de orden de cada elemento de cada
    # tupla que compone comb y el valor, la lista de números que aparecen en esa posición

    # elementos que componen cada tupla:

    combsize = len(comb)  # Número de combinaciones analizadas
    betsize = len(comb[0])  # Cantidad de números que componen la apuesta
    if not combsize:
        print('siblinged: No hay combinaciones que analizar')
        exit()

    firstmostextracted = [valext[0] for valext in Counter([comb[k][0] for k in range(combsize)]).most_common(qcomb)]
    # newcomb = {k: Counter([comb[i][k] for i in range(qnumb)]).most_common(qcomb) for k in range(qcomb)}
    print(f'siblinged: {firstmostextracted[:qcomb]}. \n{combsize} combinaciones analizadas')

    selcomb = {}
    #bucle para ir extrayendo los números hermanados
    for firstnumb in firstmostextracted:
        # mostextracted = [valext[0] for valext in Counter([comb[k][idxpos] for k in range(combsize)]).most_common(qcomb)]
        # prevext = mostextracted[idxpos]  # El número extraído en la posición anterior a la buscada
        selcomb[firstmostextracted.index(firstnumb)] = [firstnumb,]
        prevext = firstnumb
        for ordenextraccion in range(1,betsize):
            nextmostextracted = [nextval[0] for nextval in Counter([comb[k][ordenextraccion]
                                  for k in range(combsize)
                                  # if comb[k][ordenextraccion - 1] == prevext]).most_common(qcomb)]
                                  if comb[k][0] == prevext]).most_common(qcomb)]
            # print(f'Valores frecuentes extraídos en {ordenextraccion + 1}º lugar cuando el primero es '
            #       f'es {prevext}: {nextmostextracted}')
            added = False
            num2add = nextmostextracted[0]
            for i in range(len(nextmostextracted)):
                # Compruebo que el número a añadir no es None y que no ha sido seleccionado previamente entre los 6
                # primeros números de Primitiva o los 5 de Euromillón, lo que equivale a que los 2 últimos números sí
                # podrían estar repetidos (complementario y reintegro o las 2 estrellas)
                if nextmostextracted[i] and \
                        (i < betsize-2 and nextmostextracted[i] not in selcomb[firstmostextracted.index(firstnumb)]):
                    num2add = nextmostextracted[i]
                    break
            selcomb[firstmostextracted.index(firstnumb)].append(num2add)
            # Actualizamos el siguiente número a buscar (lo desestimamos si es None)
            # prevext = nextmostextracted[0] if nextmostextracted[0] else nextmostextracted[1]
        # print(f'Combinación {firstmostextracted.index(firstnumb)}: {selcomb[firstmostextracted.index(firstnumb)]}')

    # print(f'Combinaciones seleccionadas: {selcomb}')

    return selcomb

def formateafecha(strfecha:str) -> str:
    """
    Convierte una cadena de fecha en formato AAAA-mm-dd en una cadena de texto Año.semana (2021.48)
    :param strfecha: Cadena con formato fecha datetime
    :return: Cadena con formato año.semana para base de datos Loterias.db, cálculos con total sorteos
    """
    weekstrfecha = int(datetime.strptime(strfecha, "%Y-%m-%d").isocalendar().week)
    fechaformateada = f'{datetime.strptime(strfecha, "%Y-%m-%d").isocalendar().year}.{weekstrfecha}'
    return fechaformateada

def iseven(val: int) -> bool:
    '''
    Devuelve True si val es par o None y false si es impar
    :param val: número a comprobar si es par o im par
    :return:
    '''
    evenval = False if val and val%2 else True
    return evenval


def evenodded(comb: list[tuple[int]], qcomb: int = 10) -> dict[int:list]:
    '''
    evenodded es un alias de la estrategia parimparada, definida para mis Hermanos
    Ordeno por frecuencia de mayor a menor las combinaciones de números basándome en si son pares o impares.
    A diferencia de versiones anteriores, lo que miro es si siendo impar el primer número, el segundo más frecuente
    es par o impar y así con cada posición.
    Primero se ordena la lista de combinaciones por aquellos números que salen más en primer lugar, luego miro si
    en segundo lugar son más frecuentes pares o impares, luego los de tercera posición y así sucesivamente
    La primera combinación empieza por el más frecuente, la segunda por el segundo más frecuente y así sucesivamente
    :param comb: lista formada por las tuplas de números que componen todas las combinaciones
    :param qcomb: cantidad de combinaciones que se quieren devolver
    :return: Lista con qcomb combinaciones (listas) de números
    '''
    # Convierto la lista de combinaciones en un diccionario. La clave será el nº de orden de cada elemento de cada
    # tupla que compone comb y el valor, la lista de números que aparecen en esa posición

    # elementos que componen cada tupla:

    qcombs = len(comb)  # Número de combinaciones analizadas
    betsize = len(comb[0])  # Cantidad de números que componen la apuesta
    if not qcombs:
        print('evenodded: No hay combinaciones que analizar')
        exit()

    contador_n1 = Counter([comb[k][0] for k in range(qcombs) if comb[k][0]])
    frq_n1 = {x:round(y/sum(contador_n1.values())*100, 1) for x, y in contador_n1.items()}
    frq_n1 = dict(sorted(frq_n1.items(), key=lambda item: item[1]))

    avg_frq_n1 = round(sum(frq_n1.values())/len(frq_n1), 2)
    closest_avg = list(frq_n1.keys())[bisect_left(list(frq_n1.values()), avg_frq_n1)]
    firstmostextracted = [valext[0] for valext in Counter([comb[k][0] for k in range(qcombs)]).most_common(qcomb)]
    # newcomb = {k: Counter([comb[i][k] for i in range(qnumb)]).most_common(qcomb) for k in range(qcomb)}
    print(f'evenodded. Números en posición n1 más frecuentes: {firstmostextracted[:qcomb]}.\n'
          f'{qcombs} combinaciones analizadas')

    selcomb = {}
    selevenodd = {}
    selcombmod = {}  # Diccionario para pruebas
    selevenoddmod = {}  # Diccionario para pruebas
    # bucle para ir extrayendo los números hermanados + parimparados
    for firstnumb in firstmostextracted:
        # añado a la combinación el primer número seleccionado
        selcomb[firstmostextracted.index(firstnumb)] = [firstnumb,]
        selevenodd[firstmostextracted.index(firstnumb)] = [iseven(firstnumb)]

        # Bloque de pruebas para ver las hermanadas, pero, en lugar de tomar siempre los números más frecuentes
        # asociados al más frecuente que sale en primera posición, miro el más frecuente de posición n+1 cuando n vale
        # lo que haya salido anteriormente.
        selcombmod[firstmostextracted.index(firstnumb)] = [firstnumb,]
        selevenoddmod[firstmostextracted.index(firstnumb)] = [iseven(firstnumb)]

        prevext = firstnumb
        prevextmod = firstnumb  # para pruebas versión 2 hermanadas
        # ********** eliminar después de probar

        # TODO ********** eliminar después de probar
        for ordenextraccion in range(1,betsize):
            # Tomo los siguientes números más frecuentes excluyendo los None
            nextmostextractedlist = [comb[k][ordenextraccion]
                                     for k in range(qcombs)
                                     if comb[k][0] == prevext and
                                     comb[k][ordenextraccion]]
            contador_nme = Counter(nextmostextractedlist)
            nextmostextractedlistmod = [comb[k][ordenextraccion]
                                        for k in range(qcombs)
                                        if comb[k][ordenextraccion-1] == prevextmod and
                                        comb[k][ordenextraccion]]
            contador_nmemod = Counter(nextmostextractedlistmod)
            nextmostextracted = [nextval[0] for nextval in contador_nme.most_common(qcomb)]
            nextmostfreqevenodd = Counter([iseven(comb[k][ordenextraccion])
                                  for k in range(qcombs)
                                  if comb[k][0] == prevext]).most_common()
            # Pruebas hermanadas 2
            nextmostextractedmod = [nextval[0] for nextval in contador_nmemod.most_common(qcomb)]
            nextmostfreqevenoddmod = Counter([iseven(comb[k][ordenextraccion])
                                  for k in range(qcombs)
                                  if comb[k][ordenextraccion - 1] == prevextmod]).most_common()
            # print(f'Valores frecuentes extraídos en {ordenextraccion + 1}º lugar cuando el primero es '
            #       f'es {prevext}: {nextmostextracted}')
            # print(f'Valores frecuentes extraídos en {ordenextraccion + 1}º lugar cuando el anterior es '
            #       f'es {prevextmod}: {nextmostextractedmod}')
            prevextmod = nextmostextractedmod[0]
            # added = False
            num2add = nextmostextracted[0]
            num2addevenodd = nextmostfreqevenodd[0][0]  # Nos indica si el número a añadir debe ser par o impar
            for i in range(len(nextmostextracted)):
                # Compruebo que el número a añadir no es None, que no ha sido seleccionado previamente entre los 6
                # primeros números de Primitiva o los 5 de Euromillón, lo que equivale a que los 2 últimos números sí
                # podrían estar repetidos (complementario y reintegro o las 2 estrellas), y que es par o impar según
                # el valor de nextmostfreqevenodd
                if nextmostextracted[i] and \
                        iseven(nextmostextracted[i]) == num2addevenodd and \
                        (i < betsize-2 and nextmostextracted[i] not in selcomb[firstmostextracted.index(firstnumb)]):
                    num2add = nextmostextracted[i]
                    break

            # INI bloque pruebas
            num2addmod = nextmostextractedmod[0]
            num2addevenoddmod = nextmostfreqevenoddmod[0][0]  # Nos indica si el número a añadir debe ser par o impar
            for i in range(len(nextmostextractedmod)):
                # Compruebo que el número a añadir no es None, que no ha sido seleccionado previamente entre los 6
                # primeros números de Primitiva o los 5 de Euromillón, lo que equivale a que los 2 últimos números sí
                # podrían estar repetidos (complementario y reintegro o las 2 estrellas), y que es par o impar según
                # el valor de nextmostfreqevenodd
                if nextmostextractedmod[i] and \
                        iseven(nextmostextractedmod[i]) == num2addevenoddmod and \
                        (i < betsize-2 and nextmostextractedmod[i] not in
                         selcombmod[firstmostextracted.index(firstnumb)]):
                    num2addmod = nextmostextractedmod[i]
                    break
            # FIN Bloque pruebas
            selcomb[firstmostextracted.index(firstnumb)].append(num2add)
            selcombmod[firstmostextracted.index(firstnumb)].append(num2addmod)
            # Actualizamos el siguiente número a buscar (lo desestimamos si es None)
            # prevext = nextmostextracted[0] if nextmostextracted[0] else nextmostextracted[1]
        # print(f'Combinación {firstmostextracted.index(firstnumb)}: {selcomb[firstmostextracted.index(firstnumb)]}')

    print(f'\n'
          f'**************************************\n'
          f'*  Resultados siblinged parimparada  *\n'
          f'**************************************')
    for clave, valor in selcomb.items():
        print(f'Combinación {clave + 1}: {valor}')

    print(f'\n'
          f'*****************************************\n'
          f'*  Resultados siblinged parimparada V2  *\n'
          f'*****************************************')
    for clave, valor in selcombmod.items():
        print(f'Combinación {clave + 1}: {valor}')


    return selcomb


def buscapremios():
    """
    Busca si alguna de las combinaciones de las tablas SelEuro y SelPrimi aparece en PremiadosEuro o
    PremiadosPrimi.
    En el caso de la Primitiva no se tiene en cuenta el complementario
    :return: None si no hay o diccionario con la combinación premiada y las fechas del premio y cuando fue sellada
    """
    tablasresultados = [lotoparams.PRIMITIVA, lotoparams.EUROMILLONES]
    tablaspremios = [lotoparams.PREMIADOSPRIMI, lotoparams.PREMIADOSEURO]
    tablasjugadas = [lotoparams.SELPRIMI, lotoparams.SELPRIMITOT, lotoparams.SELEURO, lotoparams.SELEUROTOT]
    encontradosprimi = 0
    encontradoseuro = 0
    try:
        con = sql_connection()
        cursor = con.cursor()
        for misapuestas in tablasjugadas:
            # En la primitiva se verifican los 6 números de la combinación y en euromillones, por un lado los
            # 5 números y por otro las 2 estrellas
            qnumverif = 6 if tablasjugadas.index(misapuestas) in [0, 1] else 5
            sorteo = lotoparams.PRIMITIVA if qnumverif == 6 else lotoparams.EUROMILLONES

            camposjugados = sql_getcolumnname(con, misapuestas)
            del(camposjugados[1])  # No consideramos el campo idcomb de las tablas de combinaciones seleccionadas
            sqlcamposjugados = ', '.join(camposjugados)
            camposextraidos = sql_getcolumnname(con, sorteo)
            # del(camposextraidos[0])  # No consideramos el campo idx de las tablas de combinaciones extraidas
            # en los sorteos
            camposextraidos.remove('idx')  # No consideramos el campo idx de las tablas de combinaciones extraidas
            # en los sorteos
            if 'compl' in camposextraidos:
                camposextraidos.remove('compl')  # No consideramos el campo compl de las tablas de
                # combinaciones extraidas en los sorteos
            sqlcamposextraidos = ', '.join(camposextraidos)

            sql_command = f'SELECT {sqlcamposjugados} FROM {misapuestas}'
            cursor.execute(sql_command)
            jugados = cursor.fetchall()  # tupla con todas las combinaciones seleccionadas
            # Extraigo las fechas a verificar
            fechasaverif = list(set([c[0] for c in jugados]))
            sql_command = f'SELECT {sqlcamposextraidos} FROM {sorteo}'
            cursor.execute(sql_command)
            extraidos = cursor.fetchall()  # tupla con todas las combinaciones extraídas
            for fecha in fechasaverif:
                # Busco los resultados del sorteo para esa fecha:
                if '.' in fecha:  # se trata de una combinación calculada con el total de los sorteos y tiene
                                    # formato AAAA.ss (año.semana)
                    premiada = [cpremi for cpremi in extraidos if formateafecha(cpremi[0]) == fecha]
                else:
                    premiada = [cpremi for cpremi in extraidos if cpremi[0] == fecha]

                if not premiada:  # Premiada es None cuando aún no se ha celebrado un sorteo para el que hemos apostado
                    continue
                # if qnumverif == 6:  # En la primitiva, no considero el complementario
                #     complementario = premiada[0][7]
                #     premiada = list(premiada[0])
                #     premiada.remove(complementario)
                seleccionadas = [cselec for cselec in jugados if cselec[0] == fecha]
                printreintegro = True
                for seleccionada in seleccionadas:
                    # numcoincidentes = list(set(premiada[0][1:qnumverif+1]) & set(seleccionada[1:qnumverif+1]))
                    numcoincidentes = list(set(premiada[0][1:qnumverif]) & set(seleccionada[1:qnumverif]))
                    qnumcoincidentes = len(numcoincidentes)
                    # print(f'{fecha}: {qnumcoincidentes} aciertos en {misapuestas}')

                    msgpremios = ''  # Mensaje de combinaciones premiadas
                    if qnumverif == 5:  # Euromillones, compruebo las estrellas
                        estrellascoincidentes = list(set(premiada[0][qnumverif+1:]) & set(seleccionada[qnumverif+1:]))
                        qestrellascoincidentes = len(estrellascoincidentes)
                        if qnumcoincidentes == 1:  # En Euromillones, se premia desde 1 num + 2 estrellas o 2 num
                            if qestrellascoincidentes == 2:
                                encontradoseuro += 1
                                msgpremios = f'La apuesta de Euromillón de {seleccionada[0]}: {seleccionada[1:]} ' \
                                             f'tiene premio. \n ' \
                                             f'Se ha acertado {qnumcoincidentes} número y {qestrellascoincidentes} ' \
                                             f'estrellas \n\t{numcoincidentes} + {estrellascoincidentes}'
                        elif qnumcoincidentes >= 2:
                            encontradoseuro += 1
                            if qestrellascoincidentes > 0:
                                msgpremios = f'La apuesta de Euromillón de {seleccionada[0]}: {seleccionada[1:]} ' \
                                             f'tiene premio. \n ' \
                                             f'Se han acertado {qnumcoincidentes} números y {qestrellascoincidentes} ' \
                                             f'estrellas \n\t{numcoincidentes} + {estrellascoincidentes}'
                            else:
                                msgpremios = f'la apuesta de Euromillón de {seleccionada[0]}: {seleccionada[1:]} ' \
                                             f'tiene premio. \n ' \
                                             f'Se han acertado {qnumcoincidentes} números' \
                                             f'\n\t{numcoincidentes} + {estrellascoincidentes}'
                    else:  # Primitiva, compruebo los aciertos
                        recoincidente = list(set(premiada[0][qnumverif+1:]) & set(seleccionada[qnumverif+1:]))
                        if qnumcoincidentes >= 3:
                            encontradosprimi += 1
                            if recoincidente and printreintegro:  # Ha tocado el reintegro
                                printreintegro = False  # Para imprimir sólo una vez el premio del reintegro
                                msgpremios = f'La apuesta de Primitiva de {seleccionada[0]}: {seleccionada[1:]} ' \
                                             f'tiene premio. \n ' \
                                             f'Se han acertado {qnumcoincidentes} números y ' \
                                             f'el reintegro\t{recoincidente} \n' \
                                             f'Números acertados\t{numcoincidentes}'

                            else:  # Premio de Primitiva, más de 3 aciertos
                                msgpremios = f'La apuesta de Primitiva de {seleccionada[0]}: {seleccionada[1:]} ' \
                                             f'tiene premio. \n ' \
                                             f'Se han acertado {qnumcoincidentes} números \n' \
                                             f'Números acertados\t{numcoincidentes}'
                        elif recoincidente and printreintegro:  # Sólo reintegro
                            printreintegro = False  # Para imprimir sólo una vez el premio del reintegro
                            encontradosprimi += 1
                            msgpremios = f'La apuesta de Primitiva de {seleccionada[0]}: {seleccionada[1:]} ' \
                                         f'ha obtenido el reintegro\t{recoincidente}'

                    if msgpremios:
                        print(msgpremios)
    except Error:
        print(f'{sys.modules[__name__]}: Error abriendo la base de datos de loterías')

    print(f'Se han encontrado {encontradosprimi} en la Primitiva')
    print(f'Se han encontrado {encontradoseuro} en Euromillones')


buscapremios()
