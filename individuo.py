import Funcion_evaluacion


class Individuo:

    def __init__(self, asignacion):
        # self.asignacion (list[int]): recorrido, orden en que se visitan las ciudades.
        self.asignacion = asignacion

        # self.evaluado (bool): True si el individuo ya ha sido evaluado, False en caso contrario.
        self.evaluado = False

        # self.coste (float | None): Almacena el coste (longitud del recorrido) del individuo.
        # Es None hasta que se calcula por primera vez.
        self.coste = None
        self.elite = False
        self.generacion = 0

    def evaluar(self, matriz_distancias):
        """
            Calcula el coste del recorrido si no ha sido evaluado previamente.
            Devuelve el coste y el número de evaluaciones gastadas (0 o 1).
        """
        if self.evaluado:
            return self.coste, 0
        self.coste = Funcion_evaluacion.evaluar(matriz_distancias, self.asignacion)
        self.evaluado = True
        return self.coste, 1

    def copia(self):
        """
            Devuelve un individuo nuevo con la misma asignación y el mismo coste,
            para que mutar la copia no modifique al original.
        """
        nuevo = Individuo(self.asignacion.copy())
        nuevo.evaluado = self.evaluado
        nuevo.coste = self.coste
        nuevo.elite = self.elite
        nuevo.generacion = self.generacion
        return nuevo
