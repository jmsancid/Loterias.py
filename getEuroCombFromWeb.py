import requests
from bs4 import BeautifulSoup
# from loterias_tools.loteriasdb import lotoparams
import constants as cte
import datetime


def procesaFecha(fecha: str):
    """
    procesa la fecha de un determinado sorteo, extraída como string de la web de euromillones
    y la convierte en un objeto Datetime
    :param fecha:
    :return:
    """
    meses = {'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06',
             'julio': '07', 'agosto': '08', 'septiembre': '09', 'octubre': 10, 'noviembre': 11, 'diciembre': 12}

    fecha_indice = fecha.find(', ')
    fecha_indice += 2
    # print('Fecha encontrada en carácter ', fecha_indice)
    fecha_larga = fecha[fecha_indice:]
    fecha_corta = fecha_larga.split(' de ')
    dia = int(fecha_corta[0].strip() if len(fecha_corta[0].strip()) > 1 else '0' + fecha_corta[0].strip())
    mes = int(meses[fecha_corta[1]])
    anno = int(fecha_corta[2])
    fecha = datetime.datetime(anno, mes, dia).date()

    # print('Fecha corta: ', fecha_corta)
    return fecha


def getEuroLatestResults():
    '''
    Devuelve un diccionario con los últimos resultados de euromillones, siendo la clave una cadena
    con la fecha y el valor una lista con los números extraídos
    :return: diccionario {fecha: [num1, num2, num3, num4, num5, estrella1, estrella2]}
    '''
    response = requests.get(cte.EUROWEB)
    # response = requests.get(lotoparams.EUROWEB)
    # soup = BeautifulSoup(response.text, 'lxml')
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup.title.text)
    # print(soup.prettify())
    numestre = soup.find_all('div', attrs={'class': 'numestre'})
    print('**************   COMBINACIONES EUROMILLONES       ****************')
    i = 0
    combinacionesExtraidas = {}
    for elemento in numestre:
        # print(elemento.text)
        fechas = elemento.find_all('h4')
        if fechas[0].text.find('Euromillones') == -1:
            continue
        # print('Fecha: ', fechas[0].text)
        i += 1
        # print('\t\t  ===========  Elemento nº', i)
        fecha = procesaFecha(fechas[0].text)
        combi = elemento.find_all('div', {'class': 'numhisto'})
        for elem in combi:
            # print(dir(elem), elem.contents)
            numeros = elem.find_all('li', {'class': 'numeros'})
            comb_num = []
            for numero in numeros:
                # print(numero.text)
                comb_num.append(int(numero.text))
            estrellas = elem.find_all('li', {'class': 'estrellas'})
            comb_est = []
            for estrella in estrellas:
                # print(estrella.text)
                comb_est.append(int(estrella.text))
            combinacion = comb_num + comb_est
            combinacionesExtraidas[fecha] = combinacion
            # print(fecha, combinacionesExtraidas[fecha])

    return combinacionesExtraidas
