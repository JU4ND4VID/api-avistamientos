# Justificación de las pruebas: API de avistamientos

Juan David Peña Cubillos. ISW-2, Sesión 22. Código en Python con Flask y SQLite; pruebas con pytest y pytest-cov.

## 1. Qué cambió en el código

- **Se extrajo la validación a `validador.py`** (`ValidadorDeAvistamiento`). Antes era una función mezclada con el controlador en `app.py`. Ahora es lógica pura, sin Flask ni base de datos, así que se prueba como unidad aislada. Devuelve un diccionario `{campo: mensaje}`, que permite verificar exactamente qué campo falló.
- **Se implementó la regla de negocio:** especie de 3 a 50 caracteres (sin contar espacios en los extremos), fecha `AAAA-MM-DD` real y no posterior a hoy, y lugar y observador no vacíos. Si falla, POST y PUT responden 400 con `{"error": ..., "detalles": {campo: mensaje}}`.
- **Se envolvió el reloj en una interfaz** (`Reloj`, con `RelojSistema` como implementación real). El validador recibe el reloj por constructor, así que una prueba puede entregarle un reloj fijo. Sin esto, la regla "no posterior a hoy" dependería del día en que se corra la prueba.
- **No se creó una capa de repositorio.** La API es pequeña y las pruebas de integración usan una base SQLite temporal real, aislada por prueba. Introducir un repositorio solo para poder simularlo agregaría código sin resolver un problema concreto.
- Las pruebas se movieron a la carpeta `tests/`.

## 2. Tabla de casos de la Parte A

Con un reloj fijo en **2026-10-21**. Para la especie se mide la longitud sin espacios en los extremos (rango válido: 3 a 50).

| Campo | Valor | Tipo de caso | Esperado | Por qué este valor y no otro |
|---|---|---|---|---|
| especie | `"colibrí"` (7) | Representativo | Válido | Representa toda la clase válida; otros valores del interior se comportan igual. |
| especie | `"ab"` (2) | Límite | Inválido | Borde inferior, lado de afuera. |
| especie | `"abc"` (3) | Límite | Válido | Borde inferior, lado de adentro. |
| especie | 50 × `"a"` | Límite | Válido | Borde superior, lado de adentro. |
| especie | 51 × `"a"` | Límite | Inválido | Borde superior, lado de afuera. |
| especie | `"     "` | Inválido | Inválido | Clase "solo espacios": mide 5 con espacios y 0 sin ellos; detecta un `strip` olvidado. |
| especie | `123` | Inválido | Inválido | Clase "no es texto"; sin ella el validador fallaría con una excepción en vez de un 400. |
| fecha | `"2026-10-01"` | Representativo | Válido | Clase "formato correcto y no futura". |
| fecha | `"2026-10-21"` | Límite | Válido | Borde exacto de "no posterior a hoy": hoy se acepta. |
| fecha | `"2026-10-22"` | Límite | Inválido | Primer día prohibido; detecta un `>=` escrito en vez de `>`. |
| fecha | `"21/10/2026"` | Inválido | Inválido | Clase "formato incorrecto". |
| fecha | `"2026-02-30"` | Inválido | Inválido | Formato correcto pero fecha inexistente; el patrón de formato solo no la detecta. |
| lugar, observador | `""` | Inválido | Inválido | Clase "vacío", una prueba por campo. |

Se aplicó **partición de equivalencia** para elegir un representante por clase y **análisis de valores límite** en los dos bordes de cada rango (2/3, 50/51 y hoy/mañana). No se probaron especies de 10, 20 o 30 caracteres porque pertenecen a la misma clase que `"colibrí"` y no aportan información nueva.

## 3. Por qué cada nivel

