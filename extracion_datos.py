import math
import numpy as np


def extraccion_Archivo(nombre_archivo):
    try:
        coordenadas = []
        n = 0
        nombre = ""
        comentario = ""
        leyendo_coordenadas = False

        # 1. Lectura del archivo y extracción de datos
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                linea = linea.strip()

                if not linea or linea == "EOF":
                    continue
                if linea.startswith("NAME"):
                    nombre = linea.split(":")[-1].strip()
                    continue
                if linea.startswith("COMMENT"):
                    comentario = linea.split(":")[-1].strip()
                    continue
                if linea.startswith("DIMENSION"):
                    n = int(linea.split(":")[-1].strip())
                    continue

                if linea == "NODE_COORD_SECTION":
                    leyendo_coordenadas = True
                    continue

                if leyendo_coordenadas:
                    partes = linea.split()
                    if len(partes) >= 3:
                        x = float(partes[1])
                        y = float(partes[2])
                        coordenadas.append((x, y))


        m_coordenadas = np.array(coordenadas, dtype=np.float32)
        diff = m_coordenadas[:, None, :] - m_coordenadas[None, :, :]
        m_distancias = np.sqrt((diff ** 2).sum(axis=2)).astype(np.float32)

        return n, m_coordenadas, m_distancias, nombre, comentario

    except FileNotFoundError:
        print("Error: El fichero no existe.")
        return None, None, None, None, None
    except Exception as e:
        print(f"Error al procesar el fichero: {e}")
        return None, None, None, None, None