import numpy as np
import random
from funcion_coste import calcular_coste_solucion

def algoritmo_greedy_aleatorizado(m_distancias, k=5, semilla=None):
    """
    Algoritmo Greedy Aleatorizado (GRA)
    """
    if semilla is not None:
        random.seed(semilla)

    n = m_distancias.shape[0]


    sumatorio_distancias = m_distancias.sum(axis=1)

    ciudades_ordenadas = np.argsort(sumatorio_distancias)

    k_inicial = min(k, n)
    idx_seleccionado = random.randint(0, k_inicial - 1)
    ciudad_inicial = int(ciudades_ordenadas[idx_seleccionado])

    solucion = [ciudad_inicial]
    visitadas = set(solucion)


    ciudad_actual = ciudad_inicial
    while len(solucion) < n:
        candidatas = [c for c in range(n) if c not in visitadas]

        candidatas.sort(key=lambda c: m_distancias[ciudad_actual, c])

        k_actual = min(k, len(candidatas))
        idx_elegido = random.randint(0, k_actual - 1)
        siguiente_ciudad = candidatas[idx_elegido]

        solucion.append(siguiente_ciudad)
        visitadas.add(siguiente_ciudad)
        ciudad_actual = siguiente_ciudad

    coste = calcular_coste_solucion(solucion, m_distancias)
    return solucion, coste


#TODO: Comentar la función.