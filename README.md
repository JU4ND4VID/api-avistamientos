# API de avistamientos de aves

API REST para registrar avistamientos de aves. Trabajo en clase de Ingeniería de Software 2 (ISW-2), Sesión 17.

Está hecha con **Python + Flask** y guarda los datos en **SQLite** (base de datos embebida). Recibe y responde en **JSON**.

## Recurso: avistamiento

| Campo | Descripción |
|---|---|
| `id` | Lo asigna el sistema |
| `especie` | Nombre de la especie, por ejemplo "colibrí" |
| `lugar` | Dónde se observó |
| `fecha` | Texto en formato `AAAA-MM-DD` |
| `observador` | Quién lo registró |

## Requisitos

- Python 3.10 o superior
- Git

## Instalación

**Windows (PowerShell o CMD):**

```
git clone https://github.com/JU4ND4VID/api-avistamientos.git
cd api-avistamientos
python -m venv .venv
```

Activa el entorno según tu terminal:

- PowerShell: `.venv\Scripts\Activate.ps1`
- CMD: `.venv\Scripts\activate.bat`

Verás `(.venv)` al inicio de la línea. Luego instala las dependencias:

```
python -m pip install -r requirements.txt
```

> Si PowerShell dice que la ejecución de scripts está deshabilitada, ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y repite la activación.
>
> Alternativa sin activar el entorno (funciona aunque PowerShell bloquee scripts):
>
> ```
> .venv\Scripts\python.exe -m pip install -r requirements.txt
> .venv\Scripts\python.exe app.py
> ```

**Mac o Linux:**

```bash
git clone https://github.com/JU4ND4VID/api-avistamientos.git
cd api-avistamientos
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Ejecución

```bash
python app.py
```

La API queda disponible en `http://127.0.0.1:5000`. La base de datos `avistamientos.db` se crea sola la primera vez.

Para detenerla, presiona `Ctrl + C`.

## Endpoints

Los ejemplos usan `curl` y los archivos JSON de la carpeta `ejemplos/`, así funcionan igual en cualquier sistema operativo. La opción `-i` muestra el código de estado.

> En Windows PowerShell usa `curl.exe` en lugar de `curl`. En CMD, Mac y Linux basta con `curl`. Ejecuta los comandos uno por uno.

> Los ejemplos de ver, actualizar y eliminar usan el `id` 1. Ejecuta primero el de **Registrar** para que ese avistamiento exista.

| Acción | Petición | Respuesta |
|---|---|---|
| Listar | `GET /avistamientos` | 200 con la lista |
| Ver uno | `GET /avistamientos/{id}` | 200, o 404 si no existe |
| Registrar | `POST /avistamientos` | 201 con el avistamiento creado, o 400 si faltan datos |
| Actualizar | `PUT /avistamientos/{id}` | 200, o 404 si no existe, o 400 si los datos son inválidos |
| Eliminar | `DELETE /avistamientos/{id}` | 204 sin cuerpo, o 404 si no existe |
| Resumen (bonus) | `GET /avistamientos/resumen` | 200 con el conteo por especie |

### Listar todos

```bash
curl -i http://127.0.0.1:5000/avistamientos
```

### Ver uno

```bash
curl -i http://127.0.0.1:5000/avistamientos/1
```

### Registrar

```bash
curl -i -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" -d "@ejemplos/nuevo.json"
```

Cuerpo de ejemplo (`ejemplos/nuevo.json`):

```json
{
  "especie": "colibrí",
  "lugar": "Jardín Botánico",
  "fecha": "2026-09-29",
  "observador": "Peña"
}
```

Si falta algún campo, está vacío o la fecha no tiene el formato `AAAA-MM-DD`, responde 400:

```bash
curl -i -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" -d "@ejemplos/incompleto.json"
```

### Actualizar

Reemplaza el avistamiento completo, por eso se envían los cuatro campos:

```bash
curl -i -X PUT http://127.0.0.1:5000/avistamientos/1 -H "Content-Type: application/json" -d "@ejemplos/actualizado.json"
```

### Eliminar

```bash
curl -i -X DELETE http://127.0.0.1:5000/avistamientos/1
```

### Resumen por especie (bonus)

```bash
curl -i http://127.0.0.1:5000/avistamientos/resumen
```

Ejemplo de respuesta:

```json
[
  { "especie": "colibrí", "total": 2 },
  { "especie": "águila", "total": 1 }
]
```

## Pruebas

Las pruebas de integración cubren los seis endpoints y sus códigos de estado (200, 201, 204, 400 y 404). Cada prueba usa una base de datos temporal, así que no tocan los datos reales.

```
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

## Uso de IA

Para este trabajo se utilizó **Claude (modelo Sonnet 5.5)**, de Anthropic, como asistente: guió el desarrollo paso a paso y generó el código base de la API y de las pruebas. Se ejecutó el código, y se probó cada endpoint con `curl` (también en otra máquina) y se comprendio el funcionamiento de cada parte.

## Referencias

- Material de clase de ISW-2, Sesión 16 (REST, métodos HTTP, códigos de estado y JSON) y enunciado de la Sesión 17.
- Documentación de Flask: https://flask.palletsprojects.com
- Documentación del módulo `sqlite3` de Python: https://docs.python.org/3/library/sqlite3.html
- Documentación de pytest: https://docs.pytest.org

## Autor

Juan David Peña Cubillos.