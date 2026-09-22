import Funcion_evaluacion as evaluacion

def busqueda_local (matriz_distancias,n):
    v_asignacion = []
    db=[0]*n
    for i in range(n):
        if (db[i]==0):
            flag_mejora=False
        for j=i+1 in range(n):
            #checkMove(i,j)
            if flag_mejora:
                #applymove(i,j)
                db[i]=0
                db[j]=0
                flag_mejora=True
        if flag_mejora== False:
            db[i]=1

    return v_asignacion

def ejecucion (matriz_distancias,n):

    v_asignacion=busqueda_local(matriz_distancias,n)
    return evaluacion.evaluar(matriz_distancias,v_asignacion)