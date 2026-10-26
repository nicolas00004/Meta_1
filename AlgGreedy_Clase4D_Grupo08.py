import numpy as np
import Funcion_evaluacion



def greedy(m_distancias):

    vector= []
    vector_asignacion = []
    for i in range(m_distancias.shape[0]):
        vector.append((i,float(m_distancias[i].sum(dtype=np.float64))))

    vector.sort(key=lambda x: x[1])
    for i in range(len(vector)):
        vector_asignacion.append(vector[i][0])


    return vector_asignacion

def ejecucion(m_distancias, configuracion):
    vector = greedy(m_distancias)
    distancia_total = Funcion_evaluacion.evaluar(m_distancias, vector)
    return distancia_total
