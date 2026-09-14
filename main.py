import os
import extracion_datos

if __name__ == "__main__":
    carpeta = "Material de práctica 1 y 2-20260910"

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
            print("=" * 50 + "\n")
        else:
            print(f"Error al cargar el archivo {nombre_fichero}\n")