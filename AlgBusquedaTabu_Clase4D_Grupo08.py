import numpy as np

import Funcion_evaluacion as evaluacion
import AlgGreedyAleatorio_Clase4D_Grupo08 as greedya


# La memoria es una única matriz n x n:
#   - Triángulo superior [min][max] -> MCP (tenencia restante de cada movimiento)
#   - Triángulo inferior [max][min] -> MLP (veces que se ha usado cada arco)


def es_tabu(memoria, solucion, i, j):
    pos_a, pos_b = (i, j) if i < j else (j, i)
    ciudad_a, ciudad_b = solucion[i], solucion[j]
    if ciudad_a > ciudad_b:
        ciudad_a, ciudad_b = ciudad_b, ciudad_a
    return memoria[pos_a, pos_b] > 0 or memoria[ciudad_a, ciudad_b] > 0


def insertar_tabu(memoria, activos, solucion, i, j, tenencia):
    # Se guardan dos valores: el par de posiciones y el par de ciudades intercambiadas
    pos = (i, j) if i < j else (j, i)
    ciudad_a, ciudad_b = solucion[i], solucion[j]
    ciudades = (ciudad_a, ciudad_b) if ciudad_a < ciudad_b else (ciudad_b, ciudad_a)
    for par in (pos, ciudades):
        memoria[par] = tenencia
        activos.add(par)


def actualizar_mcp(memoria, activos):
    # Decrementa en 1 los movimientos tabú y libera los que llegan a 0
    for par in list(activos):
        memoria[par] -= 1
        if memoria[par] <= 0:
            memoria[par] = 0
            activos.discard(par)


def reiniciar_mcp(memoria, activos):
    for par in activos:
        memoria[par] = 0
    activos.clear()


def actualizar_mlp(memoria, solucion):
    # Incrementa cada arco (ciudad -> siguiente ciudad) de la solución
    origen = np.asarray(solucion)
    destino = np.roll(origen, -1)
    np.add.at(memoria, (np.maximum(origen, destino), np.minimum(origen, destino)), 1)


def frecuencias(memoria, ciudad, n):
    # Frecuencia de los arcos de 'ciudad' con el resto, leyendo solo la MLP
    f = np.zeros(n, dtype=memoria.dtype)
    f[:ciudad] = memoria[ciudad, :ciudad]
    f[ciudad + 1:] = memoria[ciudad + 1:, ciudad]
    return f


def construir_desde_mlp(memoria, n, random, k, mas_frecuentes):
    # Construye un recorrido eligiendo al azar entre las k ciudades no visitadas
    # con más (intensificación) o menos (diversificación) frecuencia en la MLP
    visitado = np.zeros(n, dtype=bool)
    actual = random.randint(0, n - 1)
    solucion = [actual]
    visitado[actual] = True

    while len(solucion) < n:
        no_visitadas = np.flatnonzero(~visitado)
        f = frecuencias(memoria, actual, n)[no_visitadas]
        if len(no_visitadas) <= k:
            candidatas = no_visitadas
        else:
            orden = -f if mas_frecuentes else f
            candidatas = no_visitadas[np.argpartition(orden, k - 1)[:k]]
        actual = int(candidatas[random.randint(0, len(candidatas) - 1)])
        solucion.append(actual)
        visitado[actual] = True

    return solucion


def intensificacion(memoria, n, random, k):
    return construir_desde_mlp(memoria, n, random, k, True)


def diversificacion(memoria, n, random, k):
    return construir_desde_mlp(memoria, n, random, k, False)


