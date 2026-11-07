#Héctor Uriel Martínez Medina PROYECTO SEGUNDO PARCIAL

Proyecto individual de Inteligencia Artificial. Modela la planificación de rutas para un vehículo de entregas en una red de 12x12 casillas con obstáculos, costos variables, límite de combustible y la interferencia de un competidor.

Requisitos

Python 3.10 o superior.

Librerías necesarias para la generación de resultados visuales:

pip install -r requirements.txt


Ejecución

Para ejecutar el flujo completo del proyecto (todos los módulos, la integración y las gráficas):

python main.py


También es posible ejecutar módulos específicos de forma individual:

python main.py a            # Búsqueda heurística (Greedy vs A*)
python main.py b            # Búsqueda local (Hill Climbing)
python main.py c            # Metaheurísticas (Recocido y Genético)
python main.py d            # Teoría de Juegos
python main.py e            # Búsqueda adversaria (Minimax y Alfa-Beta)
python main.py integracion  # Flujo integrado final
python main.py graficas     # Generación de gráficas en PNG


Pruebas

Para ejecutar la batería de pruebas unitarias:

python -m unittest discover -s tests -v


Configuración

Los parámetros del entorno y los mapas se gestionan desde la carpeta config:

config/escenario1.json, escenario2.json, escenario3.json: Definen las posiciones de inicio, destino, entregas, obstáculos, costos especiales y semillas de aleatoriedad.

config/parametros.json: Controla las ejecuciones por método y los parámetros de los algoritmos de búsqueda.

Resultados

Al finalizar la ejecución, los datos numéricos en formato .csv y las gráficas generadas en .png se almacenan automáticamente dentro de la carpeta resultados.
