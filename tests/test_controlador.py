"""Pruebas del controlador y el presentador SIN Flask: devuelven RespuestaHttp."""
import pytest

from avistamientos.adapters.controlador import ControladorAvistamientos
from avistamientos.adapters.presentador import PresentadorJson
from avistamientos.application.casos_de_uso import (
    ActualizarAvistamiento, EliminarAvistamiento, ListarAvistamientos,
    ObtenerAvistamiento, RegistrarAvistamiento, ResumirPorEspecie)
from avistamientos.domain.validador import ValidadorDeAvistamiento
from dobles import RelojFijo, RepositorioEnMemoria

DATOS = {"especie": "colibrí", "lugar": "Jardín Botánico",
         "fecha": "2026-09-29", "observador": "Peña"}


@pytest.fixture
def controlador():
    repo = RepositorioEnMemoria()
    val = ValidadorDeAvistamiento(RelojFijo())
    return ControladorAvistamientos(
        ListarAvistamientos(repo), ObtenerAvistamiento(repo),
        RegistrarAvistamiento(repo, val), ActualizarAvistamiento(repo, val),
        EliminarAvistamiento(repo), ResumirPorEspecie(repo), PresentadorJson())


def test_crear_valido_responde_201_con_id(controlador):
    r = controlador.crear(DATOS)
    assert r.estado == 201
    assert r.cuerpo["id"] == 1 and r.cuerpo["especie"] == "colibrí"


def test_crear_invalido_responde_400_con_detalles(controlador):
    r = controlador.crear({**DATOS, "especie": "ab"})
    assert r.estado == 400
    assert r.cuerpo["error"] == "Datos inválidos en: especie"
    assert "especie" in r.cuerpo["detalles"]


def test_obtener_inexistente_responde_404(controlador):
    r = controlador.obtener(999)
    assert (r.estado, r.cuerpo) == (404, {"error": "Avistamiento no encontrado"})


def test_eliminar_responde_204_sin_cuerpo_y_luego_404(controlador):
    controlador.crear(DATOS)
    r = controlador.eliminar(1)
    assert (r.estado, r.cuerpo) == (204, None)
    assert controlador.eliminar(1).estado == 404


def test_actualizar_inexistente_responde_404_aunque_los_datos_sean_invalidos(controlador):
    assert controlador.actualizar(999, {"especie": "ab"}).estado == 404


def test_listar_y_resumen_devuelven_listas_de_diccionarios(controlador):
    controlador.crear(DATOS)
    assert controlador.listar().cuerpo[0]["lugar"] == "Jardín Botánico"
    assert controlador.resumen().cuerpo == [{"especie": "colibrí", "total": 1}]