def busqueda_tabu(matriz_distancias, n, max_iteraciones, k, random,tenencia, estancamiento, oscilacion, logger=None):


    #Inicialización: solución inicial por greedy aleatorio y evaluación
    solucion_actual = greedya.greedy_aleatorio(matriz_distancias, random, k)
    peso_actual = evaluacion.evaluar(matriz_distancias, solucion_actual)
    #Creación de la memoria y variables de control
    mejor_momento_actual, peso_momento_actual = solucion_actual.copy(), peso_actual
    mejor_global, peso_global = solucion_actual.copy(), peso_actual

    if logger is not None:
        logger.log_inicio_tabu(solucion_actual, peso_actual)

    memoria = np.zeros((n, n), dtype=np.int32)
    activos = set()
    db = [0] * n

    limite_estancamiento = int(estancamiento * max_iteraciones)
    contador_estancamiento = 0
    n_reinicios = 0
    n_iteraciones = 0
    i = 0

    while n_iteraciones < max_iteraciones:
        # Exploración del entorno con DLB (first improvement), descartando los tabú.
        # Se guarda el mejor vecino no tabú por si no hay ninguno que mejore.
        mov_i = mov_j = -1
        mejor_vecino = None
        while not all(db):
            if db[i] == 0:
                for offset in range(1, n):
                    j = (i + offset) % n
                    if es_tabu(memoria, solucion_actual, i, j):
                        continue
                    peso_vecino = evaluacion.coste_intercambio(
                        matriz_distancias, solucion_actual, i, j, peso_actual
                    )
                    if peso_vecino < peso_actual:
                        mov_i, mov_j = i, j
                        break
                    if mejor_vecino is None or peso_vecino < mejor_vecino[2]:
                        mejor_vecino = (i, j, peso_vecino)
                if mov_i != -1:
                    break
                db[i] = 1
            i = (i + 1) % n

        if mov_i == -1:
            if mejor_vecino is None:
                # el entorno explorado es tabú: se considera estancamiento
                contador_estancamiento = limite_estancamiento
            else:
                # Ninguno mejora: nos movemos a la mejor de las peores
                mov_i, mov_j = mejor_vecino[0], mejor_vecino[1]

        if mov_i != -1:
            coste_anterior = peso_actual
            actualizar_mcp(memoria, activos)
            insertar_tabu(memoria, activos, solucion_actual, mov_i, mov_j, tenencia)
            evaluacion.apply_move(solucion_actual, mov_i, mov_j)
            peso_actual = evaluacion.evaluar(matriz_distancias, solucion_actual)
            actualizar_mlp(memoria, solucion_actual)
            db[mov_i] = 0
            db[mov_j] = 0
            n_iteraciones += 1

            if peso_actual < peso_momento_actual:
                mejor_momento_actual, peso_momento_actual = solucion_actual.copy(), peso_actual
                contador_estancamiento = 0
                if peso_actual < peso_global:
                    mejor_global, peso_global = solucion_actual.copy(), peso_actual
            else:
                contador_estancamiento += 1

            if logger is not None:
                logger.log_movimiento_tabu(
                    n_iteraciones, mov_i, mov_j, coste_anterior, peso_actual,
                    peso_momento_actual, peso_global, contador_estancamiento,
                )

        if contador_estancamiento >= limite_estancamiento and n_iteraciones < max_iteraciones:
            # Oscilación estratégica: nueva solución por intensificación o diversificación
            if random.random() < oscilacion:
                tipo = "intensificación"
                solucion_actual = intensificacion(memoria, n, random, k)
            else:
                tipo = "diversificación"
                solucion_actual = diversificacion(memoria, n, random, k)
            peso_actual = evaluacion.evaluar(matriz_distancias, solucion_actual)
            n_reinicios += 1

            # Se reinicia todo excepto la MLP
            mejor_momento_actual, peso_momento_actual = solucion_actual.copy(), peso_actual
            if peso_actual < peso_global:
                mejor_global, peso_global = solucion_actual.copy(), peso_actual
            reiniciar_mcp(memoria, activos)
            db = [0] * n
            contador_estancamiento = 0
            i = 0

            if logger is not None:
                logger.log_reinicio_tabu(n_iteraciones, tipo, solucion_actual, peso_actual)

    if logger is not None:
        logger.log_fin_tabu(mejor_global, peso_global, n_iteraciones, n_reinicios)

    return mejor_global


def ejecucion(matriz_distancias, n, n_iteraciones, k, random,
              tenencia, estancamiento, oscilacion, logger=None):
    v_asignacion = busqueda_tabu(
        matriz_distancias, n, n_iteraciones, k, random,
        tenencia, estancamiento, oscilacion, logger=logger,
    )
    return evaluacion.evaluar(matriz_distancias, v_asignacion)
