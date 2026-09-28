from operator import truediv


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

def factorizacion(m_distancias, vector_asignaciones, posi, posj, m_valor_pasado):
    if posi == posj:
        return False

    n = len(vector_asignaciones)

    # Predecesores y sucesores considerando el recorrido circular (módulo n)
    prev_i, next_i = (posi - 1) % n, (posi + 1) % n
    prev_j, next_j = (posj - 1) % n, (posj + 1) % n

    node_i = vector_asignaciones[posi]
    node_j = vector_asignaciones[posj]

    # Caso 1: posi y posj son adyacentes (posj va inmediatamente después de posi)
    if next_i == posj:
        peso_a_quitar = (
            m_distancias[vector_asignaciones[prev_i]][node_i] +
            m_distancias[node_i][node_j] +
            m_distancias[node_j][vector_asignaciones[next_j]]
        )
        peso_a_anadir = (
            m_distancias[vector_asignaciones[prev_i]][node_j] +
            m_distancias[node_j][node_i] +
            m_distancias[node_i][vector_asignaciones[next_j]]
        )

    # Caso 2: posj y posi son adyacentes (posi va inmediatamente después de posj)
    elif next_j == posi:
        peso_a_quitar = (
            m_distancias[vector_asignaciones[prev_j]][node_j] +
            m_distancias[node_j][node_i] +
            m_distancias[node_i][vector_asignaciones[next_i]]
        )
        peso_a_anadir = (
            m_distancias[vector_asignaciones[prev_j]][node_i] +
            m_distancias[node_i][node_j] +
            m_distancias[node_j][vector_asignaciones[next_i]]
        )

    # Caso 3: No son adyacentes
    else:
        peso_a_quitar = (
            m_distancias[vector_asignaciones[prev_i]][node_i] +
            m_distancias[node_i][vector_asignaciones[next_i]] +
            m_distancias[vector_asignaciones[prev_j]][node_j] +
            m_distancias[node_j][vector_asignaciones[next_j]]
        )
        peso_a_anadir = (
            m_distancias[vector_asignaciones[prev_i]][node_j] +
            m_distancias[node_j][vector_asignaciones[next_i]] +
            m_distancias[vector_asignaciones[prev_j]][node_i] +
            m_distancias[node_i][vector_asignaciones[next_j]]
        )

    m_valor_actual = m_valor_pasado - peso_a_quitar + peso_a_anadir

    return m_valor_actual < m_valor_pasado


def check_move(matriz_distancias,vector_asignaciones,posi,posj,peso_actual):
    return factorizacion(matriz_distancias,vector_asignaciones,posi,posj,peso_actual)

def apply_move(vector_asignacion, posi,posj):
    valor_i=vector_asignacion[posi]
    vector_asignacion[posi]=vector_asignacion[posj]
    vector_asignacion[posj]=valor_i

