import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False
DB_PATH = "avistamientos.db"
CAMPOS = ["especie", "lugar", "fecha", "observador"]


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


def validar(datos):
    """Devuelve un mensaje de error, o None si los datos son válidos."""
    if not isinstance(datos, dict):
        return "El cuerpo debe ser un objeto JSON"
    faltan = [c for c in CAMPOS
              if not isinstance(datos.get(c), str) or not datos[c].strip()]
    if faltan:
        return "Faltan datos o son inválidos: " + ", ".join(faltan)
    try:
        datetime.strptime(datos["fecha"], "%Y-%m-%d")
    except ValueError:
        return "La fecha debe tener el formato AAAA-MM-DD"
    return None


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
    error = validar(datos)
    if error:
        return jsonify({"error": error}), 400

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO avistamientos (especie, lugar, fecha, observador) "
        "VALUES (?, ?, ?, ?)",
        (datos["especie"].strip(), datos["lugar"].strip(),
         datos["fecha"], datos["observador"].strip()),
    )
    conn.commit()
    fila = conn.execute(
        "SELECT * FROM avistamientos WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
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


@app.errorhandler(404)
def no_encontrado(e):
    return jsonify({"error": "Recurso no encontrado"}), 404

def buscar(conn, id):
    return conn.execute(
        "SELECT * FROM avistamientos WHERE id = ?", (id,)
    ).fetchone()


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

    error = validar(datos)
    if error:
        conn.close()
        return jsonify({"error": error}), 400

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

if __name__ == "__main__":
    init_db()
    app.run(debug=True)