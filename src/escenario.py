
import json
from collections import deque

MOVIMIENTOS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def cargar_escenario(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            d = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"No existe el archivo de escenario: {ruta}")
    except json.JSONDecodeError as e:
        raise ValueError(f"El archivo {ruta} no es un JSON válido: {e}")

    for clave in ("tamano", "inicio", "destino", "entregas", "obstaculos"):
        if clave not in d:
            raise ValueError(f"Falta la clave '{clave}' en {ruta}")

    n = d["tamano"]
    esc = {
        "nombre": d.get("nombre", "escenario"),
        "n": n,
        "inicio": tuple(d["inicio"]),
        "destino": tuple(d["destino"]),
        "entregas": [tuple(e) for e in d["entregas"]],
        "obstaculos": {tuple(o) for o in d["obstaculos"]},
        "combustible_maximo": d.get("combustible_maximo"),
        "competidor": d.get("competidor", {}),
        "base_competidor": tuple(d["base_competidor"]) if "base_competidor" in d else tuple(d["destino"]),
        "ganancias_entregas": d.get("ganancias_entregas", [100] * len(d["entregas"])),
        "semilla": d.get("semilla", 0),
    }

    # costo base 1 en todas las casillas; luego los costos especiales
    costos = {(f, c): 1 for f in range(n) for c in range(n)}
    for f, c, costo in d.get("costos_especiales", []):
        if costo < 1:
            raise ValueError(f"Costo inválido en {(f, c)}: debe ser >= 1")
        costos[(f, c)] = costo
    esc["costos"] = costos

    _validar(esc)
    return esc


def _dentro(esc, p):
    return 0 <= p[0] < esc["n"] and 0 <= p[1] < esc["n"]


def _validar(esc):
    puntos = [("inicio", esc["inicio"]), ("destino", esc["destino"])]
    puntos += [(f"entrega {i + 1}", e) for i, e in enumerate(esc["entregas"])]

    if len(esc["entregas"]) < 3:
        raise ValueError("Debe haber al menos 3 puntos de entrega")
    if len(esc["ganancias_entregas"]) != len(esc["entregas"]):
        raise ValueError("ganancias_entregas debe tener un valor por cada entrega")
    puntos.append(("base del competidor", esc["base_competidor"]))

    for nombre, p in puntos:
        if not _dentro(esc, p):
            raise ValueError(f"{nombre} {p} está fuera del mapa")
        if p in esc["obstaculos"]:
            raise ValueError(f"{nombre} {p} está sobre un obstáculo")

    for o in esc["obstaculos"]:
        if not _dentro(esc, o):
            raise ValueError(f"Obstáculo {o} fuera del mapa")

    # escenario sin solución: todos los puntos clave deben ser alcanzables
    alcanzables = _alcanzables(esc, esc["inicio"])
    for nombre, p in puntos:
        if p not in alcanzables:
            raise ValueError(f"Escenario sin solución: {nombre} {p} no es alcanzable")


def _alcanzables(esc, origen):
    vistos = {origen}
    cola = deque([origen])
    while cola:
        actual = cola.popleft()
        for sig, _ in vecinos(esc, actual):
            if sig not in vistos:
                vistos.add(sig)
                cola.append(sig)
    return vistos


def costo_casilla(esc, p, estrategia_competidor=None):
    """Costo de entrar a la casilla p. Si el competidor eligió una estrategia,
    las casillas de su franja suman un recargo."""
    costo = esc["costos"][p]
    if estrategia_competidor:
        filas = esc["competidor"]["estrategias"][estrategia_competidor]
        if filas[0] <= p[0] <= filas[1]:
            costo += esc["competidor"]["recargo"]
    return costo


def vecinos(esc, p, estrategia_competidor=None):
    """Devuelve [(casilla_vecina, costo_de_moverse_a_ella), ...]"""
    resultado = []
    for df, dc in MOVIMIENTOS:
        sig = (p[0] + df, p[1] + dc)
        if _dentro(esc, sig) and sig not in esc["obstaculos"]:
            resultado.append((sig, costo_casilla(esc, sig, estrategia_competidor)))
    return resultado


def mostrar_mapa(esc, ruta=None):
    # Se desactiva la impresión en consola para mantener la salida limpia
    pass


if __name__ == "__main__":
    import sys
    ruta = sys.argv[1] if len(sys.argv) > 1 else "config/escenario1.json"
    esc = cargar_escenario(ruta)
    mostrar_mapa(esc)
    print("\nvecinos de inicio:", vecinos(esc, esc["inicio"]))
