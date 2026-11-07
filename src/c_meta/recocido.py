import os
import sys
import math
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from b_local.hill_climbing import costo_orden

T_INICIAL = 30.0
ALFA = 0.95
T_MIN = 0.1
INTENTOS_POR_T = 10


def recocido_simulado(esc, M, rng, t_inicial=T_INICIAL, alfa=ALFA,
                      t_min=T_MIN, intentos_por_t=INTENTOS_POR_T):
    t0 = time.perf_counter()
    n = len(esc["entregas"])
    actual = list(esc["entregas"])
    rng.shuffle(actual)
    c_actual = costo_orden(esc, actual, M)
    mejor, c_mejor = list(actual), c_actual
    evaluaciones = 1
    aceptadas_peores = 0
    historial = [c_mejor]
    T = t_inicial

    while T > t_min:
        for _ in range(intentos_por_t):
            i, j = rng.sample(range(n), 2)
            vecino = list(actual)
            vecino[i], vecino[j] = vecino[j], vecino[i]
            c_vecino = costo_orden(esc, vecino, M)
            evaluaciones += 1
            delta = c_vecino - c_actual

            if delta <= 0:
                actual, c_actual = vecino, c_vecino
            elif rng.random() < math.exp(-delta / T):
                actual, c_actual = vecino, c_vecino
                aceptadas_peores += 1

            if c_actual < c_mejor:
                mejor, c_mejor = list(actual), c_actual
        historial.append(c_mejor)
        T *= alfa

    return {"orden": mejor, "costo": c_mejor, "evaluaciones": evaluaciones,
            "aceptadas_peores": aceptadas_peores, "historial": historial,
            "tiempo": time.perf_counter() - t0}