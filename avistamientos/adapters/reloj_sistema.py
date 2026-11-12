"""Adaptador: implementación real del puerto `Reloj` con el reloj del computador."""
from datetime import date

from avistamientos.domain.validador import Reloj


class RelojSistema(Reloj):
    def hoy(self) -> date:
        return date.today()
