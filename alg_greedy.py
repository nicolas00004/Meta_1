import numpy as np
from funcion_coste import calcular_coste_solucion

def algoritmo_greedy(m_distancias):
    """
    Algoritmo Greedy Determinista (GRE)
    """
    n = m_distancias.shape[0]


    sumatorio_distancias = m_distancias.sum(axis=1)


    ciudad_inicial = int(np.argmin(sumatorio_distancias))

    solucion = [ciudad_inicial]
    visitadas = set(solucion)


    ciudad_actual = ciudad_inicial
    while len(solucion) < n:
        candidatas = [c for c in range(n) if c not in visitadas]


        siguiente_ciudad = min(candidatas, key=lambda c: m_distancias[ciudad_actual, c])

        solucion.append(siguiente_ciudad)
        visitadas.add(siguiente_ciudad)
        ciudad_actual = siguiente_ciudad

    coste = calcular_coste_solucion(solucion, m_distancias)
    return solucion, coste


#TODO: Comentar la función.