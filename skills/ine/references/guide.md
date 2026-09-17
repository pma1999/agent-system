# Guía de flujos de trabajo con el INE

Guía práctica para resolver las peticiones más habituales. Complementa al SKILL.md con el detalle operativo. Toda la información está verificada contra el servicio real (jul-ago 2026).

## 1. Obtener identificadores desde INEbase (cuando el usuario da URLs o navega)

El usuario puede llegar con una URL de ine.es. El identificador a usar en la API depende de la fuente:

| Fuente | URL típica | Identificador para la API |
|---|---|---|
| Tempus3 | `https://www.ine.es/jaxiT3/Tabla.htm?t=50902` | el parámetro `t`: `50902` |
| Tempus3 (serie) | `https://www.ine.es/jaxiT3/Datos.htm?t=IPC251852` | el parámetro `t`: `IPC251852` (solo series Tempus3) |
| PC-Axis | `https://www.ine.es/jaxi/Tabla.htm?path=/t20/e245/p08/l0/&file=01001.px` | concatenación `path+file`: `t20/e245/p08/l0/01001.px` |
| tpx | `https://www.ine.es/jaxi/Datos.htm?tpx=33387&L=0` | el parámetro `tpx`: `33387` |

Cómo distinguir la fuente sin mirar la URL: pide `series-table <id> --tip M`. Si la respuesta trae `MetaData` con `T3_Variable`/`Codigo` alfanuméricos → pc-axis o tpx (y `series-table` sin `--tip M` devuelve `FK_Operacion` para pc-axis). Si trae `COD` tipo `IPCxxxxx` → Tempus3.

## 2. Localizar la operación correcta

- `python ine/scripts/ine.py search <palabra>` filtra el catálogo por nombre, código e IOE (112 operaciones; no hay endpoint de búsqueda en el INE).
- Palabras que funcionan: "precios de consumo" (IPC/IPCA), "población activa" (EPA), "contabilidad" (CNE/CNTR), "población" (13 operaciones), "salarios", "turismo", "industria", "comercio", "vivienda", "condiciones de vida" (ECV).
- El catálogo completo con códigos está en `operations-catalog.md` (snapshot). Para el listado vivo: `python ine/scripts/ine.py ops`.
- Cada operación admite 3 códigos en la API: `Id` (25), `Codigo` (IPC), `IOE<n>` (IOE30138). El script acepta los tres.

## 3. De la operación a los datos

### Ruta A — por tabla (conjuntos de series)
1. `tables <op>` → lista de tablas con Id, periodicidad, año de inicio y última actualización.
2. `table-data <id> --nult N --tip A` → todas las series de la tabla con los últimos N periodos.
3. Para acotar: `groups <id>` (combos de la tabla) → `group-values <id> <grupo>` (valores con sus Ids) → `table-data <id> --tv id_var:id_valor ...`.

### Ruta B — por serie (una magnitud concreta)
1. `series-table <id> --search <palabra>` o `series-op <op> --search <palabra> --max 10` → localiza el código de serie.
2. `series <cod>` → confirma nombre, unidad, periodicidad, clasificación (base) y última actualización.
3. `series-data <cod> --nult N --tip A` (o `--date 2024-01-01:2024-12-31`) → los datos.

### Ruta C — filtro por metadatos de operación (potente)
`meta-op <op> --g id_var:id_valor --g id_var2:id_valor2 [--p 1|3|6|12] [--nult N]`
- OR dentro de un mismo `--g` (repite el flag con varios valores: `--g 115:28 --g 115:29` = Madrid o Barcelona), AND entre `--g` distintos.
- Ejemplo (IPC de la provincia de Madrid, variación mensual, todos los grupos ECOICOP):
  `python ine/scripts/ine.py meta-op IPC --g 115:29 --g 3:84 --g 762: --p 1 --nult 1 --tip A`
- Útil cuando la tabla "oficial" no existe o quieres un cruce específico. `series-meta-op` devuelve solo las series (ligero).

## 4. Casos por operación frecuente

### IPC (Id 25) — inflación
- Series nacionales vigentes (**Base 2025, en vigor desde 2026** — el INE cambia la base periódicamente): `IPC290751` índice general, `IPC290752` var. mensual, `IPC290750` var. anual, `IPC290753` var. en lo que va de año. Las series `IPC251852/855/856` (Base 2021) siguen consultables pero son de la base anterior.
- Tablas: la operación lista hoy la "ver.2" `76125` (Índices nacionales: general y de grupos ECOICOP ver.2); `50902` es la tabla de la base anterior (sigue funcionando en `table-data` pero ya no aparece en `tables IPC`). Por CCAA: `76136` (ver.2); provinciales: `76141` (ver.2).
- Filtrar CCAA en 76136: `--tv 70:9003` (Castilla y León), `--tv 70:8997` (Andalucía)... IDs en `group-values 76136 110924`. Grupos ECOICOP: `--tv 762:304092` (índice general), `--tv 762:304093` (alimentos...). Tipo de dato (var. 3): 74 = variación anual, 84 = variación mensual, 83 = índice, 87 = var. en lo que va de año (ver `values 3 --op 25`).
- Para localizar las series de la base vigente usa el filtro de metadatos: `series-meta-op IPC --g 3:74 --g 349:16473 --g 762:304092 --p 1` → `IPC290750` (Nacional. Índice general. Variación anual).
- IPCA (Id 18) es la versión armonizada (comparativa UE).

