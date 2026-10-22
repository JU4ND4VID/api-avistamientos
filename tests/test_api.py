import pytest
import app as api

NUEVO = {
    "especie": "colibrí",
    "lugar": "Jardín Botánico",
    "fecha": "2026-09-29",
    "observador": "Peña",
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Cada prueba usa una base de datos temporal, vacía y aparte de la real
    monkeypatch.setattr(api, "DB_PATH", str(tmp_path / "test.db"))
    api.init_db()
    api.app.config["TESTING"] = True
    return api.app.test_client()


def crear(client, datos=None):
    return client.post("/avistamientos", json=datos or NUEVO)


def test_listar_vacio(client):
    r = client.get("/avistamientos")
    assert r.status_code == 200
    assert r.get_json() == []


def test_crear_devuelve_201(client):
    r = crear(client)
    assert r.status_code == 201
    assert r.get_json()["id"] == 1
    assert r.get_json()["especie"] == "colibrí"


def test_crear_incompleto_devuelve_400(client):
    r = client.post("/avistamientos", json={"especie": "colibrí"})
    assert r.status_code == 400


def test_crear_fecha_invalida_devuelve_400(client):
    r = crear(client, {**NUEVO, "fecha": "29/09/2026"})
    assert r.status_code == 400


def test_obtener_existente_devuelve_200(client):
    crear(client)
    r = client.get("/avistamientos/1")
    assert r.status_code == 200
    assert r.get_json()["lugar"] == "Jardín Botánico"


def test_obtener_inexistente_devuelve_404(client):
    assert client.get("/avistamientos/999").status_code == 404


def test_actualizar_devuelve_200(client):
    crear(client)
    r = client.put("/avistamientos/1", json={**NUEVO, "especie": "águila"})
    assert r.status_code == 200
    assert r.get_json()["especie"] == "águila"


def test_actualizar_inexistente_devuelve_404(client):
    assert client.put("/avistamientos/999", json=NUEVO).status_code == 404


def test_actualizar_incompleto_devuelve_400(client):
    crear(client)
    r = client.put("/avistamientos/1", json={"especie": "águila"})
    assert r.status_code == 400


def test_eliminar_devuelve_204_y_luego_404(client):
    crear(client)
    assert client.delete("/avistamientos/1").status_code == 204
    assert client.get("/avistamientos/1").status_code == 404


def test_eliminar_inexistente_devuelve_404(client):
    assert client.delete("/avistamientos/999").status_code == 404


def test_resumen_cuenta_por_especie(client):
    crear(client)
    crear(client)
    crear(client, {**NUEVO, "especie": "águila"})
    r = client.get("/avistamientos/resumen")
    assert r.status_code == 200
    assert r.get_json() == [
        {"especie": "colibrí", "total": 2},
        {"especie": "águila", "total": 1},
    ]