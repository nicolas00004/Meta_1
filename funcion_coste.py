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
