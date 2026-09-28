from math import radians

import Funcion_evaluacion as evaluacion
import greedy_aleatorio as greedya


def busqueda_local (matriz_distancias,n,max_iteraciones,k,random):
    v_greedy_aleatorio=greedya.greedy_aleatorio(matriz_distancias,random,k)
    peso_actual=evaluacion.evaluar(matriz_distancias,v_greedy_aleatorio)
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
                    evaluacion.apply_move(v_greedy_aleatorio ,i,j)
                    n_iteraciones += 1
                    db[i]=0
                    db[j]=0
            if flag_mejora== False:
                db[i]=1

    return v_greedy_aleatorio


def ejecucion (matriz_distancias,n,n_iteraciones,k,random):

    v_asignacion=busqueda_local(matriz_distancias,n,n_iteraciones,k,random)
    return evaluacion.evaluar(matriz_distancias,v_asignacion)