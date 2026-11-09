import time
import numpy as np
import individuo

# Esquema de cada generación:
# inicializa -> evalúa -> selección por torneo junto con la recombinación (tam_poblacion/2 parejas,
# cada pareja da dos hijos) -> mutación -> evaluación de los hijos (solo los que no estaban evaluados)
# -> se comprueba si los élites siguen en la nueva población; si no están, entran por torneo de perdedores.


def creacion_sol_aleatorias(num_sol, aleatorio, tam_sol):
    poblacion_aleatoria = []

    for i in range(num_sol):
        solucion = list(range(tam_sol))
        aleatorio.shuffle(solucion)
        individuo_aleatorio = individuo.Individuo(solucion)
        poblacion_aleatoria.append(individuo_aleatorio)

    return poblacion_aleatoria


def orden_greedy(m_distancias):
    '''
    Ciudades ordenadas por la suma de su fila de distancias, como en el greedy aleatorio de la P1.
    Ese orden no cambia entre llamadas, así que se calcula una sola vez por ejecución
    (la P1 reordena la lista tras cada ciudad y en d18512 cada greedy tarda unos 10 s).
    '''
    vector = [(i, float(m_distancias[i].sum(dtype=np.float64))) for i in range(m_distancias.shape[0])]
    vector.sort(key=lambda x: x[1])
    return vector


def greedy_aleatorio_ordenado(orden, aleatorio, k):
    '''
    Greedy aleatorio de la P1 partiendo del orden ya calculado: hace las mismas llamadas
    al generador aleatorio, así que con la misma semilla devuelve la misma solución.
    '''
    vector = orden.copy()
    v_asignacion = []
    while vector:
        if len(vector) < k:
            indice_aleatorio = aleatorio.randint(0, len(vector) - 1)
        else:
            indice_aleatorio = aleatorio.randint(0, k - 1)
        v_asignacion.append(vector.pop(indice_aleatorio)[0])
    return v_asignacion


def poblacion_inicial(tam_sol, k, tam_poblacion, porcentaje_greedy, m_distancias, aleatorio):
    # Una parte de la población sale del greedy aleatorio de la P1 (k = tamaño de la LRC)
    # y el resto son permutaciones aleatorias puras
    tam_greedy_sol = int(tam_poblacion * porcentaje_greedy)
    tam_aleatorios = tam_poblacion - tam_greedy_sol

    poblacion_greedy = []
    orden = orden_greedy(m_distancias)
    for i in range(tam_greedy_sol):
        sol = greedy_aleatorio_ordenado(orden, aleatorio, k)
        poblacion_greedy.append(individuo.Individuo(sol))

    poblacion_aleatoria = creacion_sol_aleatorias(tam_aleatorios, aleatorio, tam_sol)

    return poblacion_greedy + poblacion_aleatoria


def evaluar_poblacion(poblacion, m_distancias):
    '''
    Evalúa los individuos que no se han evaluado todavía y devuelve cuántas evaluaciones se han gastado.
    '''
    evaluaciones = 0
    for ind in poblacion:
        _, gastadas = ind.evaluar(m_distancias)
        evaluaciones += gastadas
    return evaluaciones


def ox2_imponer(i, j, posiciones):
    '''
    Copia de i en la que las ciudades que j tiene en las posiciones elegidas se colocan
    en el orden en que aparecen en j.
    '''
    hijo = individuo.Individuo(i.asignacion.copy())
    lista_seleccionados = [j.asignacion[p] for p in posiciones]
    # Conjunto para que la comprobación sea O(1): con listas el cruce es O(n^2) y en d18512 no termina
    conjunto_seleccionados = set(lista_seleccionados)
    siguiente = 0
    for indice in range(len(hijo.asignacion)):
        if hijo.asignacion[indice] in conjunto_seleccionados:
            hijo.asignacion[indice] = lista_seleccionados[siguiente]
            siguiente += 1
    return hijo


def cruce_ox2(i, j, aleatorio, prob_posicion):
    '''
    Cruce OX2: se eligen al azar varias posiciones (cada una con probabilidad prob_posicion) y se usan
    las mismas posiciones para los dos hijos, cambiando el papel de los padres.
    '''
    posiciones = [p for p in range(len(i.asignacion)) if aleatorio.random() < prob_posicion]
    return ox2_imponer(i, j, posiciones), ox2_imponer(j, i, posiciones)


