"""
Algoritmo de Búsqueda Tabú (TA) para el TSP.

Esquema:
- Solución: permutación de ciudades. Vecino: intercambio de dos posiciones (i, j),
  evaluado por factorización (simétrico), igual que en Busqueda_local.py.
- Entorno con DLB: mientras haya bits a 0 se hace primer mejor; cuando todos los
  bits están a 1 (óptimo local) se explora el entorno completo y se mueve al
  mejor vecino no tabú aunque empeore.
- Memoria única (matriz n x n):
    * triángulo inferior (fila > columna) -> MCP (tenencia tabú, t=10)
    * triángulo superior (fila < columna) -> MLP (frecuencia de arcos)
- Sin criterio de aspiración.
- Estancamiento: 5% de las iteraciones totales con movimientos consecutivos que
  no mejoran el mejor_momento_actual.
- Al estancarse: reinicio por oscilación estratégica 50% (intensificación o
  diversificación según la MLP). Se reinician todas las estructuras salvo la MLP.
"""
import time

import numpy as np

import Funcion_evaluacion as evaluacion
import greedy_aleatorio as greedya

EPS = 1e-7


class _Entorno:
    """Cálculo vectorizado de deltas de intercambio y gestión de las memorias."""

    def __init__(self, matriz_distancias, n, tenencia):
        self.D = np.asarray(matriz_distancias, dtype=np.float64)
        self.n = n
        self.tenencia = tenencia
        self.memoria = np.zeros((n, n), dtype=np.int32)
        self.activos = []  # pares (fila, col) con tenencia > 0 en la MCP

    # ------------------------------------------------------------------ MCP
    def es_tabu_vector(self, ciudad, ciudades):
        mayor = np.maximum(ciudad, ciudades)
        menor = np.minimum(ciudad, ciudades)
        return self.memoria[mayor, menor] > 0

    def actualizar_mcp(self, ciudad_a, ciudad_b):
        # decrementa los movimientos tabú existentes
        restantes = []
        for (f, c) in self.activos:
            self.memoria[f, c] -= 1
            if self.memoria[f, c] > 0:
                restantes.append((f, c))
        self.activos = restantes
        # añade el movimiento actual
        f, c = max(ciudad_a, ciudad_b), min(ciudad_a, ciudad_b)
        self.memoria[f, c] = self.tenencia
        if (f, c) not in self.activos:
            self.activos.append((f, c))

    def reiniciar_mcp(self):
        for (f, c) in self.activos:
            self.memoria[f, c] = 0
        self.activos = []

    # ------------------------------------------------------------------ MLP
    def actualizar_mlp(self, sol):
        siguiente = np.roll(sol, -1)
        filas = np.minimum(sol, siguiente)
        cols = np.maximum(sol, siguiente)
        self.memoria[filas, cols] += 1

    # --------------------------------------------------------------- deltas
    def _delta_adyacente(self, sol, i, j):
        """Delta cuando la posición j es la siguiente a i (circular)."""
        n, D = self.n, self.D
        a, b = sol[i], sol[j]
        pa, nb = sol[(i - 1) % n], sol[(j + 1) % n]
        quitar = D[pa, a] + D[a, b] + D[b, nb]
        anadir = D[pa, b] + D[b, a] + D[a, nb]
        return anadir - quitar

    def deltas_fila(self, sol, prev, nxt, i):
        """Delta de intercambiar la posición i con todas las posiciones j."""
        n, D = self.n, self.D
        a, pa, na = sol[i], prev[i], nxt[i]
        quitar = D[pa, a] + D[a, na] + D[prev, sol] + D[sol, nxt]
        anadir = D[pa, sol] + D[sol, na] + D[prev, a] + D[a, nxt]
        delta = anadir - quitar
        j_sig = (i + 1) % n
        j_ant = (i - 1) % n
        delta[j_sig] = self._delta_adyacente(sol, i, j_sig)
        delta[j_ant] = self._delta_adyacente(sol, j_ant, i)
        delta[i] = np.inf
        return delta

    def primera_mejora(self, sol, prev, nxt, i):
        """Primer j (en orden circular desde i+1) con delta<0 y movimiento no tabú."""
        n = self.n
        delta = self.deltas_fila(sol, prev, nxt, i)
        delta[self.es_tabu_vector(sol[i], sol)] = np.inf
        orden = (i + np.arange(1, n)) % n
        candidatos = np.nonzero(delta[orden] < -EPS)[0]
        if candidatos.size == 0:
            return None
        return int(orden[candidatos[0]])

    def mejor_vecino(self, sol):
        """Mejor movimiento no tabú de todo el entorno (aunque empeore)."""
        n = self.n
        prev, nxt = np.roll(sol, 1), np.roll(sol, -1)
        mejor = (np.inf, None, None)
        for i in range(n):
            delta = self.deltas_fila(sol, prev, nxt, i)
            delta[self.es_tabu_vector(sol[i], sol)] = np.inf
            j = int(np.argmin(delta))
            if delta[j] < mejor[0]:
                mejor = (delta[j], i, j)
        if mejor[1] is None:
            return None
        return mejor[1], mejor[2]

    # ----------------------------------------- generación de nueva solución
    def solucion_desde_mlp(self, random, intensificar):
        """
        Construye una solución usando la frecuencia de arcos (MLP).
        - intensificar: prefiere arcos más frecuentes.
        - diversificar: prefiere arcos menos frecuentes.
        Los empates se resuelven por menor distancia.
        """
        n, D = self.n, self.D
        signo = -1 if intensificar else 1
        visitado = np.zeros(n, dtype=bool)
        actual = random.randrange(n)
        visitado[actual] = True
        sol = [actual]
        for _ in range(n - 1):
            cand = np.nonzero(~visitado)[0]
            freq = self.memoria[np.minimum(actual, cand), np.maximum(actual, cand)]
            orden = np.lexsort((D[actual, cand], signo * freq))
            actual = int(cand[orden[0]])
            visitado[actual] = True
            sol.append(actual)
        return np.array(sol, dtype=np.int64)


