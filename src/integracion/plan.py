import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # permite importar escenario.py (carpeta src)

import itertools
import random

from escenario import cargar_escenario, mostrar_mapa
from parametros import cargar_parametros, ruta_proyecto
from a_heuristica.busqueda import buscar
from b_local.hill_climbing import matriz_costos, costo_orden
from c_meta.recocido import recocido_simulado
from d_juegos.juego import construir_juego, analizar_juego, zona_de
from e_adversaria.minimax import Juego, beneficios, reparto_optimo


def planificar(esc, params, verbose=True):
    log = print if verbose else (lambda *a, **k: None)
    idx = {e: i + 1 for i, e in enumerate(esc["entregas"])}
    num = lambda orden: [idx[e] for e in orden]
    res = {"escenario": esc["nombre"]}

    # 2. Módulo A
    ref = buscar(esc, esc["inicio"], esc["destino"], "astar")
    res["ruta_referencia_costo"] = ref["costo"]
    log(f"[A] ruta de referencia inicio->destino con A*: costo {ref['costo']}, "
        f"{ref['expandidos']} nodos expandidos")

    # 3. Módulos B/C: plan base sin competidor
    M0 = matriz_costos(esc)
    rec = recocido_simulado(esc, M0, random.Random(esc["semilla"]), **params["c_meta"]["recocido"])
    res["plan_base"] = {"orden": num(rec["orden"]), "costo_sin_competidor": rec["costo"]}
    log(f"[C] plan base (recocido, sin competidor): orden {num(rec['orden'])}, costo {rec['costo']}")

    # 4. Módulo D: juego contra el competidor
    juego = construir_juego(esc, params["d_juegos"]["estrategias"])
    an = analizar_juego(juego)
    zona_prio = an["plan_maximin_A"].replace("prioridad_", "")
    respuestas = an["mejores_respuestas_B"][an["plan_maximin_A"]]
    congestion = respuestas[0].replace("congestiona_", "")
    res["juego"] = {"plan_maximin": an["plan_maximin_A"], "congestion_esperada": congestion,
                    "nash_puros": [list(x) for x in an["nash_puros"]]}
    log(f"[D] plan maximin: {an['plan_maximin_A']}; el competidor responde congestionando "
        f"'{congestion}'; Nash puros: {an['nash_puros'] or 'ninguno'}")

    M_exp = matriz_costos(esc, congestion)
    res["plan_base"]["costo_bajo_congestion_esperada"] = costo_orden(esc, rec["orden"], M_exp)

    # 5. Módulo E: reparto de entregas por turnos
    ben_a, ben_b = beneficios(esc)
    mias, suyas = reparto_optimo(Juego(ben_a, ben_b))
    asignadas = [esc["entregas"][d] for d in mias]
    res["reparto"] = {"nuestras": sorted(num(asignadas)),
                      "del_competidor": sorted(num([esc["entregas"][d] for d in suyas]))}
    log(f"[E] reparto óptimo por minimax: nuestras {res['reparto']['nuestras']}, "
        f"del competidor {res['reparto']['del_competidor']}")

    # 6. Plan final
    en_zona = {e for e in asignadas if zona_de(esc, e) == zona_prio}
    mejor, mejor_c = None, float("inf")
    for p in itertools.permutations(asignadas):
        if set(p[:len(en_zona)]) != en_zona:
            continue
        c = costo_orden(esc, p, M_exp)
        if c < mejor_c:
            mejor, mejor_c = list(p), c
    puntos = [esc["inicio"]] + mejor + [esc["destino"]]
    ruta = [puntos[0]]
    for a, b in zip(puntos, puntos[1:]):
        ruta += buscar(esc, a, b, "astar", congestion)["ruta"][1:]
    ganancia = sum(esc["ganancias_entregas"][idx[e] - 1] for e in mejor)
    limite = esc.get("combustible_maximo")
    res["plan_final"] = {"orden": num(mejor), "costo": mejor_c, "casillas_recorridas": len(ruta) - 1,
                         "combustible_maximo": limite,
                         "cumple_combustible": (limite is None or mejor_c <= limite),
                         "ganancia_bruta": ganancia, "ganancia_neta": ganancia - mejor_c,
                         "ruta": [list(p) for p in ruta]}
    log(f"[Final] visita las entregas {num(mejor)} (zona prioritaria: {zona_prio}); "
        f"costo {mejor_c} bajo congestión '{congestion}', combustible "
        f"{mejor_c}/{limite} -> {'OK' if res['plan_final']['cumple_combustible'] else 'EXCEDE'}")
    if verbose:
        mostrar_mapa(esc, ruta)
    return res


if __name__ == "__main__":
    P = cargar_parametros()
    ruta_esc = sys.argv[1] if len(sys.argv) > 1 else P["escenarios"][0]
    planificar(cargar_escenario(ruta_proyecto(ruta_esc)), P)
