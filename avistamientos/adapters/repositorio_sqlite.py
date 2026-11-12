"""Adaptador de persistencia: implementa el puerto RepositorioAvistamientos con SQLite.

Es el único módulo del proyecto que contiene SQL. Traduce entre filas de la
base de datos y la entidad Avistamiento: las filas nunca salen de aquí.
"""
import sqlite3
from contextlib import closing
from typing import List, Optional

from avistamientos.application.dto import ResumenEspecie
from avistamientos.application.puertos import RepositorioAvistamientos
from avistamientos.domain.avistamiento import Avistamiento


class RepositorioSqlite(RepositorioAvistamientos):
    def __init__(self, ruta_db: str):
        self.ruta_db = ruta_db

    def _conectar(self):
        conn = sqlite3.connect(self.ruta_db)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _a_entidad(fila) -> Avistamiento:
        return Avistamiento(
            id=fila["id"], especie=fila["especie"], lugar=fila["lugar"],
            fecha=fila["fecha"], observador=fila["observador"],
        )

    def crear_esquema(self) -> None:
        with closing(self._conectar()) as conn:
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

    def listar(self) -> List[Avistamiento]:
        with closing(self._conectar()) as conn:
            filas = conn.execute("SELECT * FROM avistamientos").fetchall()
        return [self._a_entidad(f) for f in filas]

    def obtener(self, id: int) -> Optional[Avistamiento]:
        with closing(self._conectar()) as conn:
            fila = conn.execute(
                "SELECT * FROM avistamientos WHERE id = ?", (id,)
            ).fetchone()
        return self._a_entidad(fila) if fila else None

    def guardar(self, a: Avistamiento) -> Avistamiento:
        with closing(self._conectar()) as conn:
            cur = conn.execute(
                "INSERT INTO avistamientos (especie, lugar, fecha, observador) "
                "VALUES (?, ?, ?, ?)",
                (a.especie, a.lugar, a.fecha, a.observador),
            )
            conn.commit()
            nuevo_id = cur.lastrowid
        return self.obtener(nuevo_id)

    def actualizar(self, a: Avistamiento) -> Avistamiento:
        with closing(self._conectar()) as conn:
            conn.execute(
                "UPDATE avistamientos "
                "SET especie = ?, lugar = ?, fecha = ?, observador = ? "
                "WHERE id = ?",
                (a.especie, a.lugar, a.fecha, a.observador, a.id),
            )
            conn.commit()
        return self.obtener(a.id)

    def eliminar(self, id: int) -> None:
        with closing(self._conectar()) as conn:
            conn.execute("DELETE FROM avistamientos WHERE id = ?", (id,))
            conn.commit()

    def resumen_por_especie(self) -> List[ResumenEspecie]:
        with closing(self._conectar()) as conn:
            filas = conn.execute(
                "SELECT especie, COUNT(*) AS total "
                "FROM avistamientos "
                "GROUP BY especie COLLATE NOCASE "
                "ORDER BY total DESC, especie"
            ).fetchall()
        return [ResumenEspecie(f["especie"], f["total"]) for f in filas]
