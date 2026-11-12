"""Pruebas de los casos de uso SIN Flask y SIN base de datos.

Es la prueba práctica de la regla de dependencia: como el caso de uso solo
conoce la interfaz del repositorio, se puede probar con uno en memoria.
"""
import pytest

from avistamientos.application.casos_de_uso import (
    ActualizarAvistamiento, EliminarAvistamiento, ListarAvistamientos,
    ObtenerAvistamiento, RegistrarAvistamiento, ResumirPorEspecie)
from avistamientos.application.dto import ResumenEspecie
from avistamientos.application.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.domain.validador import ValidadorDeAvistamiento
from dobles import RelojFijo, RepositorioEnMemoria

DATOS = {"especie": "colibrí", "lugar": "Jardín Botánico",
         "fecha": "2026-09-29", "observador": "Peña"}


@pytest.fixture
def repo():
    return RepositorioEnMemoria()


@pytest.fixture
def validador():
    return ValidadorDeAvistamiento(RelojFijo())


def test_registrar_valido_guarda_y_devuelve_con_id(repo, validador):
    creado = RegistrarAvistamiento(repo, validador).ejecutar(DATOS)
    assert creado.id == 1
    assert repo.obtener(1) == creado


def test_registrar_quita_espacios_sobrantes(repo, validador):
    creado = RegistrarAvistamiento(repo, validador).ejecutar({**DATOS, "especie": "  águila  "})
    assert creado.especie == "águila"


def test_registrar_invalido_lanza_error_y_no_guarda(repo, validador):
    with pytest.raises(DatosInvalidos) as e:
        RegistrarAvistamiento(repo, validador).ejecutar({**DATOS, "especie": "ab"})
    assert "especie" in e.value.errores
    assert repo.listar() == []


def test_obtener_inexistente_lanza_no_encontrado(repo):
    with pytest.raises(AvistamientoNoEncontrado):
        ObtenerAvistamiento(repo).ejecutar(999)


def test_actualizar_inexistente_se_reporta_antes_que_los_datos_invalidos(repo, validador):
    with pytest.raises(AvistamientoNoEncontrado):
        ActualizarAvistamiento(repo, validador).ejecutar(999, {"especie": "ab"})


def test_actualizar_valido_reemplaza_los_datos(repo, validador):
    RegistrarAvistamiento(repo, validador).ejecutar(DATOS)
    nuevo = ActualizarAvistamiento(repo, validador).ejecutar(1, {**DATOS, "lugar": "Chingaza"})
    assert nuevo.lugar == "Chingaza" and nuevo.id == 1


def test_actualizar_invalido_no_modifica(repo, validador):
    RegistrarAvistamiento(repo, validador).ejecutar(DATOS)
    with pytest.raises(DatosInvalidos):
        ActualizarAvistamiento(repo, validador).ejecutar(1, {**DATOS, "especie": "ab"})
    assert repo.obtener(1).especie == "colibrí"


def test_eliminar_existente_y_luego_inexistente(repo, validador):
    RegistrarAvistamiento(repo, validador).ejecutar(DATOS)
    EliminarAvistamiento(repo).ejecutar(1)
    assert ListarAvistamientos(repo).ejecutar() == []
    with pytest.raises(AvistamientoNoEncontrado):
        EliminarAvistamiento(repo).ejecutar(1)


def test_resumen_delega_en_el_repositorio(repo, validador):
    RegistrarAvistamiento(repo, validador).ejecutar(DATOS)
    assert ResumirPorEspecie(repo).ejecutar() == [ResumenEspecie("colibrí", 1)]
