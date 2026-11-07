
import json
import os

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def ruta_proyecto(relativa):
    return os.path.join(RAIZ, relativa)


def cargar_parametros(ruta="config/parametros.json"):
    with open(ruta_proyecto(ruta), encoding="utf-8") as f:
        return json.load(f)
