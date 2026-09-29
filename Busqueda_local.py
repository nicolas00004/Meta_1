import Funcion_evaluacion as evaluacion
import greedy_aleatorio as greedya


def busqueda_local(matriz_distancias, n, max_iteraciones, k, random, logger=None):
    v_greedy_aleatorio=greedya.greedy_aleatorio(matriz_distancias,random,k)
    peso_actual=evaluacion.evaluar(matriz_distancias,v_greedy_aleatorio)
    if logger is not None:
        logger.log_inicio_busqueda_local(v_greedy_aleatorio, peso_actual)

    db=[0]*n
    flag_mejora=False
    n_iteraciones=0

    while(n_iteraciones<max_iteraciones and not all (db)):
        for i in range(0,n):
            if (db[i]==0):
                flag_mejora=False
            for limitej in range(1, n):
                j = (i + limitej) % n
                flag_mejora=evaluacion.check_move(matriz_distancias,v_greedy_aleatorio,i,j,peso_actual)
                if flag_mejora:
                    coste_anterior = peso_actual
                    evaluacion.apply_move(v_greedy_aleatorio ,i,j)
                    peso_actual=evaluacion.evaluar(matriz_distancias,v_greedy_aleatorio)
                    n_iteraciones += 1
                    if logger is not None and peso_actual < coste_anterior:
                        logger.log_movimiento_busqueda_local(
                            n_iteraciones,
                            i,
                            j,
                            coste_anterior,
                            peso_actual,
                        )
                    db[i]=0
                    db[j]=0
            if flag_mejora== False:
                db[i]=1

    if logger is not None:
        if n_iteraciones >= max_iteraciones:
            motivo = "alcanzado el máximo de movimientos"
        else:
            motivo = "no se encontraron más movimientos de mejora"
        logger.log_fin_busqueda_local(
            v_greedy_aleatorio,
            peso_actual,
            n_iteraciones,
            motivo,
        )

    return v_greedy_aleatorio


def ejecucion(matriz_distancias, n, n_iteraciones, k, random, logger=None):

    v_asignacion=busqueda_local(matriz_distancias, n, n_iteraciones, k, random, logger=logger)
    return evaluacion.evaluar(matriz_distancias,v_asignacion)