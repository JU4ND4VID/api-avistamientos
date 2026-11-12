"""Imprime una muestra determinista de las respuestas de la API.

Sirve para comprobar que la API responde igual antes y después del refactor:
se ejecuta en cada versión y se comparan las salidas con `diff`.

Uso:  python scripts/muestra_api.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NUEVO = {"especie": "colibrí", "lugar": "Jardín Botánico",
         "fecha": "2026-09-29", "observador": "Peña"}


def crear_cliente():
    ruta_db = os.path.join(tempfile.mkdtemp(), "muestra.db")
    import app as api

    if hasattr(api, "crear_app"):          # versión con arquitectura nueva
        return api.crear_app(ruta_db).test_client()
    api.DB_PATH = ruta_db                   # versión original (monolito)
    api.init_db()
    return api.app.test_client()


def mostrar(titulo, respuesta):
    cuerpo = respuesta.get_data(as_text=True).strip()
    if respuesta.is_json:
        cuerpo = json.dumps(respuesta.get_json(), ensure_ascii=False, sort_keys=True)
    print(f"{titulo}\n  -> {respuesta.status_code} {cuerpo}")


def main():
    c = crear_cliente()
    mostrar("GET /", c.get("/"))
    mostrar("GET /avistamientos (vacío)", c.get("/avistamientos"))
    mostrar("POST /avistamientos (válido)", c.post("/avistamientos", json=NUEVO))
    mostrar("POST /avistamientos (válido, otra especie)",
            c.post("/avistamientos", json={**NUEVO, "especie": "  águila  "}))
    mostrar("POST /avistamientos (colibrí otra vez)", c.post("/avistamientos", json=NUEVO))
    mostrar("POST /avistamientos (incompleto)", c.post("/avistamientos", json={"especie": "colibrí"}))
    mostrar("POST /avistamientos (fecha futura)",
            c.post("/avistamientos", json={**NUEVO, "fecha": "2999-01-01"}))
    mostrar("POST /avistamientos (fecha irreal)",
            c.post("/avistamientos", json={**NUEVO, "fecha": "2026-13-45"}))
    mostrar("POST /avistamientos (cuerpo no JSON)",
            c.post("/avistamientos", data="hola", content_type="text/plain"))
    mostrar("GET /avistamientos", c.get("/avistamientos"))
    mostrar("GET /avistamientos/1", c.get("/avistamientos/1"))
    mostrar("GET /avistamientos/999", c.get("/avistamientos/999"))
    mostrar("GET /avistamientos/abc", c.get("/avistamientos/abc"))
    mostrar("PUT /avistamientos/1 (válido)",
            c.put("/avistamientos/1", json={**NUEVO, "lugar": "Chingaza"}))
    mostrar("PUT /avistamientos/1 (inválido)",
            c.put("/avistamientos/1", json={**NUEVO, "especie": "ab"}))
    mostrar("PUT /avistamientos/999 (inexistente, cuerpo inválido)",
            c.put("/avistamientos/999", json={"especie": "ab"}))
    mostrar("GET /avistamientos/resumen", c.get("/avistamientos/resumen"))
    mostrar("DELETE /avistamientos/2", c.delete("/avistamientos/2"))
    mostrar("DELETE /avistamientos/2 (otra vez)", c.delete("/avistamientos/2"))
    mostrar("GET /ruta-que-no-existe", c.get("/ruta-que-no-existe"))


if __name__ == "__main__":
    main()