### EPA (Id 293) — empleo/paro
- Las series de la EPA se localizan mejor por **metadatos** (`series-meta-op`, no pagina) que por nombre (`series-op` pagina por 500). Variables y valores verificados:
  - **Tipo de dato** (var. 3): valor `283910` = "Tasa de paro de la población", `21332` = "Ocupado/a", `21335` = "Parados" (estos dos en var. 114 "Relación con la actividad").
  - **Total Nacional** (var. 349): valor `16473`.
  - **Sexo** (var. 18): `451` Total, `452` Hombres, `453` Mujeres, `454` Ambos sexos.
  - **Semiintervalos de edad** (var. 357): `10559` = "16 y más años" (la tasa de paro estándar).
  - **Grupos de edad** (var. 360): `283906` = "De 16 a 64 años".
- Receta para la tasa de paro nacional del último trimestre:
  `series-meta-op EPA --g 3:283910 --g 349:16473 --g 18:454 --g 357:10559 --p 3`
  → devuelve la serie vigente (ver "Series congeladas" abajo), p. ej. `EPA424243` (Base 2021). Luego `series-data EPA424243 --nult 1 --tip A`.
  ⚠️ Esta consulta recorre toda la operación y puede tardar 1-3 minutos; si da timeout, repítela (o usa `$env:INE_TIMEOUT=300`). El filtro de edad (357:10559 = 16 y más) reduce mucho el resultado; si lo omites, llegan también los cruces por nivel de formación.
- Unidad "Tasas" (%); la EPA es trimestral (`T3_Periodo`: T1..T4).

### Población / Padrón (DPOP Id 22, ePOBa Id 21, Cifras de Población Id 72)
- La tabla pc-axis `t20/e245/p08/l0/01001.px` (Población por edad, españoles/extranjeros, sexo y año) cubre **1998–2022**; filtros alfanuméricos: `--tv sexo:mujeres`, `--tv espanolesextranjeros:espanoles`, `--tv edad3gruposdeedad:totaledades`. La serie "TOTAL EDADES, TOTAL, Ambos sexos" es la población total a 1 de enero.
- `DPOP1` "Total Nacional. Total. Total habitantes. Personas." (padrón, anual) llega hasta 2021 (el padrón se sustituyó por las Cifras de Población).
- Para 2023+ usa la operación **Cifras de Población** (CP, Id 72) — no tiene tablas Tempus3 (busca sus series/tablas tpx en INEbase) — o **ePOBa** (Id 21, Estimaciones de la Población Actual, a 1 de julio; series anuales "Población..." — ojo: las series mensuales antiguas como EPOB0 terminan en 2012).
- Para CCAA/provincias/municipios: `tables DPOP --search <término>` y explora; los datos municipales del padrón están en tablas con la variable "Municipios" (Id 19).

### Series congeladas por cambio de base/clasificación (¡importante!)
Cuando el INE cambia la base (p. ej. IPC base 2021, EPA censo 2021), **las series antiguas dejan de actualizarse** pero siguen en Tempus3. Síntoma: `PubFechaAct` de la publicación es reciente pero la serie termina años antes (p. ej. `EPA7532` "16 a 64 años, Censo 2011" acaba en 2023; `EPOB0` acaba en 2012).
Cómo detectar y elegir la serie vigente:
1. `series <cod>` → mira `Clasificacion` ("Base 2021 (EPA)", "Censo 2011"...) y `Publicacion.PubFechaAct`.
2. Si hay varias candidatas, elige la de **clasificación más reciente** con `PubFechaAct` reciente.
3. Para encontrarlas todas, usa `series-meta-op` (no pagina) y revisa las clasificaciones de los resultados.

### PIB / Contabilidad Nacional (CNTR2010 Id 237, CNE Id 247)
- PIB trimestral: `tables CNTR2010 --search PIB`. Series típicas "PIB pm. Precios corrientes. Nacional", "PIB pm. Precios constantes. Nacional" — confirma con `series <cod>` (Unidad: "Millones de euros" o "Miles de millones").
- Filtrar por ramas de actividad: variable "Ramas de actividad (CNEA)" — `variables CNTR2010` para el Id exacto.

## 5. Matriz de formatos y exportación

