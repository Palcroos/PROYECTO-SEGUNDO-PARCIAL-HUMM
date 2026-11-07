import itertools
import random
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from escenario import cargar_escenario
from a_heuristica.busqueda import buscar

PENALIZACION = 10


def matriz_costos(esc, estrategia_competidor=None):
    puntos = [esc["inicio"]] + esc["entregas"] + [esc["destino"]]
    M = {}
    for a in puntos:
        for b in puntos:
            if a != b:
                M[(a, b)] = buscar(esc, a, b, "astar", estrategia_competidor)["costo"]
    return M


def costo_orden(esc, orden, M):
    puntos = [esc["inicio"]] + list(orden) + [esc["destino"]]
    total = sum(M[(puntos[i], puntos[i + 1])] for i in range(len(puntos) - 1))
    limite = esc.get("combustible_maximo")
    if limite is not None and total > limite:
        total += PENALIZACION * (total - limite)
    return total


def vecinos_swap(orden):
    n = len(orden)
    for i in range(n - 1):
        for j in range(i + 1, n):
            v = list(orden)
            v[i], v[j] = v[j], v[i]
            yield v


def hill_climbing(esc, M, orden_inicial):
    actual = list(orden_inicial)
    c_actual = costo_orden(esc, actual, M)
    inicial = c_actual
    iteraciones = 0
    evaluaciones = 1
    t0 = time.perf_counter()

    while True:
        mejor_v, mejor_c, iguales = None, c_actual, 0
        for v in vecinos_swap(actual):
            c = costo_orden(esc, v, M)
            evaluaciones += 1
            if c < mejor_c:
                mejor_v, mejor_c = v, c
            elif c == c_actual:
                iguales += 1
        if mejor_v is None:
            break
        actual, c_actual = mejor_v, mejor_c
        iteraciones += 1

    return {"orden": actual, "costo": c_actual, "costo_inicial": inicial,
            "iteraciones": iteraciones, "evaluaciones": evaluaciones,
            "vecinos_iguales_al_final": iguales,
            "tiempo": time.perf_counter() - t0}


def fuerza_bruta(esc, M):
    mejor, mejor_c = None, float("inf")
    for p in itertools.permutations(esc["entregas"]):
        c = costo_orden(esc, p, M)
        if c < mejor_c:
            mejor, mejor_c = list(p), c
    return mejor, mejor_c


def ordenes_iniciales(esc, k=10):
    rng = random.Random(esc["semilla"])
    resultado = []
    for _ in range(k):
        o = list(esc["entregas"])
        rng.shuffle(o)
        resultado.append(o)
    return resultado


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "config/escenario1.json"
    esc = cargar_escenario(ruta)
    M = matriz_costos(esc)
    opt, c_opt = fuerza_bruta(esc, M)
    print(f"{esc['nombre']}: {len(esc['entregas'])} entregas, óptimo real = {c_opt}\n")
    for i, o in enumerate(ordenes_iniciales(esc, 10), 1):
        r = hill_climbing(esc, M, o)
        marca = "ÓPTIMO" if r["costo"] == c_opt else "óptimo local"
        print(f"inicio {i:2}: {r['costo_inicial']:4} -> {r['costo']:4} iter={r['iteraciones']} eval={r['evaluaciones']} {marca}")