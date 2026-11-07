import csv
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from escenario import cargar_escenario
from parametros import cargar_parametros, ruta_proyecto
from b_local.hill_climbing import matriz_costos, fuerza_bruta, ordenes_iniciales, hill_climbing

P = cargar_parametros()
ESCENARIOS = P["escenarios"]
EJECUCIONES = P["b_local"]["ejecuciones"]


def main():
    os.makedirs(ruta_proyecto("resultados/b_local"), exist_ok=True)
    filas, resumen = [], []

    for ruta in ESCENARIOS:
        esc = cargar_escenario(ruta_proyecto(ruta))
        M = matriz_costos(esc)
        _, c_opt = fuerza_bruta(esc, M)
        costos, aciertos = [], 0

        for i, o in enumerate(ordenes_iniciales(esc, EJECUCIONES), 1):
            r = hill_climbing(esc, M, o)
            es_opt = r["costo"] == c_opt
            aciertos += es_opt
            costos.append(r["costo"])
            filas.append([esc["nombre"], i, r["costo_inicial"], r["costo"], c_opt,
                          "si" if es_opt else "no", r["iteraciones"], r["evaluaciones"],
                          r["vecinos_iguales_al_final"], round(r["tiempo"] * 1000, 3),
                          str([esc["entregas"].index(e) + 1 for e in r["orden"]])])

        resumen.append([esc["nombre"], c_opt, min(costos), round(statistics.mean(costos), 2),
                        round(statistics.pstdev(costos), 2), max(costos), aciertos, EJECUCIONES])

    with open(ruta_proyecto("resultados/b_local/hill_climbing.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "inicio_n", "costo_inicial", "costo_final", "optimo_real",
                    "llego_al_optimo", "iteraciones", "evaluaciones",
                    "vecinos_iguales_al_final", "tiempo_ms", "orden_final_entregas"])
        w.writerows(filas)

    with open(ruta_proyecto("resultados/b_local/resumen.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "optimo_real", "mejor", "promedio", "desv_estandar",
                    "peor", "veces_optimo", "ejecuciones"])
        w.writerows(resumen)

    print("Resultados de búsqueda local guardados correctamente.")


if __name__ == "__main__":
    main()