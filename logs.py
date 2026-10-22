from datetime import datetime
from pathlib import Path
import time


class Logs:
    def __init__(self, archivo):
        self.archivo = Path(archivo)
        self._tiempo_escritura = 0.0
        self._movimientos_pendientes = []
        self._datos_resumen = {}
        self._resumen_busqueda_local = {}
        self.archivo.parent.mkdir(parents=True, exist_ok=True)
        if not self.archivo.exists() or self.archivo.stat().st_size == 0:
            self.log(f"--- Log iniciado el {self._obtener_tiempo()} ---", "SETUP")

    @staticmethod
    def _obtener_tiempo():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log(self, mensaje, nivel="INFO"):
        self._vaciar_movimientos()
        linea = f"[{self._obtener_tiempo()}] [{nivel}] {mensaje}\n"
        self._escribir_lineas([linea])

    def _escribir_lineas(self, lineas):
        if not lineas:
            return
        inicio = time.perf_counter()
        try:
            with self.archivo.open("a", encoding="utf-8") as archivo:
                archivo.writelines(lineas)
        finally:
            self._tiempo_escritura += time.perf_counter() - inicio

    def _vaciar_movimientos(self):
        if self._movimientos_pendientes:
            movimientos = self._movimientos_pendientes
            self._movimientos_pendientes = []
            self._escribir_lineas(movimientos)

    def log_parametros(self, nombre_algoritmo, fichero, semilla, **kwargs):
        self._datos_resumen = {
            "Algoritmo": nombre_algoritmo,
            "Fichero": fichero,
            "Semilla": semilla,
            **kwargs,
        }
        self.log(
            f"Comenzando ejecución del fichero: {fichero} "
            f"con el algoritmo: {nombre_algoritmo}",
            "SETUP",
        )
        self.log(f"Semilla: {semilla}", "SETUP")
        for clave, valor in kwargs.items():
            self.log(f"{clave}: {valor}", "SETUP")

    def log_resultado(self, nombre_algoritmo, fichero, resultado, tiempo_total):
        self.log(
            f"Algoritmo: {nombre_algoritmo}; fichero: {fichero}; "
            f"resultado: {resultado}; tiempo: {tiempo_total:.6f} s",
            "RESULT",
        )
        self.log("=== RESUMEN DE LA EJECUCIÓN ===", "SUMMARY")
        resumen = {
            **self._datos_resumen,
            "Resultado": resultado,
            "Tiempo de ejecución (s)": f"{tiempo_total:.6f}",
            **self._resumen_busqueda_local,
        }
        for clave, valor in resumen.items():
            self.log(f"{clave}: {valor}", "SUMMARY")
        self.log("=== FIN DE EJECUCIÓN ===", "RESULT")

    @staticmethod
    def _formatear_vector_bits(vector_bits):
        return "".join(str(bit) for bit in vector_bits)

    def log_inicio_busqueda_local(self, solucion, coste, vector_bits):
        self._vaciar_movimientos()
        self.log_solucion_inicial(solucion, coste)
        self.log(
            f"Vector de bits inicial: {self._formatear_vector_bits(vector_bits)}",
            "INIT",
        )

    def log_movimiento_busqueda_local(
        self,
        iteracion,
        pos_i,
        pos_j,
        solucion,
        coste_anterior,
        coste_actual,
        vector_bits,
    ):
        self._movimientos_pendientes.append(
            f"[{self._obtener_tiempo()}] [MOVE] Iteración {iteracion}: "
            f"intercambio ({pos_i}, {pos_j}) — MEJORA\n"
            f"[{self._obtener_tiempo()}] [MOVE] Solución: {solucion}\n"
            f"[{self._obtener_tiempo()}] [MOVE] Coste anterior: {coste_anterior}\n"
            f"[{self._obtener_tiempo()}] [MOVE] Coste nuevo: {coste_actual}\n"
            f"[{self._obtener_tiempo()}] [MOVE] Vector de bits: "
            f"{self._formatear_vector_bits(vector_bits)}\n"
            f"[{self._obtener_tiempo()}] [MOVE] ---\n"
        )
        if len(self._movimientos_pendientes) >= 100:
            self._vaciar_movimientos()

    def log_fallo_intercambio_busqueda_local(self, posicion, vector_bits):
        self._movimientos_pendientes.append(
            f"[{self._obtener_tiempo()}] [MOVE] Sin mejora para la posición "
            f"{posicion}; bit: 0->1\n"
            f"[{self._obtener_tiempo()}] [MOVE] Vector de bits: "
            f"{self._formatear_vector_bits(vector_bits)}\n"
            f"[{self._obtener_tiempo()}] [MOVE] ---\n"
        )
        if len(self._movimientos_pendientes) >= 100:
            self._vaciar_movimientos()

    def log_fin_busqueda_local(
        self, solucion, coste, movimientos, motivo, vector_bits
    ):
        self._resumen_busqueda_local = {
            "Movimientos realizados": movimientos,
            "Motivo de finalización": motivo,
            "Coste final": coste,
        }
        self._vaciar_movimientos()
        self.log(
            f"Búsqueda local finalizada: {motivo}; movimientos: {movimientos}",
            "RESULT",
        )
        self.log("Solución final:", "RESULT")
        self.log(f"  {solucion}", "RESULT")
        self.log(f"Coste final: {coste}", "RESULT")
        self.log(
            f"Vector de bits final: {self._formatear_vector_bits(vector_bits)}",
            "RESULT",
        )

    def ejecutar_y_registrar(
        self, algoritmo, fichero, semilla, numero_ejecucion, funcion, **parametros
    ):
        self.log_parametros(
            algoritmo,
            fichero,
            semilla,
            ejecucion=numero_ejecucion,
            **parametros,
        )
        inicio = time.perf_counter()
        tiempo_escritura_inicio = self._tiempo_escritura
        try:
            resultado = funcion()
        finally:
            self._vaciar_movimientos()
        tiempo_total = max(
            0.0,
            time.perf_counter()
            - inicio
            - (self._tiempo_escritura - tiempo_escritura_inicio),
        )
        self.log_resultado(algoritmo, fichero, resultado, tiempo_total)
        return resultado, tiempo_total

    def log_solucion_inicial(self, solucion, coste):
        self.log(f"Solución inicial: {solucion}", "INIT")
        self.log(f"Coste inicial: {coste}", "INIT")
        self.log("---", "INIT")

    def log_solucion_final(self, solucion, coste, tiempo_total):
        self.log("Solución final:", "RESULT")
        self.log(f"  {solucion}", "RESULT")
        self.log(f"Coste final: {coste}", "RESULT")
        self.log(f"Tiempo total: {tiempo_total:.3f} s", "RESULT")
        self.log("=== FIN DE EJECUCIÓN ===", "RESULT")

    def log_movimiento(self, iteracion, pos_i, pos_j, solucion, coste, es_mejora):
        if pos_i == -1 and pos_j == -1:
            mensaje = f"Iteración {iteracion}: Movimiento al mejor vecino (DLB completo)"
        else:
            mensaje = f"Iteración {iteracion}: Intercambio pos [{pos_i} ↔ {pos_j}]"

        if es_mejora:
            mensaje += " ✓ NUEVA MEJOR SOLUCIÓN"

        self.log(mensaje, "TABU")
        self.log(f"  Solución: {solucion}", "TABU")
        self.log(f"  Coste: {coste}", "TABU")
