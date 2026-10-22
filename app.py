import sqlite3
from flask import Flask, jsonify, request
from validador import ValidadorDeAvistamiento

app = Flask(__name__)
app.json.ensure_ascii = False
DB_PATH = "avistamientos.db"
validador = ValidadorDeAvistamiento()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS avistamientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            especie TEXT NOT NULL,
            lugar TEXT NOT NULL,
            fecha TEXT NOT NULL,
            observador TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def buscar(conn, id):
    return conn.execute(
        "SELECT * FROM avistamientos WHERE id = ?", (id,)
    ).fetchone()


def error_validacion(errores):
    campos = ", ".join(errores)
    return jsonify({
        "error": f"Datos inválidos en: {campos}",
        "detalles": errores,
    }), 400


@app.route("/")
def inicio():
    return jsonify({"mensaje": "API de avistamientos funcionando"})


@app.route("/avistamientos", methods=["GET"])
def listar():
    conn = get_db()
    filas = conn.execute("SELECT * FROM avistamientos").fetchall()
    conn.close()
    return jsonify([dict(f) for f in filas]), 200


@app.route("/avistamientos", methods=["POST"])
def crear():
    datos = request.get_json(silent=True)
    errores = validador.validar(datos)
    if errores:
        return error_validacion(errores)

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO avistamientos (especie, lugar, fecha, observador) "
        "VALUES (?, ?, ?, ?)",
        (datos["especie"].strip(), datos["lugar"].strip(),
         datos["fecha"], datos["observador"].strip()),
    )
    conn.commit()
    fila = buscar(conn, cur.lastrowid)
    conn.close()
    return jsonify(dict(fila)), 201


@app.route("/avistamientos/resumen", methods=["GET"])
def resumen():
    conn = get_db()
    filas = conn.execute(
        "SELECT especie, COUNT(*) AS total "
        "FROM avistamientos "
        "GROUP BY especie COLLATE NOCASE "
        "ORDER BY total DESC, especie"
    ).fetchall()
    conn.close()
    return jsonify([dict(f) for f in filas]), 200


@app.route("/avistamientos/<int:id>", methods=["GET"])
def obtener(id):
    conn = get_db()
    fila = buscar(conn, id)
    conn.close()
    if fila is None:
        return jsonify({"error": "Avistamiento no encontrado"}), 404
    return jsonify(dict(fila)), 200


@app.route("/avistamientos/<int:id>", methods=["PUT"])
def actualizar(id):
    datos = request.get_json(silent=True)
    conn = get_db()
    if buscar(conn, id) is None:
        conn.close()
        return jsonify({"error": "Avistamiento no encontrado"}), 404

    errores = validador.validar(datos)
    if errores:
        conn.close()
        return error_validacion(errores)

    conn.execute(
        "UPDATE avistamientos "
        "SET especie = ?, lugar = ?, fecha = ?, observador = ? "
        "WHERE id = ?",
        (datos["especie"].strip(), datos["lugar"].strip(),
         datos["fecha"], datos["observador"].strip(), id),
    )
    conn.commit()
    fila = buscar(conn, id)
    conn.close()
    return jsonify(dict(fila)), 200


@app.route("/avistamientos/<int:id>", methods=["DELETE"])
def eliminar(id):
    conn = get_db()
    if buscar(conn, id) is None:
        conn.close()
        return jsonify({"error": "Avistamiento no encontrado"}), 404

    conn.execute("DELETE FROM avistamientos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return "", 204


@app.errorhandler(404)
def no_encontrado(e):
    return jsonify({"error": "Recurso no encontrado"}), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)