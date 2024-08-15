#!
# -*- coding: cp1252 -*-

import requests
from bs4 import BeautifulSoup
from loterias_tools.loteriasdb import lotoparams
import re

def procesa_fecha(fecha):
    meses = {'ene':'01', 'feb':'02', 'mar':'03', 'abr':'04', 'mayo':'05', 'jun':'06',
             'jul':'07', 'ago':'08', 'sep':'09', 'oct':'10', 'nov':'11', 'dic':'12'}

    fecha = fecha.text.strip().split(' ')
    # print('procesa fecha', fecha)
    dia = re.sub("[^0-9]", "", fecha[0])
    dia = dia if int(dia) > 9 else '0' + dia
    mes = meses[fecha[1]]
    anno = fecha[2]
    fecha_corta =  anno + '-' + mes + '-' + dia
    return fecha_corta

def get_primi_latest_results():
    '''
    Devuelve un diccionario con los últimos resultados de primitiva, siendo la clave una cadena
    con la fecha y el valor una lista con los números extraídos
    :return: diccionario {fecha: [num1, num2, num3, num4, num5, estrella1, estrella2]}
    '''
    response = requests.get(lotoparams.PRIMIWEB)
    soup = BeautifulSoup(response.text,'lxml')
    # print(soup)
    print('++++++++++++++   COMBINACIONES PRIMITIVA +++++++++++++++++')
    combinaciones_extraidas = {}

    sorteos = soup.find_all('h2')
    for sorteo in sorteos:
        fechas = sorteo.find_all('a', attrs={'class': 'elem2'})
        bolas = sorteo.find_all('li', attrs={'class': 'ball'})
        complementarios = sorteo.find_all('li', attrs={'class': 'bonus-ball bonus'})
        reintegros = sorteo.find_all('li', attrs={'class': 'reintegro bonus'})
        comb = []
        for fecha in fechas:
            fecha = procesa_fecha(fecha)
            # print('Fecha', fecha)
            for bola in bolas:
                # print('Bola', bola.text)
                comb.append(int(bola.text))
            for complementario in complementarios:
                # print('Complementario', complementario.text)
                comb.append(int(complementario.text))
            for reintegro in reintegros:
                # print('Reintegro', reintegro.text)
                comb.append(int(reintegro.text))
            combinaciones_extraidas[fecha] = comb

    # for combinacion in reversed(ult_result):
    #     print(combinacion, ult_result[combinacion])

    return combinaciones_extraidas


# print(get_primi_latest_results())