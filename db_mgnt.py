#!/usr/bin/env python3
# -*- coding: cp1252 -*-

import sys
import sqlite3
from collections import Counter
from sqlite3 import Error

import constants as cte


def sql_connection(db: [str, None] = None):
    """
    Conexión a la base de datos de loterías
    :return: conexión a la base de datos
    """
    con = None
    if not db:
        print(f"{__file__} ERROR - No se ha introducido ninguna base de datos a la que conectar")
    try:
        con = sqlite3.connect(db)
        return con
    except Error:
        con.close()
        print('Error abriendo base de datos en sql_connection')
        print(Error)


def sql_table(con, tabla):
    """
    ************    SIN USO ****************
    función para insertar tablas en la db de loterias
    :param con: conexión a base de datos
    :param tabla: tabla a crear
    :return:
    """
    campos = None  # Inicializo los campos
    if tabla == cte.PRIMITIVA:
        campos = list(zip(cte.PRIMIFIELDS,
                          list(map(lambda x: 'date' if x == 'fecha' else 'integer', cte.PRIMIFIELDS))))
    elif tabla == cte.EUROMILLONES:
        campos = list(zip(cte.EUROFIELDS,
                          list(map(lambda x: 'date' if x == 'fecha' else 'integer', cte.EUROFIELDS))))

    sqlorder = f'CREATE TABLE if not exists {tabla}('
    primercampo = True
    # construimos la tabla con sus campos
    for campo in campos:
        print('sql_table', campo)
        if primercampo:
            sqlorder += f'{campo[0]} {campo[1]} PRIMARY KEY'
            primercampo = False
        else:
            sqlorder += f', {campo[0]} {campo[1]}'
    sqlorder += ')'
    cursorObj = con.cursor()  # objeto cursor sqlite3
    # print('sql_table: ', sqlorder)
    cursorObj.execute(sqlorder)
    con.commit()


def sql_insert(con, tabla, campos, valores):
    cur = con.cursor()
    vals = '?' + ', ?' * (len(campos) - 1)
    campos2insert = ', '.join(campos)
    sqlstmt = f'INSERT INTO {tabla}({campos2insert}) VALUES({vals})'
    try:
        cur.execute(sqlstmt, valores)
        con.commit()
        print('Registro insertado (sql_insert)')
    except Error:
        print('Error insertando registro en sql_insert')


def sql_find(con, tabla, campo, valor):
    cursorObj = con.cursor()
    sqlorder = f'SELECT * FROM {tabla} WHERE {campo}="{valor}"'

    # print('sql_find', sqlorder)
    cursorObj.execute(sqlorder)
    registro = cursorObj.fetchall()
    return registro


def sql_recordcount(con, tabla):
    """
    devuelve el número de registros de una tabla
    :param con:
    :param tabla:
    :return:
    """
    cursorObj = con.cursor()
    cursorObj.execute(f'SELECT * FROM {tabla}')
    q_registros = len(cursorObj.fetchall())
    return q_registros


def sql_getcolumn(con, tabla, campos, dias=(x for x in range(7)), ):
    """
    devuelve los valores de las campos seleccionados en las fechas seleccionadas
    en el campo dias. dia 0 es domingo, dia 6 es sábado. Ojo, domingo puede ser 0 ó 7, pero no afecta.
    :param con: conexión a base de datos sqlite3
    :param tabla: datos de las loterias
    :param dias: dias seleccionados para el sorteo
    :param campos: campos de la base de datos
    :return: diccionario con el campo como clave y una lista con los datos selecconados como valor
    """

    cursorObj = con.cursor()
    if isinstance(campos, (list, tuple)):
        sqlcampos = ', '.join(campos)
    else:
        sqlcampos = campos
        campos = [campos, ]

    if not isinstance(dias, (list, tuple)):
        sqlcommand = f'SELECT {sqlcampos} FROM {tabla} WHERE CAST (strftime("%w", fecha) AS Integer) = {dias}'
    else:
        sqlcommand = f'SELECT {sqlcampos} FROM {tabla} WHERE CAST (strftime("%w", fecha) AS Integer) in {dias}'

    try:
        cursorObj.execute(sqlcommand)
        valores = cursorObj.fetchall()
        valores = {campo: [val[campos.index(campo)] for val in valores] for campo in campos}
        # print(f'{len(valores)} valores encontrados', valores)
        return valores
    except Error:
        print(f'Error recuperando datos de campo {campos}')