- **`test_especie_de_3_caracteres_se_acepta` es unitaria.** La regla se decide dentro de una función pura. Una prueba de integración pagaría el costo de HTTP y base de datos para verificar algo que se resuelve sin ellos, y si fallara no diría si el defecto está en la regla o en la ruta.
- **`test_post_valido_y_luego_get_devuelve_el_mismo_avistamiento` es de integración.** Cruza la frontera HTTP, el controlador, SQLite y la serialización JSON. La prueba unitaria del validador **no puede detectar** que la ruta esté mal registrada, que el método HTTP sea incorrecto, que el `INSERT` no guarde algún campo, que el código no sea 201 o que el `id` no se asigne.
- **`test_post_con_especie_corta_responde_400_y_no_guarda_nada` es de integración.** Un validador perfecto pasaría todas sus pruebas unitarias aunque el controlador olvidara llamarlo. Esta prueba verifica el cableado y el efecto: además del 400, comprueba que la lista quedó vacía.

## 4. Los dobles

- **`RelojFijo` es un stub:** entrega siempre la misma fecha (indirect input) y no verifica cómo ni cuántas veces lo llaman. Si verificara las llamadas sería un mock o un spy, pero a esta prueba solo le importa el resultado de la validación. No necesita ser un fake porque no tiene estado ni lógica que simular.
- **Sin el stub**, la prueba de "fecha de mañana" tendría que escribir una fecha fija, que pasa hoy y falla cuando el calendario avance, o calcular mañana con el reloj real, que no permite fijar casos como un fin de mes y es frágil cerca de la medianoche.
- **La base de datos no es un doble.** Las pruebas de integración usan una SQLite real en un archivo temporal distinto para cada prueba (`tmp_path` y `monkeypatch`), de modo que cada una prepara sus datos y no depende del orden.
- En la prueba de integración de fecha futura se calcula mañana con el reloj real (`date.today() + 1 día`). Es aceptable porque el valor se recalcula en cada ejecución y no caduca; la verificación exacta de los límites se hizo en el nivel unitario con el stub.

## 5. Lo que no probaron

1. **La ruta `/` (`inicio`).** No contiene regla de negocio; una prueba repetiría el texto fijo y fallaría si cambia el mensaje, sin detectar un defecto real.
2. **El arranque del servidor (`if __name__ == "__main__"`).** Probarlo exige levantar un proceso real, es decir, una prueba de sistema, de costo alto y riesgo bajo. Se verifica manualmente con los `curl` del README.
3. **El `raise NotImplementedError` de la interfaz `Reloj`.** Es un método abstracto que ninguna implementación usa; no es comportamiento del sistema.
4. **Errores 500 por fallo de la base de datos.** Habría que forzar el error en SQLite con un doble. Como la API no tiene capa de repositorio, hacerlo implicaría parchear el módulo `sqlite3`, un costo desproporcionado frente al riesgo en una API académica sin concurrencia.

## 6. Lectura de la cobertura

Se mide con el **criterio de sentencias y ramas** (`--cov-branch`). Comando:

```
python -m pytest --cov=app --cov=validador --cov-branch --cov-report=term-missing
```

Reporte final (también guardado en `docs/cobertura.txt`):

```
Name           Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------
app.py            88      3     12      1    96%   48, 147-148
validador.py      40      1     10      0    98%   13
----------------------------------------------------------
TOTAL            128      4     22      1    97%
```

- **Hallazgo y acción:** la primera medición (96% total) mostraba sin cubrir el manejador global de 404 de `app.py`. Las pruebas de 404 existentes pasaban por otro camino: el `return` de `obtener`, cuando el id no existe, y nunca por el manejador, que responde cuando la ruta no existe. Ese contrato ("los errores salen en JSON, no en HTML") no estaba verificado, así que se agregaron dos pruebas de integración y la cobertura subió a 97%.
- **Líneas sin cubrir que se aceptan:** `48` (ruta `/`), `147-148` (arranque del servidor) y `13` (método abstracto), por las razones de la sección 5. La rama parcial de `app.py` es el `if __name__`, que solo se evaluó por el lado en que no arranca el servidor.
- **Límite de la métrica:** la cobertura dice qué código se ejecutó, no si las pruebas verifican algo útil. Por eso cada prueba tiene `assert` sobre el estado, el cuerpo y el efecto, y no se persiguió el 100%.