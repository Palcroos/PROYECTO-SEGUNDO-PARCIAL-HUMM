import os
import sys
import csv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from escenario import cargar_escenario
from parametros import cargar_parametros, ruta_proyecto
from d_juegos.juego import construir_juego, analizar_juego, mostrar_matriz

P = cargar_parametros()


def main():
    os.makedirs(ruta_proyecto("resultados/d_juegos"), exist_ok=True)
    estrategias = P["d_juegos"]["estrategias"]
    filas_matriz, filas_analisis = [], []

    for ruta in P["escenarios"]:
        esc = cargar_escenario(ruta_proyecto(ruta))
        juego = construir_juego(esc, estrategias)
        an = analizar_juego(juego)

        print(f"\n=== {esc['nombre']} (pagos de A, B; A = -costo, B = +costo)")
        mostrar_matriz(juego)
        print("mejores respuestas de A:", an["mejores_respuestas_A"])
        print("mejores respuestas de B:", an["mejores_respuestas_B"])
        print("dominantes A (estricta/débil):", an["dominante_estricta_A"], an["dominante_debil_A"])
        print("dominantes B (estricta/débil):", an["dominante_estricta_B"], an["dominante_debil_B"])
        print("equilibrios de Nash puros:", an["nash_puros"] or "ninguno")
        print(f"plan maximin de A: {an['plan_maximin_A']} (peor caso: costo {an['costo_peor_caso_maximin']})")

        for i, e in enumerate(estrategias):
            for j, f in enumerate(estrategias):
                filas_matriz.append([esc["nombre"], f"prioridad_{e}", f"congestiona_{f}",
                                     juego["costos"][i][j], juego["ua"][i][j], juego["ub"][i][j],
                                     str([esc["entregas"].index(x) + 1 for x in juego["planes"][i]])])
        
        filas_analisis.append([esc["nombre"], str(an["mejores_respuestas_A"]), str(an["mejores_respuestas_B"]),
                               str(an["dominante_estricta_A"]), str(an["dominante_debil_A"]),
                               str(an["dominante_estricta_B"]), str(an["dominante_debil_B"]),
                               str(an["nash_puros"]) if an["nash_puros"] else "ninguno",
                               an["plan_maximin_A"], an["costo_peor_caso_maximin"]])

    with open(ruta_proyecto("resultados/d_juegos/matriz_pagos.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "estrategia_A", "estrategia_B", "costo_A", "utilidad_A", "utilidad_B", "orden_del_plan"])
        w.writerows(filas_matriz)

    with open(ruta_proyecto("resultados/d_juegos/analisis.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "mejores_respuestas_A", "mejores_respuestas_B", "dominante_estricta_A",
                    "dominante_debil_A", "dominante_estricta_B", "dominante_debil_B", "nash_puros",
                    "plan_maximin_A", "costo_peor_caso"])
        w.writerows(filas_analisis)

    print("Resultados de teoría de juegos guardados en resultados/d_juegos/")


if __name__ == "__main__":
    main()