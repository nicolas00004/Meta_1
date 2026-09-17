import numpy as np




def greedy(m_distancias):

    vector= []
    vector_asignacion = []
    for i in range(m_distancias.shape[0]):
        vector.append((i,sum(m_distancias[i])))

    vector.sort(key=lambda x: x[1])
    for i in range(len(vector)):
        vector_asignacion.append(vector[i][0])


    return vector_asignacion

