---
name: ine
description: >-
  Consulta y extracción de datos del Instituto Nacional de Estadística (INE) de España: estadísticas
  oficiales, INEbase, API pública JSON/CSV/XLSX. Úsala SIEMPRE que el usuario pida datos del INE o
  estadísticas oficiales españolas — IPC/IPCA (inflación), EPA (paro/empleo), PIB y Contabilidad
  Nacional, población y demografía, salarios, turismo, comercio, industria, vivienda, ECV, etc. —
  incluso si no menciona "INE" explícitamente (p. ej. "dame la inflación de España", "cuánto subió
  el paro", "población de Madrid 2023", "evolución del PIB español"). También cuando el usuario
  proporcione IDs de tablas/series de ine.es o quiera exportar datos del INE a CSV/Excel. No usar
  para datos de otros países ni para estadísticas de fuentes distintas al INE.
---

# INE — Datos del Instituto Nacional de Estadística de España

Esta skill te permite consultar la API pública del INE (WSTempus/INEbase) para obtener **estadísticas oficiales de España**: operaciones, tablas, series temporales, variables y valores, en JSON, CSV, PC-Axis o XLSX. Sin claves ni autenticación (licencia CC BY 4.0).

## Cómo piensa el INE sus datos (modelo en 60 segundos)

- **Operación** = una estadística (IPC, EPA, Cifras de Población...). Identificable por 3 códigos equivalentes: `Id` numérico (p. ej. 25), `Codigo` alfabético (IPC) e `IOE<n>` (IOE30138).
- **Tabla** = agrupación de series para difusión (p. ej. la 50902, "Índices nacionales: general y de grupos ECOICOP"). Tiene un `Id`.
- **Serie** = secuencia temporal con datos (p. ej. IPC251852, "Nacional. Índice general. Índice"). Único objeto con datos. Código tipo `IPC251852`.
- **Variable/Valor** = dimensiones que definen series (Provincias, Grupos ECOICOP, Tipo de dato...) y sus valores (Madrid, Índice general, Variación anual...). Se usan para **filtrar**.
- Tres fuentes de tablas: **Tempus3** (serie temporal completa), **pc-axis** y **tpx** (más simples). La fuente cambia qué filtros y formatos puedes usar (ver abajo).

## Flujo de trabajo (el orden importa)

1. **Identifica la operación**: `python ine/scripts/ine.py search <palabra>` (o `ops` para listar las 112). El catálogo con códigos está en `references/operations-catalog.md`.
2. **Encuentra la tabla**: `python ine/scripts/ine.py tables <op>` (filtra con `--search`). Si el usuario ya dio un Id de tabla/serie, salta directo al paso 3 o 4.
3. **Extrae datos de tabla**: `python ine/scripts/ine.py table-data <id> [--nult N] [--date ...] [--tv var:val ...]`. Úsalo cuando el usuario quiera un conjunto de series relacionadas.
4. **O extrae una serie concreta**: `python ine/scripts/ine.py series <cod>` (metadatos) y `python ine/scripts/ine.py series-data <cod> --nult N|--date ...`. Úsalo para preguntas puntuales (p. ej. "IPC de diciembre").
5. **Si necesitas filtrar**, primero inspecciona: `variables <op>`, `values <var> [--op <op>]`, `groups <tabla>` y `group-values <tabla> <grupo>` para conocer los IDs numéricos, y luego filtra con `--tv "id_var:id_valor"`.
6. **Presenta** los datos en una tabla legible (periodo | valor | tipo de dato) o guárdalos con `--out` si el usuario quiere un archivo.

El script completo: **`scripts/ine.py`** (Python 3 + `requests`). Ejecútalo siempre con `python ine/scripts/ine.py ...` desde la raíz del workspace. Usa `--help` en cualquier subcomando. Salida siempre UTF-8.

## Referencia rápida del CLI

| Subcomando | Qué hace |
|---|---|
| `search <kw>` / `ops` | Busca/listar operaciones (nombre, código, IOE) |
| `op <id>` | Detalle de una operación (acepta 25, IPC o IOE30138) |
| `tables <op> [--search] [--geo 0\|1]` | Tablas de una operación |
| `table-data <id> [--nult N] [--date ini[:fin]] [--tv v:val ...] [--tidy] [--out f.csv] [--format js\|csv\|csv_sc\|px\|xlsx]` | Datos de tabla (Tempus3, pc-axis y tpx) |
| `series <cod>` | Metadatos de una serie (unidad, periodicidad, clasificación, última actualización) |
| `series-data <cod> --nult N` o `--date ini[:fin]` | Datos de una serie (**exige uno de los dos**) |
| `series-table <id> [--search] [--tv ...]` | Series de una tabla (para localizar códigos de serie) |
| `series-op <op> [--search] [--page N]` | Series de una operación (**puede pesar MB**, usa `--search`) |
| `values-serie <cod>` | Variables/valores que definen una serie |
| `variables <op>` | Variables de una operación |
| `values <var> [--op <op>]` | Valores de una variable (con `--op`, acotados a la operación) |
| `groups <tabla>` / `group-values <tabla> <grupo>` | Combos de selección de una tabla y sus valores (para filtrar con `--tv`) |
| `meta-op <op> --g var:val [--g ...] [--p 1\|3\|6\|12] [--nult N]` | Datos de una operación **filtrados por metadatos** (OR dentro de cada `--g`, AND entre `--g` distintos) |
| `series-meta-op <op> --g ...` | Igual pero devuelve las series, no los datos |
| `periodicities` / `publications [op]` / `pub-dates <id>` | Catálogos auxiliares |
| `children <var> <valor>` | Valores hijo en jerarquías (CCAA → provincias) |
| Flags: `--lang EN`, `--det 0\|1\|2`, `--tip A\|M\|AM\|raw`, `--url`, `--json`, `--rows N` | |

## Conocimientos verificados (jul-ago 2026) — léelos antes de llamar a la API

**Comportamientos que sorprenden** (verificados contra el servicio real):

- `DATOS_SERIE`, `SERIE` y `OPERACION` devuelven un **objeto JSON, no una lista**; el resto devuelven listas. No hagas `[0]` sobre ellos.
- `DATOS_SERIE` **exige** `--nult` o `--date`; sin ellos responde 404. `--date` acepta `AAAAMMDD:AAAAMMDD`, rango abierto (`20250101:`) y en el script también `AAAA-MM-DD`.
- `--nult` cuenta **periodos** (meses/trimestres/años), no observaciones: `nult=1` en una tabla devuelve el último periodo de **todas** sus series.
- Los formatos **csv / csv_sc / px / xlsx exportan la tabla COMPLETA**: ignoran `--nult` y `--date`, y `--tv` da error 400. Úsalos solo para exportar tablas enteras (Tempus3 y tpx con prefijo `/tpx/` automático; las pc-axis no tienen exportación). El CSV real viene en **UTF-8 con BOM** aunque la cabecera diga ISO-8859-15; el script ya lo decodifica bien.
- `SERIES_OPERACION` puede devolver **megas** (IPC con det=2: ~10 MB). Prefiere `--search` para filtrar y `--max` para limitar. Si `--search` no encuentra nada en la página 1, el script escanea más páginas automáticamente; para búsquedas exhaustivas usa `series-meta-op` con filtros `--g` (no pagina).
- **Las series antiguas se congelan cuando cambia la base** (IPC base 2021, EPA censo 2021): pueden estar "al día" de publicación pero terminar hace años. Antes de dar un dato, comprueba con `series <cod>` la `Clasificacion` y el `PubFechaAct`, y elige la serie de la clasificación vigente (ver `references/guide.md` → "Series congeladas").
- Errores: tabla/serie inexistente → 404 con cuerpo HTML (el script da mensajes amigables). `det` inválido se ignora silenciosamente.
- En `TABLAS_OPERACION` con `tip=A`, `FechaRef_fin` puede ser el **string `"null"`** (no un null real) cuando la tabla está al día.
- Fechas: en modo `tip=A` vienen ISO (`2025-12-01T00:00:00.000+01:00`); en modo raw (`--tip raw`) son **epoch en milisegundos** y hay campos `FK_*` numéricos en vez de nombres `T3_*`.

**Filtros `--tv` según la fuente de la tabla** (crítico):

- **Tempus3**: IDs numéricos. Descúbrelos con `groups`/`group-values` o `variables`/`values`. Ej.: `--tv 70:9003` (Castilla y León), `--tv 762:304092` (Índice general), `--tv 3:74` (variación anual). Varios valores de una misma variable: repetir `--tv` (`--tv 70:9003 --tv 70:8999`).
- **pc-axis / tpx**: códigos alfanuméricos que aparecen en `series-table <id> --tip M` (campo `MetaData`: `T3_Variable` + `Codigo`). Ej.: `--tv sexo:mujeres`, `--tv espanolesextranjeros:espanoles`. En tablas tpx con códigos Tempus3 se puede usar el alias `~id`: `--tv 349~id:16473~id`.

**Atajos de series muy usadas** (IPC nacional, base vigente 2025): `IPC290751` índice general, `IPC290752` variación mensual, `IPC290750` variación anual. ⚠️ El INE cambió la base en 2026 (Base 2025 IPC, IPCA): las series `IPC2518xx` (Base 2021) siguen en Tempus3 pero ya no son las de referencia — verifica siempre `Clasificacion` con `series <cod>`. Operaciones frecuentes: `IPC` (25), `IPCA` (18), `EPA` (293), `CNTR2010` (237, PIB trimestral), `CNE` (247), `DPOP` (22, padrón), `ECV` (155). El catálogo completo está en `references/operations-catalog.md`.

## Ejemplos típicos

1. **"Inflación actual (último mes publicado)"** → `python ine/scripts/ine.py series-data IPC290750 --nult 3 --tip A` (variación anual, Base 2025) y `... series-data IPC290751 --nult 1 --tip A` (índice). Presenta el último mes con su tipo de dato (Definitivo/Avance) — p. ej. julio 2026 → 3,5 % (avance), índice junio 2026 103,598.
2. **"IPC de Castilla y León por grupos, últimos 12 meses"** → `groups 50913` y `group-values` para los IDs → `table-data 50913 --nult 12 --tv 70:9003` (todas las series de esa CCAA) o añade `--tv 762:304092` para solo el índice general.
3. **"Población de las CCAA en 2023"** (tabla pc-axis `t20/e245/p08/l0/01001.px` es por edad/españoles/sexo, no CCAA): busca en `tables DPOP --search comunidades` y extrae con `table-data <id> --nult 1`; para filtrar usa códigos alfanuméricos de `series-table <id> --tip M`.
4. **"Tasa de paro de la EPA del último trimestre"** → `series-meta-op EPA --g 3:283910 --g 349:16473 --g 18:454 --g 357:10559 --p 3` (tasa de paro, Total Nacional, ambos sexos, 16+ años) para localizar la serie vigente, luego `series-data <cod> --nult 1 --tip A`. (Los IDs salen de `values 3 --op EPA`, `values 349 --op EPA`, etc.)
5. **"Exporta la tabla 50902 a Excel"** → `table-data 50902 --format xlsx --out ipc_ecoicop.xlsx` (exporta completa; avisa al usuario de que es la tabla entera).

## Cita la fuente (obligatorio por licencia)

Los datos del INE se reutilizan bajo **CC BY 4.0**. Cuando presentes datos, indica la fuente: *"Fuente: INE (www.ine.es), actualizado a <fecha del último dato>"*; si transformas los datos: *"Elaboración propia con datos del INE (www.ine.es)"*.

## Cuándo leer los recursos

- **`references/guide.md`** — cuando necesites el detalle de los flujos: cómo sacar IDs desde las URLs de INEbase, casos de uso por operación (IPC, EPA, población, PIB), matriz completa de formatos, y ejemplos de filtros complejos.
- **`references/api-reference.md`** — cuando quieras hacer llamadas directas (curl, Python, o construir URLs a mano), necesites el esquema exacto de una respuesta, o los parámetros de un endpoint concreto.
- **`references/operations-catalog.md`** — para localizar el código de una operación (Id/Codigo/IOE) sin llamar a la API. Para el listado vivo, usa `search`.

## Buenas prácticas

- **Empieza pequeño**: usa `--nult` o `--date` siempre que puedas; las tablas completas pueden tener miles de filas.
- **Verifica el nombre de la serie**: los nombres incluyen ámbito + concepto + tipo de dato ("Nacional. Índice general. Variación anual."). No des por hecho que el primer resultado es el correcto; usa `--search` y lee los nombres.
- **Los valores `None`/`null` en datos** (comunes en tpx, p. ej. "2024 (avance)") son datos no publicados, no errores.
- **No inventes IDs**: si el usuario da una URL de ine.es (`jaxiT3/Tabla.htm?t=50902`), el Id es el parámetro `t`; si es `jaxi/Tabla.htm?path=...&file=...px`, el Id es `path+file`; si es `jaxi/Datos.htm?tpx=...`, el Id es `tpx`. Las series solo existen para Tempus3 (`jaxiT3/Datos.htm?t=...`).
- Si una consulta falla con 404, casi siempre es un Id erróneo o una fuente equivocada: repasa el paso 1-2 del flujo antes de reintentar.
