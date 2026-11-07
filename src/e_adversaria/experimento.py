import os
import sys
import csv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from escenario import cargar_escenario
from parametros import cargar_parametros, ruta_proyecto
from e_adversaria.minimax import Juego, beneficios, mejor_jugada, reparto_optimo

P = cargar_parametros()


def main():
    os.makedirs(ruta_proyecto("resultados/e_adversaria"), exist_ok=True)
    prof_aprox = P["e_adversaria"]["profundidad_aproximada"]
    filas = []

    for ruta in P["escenarios"]:
        esc = cargar_escenario(ruta_proyecto(ruta))
        ben_a, ben_b = beneficios(esc)
        juego = Juego(ben_a, ben_b)
        variantes = [
            ("minimax completo", dict(algoritmo="minimax")),
            ("alfa-beta (sin ordenar)", dict(algoritmo="alfa_beta")),
            ("alfa-beta (ordenado)", dict(algoritmo="alfa_beta", ordenar=True)),
            (f"minimax prof={prof_aprox} aprox.", dict(algoritmo="minimax", profundidad=prof_aprox, aproximar=True)),
            (f"alfa-beta prof={prof_aprox} aprox.", dict(algoritmo="alfa_beta", profundidad=prof_aprox, aproximar=True)),
        ]
        valores_completos = []
        for nombre, kw in variantes:
            r = mejor_jugada(juego, **kw)
            if "aprox" not in nombre:
                valores_completos.append(r["valor"])
            filas.append([esc["nombre"], nombre, r["valor"], r["jugada"] + 1, r["nodos"],
                          r["podas"], round(r["tiempo"] * 1000, 3)])

        assert len(set(valores_completos)) == 1, "minimax y alfa-beta deben dar el mismo valor"
        reparto_optimo(juego)

    with open(ruta_proyecto("resultados/e_adversaria/comparacion.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "variante", "valor", "primera_jugada_MAX", "nodos_visitados", "podas", "tiempo_ms"])
        w.writerows(filas)
        
    print("Resultados de adversarial guardados en resultados/e_adversaria/comparacion.csv")


if __name__ == "__main__":
    main()