"""Controlador: recibe lo que llegó por la web (ya como datos simples), invoca
el caso de uso que corresponde y entrega el resultado al presentador.

Flujo de control: Controlador -> Caso de uso -> Presentador.
Dependencias de código: el controlador apunta hacia adentro (casos de uso).
"""
from avistamientos.adapters.presentador import PresentadorJson, RespuestaHttp
from avistamientos.application.casos_de_uso import (
    ActualizarAvistamiento, EliminarAvistamiento, ListarAvistamientos,
    ObtenerAvistamiento, RegistrarAvistamiento, ResumirPorEspecie)
from avistamientos.application.errores import AvistamientoNoEncontrado, DatosInvalidos


class ControladorAvistamientos:
    def __init__(self, listar: ListarAvistamientos, obtener: ObtenerAvistamiento,
                 registrar: RegistrarAvistamiento, actualizar: ActualizarAvistamiento,
                 eliminar: EliminarAvistamiento, resumir: ResumirPorEspecie,
                 presentador: PresentadorJson):
        self._listar = listar
        self._obtener = obtener
        self._registrar = registrar
        self._actualizar = actualizar
        self._eliminar = eliminar
        self._resumir = resumir
        self._presentador = presentador

    def listar(self) -> RespuestaHttp:
        return self._presentador.lista(self._listar.ejecutar())

    def resumen(self) -> RespuestaHttp:
        return self._presentador.resumen(self._resumir.ejecutar())

    def obtener(self, id: int) -> RespuestaHttp:
        try:
            return self._presentador.avistamiento(self._obtener.ejecutar(id))
        except AvistamientoNoEncontrado:
            return self._presentador.no_encontrado()

    def crear(self, datos) -> RespuestaHttp:
        try:
            return self._presentador.avistamiento(self._registrar.ejecutar(datos), 201)
        except DatosInvalidos as e:
            return self._presentador.datos_invalidos(e.errores)

    def actualizar(self, id: int, datos) -> RespuestaHttp:
        try:
            return self._presentador.avistamiento(self._actualizar.ejecutar(id, datos))
        except AvistamientoNoEncontrado:
            return self._presentador.no_encontrado()
        except DatosInvalidos as e:
            return self._presentador.datos_invalidos(e.errores)

    def eliminar(self, id: int) -> RespuestaHttp:
        try:
            self._eliminar.ejecutar(id)
            return self._presentador.sin_contenido()
        except AvistamientoNoEncontrado:
            return self._presentador.no_encontrado()
