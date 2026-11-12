"""Presentador: convierte los resultados de los casos de uso en respuestas HTTP.

Devuelve una `RespuestaHttp` (estado + cuerpo en tipos simples de Python).
Quien finalmente la envía por la red es el framework web, en el círculo
exterior; aquí no se importa Flask.
"""
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from avistamientos.application.dto import ResumenEspecie
from avistamientos.domain.avistamiento import Avistamiento


@dataclass(frozen=True)
class RespuestaHttp:
    estado: int
    cuerpo: Any = None  # None = respuesta sin cuerpo (por ejemplo, 204)


class PresentadorJson:
    def avistamiento(self, a: Avistamiento, estado: int = 200) -> RespuestaHttp:
        return RespuestaHttp(estado, asdict(a))

    def lista(self, avistamientos: Iterable[Avistamiento]) -> RespuestaHttp:
        return RespuestaHttp(200, [asdict(a) for a in avistamientos])

    def resumen(self, filas: Iterable[ResumenEspecie]) -> RespuestaHttp:
        return RespuestaHttp(200, [asdict(f) for f in filas])

    def sin_contenido(self) -> RespuestaHttp:
        return RespuestaHttp(204)

    def no_encontrado(self) -> RespuestaHttp:
        return RespuestaHttp(404, {"error": "Avistamiento no encontrado"})

    def datos_invalidos(self, errores: dict) -> RespuestaHttp:
        campos = ", ".join(errores)
        return RespuestaHttp(
            400, {"error": f"Datos inválidos en: {campos}", "detalles": errores}
        )