def sql_get_value_in_column(con, tabla, campo1, campo2, valor_campo1, dias=(x for x in range(7)), ):
    """
    devuelve los valores de las campos seleccionados en las fechas seleccionadas
    en el campo dias. dia 0 es domingo, dia 6 es sábado
    :param con: conexión a base de datos sqlite3
    :param tabla: datos de las loterias
    :param campo1: campo de la base de datos en el que buscar valor_campo1
    :param campo2: campo de la base de datos de registros con campo1 = valor_campo1
    :param valor_campo1: valor a buscar en campo1
    :param dias: dias seleccionados para el sorteo
    :return: lista con los datos selecconados
    """

    if tabla == cte.PRIMITIVA:
        campos = cte.PRIMIFIELDS
    elif tabla == cte.EUROMILLONES:
        campos = cte.EUROFIELDS
    else:
        print('Analiza: Base de datos no encontrada')
        raise FileNotFoundError

    # Compruebo si los campos son válidos
    campovalido = True
    if campo1 not in campos:
        print(f'{campo1} no es un campo válido en {tabla}')
        campovalido = False
    if campo2 not in campos:
        print(f'{campo2} no es un campo válido en {tabla}')
        campovalido = False
    if not campovalido:
        print('sql_get_value_in_column: Saliendo de la aplicación por campos inválidos')
        sys.exit()

    # campoidx = campos.index(campo1)
    # nextcampo = campoidx + 1
    # if nextcampo > len(campos) - 1:
    #     print(f'sql_get_value_in_column: Superado el número de campos, {nextcampo} debe ser <= {len(campos)}')
    #     nextcampo = campoidx

    cursorObj = con.cursor()
    sqlcommand = f'SELECT {campo2} FROM {tabla} WHERE ' \
                 + f'(CAST (strftime("%w", fecha) AS Integer) = {dias} AND ' \
                 + f'{campo1} = {valor_campo1})'

    cursorObj.execute(sqlcommand)
    valores = cursorObj.fetchall()
    valores = {campo2: [val[0] for val in valores]}
    # print(f'{len(valores)} valores encontrados', valores)
    return valores


def sql_getcolumnname(con, tabla):
    cur = con.cursor()
    cursor = cur.execute(f"SELECT * FROM {tabla};")
    names = list(map(lambda x: x[0], cursor.description))
    return names


def sql_checkifexists(con, tabla, valores, campos=None):
    """
    comprueba si en la tabla "tabla" existe algún registro con la combinación de valores "valores"
    :param con: conexión de base de datos de sqlite3
    :param tabla: tabla en la que buscar
    :param valores: combinación de valores de campos a buscar
    :param campos: lista de campos en los que buscar los valores
    :return: tupla con valor True y el valor encontrado si existe
            False si no existe
    """
    if not campos:
        campos = sql_getcolumnname(con, tabla)

    if len(campos) != len(valores):
        print(f'{sys.modules[__name__]}: El nº de campos de {tabla} no coincide con la cantidad de valores')
        return False, None

    sql_command = f'SELECT * FROM {tabla} WHERE {campos[0]}="{valores[0]}" '
    for campo in campos[1:]:
        idx = campos.index(campo)
        sql_command += f'AND {campo}={valores[idx]} '
    # print('checkifexists: ', sql_command)
    cursor = con.cursor()
    cursor.execute(sql_command)
    exist = cursor.fetchone()
    if not exist:
        return False, None
    else:
        # print(f'checkifexists: el registro ({valores}) ya existe')
        return True, exist


def get_most_freq(tabla: dict, q_num: int = cte.Q_NUM_MAS_FREQ):
    """
    lista ordenada en función de la frecuencia de aparición de los números que componen las listas de valores
    de cada campo clave
    :param tabla: diccionario con los campos de los sorteos como clave y las listas con los números que han salido
    :param q_num: cantidad de números a tomar en la lista de más frecuentes
    :return: diccionario con las mismas claves que la tabla y los valores serán una lista de números, ordenados por su
    frecuencia de aparición
    """
    tabla_by_freq = {}
    for clave in tabla:
        # len_clave = len(list(Counter(tabla[clave])))
        clave_by_freq = Counter(tabla[clave]).most_common(q_num)
        clave_by_freq = [num[0] for num in clave_by_freq if num[0]][:q_num]
        tabla_by_freq[clave] = clave_by_freq

    return tabla_by_freq

def get_last_comb(con, table, day=None):
    '''
    Devuelve la ultima combinacion almacenada en la tabla "table", de la base de datos "con", del sorteo del dia "day"
    :param con: conexion a la base de datos
    :param table: tabla de la base de datos de la que se extraera la combinacion PRIMITIVA o EUROMILLONES
    :param day: dia de la semana en que tuvo lugar el sorteo. para este programa lunes, martes, jueves, viernes o
    sabado. cuando day=none, se devuelve la ultima combinacion guardada
    Eso quiere decir que extrayendo los ultimos 5 valores, debo mirar a que dia de la semana corresponde el campo
    fecha
    :return: lista con las ultimas 5 combinaciones
    '''
    cmd = f'SELECT * FROM {table} ORDER BY rowid DESC LIMIT 5'
    cursor = con.cursor()
    cursor.execute(cmd)
    combs = cursor.fetchall()
    return combs

