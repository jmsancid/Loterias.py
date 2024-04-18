#!/usr/bin/env python3
# -*- coding: cp1252 -*-

from db_update import db_update, sql_savecomb
from estadisticas import analiza
import constants as cte

if __name__ == '__main__':
    print('... Actualizando bases de datos')
    db_update()
    primicomb = analiza(cte.PRIMITIVA)
    eurocomb = analiza(cte.EUROMILLONES)
    sql_savecomb(primicomb)
    sql_savecomb(eurocomb)