def cruce_moc(i, j, aleatorio, tam):
    punto = aleatorio.randrange(tam)
    sublista_i = i.asignacion[punto:]
    sublista_j = j.asignacion[punto:]
    conjunto_i = set(sublista_i)
    conjunto_j = set(sublista_j)
    b_i = individuo.Individuo([item if item not in conjunto_j else -1 for item in i.asignacion])
    b_j = individuo.Individuo([item if item not in conjunto_i else -1 for item in j.asignacion])

    siguiente = 0
    for indice in range(len(b_i.asignacion)):
        if b_i.asignacion[indice] == -1:
            b_i.asignacion[indice] = sublista_j[siguiente]
            siguiente += 1
    siguiente = 0
    for indice in range(len(b_j.asignacion)):
        if b_j.asignacion[indice] == -1:
            b_j.asignacion[indice] = sublista_i[siguiente]
            siguiente += 1

    return b_i, b_j


def intercambio_2_opt(solucion, i, j):
    nueva_solucion = solucion.copy()
    nueva_solucion[i], nueva_solucion[j] = nueva_solucion[j], nueva_solucion[i]
    return nueva_solucion


def mutacion(poblacion, tam, probabilidad_mutacion, aleatorio):
    # Cada individuo muta con probabilidad probabilidad_mutacion: intercambio de dos posiciones distintas
    mutaciones = 0
    for ind in poblacion:
        if aleatorio.random() < probabilidad_mutacion:
            pos_i = aleatorio.randint(0, tam - 1)
            pos_j = pos_i
            while pos_j == pos_i:
                pos_j = aleatorio.randint(0, tam - 1)
            ind.asignacion = intercambio_2_opt(ind.asignacion, pos_i, pos_j)
            # Ha cambiado el recorrido, así que hay que volver a evaluarlo
            ind.evaluado = False
            ind.coste = None
            mutaciones += 1

    return mutaciones


def torneo_de_perdedores(poblacion, aleatorio, K_worst, individuo_elite):
    '''
    Ejecuta un torneo de tamaño K_worst y sustituye al peor de los participantes por el élite.
    Los élites que ya se han reinsertado no participan, para no expulsar a uno con otro.
    '''
    candidatos = [indice for indice, ind in enumerate(poblacion) if not ind.elite]
    participantes = aleatorio.sample(candidatos, min(int(K_worst), len(candidatos)))
    indice_victima = max(participantes, key=lambda indice: poblacion[indice].coste)
    poblacion[indice_victima] = individuo_elite

    return poblacion


def seleccion_padre_por_torneo(poblacion, aleatorio, Kbest):
    '''
        Ejecuta un torneo de tamaño Kbest y devuelve el mejor de los participantes.
        :param poblacion:
        :param aleatorio:
        :param Kbest:
        :return:
        '''
    # 1. Elegir k participantes al azar (sin repetición)
    participantes = aleatorio.sample(poblacion, int(Kbest))
    # 2. Seleccionar el mejor individuo entre los participantes
    ganador = min(participantes, key=lambda ind: ind.coste)
    return ganador


def heredar_coste(hijo, padre1, padre2):
    '''
    Si el cruce devuelve un hijo idéntico a uno de sus padres (padres iguales, o punto de corte 0
    en MOC), ese recorrido ya se evaluó: se copia el coste y no se gasta otra evaluación.
    '''
    for padre in (padre1, padre2):
        if padre.evaluado and hijo.asignacion == padre.asignacion:
            hijo.coste = padre.coste
            hijo.evaluado = True
            return


def seleccion_cruce(poblacion, probabilidad_cruce, aleatorio, kbest, operador_cruce, prob_posicion_ox2):
    '''
    Hace la selección junto con la recombinación: por cada pareja se eligen dos padres por torneo
    y se cruzan, así que basta con recorrer la mitad de la población para obtener una nueva entera.
    '''
    nueva_poblacion = []
    for i in range(0, len(poblacion), 2):
        padre1 = seleccion_padre_por_torneo(poblacion, aleatorio, kbest)
        padre2 = seleccion_padre_por_torneo(poblacion, aleatorio, kbest)
        if aleatorio.random() < probabilidad_cruce:
            # Se cruzan los padres
            if operador_cruce == "OX2":
                hijo1, hijo2 = cruce_ox2(padre1, padre2, aleatorio, prob_posicion_ox2)
            elif operador_cruce == "MOC":
                hijo1, hijo2 = cruce_moc(padre1, padre2, aleatorio, len(padre1.asignacion))
            else:
                raise ValueError(f"Operador de cruce desconocido: {operador_cruce}")
            heredar_coste(hijo1, padre1, padre2)
            heredar_coste(hijo2, padre1, padre2)
        else:
            # No se cruzan: los hijos son copias de los padres (ya evaluadas, no gastan evaluación)
            hijo1 = padre1.copia()
            hijo2 = padre2.copia()
        nueva_poblacion.append(hijo1)
        nueva_poblacion.append(hijo2)
    # Con tamaño de población impar sobra un hijo
    return nueva_poblacion[:len(poblacion)]


