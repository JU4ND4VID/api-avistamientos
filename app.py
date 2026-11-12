"""Punto de entrada: arranca la API.

    python app.py

Toda la lógica vive en el paquete `avistamientos/`. Para ver cómo se conectan
las piezas, ver avistamientos/frameworks/web_flask.py.
"""
from avistamientos.frameworks.web_flask import crear_app

if __name__ == "__main__":
    crear_app().run(debug=True)
