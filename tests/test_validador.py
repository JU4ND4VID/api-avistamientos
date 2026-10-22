from datetime import date

import pytest

from validador import Reloj, ValidadorDeAvistamiento

HOY = date(2026, 10, 21)


class RelojFijo(Reloj):
    """Stub: siempre responde la misma fecha, sin importar el día real."""

    def __init__(self, hoy):
        self._hoy = hoy

    def hoy(self):
        return self._hoy


@pytest.fixture
def validador():
    return ValidadorDeAvistamiento(RelojFijo(HOY))


def datos_validos(**cambios):
    datos = {
        "especie": "colibrí",
        "lugar": "Jardín Botánico",
        "fecha": "2026-10-01",
        "observador": "Peña",
    }
    datos.update(cambios)
    return datos


def test_datos_completos_y_correctos_no_producen_errores(validador):
    # Arrange
    datos = datos_validos()
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


# ---- Especie: límites 2/3 y 50/51 ----

def test_especie_de_2_caracteres_se_rechaza(validador):
    # Arrange
    datos = datos_validos(especie="ab")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "especie" in errores


def test_especie_de_3_caracteres_se_acepta(validador):
    # Arrange
    datos = datos_validos(especie="abc")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


def test_especie_de_50_caracteres_se_acepta(validador):
    # Arrange
    datos = datos_validos(especie="a" * 50)
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


def test_especie_de_51_caracteres_se_rechaza(validador):
    # Arrange
    datos = datos_validos(especie="a" * 51)
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "especie" in errores


def test_especie_de_solo_espacios_se_rechaza(validador):
    # Arrange
    datos = datos_validos(especie="     ")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "especie" in errores


def test_especie_que_no_es_texto_se_rechaza(validador):
    # Arrange
    datos = datos_validos(especie=123)
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "especie" in errores


# ---- Fecha: hoy / mañana, formato y fecha inexistente ----

def test_fecha_de_hoy_se_acepta(validador):
    # Arrange
    datos = datos_validos(fecha="2026-10-21")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


def test_fecha_de_manana_se_rechaza(validador):
    # Arrange
    datos = datos_validos(fecha="2026-10-22")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "fecha" in errores


def test_fecha_con_formato_incorrecto_se_rechaza(validador):
    # Arrange
    datos = datos_validos(fecha="21/10/2026")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "fecha" in errores


def test_fecha_que_no_existe_se_rechaza(validador):
    # Arrange
    datos = datos_validos(fecha="2026-02-30")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "fecha" in errores


# ---- Lugar y observador ----

def test_lugar_vacio_se_rechaza(validador):
    # Arrange
    datos = datos_validos(lugar="")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "lugar" in errores


def test_observador_vacio_se_rechaza(validador):
    # Arrange
    datos = datos_validos(observador="")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "observador" in errores


# ---- Cuerpo y varios errores a la vez ----

def test_cuerpo_que_no_es_un_objeto_se_rechaza(validador):
    # Arrange
    datos = "no soy un objeto"
    # Act
    errores = validador.validar(datos)
    # Assert
    assert "cuerpo" in errores


def test_reporta_todos_los_campos_que_fallan(validador):
    # Arrange
    datos = {"especie": "ab", "lugar": "", "fecha": "2026-10-22", "observador": ""}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"especie", "lugar", "fecha", "observador"}