def obtener_elite(poblacion, n_elite):
    poblacion_ordenada = sorted(poblacion, key=lambda ind: ind.coste)
    elite = []
    for i in range(int(n_elite)):
        elite.append(poblacion_ordenada[i].copia())
    return elite


def esta_poblacion(individuo, poblacion):
    for i in poblacion:
        if i.asignacion == individuo.asignacion:
            # Se marca para que el torneo de perdedores no lo pueda sustituir por otro élite
            i.elite = True
            return True

    return False


def algoritmo_evolutivo_generacional(tam, k, tam_poblacion, porcentaje_greedy, m_distancias, aleatorio,
                                     max_evaluaciones, n_elite, Kbest, K_worst, prob_mutacion, tiempo_max,
                                     operador_cruce, probabilidad_cruce, prob_posicion_ox2, logger=None):
    gen = 0
    tiempo_inicio = time.perf_counter()

    # Generamos y evaluamos la poblacion inicial
    poblacion_actual = poblacion_inicial(tam, k, tam_poblacion, porcentaje_greedy, m_distancias, aleatorio)
    cont = evaluar_poblacion(poblacion_actual, m_distancias)
    mejor_individuo = min(poblacion_actual, key=lambda ind: ind.coste).copia()
    if logger is not None:
        logger.log_inicio_agg(mejor_individuo.coste, cont)

    # El límite de tiempo incluye la creación de la población inicial
    while cont < max_evaluaciones and (time.perf_counter() - tiempo_inicio) < tiempo_max:
        gen = gen + 1
        # Obtenemos la poblacion elite
        elite = obtener_elite(poblacion_actual, n_elite)
        # Selección por torneo y cruce
        poblacion_actual = seleccion_cruce(poblacion_actual, probabilidad_cruce, aleatorio, Kbest, operador_cruce,
                                           prob_posicion_ox2)
        # Mutación
        mutaciones = mutacion(poblacion_actual, tam, prob_mutacion, aleatorio)
        # Evaluamos los hijos que todavía no tienen coste
        cont = cont + evaluar_poblacion(poblacion_actual, m_distancias)
        # Reemplazamiento: si un élite no sobrevive (no está en poblacion_actual) entra por torneo de perdedores
        reinsertados = 0
        for ind in poblacion_actual:
            ind.elite = False
        for e in elite:
            if not esta_poblacion(e, poblacion_actual):
                e.elite = True
                poblacion_actual = torneo_de_perdedores(poblacion_actual, aleatorio, K_worst, e)
                reinsertados += 1

        mejor_generacion = min(poblacion_actual, key=lambda ind: ind.coste)
        if mejor_generacion.coste < mejor_individuo.coste:
            mejor_individuo = mejor_generacion.copia()
        if logger is not None:
            logger.log_generacion_agg(gen, cont, mejor_generacion.coste, mejor_individuo.coste,
                                      mutaciones, reinsertados)

    if logger is not None:
        logger.log_fin_agg(mejor_individuo.asignacion, mejor_individuo.coste, gen, cont,
                           time.perf_counter() - tiempo_inicio)

    return mejor_individuo, cont


def ejecucion(m_distancias, n, k, random, tam_poblacion, porcentaje_greedy, max_evaluaciones, n_elite,
              kbest, kworst, prob_mutacion, tiempo_max, operador_cruce, probabilidad_cruce,
              prob_posicion_ox2, logger=None):
    mejor_individuo, _ = algoritmo_evolutivo_generacional(
        n, k, tam_poblacion, porcentaje_greedy, m_distancias, random, max_evaluaciones, n_elite,
        kbest, kworst, prob_mutacion, tiempo_max, operador_cruce, probabilidad_cruce,
        prob_posicion_ox2, logger=logger,
    )
    return mejor_individuo.coste
