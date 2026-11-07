import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from b_local.hill_climbing import costo_orden

POBLACION = 30
GENERACIONES = 40
K_TORNEO = 3
P_MUTACION = 0.2
ELITE = 2


def seleccion_torneo(poblacion, costos, rng, k=K_TORNEO):
    aspirantes = rng.sample(range(len(poblacion)), k)
    ganador = min(aspirantes, key=lambda i: costos[i])
    return poblacion[ganador]


def cruza_orden(p1, p2, rng):
    n = len(p1)
    a, b = sorted(rng.sample(range(n), 2))
    hijo = [None] * n
    hijo[a:b + 1] = p1[a:b + 1]
    faltan = [g for g in p2 if g not in hijo[a:b + 1]]
    libres = [i for i in range(n) if hijo[i] is None]
    for i, g in zip(libres, faltan):
        hijo[i] = g
    return hijo


def mutar(individuo, rng, p=P_MUTACION):
    ind = list(individuo)
    if rng.random() < p:
        i, j = rng.sample(range(len(ind)), 2)
        ind[i], ind[j] = ind[j], ind[i]
    return ind


def algoritmo_genetico(esc, M, rng, poblacion=POBLACION, generaciones=GENERACIONES,
                        elite=ELITE, p_mutacion=P_MUTACION, k_torneo=K_TORNEO):
    t0 = time.perf_counter()
    pob = []
    for _ in range(poblacion):
        o = list(esc["entregas"])
        rng.shuffle(o)
        pob.append(o)
    costos = [costo_orden(esc, o, M) for o in pob]
    evaluaciones = poblacion

    mejor_c = min(costos)
    mejor = list(pob[costos.index(mejor_c)])
    historial = [mejor_c]
    ultima_mejora = 0

    for g in range(1, generaciones + 1):
        orden_idx = sorted(range(poblacion), key=lambda i: costos[i])
        nueva = [list(pob[i]) for i in orden_idx[:elite]]
        nuevos_costos = [costos[i] for i in orden_idx[:elite]]

        while len(nueva) < poblacion:
            p1 = seleccion_torneo(pob, costos, rng, k_torneo)
            p2 = seleccion_torneo(pob, costos, rng, k_torneo)
            hijo = mutar(cruza_orden(p1, p2, rng), rng, p_mutacion)
            nueva.append(hijo)
            nuevos_costos.append(costo_orden(esc, hijo, M))
            evaluaciones += 1

        pob, costos = nueva, nuevos_costos
        if min(costos) < mejor_c:
            mejor_c = min(costos)
            mejor = list(pob[costos.index(mejor_c)])
            ultima_mejora = g
        historial.append(mejor_c)

    diversidad = len({tuple(o) for o in pob})
    return {"orden": mejor, "costo": mejor_c, "evaluaciones": evaluaciones,
            "historial": historial, "generacion_ultima_mejora": ultima_mejora,
            "diversidad_final": diversidad, "poblacion": poblacion,
            "tiempo": time.perf_counter() - t0}