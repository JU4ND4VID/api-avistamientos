"""Entidad Avistamiento (círculo de entidades)."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Avistamiento:
    especie: str
    lugar: str
    fecha: str  # texto AAAA-MM-DD
    observador: str
    id: Optional[int] = None  # lo asigna el sistema al guardar

    @classmethod
    def desde_datos(cls, datos: dict, id: Optional[int] = None) -> "Avistamiento":
        """Crea un avistamiento a partir de datos ya validados, sin espacios sobrantes."""
        return cls(
            especie=datos["especie"].strip(),
            lugar=datos["lugar"].strip(),
            fecha=datos["fecha"],
            observador=datos["observador"].strip(),
            id=id,
        )
