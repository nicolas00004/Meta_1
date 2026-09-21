import os
from random import Random

import extracion_datos
import greedy
import Extraccion_parametros
import Funcion_evaluacion
import greedy_aleatorio

if __name__ == "__main__":

    # Cargar los parámetros desde el archivo
    parametros = Extraccion_parametros.cargar_param("parametros.txt")
    carpeta=parametros['DATA']
    semilla=parametros['SEMILLA']
    k=int(parametros['K'])
    random=Random()

    semila=Extraccion_parametros.permutar_semilla_circular(semilla)
    print("La semilla es:", semilla)
    random.seed(semilla)

    # 1. Obtener la lista de todos los archivos .tsp en la carpeta
    archivos_tsp = [f for f in os.listdir(carpeta) if f.endswith('.tsp')]

    # Diccionario para guardar las matrices y datos de cada problema s
    problemas = {}

    print(f"Se encontraron {len(archivos_tsp)} archivos .tsp para procesar.\n")

    # 2. Iterar sobre cada archivo y ejecutar la extracción
    for nombre_fichero in archivos_tsp:
        ruta_archivo = os.path.join(carpeta, nombre_fichero)

        n, m_coordenadas, m_distancias, nombre, comentario = extracion_datos.extraccion_Archivo(ruta_archivo)

        if n is not None:
            # Almacenar en el diccionario
            problemas[nombre_fichero] = {
                "n": n,
                "coordenadas": m_coordenadas,
                "distancias": m_distancias,
                "nombre": nombre,
                "comentario": comentario
            }

            print("=" * 50)
            print(f"Fichero procesado: {nombre_fichero}")
            print(f"Nombre del problema: {nombre}")
            print(f"Comentario: {comentario}")
            print(f"Número de nodos: {n}")
            print(f"Forma de la matriz de distancias: {m_distancias.shape}")

            vector = greedy.greedy(m_distancias)
            distancia_total = Funcion_evaluacion.evaluar(m_distancias, vector)
            print(f"Distancia total algoritmo greedy: {distancia_total}")

            vector_asignacion_greedy=greedy_aleatorio.greedy_aleatorio(m_distancias,random,k)
            distancia_total_greedy=Funcion_evaluacion.evaluar(m_distancias, vector_asignacion_greedy)
            print(f"Distancia total algoritmo greedy aleatorio: {distancia_total_greedy}")
            print("=" * 50 + "\n")

        else:
            print(f"Error al cargar el archivo {nombre_fichero}\n")

