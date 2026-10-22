import re
from datetime import date, datetime

ESPECIE_MIN = 3
ESPECIE_MAX = 50
FORMATO_FECHA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class Reloj:
    """Interfaz: quien la implemente dice qué día es hoy."""

    def hoy(self) -> date:
        raise NotImplementedError


class RelojSistema(Reloj):
    """Implementación real: usa el reloj del computador."""

    def hoy(self) -> date:
        return date.today()


class ValidadorDeAvistamiento:
    def __init__(self, reloj=None):
        self.reloj = reloj or RelojSistema()

    def validar(self, datos):
        """Devuelve un dict {campo: mensaje}. Vacío si los datos son válidos."""
        if not isinstance(datos, dict):
            return {"cuerpo": "debe ser un objeto JSON"}

        errores = {}
        self._especie(datos.get("especie"), errores)
        self._fecha(datos.get("fecha"), errores)
        self._no_vacio("lugar", datos.get("lugar"), errores)
        self._no_vacio("observador", datos.get("observador"), errores)
        return errores

    def _especie(self, valor, errores):
        if not isinstance(valor, str) or not (
            ESPECIE_MIN <= len(valor.strip()) <= ESPECIE_MAX
        ):
            errores["especie"] = (
                f"debe ser texto de {ESPECIE_MIN} a {ESPECIE_MAX} caracteres"
            )

    def _fecha(self, valor, errores):
        if not isinstance(valor, str) or not FORMATO_FECHA.fullmatch(valor):
            errores["fecha"] = "debe tener el formato AAAA-MM-DD"
            return
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            errores["fecha"] = "no es una fecha real (revise mes y día)"
            return
        if fecha > self.reloj.hoy():
            errores["fecha"] = "no puede ser posterior a hoy"

    def _no_vacio(self, campo, valor, errores):
        if not isinstance(valor, str) or not valor.strip():
            errores[campo] = "no puede estar vacío"