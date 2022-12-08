#!/usr/bin/env python3
# -*- coding: cp1252 -*-

from loterias_tools.actualiza_loteriasdb import actualiza_loteriasdb, sql_savecomb2, sql_savecomb, lotoparams
from loterias_tools.estadisticas_new import analiza, imprimecombinacion

if __name__ == '__main__':
    print('... Actualizando bases de datos')
    actualiza_loteriasdb()
    # imprimecombinacion(analiza, lotoparams.PRIMITIVA)
    # imprimecombinacion(analiza, lotoparams.EUROMILLONES)
    primicomb = analiza(lotoparams.PRIMITIVA)
    eurocomb = analiza(lotoparams.EUROMILLONES)
    # sql_savecomb(primicomb)
    sql_savecomb2(primicomb)
    # sql_savecomb(eurocomb)
    sql_savecomb2(eurocomb)
