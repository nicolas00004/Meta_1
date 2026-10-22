import numpy as np
import greedy
import random
import Funcion_evaluacion

def greedy_aleatorio(m_distancias,random,k):

    vector= []
    v_asignacion=[]
    for i in range(m_distancias.shape[0]):
        vector.append((i, sum(m_distancias[i])))
        vector.sort(key=lambda x: x[1])
    while len(v_asignacion) < m_distancias.shape[0]:
        if len(vector)<k:
            indice_aleatorio = int(random.randint(0, len(vector)-1))
            v_asignacion.append(vector[indice_aleatorio][0])
            vector.remove(vector[indice_aleatorio])
        else:
            indice_aleatorio = int(random.randint(0, k-1))
            v_asignacion.append(vector[indice_aleatorio][0])
            vector.remove(vector[indice_aleatorio])


    return v_asignacion


def ejecucion(m_distancias, k,random):
    vector_asignacion_greedy =greedy_aleatorio(m_distancias, random, k)
    distancia_total_greedy = Funcion_evaluacion.evaluar(m_distancias, vector_asignacion_greedy)
    return distancia_total_greedy