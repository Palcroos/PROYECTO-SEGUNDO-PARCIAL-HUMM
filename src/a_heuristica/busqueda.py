import heapq
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from escenario import cargar_escenario, mostrar_mapa, vecinos


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def buscar(esc, inicio, meta, algoritmo="astar", estrategia_competidor=None):
    if algoritmo not in ("astar", "greedy"):
        raise ValueError("algoritmo debe ser 'astar' o 'greedy'")

    t0 = time.perf_counter()
    contador = 0
    frontera = [(manhattan(inicio, meta), contador, inicio)]
    g = {inicio: 0}
    padre = {inicio: None}
    explorados = set()
    expandidos = 0

    while frontera:
        _, _, actual = heapq.heappop(frontera)
        if actual in explorados:
            continue
        explorados.add(actual)
        expandidos += 1

        if actual == meta:
            ruta = []
            n = actual
            while n is not None:
                ruta.append(n)
                n = padre[n]
            ruta.reverse()
            return {"resultado": "exito", "ruta": ruta, "costo": g[actual],
                    "expandidos": expandidos,
                    "tiempo": time.perf_counter() - t0}

        for sig, costo_mov in vecinos(esc, actual, estrategia_competidor):
            nuevo_g = g[actual] + costo_mov
            if sig in explorados:
                continue
            if algoritmo == "astar":
                if sig not in g or nuevo_g < g[sig]:
                    g[sig] = nuevo_g
                    padre[sig] = actual
                    contador += 1
                    heapq.heappush(frontera, (nuevo_g + manhattan(sig, meta), contador, sig))
            else:
                if sig not in g:
                    g[sig] = nuevo_g
                    padre[sig] = actual
                    contador += 1
                    heapq.heappush(frontera, (manhattan(sig, meta), contador, sig))

    return {"resultado": "sin solucion", "ruta": [], "costo": None,
            "expandidos": expandidos, "tiempo": time.perf_counter() - t0}


if __name__ == "__main__":
    ruta_json = sys.argv[1] if len(sys.argv) > 1 else "config/escenario1.json"
    esc = cargar_escenario(ruta_json)
    inicio, meta = esc["inicio"], esc["destino"]

    for alg in ("greedy", "astar"):
        r = buscar(esc, inicio, meta, alg)
        print(alg, r)