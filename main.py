import os
from random import Random

import extracion_datos
import AlgGreedy_Clase4D_Grupo08 as greedy
import Extraccion_parametros
import AlgGreedyAleatorio_Clase4D_Grupo08 as greedy_aleatorio
import AlgBusquedaLocal_Clase4D_Grupo08 as busqueda_local
import AlgBusquedaTabu_Clase4D_Grupo08 as busqueda_tabu
from logs import Logs


if __name__ == "__main__":

    # Cargar los parámetros desde el archivo
    parametros = Extraccion_parametros.cargar_param("parametros.txt")
    carpeta=parametros['DATA']
    semilla=parametros['SEMILLA']
    semilla_inicial = semilla
    k=int(parametros['K'])
    algoritmos=parametros['ALGORITMO'].split()
    n_ejecucion=int(parametros['N_EJECUCIONES'])
    n_iteraciones=int(parametros['N_ITERACIONES'])
    tenencia=int(parametros['TENENCIA'])
    estancamiento=float(parametros['ESTANCAMIENTO'])
    oscilacion=float(parametros['OSCILACION'])

    random=Random()



    archivos_tsp = [f for f in os.listdir(carpeta) if f.endswith('.tsp')]
    problemas = {}


    for algoritmo in algoritmos:
        match (algoritmo):
            case "gre":
                for nombre_fichero in archivos_tsp:
                    #Carga los datos del fichero
                    ruta_archivo = os.path.join(carpeta, nombre_fichero)
                    nombre_base = os.path.splitext(os.path.basename(nombre_fichero))[0]
                    logger = Logs(
                        os.path.join(
                            "logs", algoritmo,
                            f"{nombre_base}_{algoritmo}_{semilla_inicial}_ejecucion_1.log",
                        )
                    )
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
                        resultado, tiempo = logger.ejecutar_y_registrar(
                            algoritmo,
                            nombre_fichero,
                            semilla_inicial,
                            1,
                            lambda: greedy.ejecucion(m_distancias, parametros),
                        )
                        print(f"Distancia total algoritmo greedy: {resultado}")
                        print(f"Tiempo de ejecución: {tiempo:.6f} s")
                        print("x"*10)
                    else:
                        print("Fallo en la lectura de fichero")

            case "grea":
                for nombre_fichero in archivos_tsp:
                    #Carga los datos del fichero
                    ruta_archivo = os.path.join(carpeta, nombre_fichero)
                    nombre_base = os.path.splitext(os.path.basename(nombre_fichero))[0]
                    n, m_coordenadas, m_distancias, nombre, comentario = extracion_datos.extraccion_Archivo(ruta_archivo)

                    # Cada algoritmo e instancia parte de la misma semilla: la ejecución k
                    # usa la misma semilla en todos los algoritmos (lo exige el guion)
                    semilla = semilla_inicial
                    for ejecu in range(n_ejecucion):
                        #Carga de la semilla
                        n_semilla = Extraccion_parametros.permutar_semilla_circular(semilla)
                        print("---------------------La semilla es:--------------", n_semilla, "en la ejecucion", ejecu)
                        random.seed(n_semilla)
                        semilla = n_semilla
                        logger = Logs(
                            os.path.join(
                                "logs", algoritmo,
                                f"{nombre_base}_{algoritmo}_{n_semilla}_ejecucion_{ejecu + 1}.log",
                            )
                        )



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
                            resultado, tiempo = logger.ejecutar_y_registrar(
                                algoritmo,
                                nombre_fichero,
                                n_semilla,
                                ejecu + 1,
                                lambda: greedy_aleatorio.ejecucion(m_distancias, k, random),
                                k=k,
                            )
                            print(f"Distancia total algoritmo greedy aleatorio: {resultado}")
                            print(f"Tiempo de ejecución: {tiempo:.6f} s")
                            print("x" * 10)
                        else:
                            print("Fallo en la lectura de fichero")
            case "b_local":
                for nombre_fichero in archivos_tsp:
                    #Carga los datos del fichero
                    ruta_archivo = os.path.join(carpeta, nombre_fichero)
                    nombre_base = os.path.splitext(os.path.basename(nombre_fichero))[0]
                    n, m_coordenadas, m_distancias, nombre, comentario = extracion_datos.extraccion_Archivo(ruta_archivo)

                    # Cada algoritmo e instancia parte de la misma semilla: la ejecución k
                    # usa la misma semilla en todos los algoritmos (lo exige el guion)
                    semilla = semilla_inicial
                    for ejecu in range(n_ejecucion):
                        #Carga de la semilla
                        n_semilla = Extraccion_parametros.permutar_semilla_circular(semilla)
                        print("---------------------La semilla es:--------------", n_semilla, "en la ejecucion", ejecu)
                        random.seed(n_semilla)
                        semilla = n_semilla
                        logger = Logs(
                            os.path.join(
                                "logs", algoritmo,
                                f"{nombre_base}_{algoritmo}_{n_semilla}_ejecucion_{ejecu + 1}.log",
                            )
                        )



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
                            resultado, tiempo = logger.ejecutar_y_registrar(
                                algoritmo,
                                nombre_fichero,
                                n_semilla,
                                ejecu + 1,
                                lambda: busqueda_local.ejecucion(
                                    m_distancias,
                                    n,
                                    n_iteraciones,
                                    k,
                                    random,
                                    logger=logger,
                                ),
                                k=k,
                                n_iteraciones=n_iteraciones,
                            )
                            print(f"Distancia total algoritmo búsqueda local: {resultado}")
                            print(f"Tiempo de ejecución: {tiempo:.6f} s")
                            print("x" * 10)
                        else:
                            print("Fallo en la lectura de fichero")
            case "tabu":
                for nombre_fichero in archivos_tsp:
                    #Carga los datos del fichero
                    ruta_archivo = os.path.join(carpeta, nombre_fichero)
                    nombre_base = os.path.splitext(os.path.basename(nombre_fichero))[0]
                    n, m_coordenadas, m_distancias, nombre, comentario = extracion_datos.extraccion_Archivo(ruta_archivo)

                    # Cada algoritmo e instancia parte de la misma semilla: la ejecución k
                    # usa la misma semilla en todos los algoritmos (lo exige el guion)
                    semilla = semilla_inicial
                    for ejecu in range(n_ejecucion):
                        #Carga de la semilla
                        n_semilla = Extraccion_parametros.permutar_semilla_circular(semilla)
                        print("---------------------La semilla es:--------------", n_semilla, "en la ejecucion", ejecu)
                        random.seed(n_semilla)
                        semilla = n_semilla
                        logger = Logs(
                            os.path.join(
                                "logs", algoritmo,
                                f"{nombre_base}_{algoritmo}_{n_semilla}_ejecucion_{ejecu + 1}.log",
                            )
                        )

                        if n is not None:
                            print(f"FICHERO PROCESADO: {nombre_fichero}")
                            print(f"Número de nodos: {n}")
                            resultado, tiempo = logger.ejecutar_y_registrar(
                                algoritmo,
                                nombre_fichero,
                                n_semilla,
                                ejecu + 1,
                                lambda: busqueda_tabu.ejecucion(
                                    m_distancias,
                                    n,
                                    n_iteraciones,
                                    k,
                                    random,
                                    tenencia,
                                    estancamiento,
                                    oscilacion,
                                    logger=logger,
                                ),
                                k=k,
                                n_iteraciones=n_iteraciones,
                                tenencia=tenencia,
                                estancamiento=estancamiento,
                                oscilacion=oscilacion,
                            )
                            print(f"Distancia total algoritmo búsqueda tabú: {resultado}")
                            print(f"Tiempo de ejecución: {tiempo:.6f} s")
                            print("x" * 10)
                        else:
                            print("Fallo en la lectura de fichero")
