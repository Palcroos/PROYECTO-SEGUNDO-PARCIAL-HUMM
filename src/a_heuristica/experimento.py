import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from escenario import cargar_escenario
from parametros import cargar_parametros, ruta_proyecto
from a_heuristica.busqueda import buscar

ESCENARIOS = cargar_parametros()["escenarios"]
SALIDA = ruta_proyecto("resultados/a_heuristica/a_heuristica.csv")


def main():
    os.makedirs(ruta_proyecto("resultados/a_heuristica"), exist_ok=True)
    filas = []

    for ruta_json in ESCENARIOS:
        esc = cargar_escenario(ruta_proyecto(ruta_json))
        for alg in ("greedy", "astar"):
            r = buscar(esc, esc["inicio"], esc["destino"], alg)
            ms = r["tiempo"] * 1000
            pasos = len(r["ruta"]) - 1 if r["ruta"] else ""
            filas.append([esc["nombre"], alg, r["resultado"], r["costo"], pasos,
                          r["expandidos"], round(ms, 4), str(r["ruta"])])

    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "algoritmo", "resultado", "costo", "pasos",
                    "nodos_expandidos", "tiempo_ms", "ruta"])
        w.writerows(filas)
    print("Resultados guardados en:", SALIDA)


if __name__ == "__main__":
    main()