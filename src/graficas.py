
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from parametros import cargar_parametros, ruta_proyecto

AZUL, NARANJA, VERDE, GRIS = "#2b6cb0", "#dd6b20", "#2f855a", "#718096"


def leer(rel):
    with open(ruta_proyecto(rel), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def guardar(fig, nombre):
    os.makedirs(ruta_proyecto("resultados/graficas"), exist_ok=True)
    fig.tight_layout()
    fig.savefig(ruta_proyecto(f"resultados/graficas/{nombre}"), dpi=130)
    plt.close(fig)
    print("  ", nombre)


def etiqueta(n):
    return n.replace("_", "\n")


def grafica_a():
    filas = leer("resultados/a_heuristica/a_heuristica.csv")
    escs = list(dict.fromkeys(r["escenario"] for r in filas))
    x = np.arange(len(escs)); w = 0.38
    fig, ejes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, col, titulo in [(ejes[0], "costo", "Costo de la ruta"), (ejes[1], "nodos_expandidos", "Nodos expandidos")]:
        for k, (alg, color, nom) in enumerate([("greedy", NARANJA, "Greedy f=h"), ("astar", AZUL, "A* f=g+h")]):
            vals = [float(next(r[col] for r in filas if r["escenario"] == e and r["algoritmo"] == alg)) for e in escs]
            barras = ax.bar(x + (k - 0.5) * w, vals, w, label=nom, color=color)
            ax.bar_label(barras, fmt="%d", fontsize=8)
        ax.set_xticks(x); ax.set_xticklabels([etiqueta(e) for e in escs], fontsize=8)
        ax.set_title(titulo); ax.legend(fontsize=8)
    fig.suptitle("Módulo A: Greedy vs A* (inicio → destino)")
    guardar(fig, "a_greedy_vs_astar.png")


def grafica_b():
    filas = leer("resultados/b_local/hill_climbing.csv")
    escs = list(dict.fromkeys(r["escenario"] for r in filas))
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, e in enumerate(escs):
        fs = [r for r in filas if r["escenario"] == e]
        ys = [float(r["costo_final"]) for r in fs]
        xs = i + np.linspace(-0.15, 0.15, len(ys))
        ax.scatter(xs, ys, color=AZUL, zorder=3, label="costo final de cada inicio" if i == 0 else None)
        opt = float(fs[0]["optimo_real"])
        ax.hlines(opt, i - 0.3, i + 0.3, color=VERDE, linewidth=2, label="óptimo real" if i == 0 else None)
    ax.set_xticks(range(len(escs))); ax.set_xticklabels([etiqueta(e) for e in escs], fontsize=8)
    ax.set_ylabel("costo total del orden de entregas")
    ax.set_title("Módulo B: Hill Climbing desde 10 soluciones iniciales"); ax.legend(fontsize=8)
    guardar(fig, "b_hill_climbing.png")


def grafica_c():
    filas = leer("resultados/c_meta/ejecuciones.csv")
    escs = list(dict.fromkeys(r["escenario"] for r in filas))
    fig, ejes = plt.subplots(1, len(escs), figsize=(11, 3.8), sharey=False)
    for ax, e in zip(ejes, escs):
        datos = [[float(r["costo"]) for r in filas if r["escenario"] == e and r["metodo"] == m]
                 for m in ("recocido", "genetico")]
        # jitter para que se vean las repeticiones (muchas ejecuciones dan el mismo costo)
        bp = ax.boxplot(datos, widths=0.5, patch_artist=True, showfliers=False)
        for parche, c in zip(bp["boxes"], (AZUL, NARANJA)):
            parche.set_facecolor(c); parche.set_alpha(0.35)
        rng = np.random.default_rng(1)
        for k, d in enumerate(datos, 1):
            ax.scatter(k + rng.uniform(-0.12, 0.12, len(d)), d, s=12, color=(AZUL, NARANJA)[k - 1], zorder=3)
        opt = float(next(r["optimo_real"] for r in filas if r["escenario"] == e))
        ax.axhline(opt, color=VERDE, linewidth=1.5, label="óptimo real")
        ax.set_xticks([1, 2]); ax.set_xticklabels(["recocido", "genético"])
        ax.set_title(etiqueta(e).replace("\n", " "), fontsize=9)
    ejes[0].set_ylabel("costo final (20 ejecuciones)"); ejes[0].legend(fontsize=8)
    fig.suptitle("Módulo C: recocido simulado vs algoritmo genético")
    guardar(fig, "c_comparacion.png")

    # convergencia (eje x = evaluaciones de la función objetivo)
    P = cargar_parametros()
    ip = P["c_meta"]["recocido"]["intentos_por_t"]
    pob, el = P["c_meta"]["genetico"]["poblacion"], P["c_meta"]["genetico"]["elite"]
    conv = leer("resultados/c_meta/convergencia.csv")
    fig, ejes = plt.subplots(1, len(escs), figsize=(11, 3.8))
    for ax, e in zip(ejes, escs):
        for m, color, nom in (("recocido", AZUL, "recocido"), ("genetico", NARANJA, "genético")):
            fs = [r for r in conv if r["escenario"] == e and r["metodo"] == m and r["ejecucion"] == "1"]
            xs = [1 + int(r["paso"]) * ip if m == "recocido" else pob + int(r["paso"]) * (pob - el) for r in fs]
            ax.step(xs, [float(r["mejor_costo"]) for r in fs], where="post", color=color, label=nom)
        ax.set_title(etiqueta(e).replace("\n", " "), fontsize=9); ax.set_xlabel("evaluaciones")
    ejes[0].set_ylabel("mejor costo encontrado"); ejes[0].legend(fontsize=8)
    fig.suptitle("Módulo C: convergencia (ejecución 1)")
    guardar(fig, "c_convergencia.png")


def grafica_d():
    filas = leer("resultados/d_juegos/matriz_pagos.csv")
    escs = list(dict.fromkeys(r["escenario"] for r in filas))
    fig, ejes = plt.subplots(1, len(escs), figsize=(12, 3.8))
    for ax, e in zip(ejes, escs):
        fs = [r for r in filas if r["escenario"] == e]
        filas_n = list(dict.fromkeys(r["estrategia_A"] for r in fs))
        cols_n = list(dict.fromkeys(r["estrategia_B"] for r in fs))
        M = np.array([[float(next(r["costo_A"] for r in fs if r["estrategia_A"] == a and r["estrategia_B"] == b))
                       for b in cols_n] for a in filas_n])
        ax.imshow(M, cmap="Oranges")
        ax.set_xticks(range(len(cols_n))); ax.set_xticklabels([c.replace("congestiona_", "cong.\n") for c in cols_n], fontsize=8)
        ax.set_yticks(range(len(filas_n))); ax.set_yticklabels([f.replace("prioridad_", "prior.\n") for f in filas_n], fontsize=8)
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=11,
                        color="white" if M[i, j] > (M.min() + M.max()) / 2 else "black")
        ax.set_title(etiqueta(e).replace("\n", " "), fontsize=9)
    fig.suptitle("Módulo D: costo para A (A minimiza, el competidor maximiza)")
    guardar(fig, "d_matriz_pagos.png")


