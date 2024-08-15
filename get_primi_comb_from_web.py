#!
# -*- coding: cp1252 -*-

import requests
from bs4 import BeautifulSoup
from loterias_tools.loteriasdb import lotoparams
import re


def procesa_fecha(fecha):
    meses = {'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
             'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'}

    fecha = fecha.text.strip().split(' ')
    # print('procesa fecha', fecha)
    dia = re.sub("[^0-9]", "", fecha[0])
    dia = dia if int(dia) > 9 else '0' + dia
    mes = meses[fecha[1].strip('.')]
    anno = fecha[2]
    fecha_corta = anno + '-' + mes + '-' + dia
    return fecha_corta


def get_primi_latest_results():
    '''
    Devuelve un diccionario con los últimos resultados de primitiva, siendo la clave una cadena
    con la fecha y el valor una lista con los números extraídos
    :return: diccionario {fecha: [num1, num2, num3, num4, num5, estrella1, estrella2]}
    '''
    response = requests.get(lotoparams.PRIMIWEB)
    # soup = BeautifulSoup(response.text, 'lxml')
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup)
    print('++++++++++++++   COMBINACIONES PRIMITIVA +++++++++++++++++')
    #
    sorteos = soup.find_all('td')
    fechas = [sorteo.find_all('a', attrs={'class': 'smallerHeading'}) for sorteo in sorteos
              if sorteo.find_all('a', attrs={'class': 'smallerHeading'})]
    fechas = [procesa_fecha(fecha[0]) for fecha in fechas]
    bolas = [sorteo.find_all('li', attrs={'class': 'ball'}) for sorteo in sorteos
             if sorteo.find_all('li', attrs={'class': 'ball'})]
    bolas = [[int(bola[i].text) for i in range(len(bola))] for bola in bolas]
    complementarios = [sorteo.find_all('li', attrs={'class': 'bonus-ball bonus'}) for sorteo in sorteos
                       if sorteo.find_all('li', attrs={'class': 'bonus-ball bonus'})]
    complementarios = [int(complementario[0].text) for complementario in complementarios]
    reintegros = [sorteo.find_all('li', attrs={'class': 'reintegro bonus'}) for sorteo in sorteos
                  if sorteo.find_all('li', attrs={'class': 'reintegro bonus'})]
    reintegros = [int(reintegro[0].text) for reintegro in reintegros]

    combinaciones_extraidas = {fechas[i]: bolas[i] + [complementarios[i]] + [reintegros[i]]
                               for i in range(len(fechas))}

    return combinaciones_extraidas

# print(get_primi_latest_results())
