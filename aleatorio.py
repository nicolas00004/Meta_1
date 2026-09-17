import numpy as np


def generar_tour_aleatorio(n, semilla=None):
    """
    Genera una permutación aleatoria de n ciudades (índices 0..n-1).
    Representa un posible tour para el problema del TSP.

    Parámetros:
        n (int): número de ciudades.
        semilla (int, opcional): semilla para reproducibilidad.

    Retorna:
        np.ndarray: array de forma (n,) con la permutación de índices.
    """
    rng = np.random.default_rng(semilla)
    tour = rng.permutation(n)
    return tour


def generar_varios_tours(n, cantidad, semilla=None):
    """
    Genera varios tours aleatorios distintos.

    Parámetros:
        n (int): número de ciudades.
        cantidad (int): cuántos tours generar.
        semilla (int, opcional): semilla para reproducibilidad.

    Retorna:
        np.ndarray: array de forma (cantidad, n) con un tour por fila.
    """
    rng = np.random.default_rng(semilla)
    tours = np.array([rng.permutation(n) for _ in range(cantidad)])
    return tours


def calcular_distancia_tour(tour, m_distancias):
    """
    Calcula la distancia total de un tour (incluye el regreso al punto de partida).

    Parámetros:
        tour (array-like): secuencia de índices de ciudades.
        m_distancias (np.ndarray): matriz de distancias (n, n).

    Retorna:
        float: distancia total del recorrido cerrado.
    """
    tour = np.asarray(tour)
    origenes = tour
    destinos = np.roll(tour, -1)  # desplaza para conectar el último con el primero
    return m_distancias[origenes, destinos].sum()


if __name__ == "__main__":
    # --- Ejemplo de uso / prueba rápida ---
    n = 10
    semilla = 42

    # Coordenadas aleatorias de prueba (sustituir por las del fichero TSP real si hace falta)
    rng = np.random.default_rng(semilla)
    coordenadas = rng.uniform(0, 100, size=(n, 2)).astype(np.float32)

    diff = coordenadas[:, None, :] - coordenadas[None, :, :]
    m_distancias = np.sqrt((diff ** 2).sum(axis=2)).astype(np.float32)

    tour = generar_tour_aleatorio(n, semilla=semilla)
    distancia = calcular_distancia_tour(tour, m_distancias)

    print("Tour generado:", tour)
    print("Distancia total del tour:", distancia)

    # Generar varios tours de golpe, para comparar
    tours = generar_varios_tours(n, cantidad=5, semilla=semilla)
    print("\nVarios tours aleatorios:")
    for i, t in enumerate(tours):
        d = calcular_distancia_tour(t, m_distancias)
        print(f"  Tour {i}: {t} -> distancia = {d:.2f}")