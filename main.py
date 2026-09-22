import os
from random import Random

import extracion_datos
import greedy
import Extraccion_parametros
import Funcion_evaluacion
import greedy_aleatorio
import time
import Busqueda_local as busqueda_local

if __name__ == "__main__":

    # Cargar los parámetros desde el archivo
    parametros = Extraccion_parametros.cargar_param("parametros.txt")
    carpeta=parametros['DATA']
    semilla=parametros['SEMILLA']
    k=int(parametros['K'])
    algoritmos=parametros['ALGORITMO'].split()
    n_ejecucion=int(parametros['N_EJECUCIONES'])

    random=Random()



    archivos_tsp = [f for f in os.listdir(carpeta) if f.endswith('.tsp')]
    problemas = {}


    for algoritmo in algoritmos:
        match (algoritmo):
            case "gre":
                for nombre_fichero in archivos_tsp:
                    #Carga los datos del fichero
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


                        print(f"FICHERO PROCESADO: {nombre_fichero}")
                        print(f"Nombre del problema: {nombre}")
                        print(f"Comentario: {comentario}")
                        print(f"Número de nodos: {n}")
                        print(f"Forma de la matriz de distancias: {m_distancias.shape}")
                        print(f"Distancia total algoritmo greedy: {greedy.ejecucion(m_distancias, parametros)}")
                        print("x"*10)
                    else:
                        print("Fallo en la lectura de fichero")

            case "grea":
                for nombre_fichero in archivos_tsp:
                    #Carga los datos del fichero
                    ruta_archivo = os.path.join(carpeta, nombre_fichero)
                    n, m_coordenadas, m_distancias, nombre, comentario = extracion_datos.extraccion_Archivo(ruta_archivo)

                    for ejecu in range(n_ejecucion):
                        #Carga de la semilla
                        n_semilla = Extraccion_parametros.permutar_semilla_circular(semilla)
                        print("---------------------La semilla es:--------------", n_semilla, "en la ejecucion", ejecu)
                        random.seed(n_semilla)
                        semilla = n_semilla



                        if n is not None:
                            # Almacenar en el diccionario
                            problemas[nombre_fichero] = {
                                "n": n,
                                "coordenadas": m_coordenadas,
                                "distancias": m_distancias,
                                "nombre": nombre,
                                "comentario": comentario
                            }

                            print(f"FICHERO PROCESADO: {nombre_fichero}")
                            print(f"Nombre del problema: {nombre}")
                            print(f"Comentario: {comentario}")
                            print(f"Número de nodos: {n}")
                            print(f"Forma de la matriz de distancias: {m_distancias.shape}")
                            print(f"Distancia total algoritmo greedy aleatorio: {greedy_aleatorio.ejecucion(m_distancias, k, random)}")
                            print("x" * 10)
                        else:
                            print("Fallo en la lectura de fichero")
            case "b_local":
                for nombre_fichero in archivos_tsp:
                    #Carga los datos del fichero
                    ruta_archivo = os.path.join(carpeta, nombre_fichero)
                    n, m_coordenadas, m_distancias, nombre, comentario = extracion_datos.extraccion_Archivo(ruta_archivo)

                    for ejecu in range(n_ejecucion):
                        #Carga de la semilla
                        n_semilla = Extraccion_parametros.permutar_semilla_circular(semilla)
                        print("---------------------La semilla es:--------------", n_semilla, "en la ejecucion", ejecu)
                        random.seed(n_semilla)
                        semilla = n_semilla



                        if n is not None:
                            # Almacenar en el diccionario
                            problemas[nombre_fichero] = {
                                "n": n,
                                "coordenadas": m_coordenadas,
                                "distancias": m_distancias,
                                "nombre": nombre,
                                "comentario": comentario
                            }

                            print(f"FICHERO PROCESADO: {nombre_fichero}")
                            print(f"Nombre del problema: {nombre}")
                            print(f"Comentario: {comentario}")
                            print(f"Número de nodos: {n}")
                            print(f"Forma de la matriz de distancias: {m_distancias.shape}")
                            print(f"Distancia total algoritmo greedy aleatorio: {busqueda_local.ejecucion(m_distancias, n)}")
                            print("x" * 10)
                        else:
                            print("Fallo en la lectura de fichero")

#TODO implementar contar tiempo y Logs
