"""Verifica la Regla de Dependencia (Martin, 2012) leyendo los imports del código.

Los círculos, de adentro hacia afuera: domain -> application -> adapters -> frameworks.
Un módulo solo puede importar de su propio círculo o de uno más interno.
"""
import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent / "avistamientos"
CIRCULOS = ["domain", "application", "adapters", "frameworks"]
LIBRERIAS_DE_DETALLE = {"flask", "sqlite3", "werkzeug"}


def importaciones(archivo):
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                yield alias.name
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            yield nodo.module


def modulos(circulo):
    return sorted((RAIZ / circulo).glob("*.py"))


@pytest.mark.parametrize("circulo", CIRCULOS[:-1])
def test_ningun_circulo_importa_de_un_circulo_mas_externo(circulo):
    externos = CIRCULOS[CIRCULOS.index(circulo) + 1:]
    prohibidos = {f"avistamientos.{c}" for c in externos}
    for archivo in modulos(circulo):
        for nombre in importaciones(archivo):
            for p in prohibidos:
                assert not (nombre == p or nombre.startswith(p + ".")), (
                    f"{archivo.name} ({circulo}) importa {nombre}, que es de un círculo más externo"
                )


@pytest.mark.parametrize("circulo", ["domain", "application"])
def test_dominio_y_aplicacion_no_conocen_flask_ni_sqlite(circulo):
    for archivo in modulos(circulo):
        for nombre in importaciones(archivo):
            assert nombre.split(".")[0] not in LIBRERIAS_DE_DETALLE, (
                f"{archivo.name} ({circulo}) importa {nombre}"
            )


def test_solo_el_repositorio_sqlite_usa_sqlite():
    for circulo in CIRCULOS:
        for archivo in modulos(circulo):
            if archivo.name == "repositorio_sqlite.py":
                continue
            assert "sqlite3" not in set(importaciones(archivo)), archivo.name


def test_solo_el_circulo_de_frameworks_usa_flask():
    for circulo in CIRCULOS[:-1]:
        for archivo in modulos(circulo):
            assert "flask" not in {n.split(".")[0] for n in importaciones(archivo)}, archivo.name
