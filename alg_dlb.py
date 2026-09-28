# 21/9/2026

# Busqueda primero el mejor: DLB
# Implementar la logica. Partir del GRA.

# 28/9/2026
#TODO: Hacer el log (Info de la ejecicion; Algoritmo, datasets, parametros)

import numpy as np
import random
from funcion_coste import factorizacion_DLB, checkMove, applyMove
from alg_greedy_aleatorio import algoritmo_greedy_aleatorizado

def dlb(m_distancias, num_iteraciones=1000):
