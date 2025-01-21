#!
# -*- coding: cp1252 -*-

import requests
import constants as cte
import re
import time

from datetime import datetime, timedelta


def getPrimiLatestResults():
    '''
    Devuelve un diccionario con los resultados de primitiva del último mes, siendo la clave una cadena
    con la fecha y el valor una lista con los números extraídos.
    La fecha final corresponde al lunes de la semana siguiente a la actual y la fecha inicial a la del lunes de
    5 semanas atrás
    :return: diccionario {fecha: [num1, num2, num3, num4, num5, num6, comp, re]}
            1 si ha habido algún error
    '''
    headers = {"User-Agent": "Mozilla/5.0",
               "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
               "Accept-Encoding": "gzip, deflate, br",
               "Connection": "keep-alive",
               }
    # Simula un retraso para evitar parecer un bot
    time.sleep(2)

    # En 2025 he tenido que cambiar la forma de extraer los números de la primitiva, utilizando una script que
    # encontré mientras inspeccionaba la web de primitivas y que se llama buscadorSorteos
    next_monday = datetime.now() + timedelta(days=8-datetime.now().isoweekday())
    four_mondays_ago = next_monday + timedelta(weeks=-4)

    url_Resultados_Primitiva = (f"https://www.loteriasyapuestas.es/servicios/buscadorSorteos?"
                               f"game_id=LAPR&celebrados=true&fechaInicioInclusiva="
                                f"{four_mondays_ago.year}{four_mondays_ago.month:02d}{four_mondays_ago.day:02d}&"
                                f"fechaFinInclusiva={next_monday.year}{next_monday.month:02d}{next_monday.day:02d}")
    response = requests.get(url_Resultados_Primitiva, headers=headers)
    response.raise_for_status()  # Lanza una excepción si hay un error HTTP
    # Verificar el estado de la respuesta
    if response.status_code != 200:
        print(f"Error accediendo a la web {cte.PRIMIWEB}\n Código de Error: {response.status_code}")
        return 1
    print('++++++++++++++   COMBINACIONES PRIMITIVA +++++++++++++++++')
    #
    sorteos = response.json()  # En 2025, la web de primitivas devuelve un json con los resultados.
    combinaciones_extraidas = {}
    for sorteo in sorteos:
        fecha = sorteo.get("fecha_sorteo")
        if fecha is None:
          continue
        str_comb = sorteo.get("combinacion")
        combinaciones_extraidas[fecha[0:10]] = list(map(int, re.findall(r'\d+', str_comb)))
    return combinaciones_extraidas


# # print(get_primi_latest_results())
#
# # Ejemplo de uso
# if __name__ == "__main__":
#     # # Fecha de ejemplo: 5 de enero de 2025
#     # fecha_ejemplo = datetime(2025, 1, 5)
#     resultados = getPrimiLatestResults()
#     print(resultados)
