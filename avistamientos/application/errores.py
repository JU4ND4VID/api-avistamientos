"""Errores de la aplicación: lo que un caso de uso avisa sin saber de HTTP."""


class DatosInvalidos(Exception):
    def __init__(self, errores: dict):
        super().__init__(", ".join(errores))
        self.errores = errores


class AvistamientoNoEncontrado(Exception):
    def __init__(self, id: int):
        super().__init__(f"No existe el avistamiento {id}")
        self.id = id
