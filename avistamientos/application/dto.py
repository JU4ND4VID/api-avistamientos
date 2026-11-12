"""Estructuras de datos simples que cruzan los límites entre círculos."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ResumenEspecie:
    especie: str
    total: int
