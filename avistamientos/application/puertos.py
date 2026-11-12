"""Puertos de salida: lo que los casos de uso necesitan del mundo exterior.

Las interfaces viven aquí, en el círculo de aplicación. Las implementa un
círculo exterior (adapters/), de modo que el código apunta hacia adentro.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from avistamientos.application.dto import ResumenEspecie
from avistamientos.domain.avistamiento import Avistamiento


class RepositorioAvistamientos(ABC):
    @abstractmethod
    def listar(self) -> List[Avistamiento]: ...

    @abstractmethod
    def obtener(self, id: int) -> Optional[Avistamiento]: ...

    @abstractmethod
    def guardar(self, avistamiento: Avistamiento) -> Avistamiento:
        """Guarda uno nuevo y lo devuelve con el id asignado."""

    @abstractmethod
    def actualizar(self, avistamiento: Avistamiento) -> Avistamiento: ...

    @abstractmethod
    def eliminar(self, id: int) -> None: ...

    @abstractmethod
    def resumen_por_especie(self) -> List[ResumenEspecie]: ...
