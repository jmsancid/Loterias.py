#!
# -*- coding: cp1252 -*-

from loterias_tools.loteriasdb import *
from functools import wraps
from bisect import bisect_left


def measure(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t = datetime.now()
        result = func(*args, **kwargs)
        print(func.__name__, 'tard� ', str(datetime.now() - t))
        return result
    return wrapper


def imprimecombinacion(func, *args):
    """
    Decorador
    func es una funci�n que analiza combinaciones de primitiva o euromillones y devuelve unas combinaciones
    dichas combinaciones son un diccionario que tiene como clave un entero que representa el d�a de la semana
    en el que se celebr� el sorteo (domingo = 0) y como valores otro diccionario que tiene como clave
    una identificaci�n de la apuesta y como valor la propia combinaci�n
    :param func:
    :return:
    """
    combinaciones = func(*args)
    diassemana = {0: 'Domingo', 1: 'Lunes', 2: 'Martes', 3: 'Mi�rcoles', 4: 'Jueves', 5: 'Viernes', 6: 'S�bado',
                  25: 'Martes + Viernes', 46: 'Jueves + S�bado'}
    reintegro = None
    for dia in combinaciones:
        print(f'Combinaciones del {diassemana[dia]}')
        for numcomb, combinacion in combinaciones[dia].items():
            if dia in [4, 6, 46]:  # Si es combinaci�n de Primitiva
                if numcomb == 0:
                    reintegro = combinacion[7]
                del combinacion[6:8]  # Eliminamos el n�mero complementario y el reintegro
            print(f'Combinaci�n {numcomb}: {combinacion}')
        if dia in [4, 6, 46]:
            print(f'\tReintegro: {reintegro}')


def analiza(lototype):
    """
    rutina para seleccionar 5 combinaciones de primitiva y 2 de euromillones.
    :param lototype: tipo de loter�a PRIMITIVA o EUROMILLONES
    :return: diccionario con la fecha, el n�mero de orden de la apuesta (del 0 al 4 en primitiva y
    del 0 al 1 en euromillones) y la apuesta correspondiente, sin complementario en el caso de la primitiva.
    """
    if lototype == lotoparams.PRIMITIVA:
        campos = lotoparams.PRIMIFIELDS
        camposstr = ', '.join(campos[2:len(campos)])
        dias = lotoparams.PRIMIDAYS
        apuestas = lotoparams.primibets
    elif lototype == lotoparams.EUROMILLONES:
        campos = lotoparams.EUROFIELDS
        camposstr = ', '.join(campos[2:len(campos)])
        dias = lotoparams.EURODAYS
        apuestas = lotoparams.eurobets
    else:
        print('Analiza: Base de datos no encontrada')
        raise FileNotFoundError

    # Para ver si un n�mero seleccionado hab�a salido ya, no tengo en cuenta el reintegro de la primi
    # ni las estrellas del eurom
    ignore_fields = 1 if lototype == lotoparams.PRIMITIVA else 2

    n1 = campos[2]  # El primer n�mero de la combinaci�n siempre es el 2� �ndice de campos
    print(f'... analizando base de datos {lototype}')
    combinacion = None
    con = None
    try:
        con = sql_connection()
        # cargo la �ltima combinaci�n para que no se repitan los n�meros
        recordscount = sql_recordcount(con, lototype)
        sqlcommand = f'SELECT {camposstr} FROM {lototype} WHERE idx = {recordscount}'
        selfulldb = f'SELECT {camposstr} FROM {lototype}'
        cursorObj = con.cursor()
        lastcomb = cursorObj.execute(sqlcommand)
        lastcomb = list(lastcomb.fetchall()[0])  # N� de orden de la �ltima combinaci�n

        # Primer an�lisis: Se utilizan todas las combinaciones
        fulldb = cursorObj.execute(selfulldb)
        fulldb = list(fulldb.fetchall())
        # Prueba 3: Con DataClasses
        if lototype == lotoparams.PRIMITIVA:
            totalprimi = PrimiDB().contador()
            freqevoltotprim = PrimiDB().freq_evolution()
            primijueves = PrimiDB().contador(4)
            freqevolprimijueves = PrimiDB().freq_evolution(4)
            primisabado = PrimiDB().contador(6)
            freqevolprimisabado = PrimiDB().freq_evolution(6)

        # totsorteos = siblinged(fulldb, apuestas) # Estrategia "hermanada"
        totsorteos = evenodded(fulldb, apuestas) # Estrategia "hermanada parimparada"
        print(f'Estad�sticas: combinaciones {lototype} por extracciones totales: {totsorteos}')

        combinacion = {x: {y: [] for y in range(apuestas)} for x in dias}
        combinacion[dias[0]] = totsorteos  # Combinaciones calculadas considerando todos los sorteos, martes + viernes
        # de euromill�n y jueves + s�bado de primitiva
        for dia in dias[1:]:  # Excluyo del bucle el an�lisis con todos los sorteos. Separo por d�a de sorteo
            sqlcommand = f'SELECT {camposstr} FROM {lototype} WHERE CAST (strftime("%w", fecha) AS Integer) = {dia}'
            combdia = cursorObj.execute(sqlcommand)
            combdia = list(combdia.fetchall())
            # combdiasel = siblinged(combdia, apuestas)  # Combinaciones hermanadas
            combdiasel = evenodded(combdia, apuestas)  # Combinaciones hermanadas + parimparadas
            combinacion[dia] = combdiasel

        # print(f'{lototype}: ', combinacion)
    except Error:
        print(Error)

    con.close()
    return combinacion


def siblinged(comb: list[tuple[int]], qcomb: int = 10) -> dict[int:list]:
    """
    siblinged es un alias de la estrategia hermanada, definida para mis Hermanos
    Primero se ordena la lista de combinaciones por aquellos n�meros que salen m�s en primer lugar, luego por los
    que m�s salen en segundo lugar cuando el primer n�mero es el m�s frecuente, luego el tercero m�s frecuente con
    el primero m�s frecuentey as� sucesivamente.
    La primera combinaci�n empieza por el m�s frecuente, la segunda por el segundo m�s frecuente y as� sucesivamente
    :param comb: lista formada por las listas de n�meros que componen todas las combinaciones
    :param qcomb: cantidad de combinaciones que se quieren devolver
    :return: Lista con qcomb combinaciones (listas) de n�meros
    """
    # Convierto la lista de combinaciones en un diccionario. La clave ser� el n� de orden de cada elemento de cada
    # tupla que compone comb y el valor, la lista de n�meros que aparecen en esa posici�n

    # elementos que componen cada tupla:

    combsize = len(comb)  # N�mero de combinaciones analizadas
    betsize = len(comb[0])  # Cantidad de n�meros que componen la apuesta
    if not combsize:
        print('siblinged: No hay combinaciones que analizar')
        exit()

    firstmostextracted = [valext[0] for valext in Counter([comb[k][0] for k in range(combsize)]).most_common(qcomb)]
    # newcomb = {k: Counter([comb[i][k] for i in range(qnumb)]).most_common(qcomb) for k in range(qcomb)}
    print(f'siblinged: {firstmostextracted[:qcomb]}. \n{combsize} combinaciones analizadas')

    selcomb = {}
    #bucle para ir extrayendo los n�meros hermanados
    for firstnumb in firstmostextracted:
        # mostextracted = [valext[0] for valext in Counter([comb[k][idxpos] for k in range(combsize)]).most_common(qcomb)]
        # prevext = mostextracted[idxpos]  # El n�mero extra�do en la posici�n anterior a la buscada
        selcomb[firstmostextracted.index(firstnumb)] = [firstnumb,]
        prevext = firstnumb
        for ordenextraccion in range(1,betsize):
            nextmostextracted = [nextval[0] for nextval in Counter([comb[k][ordenextraccion]
                                  for k in range(combsize)
                                  # if comb[k][ordenextraccion - 1] == prevext]).most_common(qcomb)]
                                  if comb[k][0] == prevext]).most_common(qcomb)]
            # print(f'Valores frecuentes extra�dos en {ordenextraccion + 1}� lugar cuando el primero es '
            #       f'es {prevext}: {nextmostextracted}')
            added = False
            num2add = nextmostextracted[0]
            for i in range(len(nextmostextracted)):
                # Compruebo que el n�mero a a�adir no es None y que no ha sido seleccionado previamente entre los 6
                # primeros n�meros de Primitiva o los 5 de Euromill�n, lo que equivale a que los 2 �ltimos n�meros s�
                # podr�an estar repetidos (complementario y reintegro o las 2 estrellas)
                if nextmostextracted[i] and \
                        (i < betsize-2 and nextmostextracted[i] not in selcomb[firstmostextracted.index(firstnumb)]):
                    num2add = nextmostextracted[i]
                    break
            selcomb[firstmostextracted.index(firstnumb)].append(num2add)
            # Actualizamos el siguiente n�mero a buscar (lo desestimamos si es None)
            # prevext = nextmostextracted[0] if nextmostextracted[0] else nextmostextracted[1]
        # print(f'Combinaci�n {firstmostextracted.index(firstnumb)}: {selcomb[firstmostextracted.index(firstnumb)]}')

    # print(f'Combinaciones seleccionadas: {selcomb}')

    return selcomb

def formateafecha(strfecha:str) -> str:
    """
    Convierte una cadena de fecha en formato AAAA-mm-dd en una cadena de texto A�o.semana (2021.48)
    :param strfecha: Cadena con formato fecha datetime
    :return: Cadena con formato a�o.semana para base de datos Loterias.db, c�lculos con total sorteos
    """
    weekstrfecha = int(datetime.strptime(strfecha, "%Y-%m-%d").isocalendar().week)
    fechaformateada = f'{datetime.strptime(strfecha, "%Y-%m-%d").isocalendar().year}.{weekstrfecha}'
    return fechaformateada

def iseven(val: int) -> bool:
    '''
    Devuelve True si val es par o None y false si es impar
    :param val: n�mero a comprobar si es par o im par
    :return:
    '''
    evenval = False if val and val%2 else True
    return evenval


def evenodded(comb: list[tuple[int]], qcomb: int = 10) -> dict[int:list]:
    '''
    evenodded es un alias de la estrategia parimparada, definida para mis Hermanos
    Ordeno por frecuencia de mayor a menor las combinaciones de n�meros bas�ndome en si son pares o impares.
    A diferencia de versiones anteriores, lo que miro es si siendo impar el primer n�mero, el segundo m�s frecuente
    es par o impar y as� con cada posici�n.
    Primero se ordena la lista de combinaciones por aquellos n�meros que salen m�s en primer lugar, luego miro si
    en segundo lugar son m�s frecuentes pares o impares, luego los de tercera posici�n y as� sucesivamente
    La primera combinaci�n empieza por el m�s frecuente, la segunda por el segundo m�s frecuente y as� sucesivamente
    :param comb: lista formada por las tuplas de n�meros que componen todas las combinaciones
    :param qcomb: cantidad de combinaciones que se quieren devolver
    :return: Lista con qcomb combinaciones (listas) de n�meros
    '''
    # Convierto la lista de combinaciones en un diccionario. La clave ser� el n� de orden de cada elemento de cada
    # tupla que compone comb y el valor, la lista de n�meros que aparecen en esa posici�n

    # elementos que componen cada tupla:

    qcombs = len(comb)  # N�mero de combinaciones analizadas
    betsize = len(comb[0])  # Cantidad de n�meros que componen la apuesta
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
    print(f'evenodded. N�meros en posici�n n1 m�s frecuentes: {firstmostextracted[:qcomb]}.\n'
          f'{qcombs} combinaciones analizadas')

    selcomb = {}
    selevenodd = {}
    selcombmod = {}  # Diccionario para pruebas
    selevenoddmod = {}  # Diccionario para pruebas
    # bucle para ir extrayendo los n�meros hermanados + parimparados
    for firstnumb in firstmostextracted:
        # a�ado a la combinaci�n el primer n�mero seleccionado
        selcomb[firstmostextracted.index(firstnumb)] = [firstnumb,]
        selevenodd[firstmostextracted.index(firstnumb)] = [iseven(firstnumb)]

        # Bloque de pruebas para ver las hermanadas, pero, en lugar de tomar siempre los n�meros m�s frecuentes
        # asociados al m�s frecuente que sale en primera posici�n, miro el m�s frecuente de posici�n n+1 cuando n vale
        # lo que haya salido anteriormente.
        selcombmod[firstmostextracted.index(firstnumb)] = [firstnumb,]
        selevenoddmod[firstmostextracted.index(firstnumb)] = [iseven(firstnumb)]

        prevext = firstnumb
        prevextmod = firstnumb  # para pruebas versi�n 2 hermanadas
        # ********** eliminar despu�s de probar

        # TODO ********** eliminar despu�s de probar
        for ordenextraccion in range(1,betsize):
            # Tomo los siguientes n�meros m�s frecuentes excluyendo los None
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
            # print(f'Valores frecuentes extra�dos en {ordenextraccion + 1}� lugar cuando el primero es '
            #       f'es {prevext}: {nextmostextracted}')
            # print(f'Valores frecuentes extra�dos en {ordenextraccion + 1}� lugar cuando el anterior es '
            #       f'es {prevextmod}: {nextmostextractedmod}')
            prevextmod = nextmostextractedmod[0]
            # added = False
            num2add = nextmostextracted[0]
            num2addevenodd = nextmostfreqevenodd[0][0]  # Nos indica si el n�mero a a�adir debe ser par o impar
            for i in range(len(nextmostextracted)):
                # Compruebo que el n�mero a a�adir no es None, que no ha sido seleccionado previamente entre los 6
                # primeros n�meros de Primitiva o los 5 de Euromill�n, lo que equivale a que los 2 �ltimos n�meros s�
                # podr�an estar repetidos (complementario y reintegro o las 2 estrellas), y que es par o impar seg�n
                # el valor de nextmostfreqevenodd
                if nextmostextracted[i] and \
                        iseven(nextmostextracted[i]) == num2addevenodd and \
                        (i < betsize-2 and nextmostextracted[i] not in selcomb[firstmostextracted.index(firstnumb)]):
                    num2add = nextmostextracted[i]
                    break

            # INI bloque pruebas
            num2addmod = nextmostextractedmod[0]
            num2addevenoddmod = nextmostfreqevenoddmod[0][0]  # Nos indica si el n�mero a a�adir debe ser par o impar
            for i in range(len(nextmostextractedmod)):
                # Compruebo que el n�mero a a�adir no es None, que no ha sido seleccionado previamente entre los 6
                # primeros n�meros de Primitiva o los 5 de Euromill�n, lo que equivale a que los 2 �ltimos n�meros s�
                # podr�an estar repetidos (complementario y reintegro o las 2 estrellas), y que es par o impar seg�n
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
            # Actualizamos el siguiente n�mero a buscar (lo desestimamos si es None)
            # prevext = nextmostextracted[0] if nextmostextracted[0] else nextmostextracted[1]
        # print(f'Combinaci�n {firstmostextracted.index(firstnumb)}: {selcomb[firstmostextracted.index(firstnumb)]}')

    print(f'\n'
          f'**************************************\n'
          f'*  Resultados siblinged parimparada  *\n'
          f'**************************************')
    for clave, valor in selcomb.items():
        print(f'Combinaci�n {clave + 1}: {valor}')

    print(f'\n'
          f'*****************************************\n'
          f'*  Resultados siblinged parimparada V2  *\n'
          f'*****************************************')
    for clave, valor in selcombmod.items():
        print(f'Combinaci�n {clave + 1}: {valor}')


    return selcomb


def buscapremios():
    """
    Busca si alguna de las combinaciones de las tablas SelEuro y SelPrimi aparece en PremiadosEuro o
    PremiadosPrimi.
    En el caso de la Primitiva no se tiene en cuenta el complementario
    :return: None si no hay o diccionario con la combinaci�n premiada y las fechas del premio y cuando fue sellada
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
            # En la primitiva se verifican los 6 n�meros de la combinaci�n y en euromillones, por un lado los
            # 5 n�meros y por otro las 2 estrellas
            qnumverif = 6 if tablasjugadas.index(misapuestas) in [0, 1] else 5
            sorteo = lotoparams.PRIMITIVA if qnumverif == 6 else lotoparams.EUROMILLONES

            camposjugados = sql_getcolumnname(con, misapuestas)
            del(camposjugados[1])  # No consideramos el campo idcomb de las tablas de combinaciones seleccionadas
            sqlcamposjugados = ', '.join(camposjugados)
            camposextraidos = sql_getcolumnname(con, sorteo)
            del(camposextraidos[0])  # No consideramos el campo idx de las tablas de combinaciones extraidas
            # en los sorteos
            sqlcamposextraidos = ', '.join(camposextraidos)

            sql_command = f'SELECT {sqlcamposjugados} FROM {misapuestas}'
            cursor.execute(sql_command)
            jugados = cursor.fetchall()  # tupla con todas las combinaciones seleccionadas
            # Extraigo las fechas a verificar
            fechasaverif = list(set([c[0] for c in jugados]))
            sql_command = f'SELECT {sqlcamposextraidos} FROM {sorteo}'
            cursor.execute(sql_command)
            extraidos = cursor.fetchall()  # tupla con todas las combinaciones extra�das
            for fecha in fechasaverif:
                # Busco los resultados del sorteo para esa fecha:
                if '.' in fecha:  # se trata de una combinaci�n calculada con el total de los sorteos y tiene
                                    # formato AAAA.ss (a�o.semana)
                    premiada = [cpremi for cpremi in extraidos if formateafecha(cpremi[0]) == fecha]
                else:
                    premiada = [cpremi for cpremi in extraidos if cpremi[0] == fecha]

                if not premiada:  # Premiada es None cuando a�n no se ha celebrado un sorteo para el que hemos apostado
                    continue
                if qnumverif == 6:  # En la primitiva, no considero el complementario
                    complementario = premiada[0][7]
                    premiada = list(premiada[0])
                    premiada.remove(complementario)
                seleccionadas = [cselec for cselec in jugados if cselec[0] == fecha]
                for seleccionada in seleccionadas:
                    numcoincidentes = list(set(premiada[0][1:qnumverif+1]) & set(seleccionada[1:qnumverif+1]))
                    qnumcoincidentes = len(numcoincidentes)
                    # print(f'{fecha}: {qnumcoincidentes} aciertos en {misapuestas}')

                    if qnumverif == 5:  # Euromillones, compruebo las estrellas
                        estrellascoincidentes = list(set(premiada[0][qnumverif+1:]) & set(seleccionada[qnumverif+1:]))
                        qestrellascoincidentes = len(estrellascoincidentes)
                        if qnumcoincidentes == 1:  # En Euromillones, se premia desde 1 num + 2 estrellas o 2 num
                            if qestrellascoincidentes == 2:
                                encontradoseuro += 1
                                print(f'la apuesta de Euromill�n de {seleccionada[0]}: {seleccionada[1:]} tiene '
                                      f'premio. \n '
                                      f'Se ha acertado {qnumcoincidentes} n�mero y {qestrellascoincidentes} estrellas')
                                print(f'\t{numcoincidentes} + {estrellascoincidentes}')
                        elif qnumcoincidentes >= 2:
                            encontradoseuro += 1
                            if qestrellascoincidentes > 0:
                                print(f'la apuesta de Euromill�n de {seleccionada[0]}: {seleccionada[1:]}  tiene '
                                      f'premio. \n '
                                      f'Se han acertado {qnumcoincidentes} n�meros y {qestrellascoincidentes} estrellas')
                                print(f'\t{numcoincidentes} + {estrellascoincidentes}')
                            else:
                                print(f'la apuesta de Euromill�n de {seleccionada[0]}: {seleccionada[1:]}  tiene '
                                      f'premio. \n '
                                      f'Se han acertado {qnumcoincidentes} n�meros')
                                print(f'\t{numcoincidentes}')
                    else:  # Primitiva, compruebo los aciertos
                        if qnumcoincidentes >= 3:  # Premio de Primitiva
                            encontradosprimi += 1
                            print(f'las apuestas de Primitiva {seleccionada[0]}: {seleccionada[1:]}  tiene premio. \n '
                                  f'Se han acertado {qnumcoincidentes} n�meros')
                            print(f'\t{numcoincidentes}')

    except Error:
        print(f'{sys.modules[__name__]}: Error abriendo la base de datos de loter�as')

    print(f'Se han encontrado {encontradosprimi} en la Primitiva')
    print(f'Se han encontrado {encontradoseuro} en Euromillones')


buscapremios()