| Formato | Ruta | Tempus3 | pc-axis | tpx | Filtros (tv/date/nult) |
|---|---|---|---|---|---|
| JSON | `/js/ES/...` | ✅ | ✅ | ✅ | ✅ (únicos que funcionan) |
| CSV (tabulado) | `/csv/ES/...` | ✅ | ❌ (204) | ✅ con `/tpx/` | ❌ exporta todo |
| CSV (punto y coma) | `/csv_sc/ES/...` | ✅ | ❌ | ✅ con `/tpx/` | ❌ |
| PC-Axis | `/px/ES/...` | ✅ | ❌ | ✅ con `/tpx/` | ❌ |
| XLSX | `/xlsx/ES/...` | ✅ | ❌ | ✅ con `/tpx/` | ❌ |

- El script `ine.py` gestiona el prefijo `/tpx/` automáticamente en la exportación (prueba la ruta normal y cae al prefijo si recibe 204/404).
- **El CSV del INE es UTF-8 con BOM** (aunque la cabecera HTTP diga ISO-8859-15); valores con coma decimal ("119,942"); columnas = variables de la tabla en formato largo (una fila por observación); periodo en formato `2025M12`.
- No existe CSV para `DATOS_SERIE` (404). Las series solo se exportan por JSON (o `--tidy`/`--out` del script, que genera un CSV limpio con cabecera).
- Para tablas enormes, mejor JSON con `--nult`/`--date`/`--tv` que CSV: el CSV siempre descarga la tabla entera.

## 6. Idiomas, paginación y límites

- `--lang EN` traduce nombres y metadatos (los códigos no cambian). Útil para informes en inglés.
- Paginación (500 ítems/página): `ops`, `variables`, `series-op` (`--page N`). El resto de endpoints no pagina. **`series-op --search` escanea automáticamente varias páginas si no encuentra nada en la primera** (acotado a 4); para búsquedas exhaustivas en toda una operación usa `series-meta-op` con filtros `--g`, que no pagina.
- No hay límite de peticiones documentado ni API key. Sé razonable: cachea resultados dentro de una misma conversación y no lances bucles de descarga masiva sin necesidad.
- El servicio a veces tarda varios segundos en tablas grandes (p. ej. `series-op IPC`). No lo interpretes como fallo.

## 7. Interpretación de respuestas

### Tempus3 (tip=A, modo por defecto del script)
```json
{
  "COD": "IPC251852",
  "Nombre": "Nacional. Índice general. Índice. ",
  "T3_Unidad": "Índice", "T3_Escala": " ",
  "Notas": [{"texto": "https://...", "Fk_TipoNota": 6, "textoTipo": null}],
  "Data": [{"Fecha": "2025-12-01T00:00:00.000+01:00", "T3_TipoDato": "Definitivo",
            "T3_Periodo": "M12", "Anyo": 2025, "Valor": 119.942}]
}
```
- `T3_Periodo`: "M01".."M12" (mensual), "T1".."T4" (trimestral), "S1"/"S2" (semestral), o el año (anual).
- `T3_TipoDato`: "Definitivo", "Avance", "Estimación", "Provisional"... — indícalo si el dato es avance/estimación.
- Con `--tip raw`: `Fecha` es epoch ms, `FK_TipoDato`/`FK_Periodo` numéricos, aparece `Secreto` (dato confidencial).

### pc-axis / tpx (más simple)
```json
[{"Nombre": "TOTAL EDADES, TOTAL, Ambos sexos",
  "Data": [{"NombrePeriodo": "2022", "Valor": 47475420.0}]}]
```
- `NombrePeriodo` puede incluir avisos ("2024 (avance)"). `Valor: null` = no publicado.
- Metadatos (para filtrar): `series-table <id> --tip M` → `MetaData: [{"T3_Variable": "Sexo", "Nombre": "Mujeres", "Codigo": "mujeres"}]`.

## 8. Trampas y errores frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| 404 al pedir `series-data` sin nult/date | Parámetro obligatorio ausente | Añade `--nult` o `--date` |
| 404 en `table-data` | Id erróneo o de otra fuente | Revisa la sección 1; usa `tables <op>` |
| 400 con `--format csv` + `--tv` | El CSV no soporta filtros | Usa JSON con filtros, o CSV sin filtros |
| 204 con `--format csv/xlsx` | Tabla pc-axis sin exportación | Usa JSON; o añade `--tpx` (el script lo hace solo) para tpx |
| Respuesta gigante | `series-op` sin filtros, o CSV de tabla completa | `--search`/`--max`/`--nult`/`--date` |
| `FechaRef_fin` = `"null"` (string) | Tabla al día con tip=A | Trátalo como sin dato |
| Fechas epoch (13 dígitos) | Modo raw | Usa `--tip A` (ISO) o `fmt_fecha` del script |
| Serie "duplicada" (ver.1 / ver.2) | Cambio de base o clasificación | Compara `Clasificacion` en `series <cod>` y elige la vigente |
| Serie termina hace años aunque la publicación esté al día | Serie congelada por cambio de base/censo | Busca la serie de la clasificación nueva (ver "Series congeladas") |
