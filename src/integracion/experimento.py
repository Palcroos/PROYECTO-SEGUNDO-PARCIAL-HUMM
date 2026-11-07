import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # permite importar escenario.py (carpeta src)

import csv
import json

from escenario import cargar_escenario
from parametros import cargar_parametros, ruta_proyecto
from integracion.plan import planificar


def main():
    P = cargar_parametros()
    carpeta = ruta_proyecto("resultados/integracion")
    os.makedirs(carpeta, exist_ok=True)
    filas = []
    for ruta in P["escenarios"]:
        esc = cargar_escenario(ruta_proyecto(ruta))
        print(f"\n######## {esc['nombre']} ########")
        r = planificar(esc, P)
        with open(os.path.join(carpeta, f"plan_final_{esc['nombre']}.json"), "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, ensure_ascii=False)
        pf, pb = r["plan_final"], r["plan_base"]
        filas.append([esc["nombre"], r["ruta_referencia_costo"], str(pb["orden"]),
                      pb["costo_sin_competidor"], pb["costo_bajo_congestion_esperada"],
                      r["juego"]["plan_maximin"], r["juego"]["congestion_esperada"],
                      str(r["reparto"]["nuestras"]), str(r["reparto"]["del_competidor"]),
                      str(pf["orden"]), pf["costo"], pf["combustible_maximo"],
                      "si" if pf["cumple_combustible"] else "no",
                      pf["ganancia_bruta"], pf["ganancia_neta"]])
    with open(os.path.join(carpeta, "resumen.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "costo_ruta_referencia", "orden_plan_base", "costo_plan_base",
                    "costo_plan_base_con_congestion", "plan_maximin", "congestion_esperada",
                    "entregas_nuestras", "entregas_competidor", "orden_plan_final", "costo_plan_final",
                    "combustible_maximo", "cumple_combustible", "ganancia_bruta", "ganancia_neta"])
        w.writerows(filas)
    print("\nGuardado en resultados/integracion/")


if __name__ == "__main__":
    main()
