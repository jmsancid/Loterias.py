import random
from math import fsum
MAX_RANDOMIZACIONES = 5

premiada = (1900, 2700, 2800, 3000, 31, 36)

c1 = (1, 15, 23, 29, 34, 49)
c2 = (3, 14, 22, 33, 41, 48)
c3 = (2, 10, 17, 31, 38, 46)
c4 = (4, 9, 20, 35, 36, 47)
c5 = (7, 12, 18, 26, 39, 45)
aux = []
numsel = list(c1 + c2 + c3 + c4 + c5)

def randomiza(comb_siblinged):
    miscombinaciones = comb_siblinged.copy()
    combinaciones = []
    combinacion = []
    id_combinacion = 0
    while True:
        if len(miscombinaciones) == 0:
            break
        idx = random.randint(0, len(miscombinaciones)-1)
        num = miscombinaciones.pop(idx)
        # print(f"número a añadir:\t{num}\nQuedan {len(numsel)} números")
        combinacion.append(num)
        if len(combinacion) == 6:
            combinaciones.append(sorted(combinacion))
            id_combinacion += 1
            # print(f"Combinacion {id_combinacion}: {sorted(combinacion)}")
            combinacion = []
    return combinaciones
# print(resultado)

def comprueba_resultado(comb_ganadora, candidata):
    aciertos = fsum(list(map(lambda x: x in comb_ganadora, candidata)))
    return int(aciertos)


hay_premio = False
randomizaciones = 0
while (not hay_premio):
    print("Dentro del while")
    resultado = randomiza(numsel)
    randomizaciones += 1
    for idx, combinacion in enumerate(resultado):
        aciertos = comprueba_resultado(premiada, combinacion)
        print(f"Combinación {idx + 1}: {combinacion}:\t{aciertos} aciertos")
        if aciertos >= 3:
            hay_premio = True
    if randomizaciones == MAX_RANDOMIZACIONES:
        break

msg1 = f"\nHan hecho falta {randomizaciones} randomizaciones"
msg2 = f"{MAX_RANDOMIZACIONES} randomizaciones sin premio"
msg = msg1 if hay_premio else msg2
print(msg)

