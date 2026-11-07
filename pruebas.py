import json
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import mapa
from a_heuristica import buscar, manhattan
from b_local import matriz_costos, costo_orden, hill_climbing, fuerza_bruta, ordenes_iniciales
from c_meta import cruza, mutar, recocido, genetico
from d_juegos import equilibrios_nash, dominante_a, mejor_respuesta_a
from e_minimax import minimax, alfa_beta

base = {"tamano": 6, "inicio": [0, 0], "destino": [5, 5], "entregas": [[1, 3], [3, 1], [4, 4]],
        "obstaculos": [[2, 2]], "costos_especiales": [], "semilla": 1}


def cargar_dict(d):
    archivo = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(d, archivo)
    archivo.close()
    try:
        return mapa.cargar_mapa(archivo.name)
    finally:
        os.remove(archivo.name)


def debe_fallar(d, texto):
    try:
        cargar_dict(d)
    except ValueError as error:
        assert texto in str(error), str(error)
        return
    raise AssertionError("debia fallar con: " + texto)


def prueba_escenarios_validos():
    for archivo in mapa.escenarios:
        m = mapa.cargar_mapa(archivo)
        assert len(m["entregas"]) >= 3


def prueba_inicio_sobre_obstaculo():
    d = dict(base)
    d["obstaculos"] = [[0, 0]]
    debe_fallar(d, "obstaculo")


def prueba_pocas_entregas():
    d = dict(base)
    d["entregas"] = [[1, 3], [3, 1]]
    debe_fallar(d, "al menos 3")


def prueba_fuera_del_mapa():
    d = dict(base)
    d["destino"] = [9, 9]
    debe_fallar(d, "fuera del mapa")


def prueba_sin_solucion():
    d = dict(base)
    d["obstaculos"] = [[0, 1], [1, 0], [1, 1]]
    debe_fallar(d, "sin solucion")


def prueba_archivo_inexistente():
    try:
        mapa.cargar_mapa("no_existe.json")
    except ValueError:
        return
    raise AssertionError("debia fallar")


def prueba_astar_no_pierde_con_greedy():
    for archivo in mapa.escenarios:
        m = mapa.cargar_mapa(archivo)
        g = buscar(m, m["inicio"], m["destino"], "greedy")["costo"]
        a = buscar(m, m["inicio"], m["destino"], "astar")["costo"]
        assert a <= g


def prueba_ruta_valida():
    for archivo in mapa.escenarios:
        m = mapa.cargar_mapa(archivo)
        r = buscar(m, m["inicio"], m["destino"], "astar")
        total = 0
        for p, q in zip(r["ruta"], r["ruta"][1:]):
            assert manhattan(p, q) == 1
            assert q not in m["obstaculos"]
            total += m["costos"][q]
        assert total == r["costo"]


def prueba_origen_igual_a_meta():
    m = cargar_dict(base)
    r = buscar(m, (0, 0), (0, 0), "astar")
    assert r["costo"] == 0


def prueba_meta_inalcanzable():
    m = cargar_dict(base)
    m["obstaculos"].add((4, 5))
    m["obstaculos"].add((5, 4))
    assert buscar(m, (0, 0), (5, 5), "astar")["resultado"] == "sin solucion"


def prueba_hill_climbing():
    m = mapa.cargar_mapa(mapa.escenarios[0])
    tabla = matriz_costos(m)
    optimo = fuerza_bruta(m, tabla)[1]
    for orden in ordenes_iniciales(m, 10):
        r = hill_climbing(m, tabla, orden)
        assert r["costo"] <= r["costo_inicial"]
        assert r["costo"] >= optimo
        assert sorted(r["orden"]) == sorted(m["entregas"])


def prueba_cruza_y_mutacion():
    rng = random.Random(3)
    for i in range(500):
        a = list(range(7))
        b = list(range(7))
        rng.shuffle(a)
        rng.shuffle(b)
        hijo = mutar(cruza(a, b, rng), rng, 1.0)
        assert sorted(hijo) == list(range(7))


def prueba_semillas():
    m = mapa.cargar_mapa(mapa.escenarios[1])
    tabla = matriz_costos(m)
    p = m["parametros"]
    r1 = recocido(m, tabla, random.Random(5), p["recocido"])
    r2 = recocido(m, tabla, random.Random(5), p["recocido"])
    assert r1["orden"] == r2["orden"]
    g1 = genetico(m, tabla, random.Random(5), p["genetico"])
    g2 = genetico(m, tabla, random.Random(5), p["genetico"])
    assert g1["orden"] == g2["orden"]


def prueba_nash():
    ua = [[-1, -3], [0, -2]]
    ub = [[-1, 0], [-3, -2]]
    assert equilibrios_nash(ua, ub) == [(1, 1)]
    assert dominante_a(ua) == [1]
    ua = [[1, -1], [-1, 1]]
    ub = [[-1, 1], [1, -1]]
    assert equilibrios_nash(ua, ub) == []
    assert mejor_respuesta_a([[5, 2], [3, 4]], 0) == [0]


def prueba_minimax_igual_alfabeta():
    for semilla in range(30):
        rng = random.Random(semilla)
        n = rng.randint(2, 7)
        ben_a = [rng.randint(-20, 60) for i in range(n)]
        ben_b = [rng.randint(-20, 60) for i in range(n)]
        todas = tuple(range(n))
        c1 = {"nodos": 0, "podas": 0}
        c2 = {"nodos": 0, "podas": 0}
        v1 = minimax(ben_a, ben_b, todas, True, 0, n, c1)
        v2 = alfa_beta(ben_a, ben_b, todas, True, 0, n, float("-inf"), float("inf"), c2)
        assert v1 == v2
        assert c2["nodos"] <= c1["nodos"]


def prueba_una_entrega():
    cuenta = {"nodos": 0, "podas": 0}
    assert minimax([10], [7], (0,), True, 0, 1, cuenta) == 10


pruebas = [prueba_escenarios_validos, prueba_inicio_sobre_obstaculo, prueba_pocas_entregas, prueba_fuera_del_mapa,
           prueba_sin_solucion, prueba_archivo_inexistente, prueba_astar_no_pierde_con_greedy, prueba_ruta_valida,
           prueba_origen_igual_a_meta, prueba_meta_inalcanzable, prueba_hill_climbing, prueba_cruza_y_mutacion,
           prueba_semillas, prueba_nash, prueba_minimax_igual_alfabeta, prueba_una_entrega]

fallos = 0
for prueba in pruebas:
    try:
        prueba()
        print("ok     ", prueba.__name__)
    except Exception as error:
        fallos += 1
        print("fallo  ", prueba.__name__, error)

print("\n" + str(len(pruebas) - fallos) + " de " + str(len(pruebas)) + " pruebas correctas")
sys.exit(1 if fallos else 0)
