"""Casos de uso: las reglas propias de esta aplicación.

Cada uno recibe sus dependencias (repositorio, validador) por el constructor
y solo conoce interfaces. No sabe si lo llama Flask, una prueba o un script,
ni si los datos terminan en SQLite o en una lista en memoria.
"""
from typing import List

from avistamientos.application.dto import ResumenEspecie
from avistamientos.application.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.application.puertos import RepositorioAvistamientos
from avistamientos.domain.avistamiento import Avistamiento
from avistamientos.domain.validador import ValidadorDeAvistamiento


class ListarAvistamientos:
    def __init__(self, repositorio: RepositorioAvistamientos):
        self.repositorio = repositorio

    def ejecutar(self) -> List[Avistamiento]:
        return self.repositorio.listar()


class ObtenerAvistamiento:
    def __init__(self, repositorio: RepositorioAvistamientos):
        self.repositorio = repositorio

    def ejecutar(self, id: int) -> Avistamiento:
        encontrado = self.repositorio.obtener(id)
        if encontrado is None:
            raise AvistamientoNoEncontrado(id)
        return encontrado


class RegistrarAvistamiento:
    def __init__(self, repositorio: RepositorioAvistamientos,
                 validador: ValidadorDeAvistamiento):
        self.repositorio = repositorio
        self.validador = validador

    def ejecutar(self, datos) -> Avistamiento:
        errores = self.validador.validar(datos)
        if errores:
            raise DatosInvalidos(errores)
        return self.repositorio.guardar(Avistamiento.desde_datos(datos))


class ActualizarAvistamiento:
    def __init__(self, repositorio: RepositorioAvistamientos,
                 validador: ValidadorDeAvistamiento):
        self.repositorio = repositorio
        self.validador = validador

    def ejecutar(self, id: int, datos) -> Avistamiento:
        # Primero se comprueba que exista (404) y luego los datos (400),
        # igual que hacía la API antes del refactor.
        if self.repositorio.obtener(id) is None:
            raise AvistamientoNoEncontrado(id)
        errores = self.validador.validar(datos)
        if errores:
            raise DatosInvalidos(errores)
        return self.repositorio.actualizar(Avistamiento.desde_datos(datos, id=id))


class EliminarAvistamiento:
    def __init__(self, repositorio: RepositorioAvistamientos):
        self.repositorio = repositorio

    def ejecutar(self, id: int) -> None:
        if self.repositorio.obtener(id) is None:
            raise AvistamientoNoEncontrado(id)
        self.repositorio.eliminar(id)


class ResumirPorEspecie:
    def __init__(self, repositorio: RepositorioAvistamientos):
        self.repositorio = repositorio

    def ejecutar(self) -> List[ResumenEspecie]:
        return self.repositorio.resumen_por_especie()
