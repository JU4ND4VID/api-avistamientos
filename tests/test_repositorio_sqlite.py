"""Pruebas de integración del adaptador SQLite contra una base temporal."""
import pytest

from avistamientos.adapters.repositorio_sqlite import RepositorioSqlite
from avistamientos.application.dto import ResumenEspecie
from avistamientos.domain.avistamiento import Avistamiento


@pytest.fixture
def repo(tmp_path):
    r = RepositorioSqlite(str(tmp_path / "test.db"))
    r.crear_esquema()
    return r


def nuevo(especie="colibrí"):
    return Avistamiento(especie, "Jardín Botánico", "2026-09-29", "Peña")


def test_guardar_asigna_id_y_obtener_lo_devuelve(repo):
    guardado = repo.guardar(nuevo())
    assert guardado.id == 1
    assert repo.obtener(1) == guardado


def test_obtener_inexistente_devuelve_none(repo):
    assert repo.obtener(999) is None


def test_actualizar_y_eliminar(repo):
    repo.guardar(nuevo())
    cambiado = repo.actualizar(Avistamiento("águila", "Chingaza", "2026-09-29", "Peña", 1))
    assert cambiado.especie == "águila"
    repo.eliminar(1)
    assert repo.listar() == []


def test_resumen_agrupa_sin_distinguir_mayusculas_y_ordena(repo):
    repo.guardar(nuevo("colibrí"))
    repo.guardar(nuevo("Colibrí"))
    repo.guardar(nuevo("águila"))
    resumen = repo.resumen_por_especie()
    assert [r.total for r in resumen] == [2, 1]
    assert resumen[1] == ResumenEspecie("águila", 1)


def test_crear_esquema_es_idempotente(repo):
    repo.guardar(nuevo())
    repo.crear_esquema()
    assert len(repo.listar()) == 1