def grafica_e():
    filas = leer("resultados/e_adversaria/comparacion.csv")
    escs = list(dict.fromkeys(r["escenario"] for r in filas))
    variantes = ["minimax completo", "alfa-beta (sin ordenar)", "alfa-beta (ordenado)"]
    x = np.arange(len(escs)); w = 0.26
    fig, ax = plt.subplots(figsize=(8.5, 4))
    for k, (v, c) in enumerate(zip(variantes, (GRIS, AZUL, VERDE))):
        vals = [float(next(r["nodos_visitados"] for r in filas if r["escenario"] == e and r["variante"] == v)) for e in escs]
        b = ax.bar(x + (k - 1) * w, vals, w, label=v, color=c)
        ax.bar_label(b, fmt="%d", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels([etiqueta(e) for e in escs], fontsize=8)
    ax.set_yscale("log"); ax.set_ylabel("nodos visitados (escala log)")
    ax.set_title("Módulo E: nodos visitados, mismo valor minimax en las tres variantes"); ax.legend(fontsize=8)
    guardar(fig, "e_nodos_visitados.png")


def main():
    print("Generando gráficas en resultados/graficas/")
    for f in (grafica_a, grafica_b, grafica_c, grafica_d, grafica_e):
        f()


if __name__ == "__main__":
    main()
