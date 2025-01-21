#!/usr/bin/env python3
# -*- coding: cp1252 -*-
from datetime import datetime

cur_year = str(datetime.now().year)  # Año actual para descargar las combinaciones de primitiva
PRIMIFIELDS = ('idx', 'fecha', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'compl', 're')  # campos de la db de primitivas
EUROFIELDS = ('idx', 'fecha', 'n1', 'n2', 'n3', 'n4', 'n5', 'e1', 'e2')  # campos de la db de euromillones
PRIMITIVA = 'Primitiva'  # Nombre de la db con todas las combinaciones históricas de Primitiva
SELPRIMI = 'SelPrimi'  # Nombre de la db con todas las apuestas de Primitiva, identificadas por jueves y sábado
SELPRIMITOT = 'SelPrimiTot'  # Nombre de la db con todas las apuestas de Primitiva considerando todos los números,
# sin separar jueves y sábados y ordenados por semanas
PREMIADOSPRIMI = 'PremiadosPrimi'  # Nombre de la db con todas las apuestas de Primitiva que coinciden
# con alguna premiada anteriormente
EUROMILLONES = 'Euromillones'  # Nombre de la db con todas las combinaciones históricas de Euromillones,
# identificados par martes y viernes
SELEURO = 'SelEuro'  # Nombre de la db con todas las apuestas de Euromillones considerando todos los números,
# sin separar martes y viernes y ordenados por semanas
SELEUROTOT = 'SelEuroTot'  # Nombre de la db con todas las apuestas de Euromillones
PREMIADOSEURO = 'PremiadosEuro'  # Nombre de la db con todas las apuestas de Euromillones que coinciden
# con alguna premiada anteriormente
DBDIR = r'/home/chema/PycharmProjects/loterias/'
DBFILE = r'loterias.db'
PICKLEDIR = r'/home/chema/PycharmProjects/loterias/pickleFiles/'
LOTOPICKERFILE = 'loterias.pkl' # contiene un diccionario con los tipos de sorte como clave y las listas de
# combinaciones como valor
EUROWEB = 'https://www.euromillones.com.es/resultados-anteriores.html'
# PRIMIWEB = 'https://www.loterias.com/la-primitiva/resultados/' + cur_year
PRIMIWEB = 'https://www.loteriasyapuestas.es/es/resultados/primitiva'  # NULO en 2025. Se extraen los resultados de
# otra forma
PRIMIDAYS = (46, 1, 4, 6)  # Días de primitiva. Domingo es día 0. Primitiva es lunes, jueves y sábado: 1, 4 y 6. El 46
# representa el total de sorteos de primitiva de jueves y sábado
EURODAYS = (25, 2, 5)  # Días de euromillones. Domingo es día 0. Euromilones es martes y viernes: 2 y 5. El 25
# representa el total de sorteos de euromillones de martes y viernes
PRIMINUMBERS = 6  # Cantidad de numeros que forman una apuesta de primitiva, sin contar complementario y reintegro
EURONUMBERS = 5  # Cantidad de numeros que forman una apuesta de euromillones, sin contar las estrellas
PRIMI_Q_BETS = 5  # Nº de apuestas de primitiva
EURO_Q_BETS = 5  # Nº de apuestas de euromillones
Q_NUM_MAS_FREQ = 10  # Cantidad de números seleccionados en la lista de más frecuentes
EVEN    = 'e'
ODD     = 'o'
LUNES       = 1
MARTES      = 2
MIERCOLES   = 3
JUEVES      = 4
VIERNES     = 5
SABADO      = 6
DOMINGO     = 7
PRIMAVERA   = 1
VERANO      = 2
OTONO       = 3
INVIERNO    = 4
ESTACIONES  = {1: 'PRIMAVERA',
               2: 'VERANO',
               3: 'OTOÑO',
               4: 'INVIERNO'}
