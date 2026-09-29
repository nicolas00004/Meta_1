import Funcion_evaluacion as evaluacion
import greedy_aleatorio as greedya


def busqueda_local(matriz_distancias, n, max_iteraciones, k, random, logger=None):
    solucion = greedya.greedy_aleatorio(matriz_distancias, random, k)
    peso_actual = evaluacion.evaluar(matriz_distancias, solucion)
    db = [0] * n
    if logger is not None:
        logger.log_inicio_busqueda_local(solucion, peso_actual, db)

    n_iteraciones = 0
    i = 0

    while n_iteraciones < max_iteraciones and not all(db):
        if db[i] == 0:
            mejora_i = False
            for offset in range(1, n):
                j = (i + offset) % n
                if evaluacion.check_move(matriz_distancias, solucion, i, j, peso_actual):
                    coste_anterior = peso_actual
                    evaluacion.apply_move(solucion, i, j)
                    peso_actual = evaluacion.evaluar(matriz_distancias, solucion)
                    n_iteraciones += 1
                    db[i] = 0
                    db[j] = 0
                    mejora_i = True
                    if logger is not None:
                        logger.log_movimiento_busqueda_local(
                            n_iteraciones,
                            i,
                            j,
                            solucion,
                            coste_anterior,
                            peso_actual,
                            db,
                        )
                    break  # first improvement: reevaluamos i desde cero
            if not mejora_i:
                db[i] = 1
                if logger is not None:
                    logger.log_fallo_intercambio_busqueda_local(i, db)
                i = (i + 1) % n
            # si hubo mejora, NO avanzamos: seguimos con la misma i
        else:
            i = (i + 1) % n

    if logger is not None:
        motivo = ("alcanzado el máximo de movimientos"
                  if n_iteraciones >= max_iteraciones
                  else "no se encontraron más movimientos de mejora")
        logger.log_fin_busqueda_local(
            solucion, peso_actual, n_iteraciones, motivo, db
        )

    return solucion


def ejecucion(matriz_distancias, n, n_iteraciones, k, random, logger=None):

    v_asignacion=busqueda_local(matriz_distancias, n, n_iteraciones, k, random, logger=logger)
    return evaluacion.evaluar(matriz_distancias,v_asignacion)