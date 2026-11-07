import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from a_heuristica.busqueda import buscar

INF = float("inf")


def beneficios(esc):
    ben_a, ben_b = [], []
    for k, e in enumerate(esc["entregas"]):
        ga = esc["ganancias_entregas"][k]
        ca = buscar(esc, esc["inicio"], e, "astar")["costo"]
        cb = buscar(esc, esc["base_competidor"], e, "astar")["costo"]
        ben_a.append(ga - ca)
        ben_b.append(ga - cb)
    return ben_a, ben_b


class Juego:
    def __init__(self, ben_a, ben_b):
        self.ben_a, self.ben_b = ben_a, ben_b
        self.n = len(ben_a)

    def estado_inicial(self):
        return (tuple(range(self.n)), True, 0, 0)

    def es_terminal(self, s):
        return len(s[0]) == 0

    def acciones(self, s):
        return list(s[0])

    def aplicar(self, s, d):
        disp, turno_max, pa, pb = s
        nuevos = tuple(x for x in disp if x != d)
        if turno_max:
            return (nuevos, False, pa + self.ben_a[d], pb)
        return (nuevos, True, pa, pb + self.ben_b[d])

    def utilidad(self, s):
        return s[2] - s[3]

    def evaluacion_aproximada(self, s):
        disp, turno_max, pa, pb = s
        restantes = sorted(disp, key=lambda d: self.ben_a[d] + self.ben_b[d], reverse=True)
        for d in restantes:
            if turno_max:
                pa += self.ben_a[d]
            else:
                pb += self.ben_b[d]
            turno_max = not turno_max
        return pa - pb


def minimax(juego, estado, profundidad, es_max, contador, aproximar=False):
    contador["nodos"] += 1
    if juego.es_terminal(estado):
        return juego.utilidad(estado)
    if profundidad == 0:
        return juego.evaluacion_aproximada(estado) if aproximar else juego.utilidad(estado)

    if es_max:
        mejor = -INF
        for d in juego.acciones(estado):
            mejor = max(mejor, minimax(juego, juego.aplicar(estado, d), profundidad - 1,
                                       False, contador, aproximar))
        return mejor
    mejor = INF
    for d in juego.acciones(estado):
        mejor = min(mejor, minimax(juego, juego.aplicar(estado, d), profundidad - 1,
                                   True, contador, aproximar))
    return mejor


def alfa_beta(juego, estado, profundidad, alfa, beta, es_max, contador,
              aproximar=False, ordenar=False):
    contador["nodos"] += 1
    if juego.es_terminal(estado):
        return juego.utilidad(estado)
    if profundidad == 0:
        return juego.evaluacion_aproximada(estado) if aproximar else juego.utilidad(estado)

    acciones = juego.acciones(estado)
    if ordenar:
        if es_max:
            acciones.sort(key=lambda d: juego.ben_a[d], reverse=True)
        else:
            acciones.sort(key=lambda d: juego.ben_b[d], reverse=True)

    if es_max:
        valor = -INF
        for d in acciones:
            valor = max(valor, alfa_beta(juego, juego.aplicar(estado, d), profundidad - 1,
                                         alfa, beta, False, contador, aproximar, ordenar))
            alfa = max(alfa, valor)
            if beta <= alfa:
                contador["podas"] += 1
                break
        return valor
    valor = INF
    for d in acciones:
        valor = min(valor, alfa_beta(juego, juego.aplicar(estado, d), profundidad - 1,
                                   alfa, beta, True, contador, aproximar, ordenar))
        beta = min(beta, valor)
        if beta <= alfa:
            contador["podas"] += 1
            break
    return valor


def mejor_jugada(juego, algoritmo="alfa_beta", profundidad=None, aproximar=False, ordenar=False):
    profundidad = juego.n if profundidad is None else profundidad
    contador = {"nodos": 1, "podas": 0}
    t0 = time.perf_counter()
    inicio = juego.estado_inicial()
    mejor_d, mejor_v = None, -INF
    alfa = -INF
    for d in juego.acciones(inicio):
        hijo = juego.aplicar(inicio, d)
        if algoritmo == "minimax":
            v = minimax(juego, hijo, profundidad - 1, False, contador, aproximar)
        else:
            v = alfa_beta(juego, hijo, profundidad - 1, alfa, INF, False, contador,
                          aproximar, ordenar)
            alfa = max(alfa, v)
        if v > mejor_v:
            mejor_d, mejor_v = d, v
    return {"jugada": mejor_d, "valor": mejor_v, "nodos": contador["nodos"],
            "podas": contador["podas"], "tiempo": time.perf_counter() - t0}


def reparto_optimo(juego):
    estado = juego.estado_inicial()
    a, b = [], []
    while not juego.es_terminal(estado):
        es_max = estado[1]
        mejor_d, mejor_v = None, (-INF if es_max else INF)
        for d in juego.acciones(estado):
            c = {"nodos": 0, "podas": 0}
            v = alfa_beta(juego, juego.aplicar(estado, d), len(estado[0]) - 1, -INF, INF,
                          not es_max, c)
            if (es_max and v > mejor_v) or ((not es_max) and v < mejor_v):
                mejor_d, mejor_v = d, v
        (a if es_max else b).append(mejor_d)
        estado = juego.aplicar(estado, mejor_d)
    return a, b