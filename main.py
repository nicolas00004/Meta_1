import os
import extracion_datos
import numpy as np
from alg_greedy import algoritmo_greedy
from alg_greedy_aleatorio import algoritmo_greedy_aleatorizado

if __name__ == "__main__":
    carpeta = "Material de práctica 1 y 2-20260910"
    archivos_tsp = [f for f in os.listdir(carpeta) if f.endswith('.tsp')]

    dni_base = 77958591
    semillas = [
        dni_base,
        int(str(dni_base)[1:] + str(dni_base)[0]),
        int(str(dni_base)[2:] + str(dni_base)[:2])
    ]

    for nombre_fichero in archivos_tsp:
        ruta_archivo = os.path.join(carpeta, nombre_fichero)
        n, m_coordenadas, m_distancias, nombre, comentario = extracion_datos.extraccion_Archivo(ruta_archivo)

        if n is not None:
            print("=" * 60)
            print(f"PROCESANDO INSTANCIA: {nombre} ({n} nodos)")
            print("=" * 60)

            #Ejecuta Algoritmo Greedy Determinista
            sol_gre, coste_gre = algoritmo_greedy(m_distancias)
            print(f"[GREEDY DETERMINISTA] Coste: {coste_gre:.2f}")

            #Ejecuta Algoritmo Greedy Aleatorizado (3 ejecuciones con semillas)

            print("[GREEDY ALEATORIZADO (K=5)]")
            costes_gra = []
            for i, sem in enumerate(semillas, 1):
                sol_gra, coste_gra = algoritmo_greedy_aleatorizado(m_distancias, k=5, semilla=sem)
                costes_gra.append(coste_gra)
                print(f"  - Ejecución {i} (Semilla {sem}): Coste = {coste_gra:.2f}")

            print(f"  -> Media GRA: {np.mean(costes_gra):.2f} | Desv. Típica: {np.std(costes_gra):.2f}\n")