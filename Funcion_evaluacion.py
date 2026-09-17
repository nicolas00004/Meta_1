


def evaluar(matriz_distancias,vector_asignaciones):
    """
    Evalúa la calidad de una solución para el problema del viajante de comercio (TSP)
    dado un vector de asignaciones y una matriz de distancias.

    Parámetros:
    - matriz_distancias: Una matriz cuadrada donde el elemento (i, j) representa la distancia
      entre el nodo i y el nodo j.
    - vector_asignaciones: Un vector que representa el orden en que se visitan los nodos.

    Retorna:
    - distancia_total: La distancia total recorrida según el vector de asignaciones.
    """

    distancia_total = 0.0
    n = len(vector_asignaciones)

    for i in range(n):
        origen = vector_asignaciones[i]
        destino = vector_asignaciones[(i + 1) % n]
        distancia_total += matriz_distancias[origen][destino]

    return distancia_total