def busqueda_tabu(
    matriz_distancias,
    n,
    max_iteraciones,
    k,
    random,
    logger=None,
    tenencia=10,
    pct_estancamiento=0.05,
    prob_oscilacion=0.5,
):
    entorno = _Entorno(matriz_distancias, n, tenencia)
    D = matriz_distancias

    # Solución inicial: greedy aleatorio
    solucion_lista = greedya.greedy_aleatorio(matriz_distancias, random, k)
    solucion_actual = np.array(solucion_lista, dtype=np.int64)
    coste_actual = float(evaluacion.evaluar(D, solucion_actual))

    mejor_momento = solucion_actual.copy()
    coste_mejor_momento = coste_actual
    mejor_global = solucion_actual.copy()
    coste_mejor_global = coste_actual

    limite_estancamiento = max(1, int(pct_estancamiento * max_iteraciones))
    empeoramientos = 0
    reinicios = {"intensificacion": 0, "diversificacion": 0}

    dlb = np.zeros(n, dtype=bool)
    iteracion = 0
    i = 0

    if logger is not None:
        logger.log_solucion_inicial(solucion_actual.tolist(), coste_actual)

    if n < 3:
        return solucion_actual.tolist()

    while iteracion < max_iteraciones:
        # ---------------------------------------------- selección de movimiento
        if not dlb.all():
            while dlb[i]:
                i = (i + 1) % n
            prev, nxt = np.roll(solucion_actual, 1), np.roll(solucion_actual, -1)
            j = entorno.primera_mejora(solucion_actual, prev, nxt, i)
            if j is None:
                dlb[i] = True
                i = (i + 1) % n
                continue
            pos_i, pos_j = i, j
        else:
            movimiento = entorno.mejor_vecino(solucion_actual)
            if movimiento is None:  # todo el entorno es tabú
                entorno.reiniciar_mcp()
                dlb[:] = False
                continue
            pos_i, pos_j = movimiento

        # ----------------------------------------------------- aplicar movimiento
        ciudad_a, ciudad_b = int(solucion_actual[pos_i]), int(solucion_actual[pos_j])
        evaluacion.apply_move(solucion_actual, pos_i, pos_j)
        coste_actual = float(evaluacion.evaluar(D, solucion_actual))
        iteracion += 1
        dlb[pos_i] = False
        dlb[pos_j] = False
        i = pos_i

        # ------------------------------------------------------------ memorias
        entorno.actualizar_mcp(ciudad_a, ciudad_b)
        entorno.actualizar_mlp(solucion_actual)

        # -------------------------------------------------- mejores soluciones
        es_mejora_global = False
        if coste_actual < coste_mejor_momento - EPS:
            mejor_momento = solucion_actual.copy()
            coste_mejor_momento = coste_actual
            empeoramientos = 0
        else:
            empeoramientos += 1
        if coste_actual < coste_mejor_global - EPS:
            mejor_global = solucion_actual.copy()
            coste_mejor_global = coste_actual
            es_mejora_global = True

        if logger is not None:
            logger.log_movimiento(
                iteracion, pos_i, pos_j, solucion_actual.tolist(),
                coste_actual, es_mejora_global,
            )

        # ------------------------------------------------------- estancamiento
        if empeoramientos >= limite_estancamiento and iteracion < max_iteraciones:
            intensificar = random.random() < prob_oscilacion
            tipo = "intensificacion" if intensificar else "diversificacion"
            reinicios[tipo] += 1
            solucion_actual = entorno.solucion_desde_mlp(random, intensificar)
            coste_actual = float(evaluacion.evaluar(D, solucion_actual))
            mejor_momento = solucion_actual.copy()
            coste_mejor_momento = coste_actual
            empeoramientos = 0
            entorno.reiniciar_mcp()
            dlb[:] = False
            i = 0
            if coste_actual < coste_mejor_global - EPS:
                mejor_global = solucion_actual.copy()
                coste_mejor_global = coste_actual
            if logger is not None:
                logger.log(
                    f"Iteración {iteracion}: ESTANCAMIENTO -> reinicio por {tipo}. "
                    f"Nuevo coste: {coste_actual}",
                    "TABU",
                )
                logger.log(f"  Solución: {solucion_actual.tolist()}", "TABU")

    if logger is not None:
        logger.log(
            f"Búsqueda tabú finalizada: iteraciones={iteracion}; "
            f"reinicios intensificación={reinicios['intensificacion']}, "
            f"diversificación={reinicios['diversificacion']}",
            "RESULT",
        )
        logger.log("Mejor solución global:", "RESULT")
        logger.log(f"  {mejor_global.tolist()}", "RESULT")
        logger.log(f"Coste final: {coste_mejor_global}", "RESULT")
        logger._resumen_busqueda_local = {
            "Iteraciones": iteracion,
            "Reinicios (intensificación)": reinicios["intensificacion"],
            "Reinicios (diversificación)": reinicios["diversificacion"],
            "Coste final": coste_mejor_global,
        }

    return mejor_global.tolist()


def ejecucion(matriz_distancias, n, n_iteraciones, k, random, logger=None,
              tenencia=10, pct_estancamiento=0.05, prob_oscilacion=0.5):
    solucion = busqueda_tabu(
        matriz_distancias, n, n_iteraciones, k, random, logger=logger,
        tenencia=tenencia, pct_estancamiento=pct_estancamiento,
        prob_oscilacion=prob_oscilacion,
    )
    return evaluacion.evaluar(matriz_distancias, solucion)