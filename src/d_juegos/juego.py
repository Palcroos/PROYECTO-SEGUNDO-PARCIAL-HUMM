import os
import sys
import itertools

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from b_local.hill_climbing import matriz_costos, costo_orden
from d_juegos.analisis import (mejores_respuestas_a, mejores_respuestas_b,
                               dominantes_a, dominantes_b,
                               equilibrios_nash_puros, nivel_seguridad_a)

ZONAS = ["norte", "centro", "sur"]


def zona_de(esc, punto):
    tercio = esc["n"] / 3
    return ZONAS[min(int(punto[0] // tercio), 2)]


def mejor_plan_con_prioridad(esc, M, zona):
    en_zona = {e for e in esc["entregas"] if zona_de(esc, e) == zona}
    mejor, mejor_c = None, float("inf")
    for p in itertools.permutations(esc["entregas"]):
        k = len(en_zona)
        if set(p[:k]) != en_zona:
            continue
        c = costo_orden(esc, p, M)
        if c < mejor_c:
            mejor, mejor_c = list(p), c
    return mejor


def construir_juego(esc, estrategias=None):
    estrategias = estrategias or ZONAS
    M0 = matriz_costos(esc)
    Ms = {e: matriz_costos(esc, e) for e in estrategias}

    planes = [mejor_plan_con_prioridad(esc, M0, z) for z in estrategias]
    costos = [[costo_orden(esc, plan, Ms[e]) for e in estrategias] for plan in planes]
    ua = [[-c for c in fila] for fila in costos]
    ub = [[c for c in fila] for fila in costos]
    return {"estrategias": list(estrategias), "planes": planes,
            "costos": costos, "ua": ua, "ub": ub}


def analizar_juego(juego):
    ua, ub, est = juego["ua"], juego["ub"], juego["estrategias"]
    n, m = len(ua), len(ua[0])
    nombres_a = [f"prioridad_{e}" for e in est]
    nombres_b = [f"congestiona_{e}" for e in est]

    br_a = {nombres_b[j]: [nombres_a[i] for i in mejores_respuestas_a(ua, j)] for j in range(m)}
    br_b = {nombres_a[i]: [nombres_b[j] for j in mejores_respuestas_b(ub, i)] for i in range(n)}
    est_a, deb_a = dominantes_a(ua)
    est_b, deb_b = dominantes_b(ub)
    nash = [(nombres_a[i], nombres_b[j]) for i, j in equilibrios_nash_puros(ua, ub)]
    i_seg, v_seg = nivel_seguridad_a(ua)

    return {"nombres_a": nombres_a, "nombres_b": nombres_b,
            "mejores_respuestas_A": br_a, "mejores_respuestas_B": br_b,
            "dominante_estricta_A": [nombres_a[i] for i in est_a],
            "dominante_debil_A": [nombres_a[i] for i in deb_a],
            "dominante_estricta_B": [nombres_b[j] for j in est_b],
            "dominante_debil_B": [nombres_b[j] for j in deb_b],
            "nash_puros": nash,
            "plan_maximin_A": nombres_a[i_seg], "costo_peor_caso_maximin": -v_seg}


def mostrar_matriz(juego):
    est = juego["estrategias"]
    print(f"{'A \\ B':14}" + "".join(f"{'cong. ' + e:>16}" for e in est))
    for i, e in enumerate(est):
        print(f"{'prior_' + e:14}" + "".join(
            f"{'(' + str(juego['ua'][i][j]) + ', ' + str(juego['ub'][i][j]) + ')':>16}"
            for j in range(len(est))))