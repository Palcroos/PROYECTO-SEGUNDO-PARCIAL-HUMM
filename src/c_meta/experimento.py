import os
import sys
import csv
import random
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from escenario import cargar_escenario
from parametros import cargar_parametros, ruta_proyecto
from b_local.hill_climbing import matriz_costos, fuerza_bruta
from c_meta.recocido import recocido_simulado
from c_meta.genetico import algoritmo_genetico

P = cargar_parametros()
ESCENARIOS = P["escenarios"]
EJECUCIONES = P["c_meta"]["ejecuciones"]
PARAMS = {"recocido": P["c_meta"]["recocido"], "genetico": P["c_meta"]["genetico"]}
METODOS = {"recocido": recocido_simulado, "genetico": algoritmo_genetico}


def main():
    os.makedirs(ruta_proyecto("resultados/c_meta"), exist_ok=True)
    filas, resumen, conv = [], [], []

    for ruta in ESCENARIOS:
        esc = cargar_escenario(ruta_proyecto(ruta))
        M = matriz_costos(esc)
        _, c_opt = fuerza_bruta(esc, M)

        for nombre, func in METODOS.items():
            costos, evals, tiempos, aciertos = [], [], [], 0
            for k in range(EJECUCIONES):
                semilla = esc["semilla"] * 1000 + k
                rng = random.Random(semilla)
                r = func(esc, M, rng, **PARAMS[nombre])
                es_opt = r["costo"] == c_opt
                aciertos += es_opt
                costos.append(r["costo"])
                evals.append(r["evaluaciones"])
                tiempos.append(r["tiempo"])
                
                extra = (f"aceptadas_peores={r['aceptadas_peores']}" if nombre == "recocido"
                         else f"ultima_mejora_gen={r['generacion_ultima_mejora']};diversidad_final={r['diversidad_final']}/{r['poblacion']}")
                
                filas.append([esc["nombre"], nombre, k + 1, semilla, r["costo"], c_opt,
                              "si" if es_opt else "no", r["evaluaciones"],
                              round(r["tiempo"] * 1000, 3), extra,
                              str([esc["entregas"].index(e) + 1 for e in r["orden"]])])
                
                if k < 3:
                    for paso, v in enumerate(r["historial"]):
                        conv.append([esc["nombre"], nombre, k + 1, paso, v])

            resumen.append([esc["nombre"], nombre, c_opt, min(costos),
                            round(statistics.mean(costos), 2), round(statistics.pstdev(costos), 2),
                            max(costos), round(statistics.mean(evals), 1),
                            round(statistics.mean(tiempos) * 1000, 3), aciertos, EJECUCIONES])

    def guardar(nombre, encabezado, datos):
        with open(ruta_proyecto(f"resultados/c_meta/{nombre}"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(encabezado)
            w.writerows(datos)

    guardar("ejecuciones.csv", ["escenario", "metodo", "ejecucion", "semilla", "costo",
            "optimo_real", "llego_al_optimo", "evaluaciones", "tiempo_ms", "extra",
            "orden_entregas"], filas)
    guardar("resumen.csv", ["escenario", "metodo", "optimo_real", "mejor", "promedio",
            "desv_estandar", "peor", "evaluaciones_prom", "tiempo_ms_prom",
            "veces_optimo", "ejecuciones"], resumen)
    guardar("convergencia.csv", ["escenario", "metodo", "ejecucion", "paso", "mejor_costo"], conv)
    print("Resultados de metaheurísticas guardados en resultados/c_meta/")


if __name__ == "__main__":
    main()