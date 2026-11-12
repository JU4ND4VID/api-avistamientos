"""Dobles de prueba compartidos: un reloj fijo y un repositorio en memoria."""
from datetime import date

from avistamientos.application.dto import ResumenEspecie
from avistamientos.application.puertos import RepositorioAvistamientos
from avistamientos.domain.avistamiento import Avistamiento
from avistamientos.domain.validador import Reloj


class RelojFijo(Reloj):
    def hoy(self):
        return date(2026, 10, 21)


class RepositorioEnMemoria(RepositorioAvistamientos):
    """Fake: guarda en un diccionario en vez de SQLite."""

    def __init__(self):
        self.datos = {}
        self.siguiente = 1

    def listar(self):
        return list(self.datos.values())

    def obtener(self, id):
        return self.datos.get(id)

    def guardar(self, a):
        guardado = Avistamiento(a.especie, a.lugar, a.fecha, a.observador, self.siguiente)
        self.datos[self.siguiente] = guardado
        self.siguiente += 1
        return guardado

    def actualizar(self, a):
        self.datos[a.id] = a
        return a

    def eliminar(self, id):
        del self.datos[id]

    def resumen_por_especie(self):
        cuenta = {}
        for a in self.datos.values():
            cuenta[a.especie] = cuenta.get(a.especie, 0) + 1
        return [ResumenEspecie(e, t) for e, t in cuenta.items()]
