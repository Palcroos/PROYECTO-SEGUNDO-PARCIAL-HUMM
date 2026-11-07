import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

def main():
    print("Prueba A: Módulo A (Búsqueda Heurística - Greedy vs A*)")
    importlib.import_module("a_heuristica.experimento").main()
    print()

    print("Prueba B: Módulo B (Búsqueda Local - Hill Climbing)")
    importlib.import_module("b_local.experimento").main()
    print()

    print("Prueba C: Módulo C (Metaheurísticas - Recocido y Genético)")
    importlib.import_module("c_meta.experimento").main()
    print()

    print("Prueba D: Módulo D (Teoría de Juegos)")
    importlib.import_module("d_juegos.experimento").main()
    print()

    print("Prueba E: Módulo E (Búsqueda Adversaria - Minimax y Alfa-Beta)")
    importlib.import_module("e_adversaria.experimento").main()
    print()

    print("Prueba Integración: Flujo Integrado Final")
    importlib.import_module("integracion.experimento").main()
    print()

    print("Prueba Gráficas: Generación de imágenes PNG")
    importlib.import_module("graficas").main()

if __name__ == "__main__":
    main()