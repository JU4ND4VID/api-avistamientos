"""Círculo más externo: Flask y la composición de todas las piezas.

Aquí viven los detalles: las rutas, el JSON, el framework web. Es poco código
de "pegamento" que llama al controlador, y el único lugar que conoce las
clases concretas de todos los círculos (raíz de composición).
"""
from flask import Flask, jsonify, request

from avistamientos.adapters.controlador import ControladorAvistamientos
from avistamientos.adapters.presentador import PresentadorJson, RespuestaHttp
from avistamientos.adapters.reloj_sistema import RelojSistema
from avistamientos.adapters.repositorio_sqlite import RepositorioSqlite
from avistamientos.application.casos_de_uso import (
    ActualizarAvistamiento, EliminarAvistamiento, ListarAvistamientos,
    ObtenerAvistamiento, RegistrarAvistamiento, ResumirPorEspecie)
from avistamientos.domain.validador import ValidadorDeAvistamiento


def _armar_controlador(ruta_db: str, reloj) -> ControladorAvistamientos:
    repositorio = RepositorioSqlite(ruta_db)
    repositorio.crear_esquema()
    validador = ValidadorDeAvistamiento(reloj)
    return ControladorAvistamientos(
        listar=ListarAvistamientos(repositorio),
        obtener=ObtenerAvistamiento(repositorio),
        registrar=RegistrarAvistamiento(repositorio, validador),
        actualizar=ActualizarAvistamiento(repositorio, validador),
        eliminar=EliminarAvistamiento(repositorio),
        resumir=ResumirPorEspecie(repositorio),
        presentador=PresentadorJson(),
    )


def _responder(r: RespuestaHttp):
    if r.cuerpo is None:
        return "", r.estado
    return jsonify(r.cuerpo), r.estado


def crear_app(ruta_db: str = "avistamientos.db", reloj=None) -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False
    controlador = _armar_controlador(ruta_db, reloj or RelojSistema())

    @app.route("/")
    def inicio():
        return jsonify({"mensaje": "API de avistamientos funcionando"})

    @app.route("/avistamientos", methods=["GET"])
    def listar():
        return _responder(controlador.listar())

    @app.route("/avistamientos", methods=["POST"])
    def crear():
        return _responder(controlador.crear(request.get_json(silent=True)))

    @app.route("/avistamientos/resumen", methods=["GET"])
    def resumen():
        return _responder(controlador.resumen())

    @app.route("/avistamientos/<int:id>", methods=["GET"])
    def obtener(id):
        return _responder(controlador.obtener(id))

    @app.route("/avistamientos/<int:id>", methods=["PUT"])
    def actualizar(id):
        return _responder(controlador.actualizar(id, request.get_json(silent=True)))

    @app.route("/avistamientos/<int:id>", methods=["DELETE"])
    def eliminar(id):
        return _responder(controlador.eliminar(id))

    @app.errorhandler(404)
    def no_encontrado(e):
        return jsonify({"error": "Recurso no encontrado"}), 404

    return app
