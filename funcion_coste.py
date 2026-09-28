def calcular_coste_solucion(solucion, m_distancias):
    """
    Calcula la distancia total del recorrido cerrando el ciclo.
    """
    coste = 0.0
    num_ciudades = len(solucion)
    for i in range(num_ciudades):
        origen = solucion[i]
        destino = solucion[(i + 1) % num_ciudades]
        coste += m_distancias[origen, destino]
    return coste




#TODO: Funcion factorizacion para el DLB
# implementar el check y el apply

def factorizacion_DLB(solucion, m_distancias):
    """
    Factoriza la solución para el algoritmo DLB.
    """
    # Implementar la lógica de factorización aquí
    pass

def checkMove(solucion, m_distancias, i, j):
    """
    Verifica si el movimiento de intercambio entre las posiciones i y j es beneficioso.
    """
    # Implementar la lógica de verificación aquí
    pass

def applyMove(solucion, i, j):
    """
    Aplica el movimiento de intercambio entre las posiciones i y j.
    """
    # Implementar la lógica de aplicación aquí
    pass