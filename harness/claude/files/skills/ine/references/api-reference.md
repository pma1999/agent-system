# Referencia de la API del INE (WSTempus)

Referencia técnica completa del servicio OpenAPI del INE (`servicios.ine.es/wstempus`), verificada contra el servicio real en julio-agosto de 2026. Especificación oficial: `https://www.ine.es/OpenAPI/includes/files/es/wstempus.yaml` (Swagger UI en `https://www.ine.es/OpenAPI/`). Documentación oficial: sección "Datos abiertos → API JSON" de ine.es.

## Índice
1. [Estructura de las peticiones](#1-estructura-de-las-peticiones)
2. [Parámetros comunes](#2-parámetros-comunes)
3. [Endpoints](#3-endpoints)
4. [Esquemas de respuesta](#4-esquemas-de-respuesta)
5. [Comportamientos verificados y límites](#5-comportamientos-verificados-y-límites)

## 1. Estructura de las peticiones

```
https://servicios.ine.es/wstempus/{formato}/{idioma}/{FUNCION}/{input}[?parametros]
```

- **formato**: `js` (JSON) · `csv` (tabulado) · `csv_sc` (punto y coma) · `px` (PC-Axis) · `xlsx`
- **idioma**: `ES` · `EN`
- **FUNCION/input**: los de la tabla de abajo
- Sin autenticación. Licencia CC BY 4.0.

Alternativas de host documentadas: `servicios.ine.es/wstempus/jsCache/ES/...` para `SERIES_TABLA` (equivalente a `js`; verificado: misma respuesta).

## 2. Parámetros comunes

| Parámetro | Valores | Efecto |
|---|---|---|
| `nult` | entero ≥ 1 | Últimos N **periodos** (meses/trimestres/años), no observaciones |
| `date` | `aaaammdd:aaaammdd` | Rango de fechas; abierto al final: `20250101:` (desde esa fecha en adelante) |
| `det` | `0` \| `1` \| `2` | Nivel de detalle: 0 básico (IDs/FK), 1 detallado, 2 máximo (objetos anidados). Un `det` inválido se ignora silenciosamente |
| `tip` | `A` \| `M` \| `AM` | `A`=amigable (nombres `T3_*`, fechas ISO), `M`=incluye metadatos, `AM`=ambos |
| `tv` | `id_variable:id_valor` (repetible) | Filtro de tabla. `var:` = todos los valores de esa variable. Varios valores de una misma variable → repetir `tv` |
| `g1`..`gn` | `id_variable:id_valor` (repetible) | Filtros de operación por metadatos: OR dentro de un mismo `gi`, AND entre `gi` distintos |
| `p` | `1` \| `3` \| `6` \| `12` | Periodicidad: mensual, trimestral, semestral, anual |
| `geo` | `0` \| `1` | 0 = solo resultados nacionales; 1 = con desagregación territorial |
| `page` | entero ≥ 1 | Paginación: **500 elementos por página** (solo `OPERACIONES_DISPONIBLES`, `VARIABLES`, `VARIABLES_OPERACION`, `SERIES_OPERACION`) |
| `clasif` | entero | Clasificación para `VALORES_VARIABLE` (lista en `CLASIFICACIONES`) |

## 3. Endpoints

Todos bajo `https://servicios.ine.es/wstempus/js/ES/` (o `/EN/`). Salvo indicación, la respuesta es un array JSON.

### Datos
| Endpoint | Input | Parámetros | Respuesta |
|---|---|---|---|
| `DATOS_TABLA/{IdTABLA}` | Id tabla (Tempus3, pc-axis o tpx) | `nult`, `det`, `tip`, `tv`, `date` | array de series con `Data` |
| `DATOS_SERIE/{IdSERIE}` | Código de serie (solo Tempus3) | **`nult` o `date` obligatorios**, `det`, `tip` | **objeto** (no array) con `Data` |
| `DATOS_METADATAOPERACION/{IdOPERACION}` | Operación | `p`, `nult`, `det`, `tip`, `g1`..`gn` | array de series con `Data` filtradas por metadatos |

### Operaciones
| Endpoint | Input | Parámetros | Respuesta |
|---|---|---|---|
| `OPERACIONES_DISPONIBLES` | — | `det`, `geo`, `page` | array (112 operaciones; `page=2` → `[]`) |
| `OPERACION/{IdOPERACION}` | Id, Codigo o IOE | `det` | **objeto** `{Id, Cod_IOE, Nombre, Codigo, Url}` |

### Tablas
| Endpoint | Input | Parámetros | Respuesta |
|---|---|---|---|
| `TABLAS_OPERACION/{IdOPERACION}` | Operación | `det`, `geo`, `tip` | array de tablas |
| `GRUPOS_TABLA/{IdTABLA}` | Tabla Tempus3 | — | array `{Id, Nombre}` (combos de selección) |
| `VALORES_GRUPOSTABLA/{IdTABLA}/{IdGRUPO}` | Tabla + grupo | `det` | array de valores (con `Variable`) |

### Series
| Endpoint | Input | Parámetros | Respuesta |
|---|---|---|---|
| `SERIE/{IdSERIE}` | Código serie | `det`, `tip` | **objeto** con operación, periodicidad, unidad, clasificación, publicación |
| `SERIES_OPERACION/{IdOPERACION}` | Operación | `det`, `tip`, `page` | array (¡puede pesar MB!) |
| `SERIES_TABLA/{IdTABLA}` | Tabla | `det`, `tip`, `tv` | array de series |
| `VALORES_SERIE/{IdSERIE}` | Código serie | `det` | array de variables/valores que definen la serie |
| `SERIE_METADATAOPERACION/{IdOPERACION}` | Operación | `p`, `det`, `tip`, `g1`..`gn` | array de series filtradas por metadatos |

### Variables y valores
| Endpoint | Input | Parámetros | Respuesta |
|---|---|---|---|
| `VARIABLES` | — | `page` | array (todas las variables del sistema) |
| `VARIABLES_OPERACION/{IdOPERACION}` | Operación | `page` | array de variables usadas |
| `VALORES_VARIABLE/{IdVARIABLE}` | Variable | `det`, `clasif` | array de valores |
| `VALORES_VARIABLEOPERACION/{IdVARIABLE}/{IdOPERACION}` | Variable + operación | `det` | array de valores válidos en esa operación |
| `VALORES_HIJOS/{IdVARIABLE}/{IdVALOR}` | Variable + valor | `det` | array de valores hijo (jerarquía; con `det=2` incluye `JerarquiaPadres`) |

### Catálogos
| Endpoint | Input | Parámetros | Respuesta |
|---|---|---|---|
| `PERIODICIDADES` | — | — | array (1=Mensual, 3=Trimestral, 6=Semestral, 12=Anual, ...) |
| `PUBLICACIONES` | — | `det`, `tip` | array |
| `PUBLICACIONES_OPERACION/{IdOPERACION}` | Operación | `det`, `tip` | array |
| `PUBLICACIONFECHA_PUBLICACION/{IdPUBLICACION}` | Publicación | `det`, `tip` | array de fechas de publicación |
| `CLASIFICACIONES` | — | — | array |
| `CLASIFICACIONES_OPERACION/{IdOPERACION}` | Operación | — | array |

### Identificadores (input)
- **Tabla Tempus3**: parámetro `t` de `ine.es/jaxiT3/Tabla.htm?t=XXX`.
- **Tabla PC-Axis**: concatenación `path+file` de `ine.es/jaxi/Tabla.htm?path=AAA&file=BBB` → `AAABBB` (con barras).
- **Tabla tpx**: parámetro `tpx` de `ine.es/jaxi/Datos.htm?tpx=XXX&L=0`.
- **Serie**: solo Tempus3; parámetro `t` de `ine.es/jaxiT3/Datos.htm?t=XXX`, o campo `COD` de `SERIES_TABLA`.

## 4. Esquemas de respuesta

### Datos de serie — Tempus3, `tip=A` (recomendado)
```json
{
  "COD": "IPC251852",
  "Nombre": "Nacional. Índice general. Índice. ",
  "T3_Unidad": "Índice",
  "T3_Escala": " ",
  "Notas": [{"texto": "https://...", "Fk_TipoNota": 6, "textoTipo": null}],
  "Data": [
    {"Fecha": "2025-12-01T00:00:00.000+01:00", "T3_TipoDato": "Definitivo",
     "T3_Periodo": "M12", "Anyo": 2025, "Valor": 119.942}
  ]
}
```
`DATOS_TABLA` → array de estos objetos. `DATOS_SERIE` → un único objeto igual.

### Datos de serie — Tempus3, modo raw (sin `tip` o `--tip raw`)
```json
{
  "COD": "IPC251852", "Nombre": "...", "FK_Unidad": 133, "FK_Escala": 1,
  "Notas": [{"texto": "...", "Fk_TipoNota": 6, "textoTipo": null}],
  "Data": [{"Fecha": 1764543600000, "FK_TipoDato": 1, "FK_Periodo": 12,
            "Anyo": 2025, "Valor": 119.942, "Secreto": false}]
}
```
`Fecha` en **epoch ms**. `Secreto=true` indica dato confidencial. Los `FK_*` se resuelven con `det`/`tip=M` o los catálogos.

### Datos de tabla — pc-axis y tpx (idéntico para ambas fuentes)
```json
[
  {"Nombre": "TOTAL EDADES, TOTAL, Ambos sexos",
   "Data": [{"NombrePeriodo": "2022", "Valor": 47475420.0}]}
]
```
Sin `COD` ni `T3_*`; `NombrePeriodo` es la etiqueta completa del periodo (puede incluir "(avance)"); `Valor` puede ser `null`.

### Serie (metadatos) — `det=2&tip=A`
```json
{
  "COD": "IPC251852",
  "Operacion": {"Cod_IOE": "30138", "Codigo": "IPC", "Nombre": "Índice de Precios de Consumo (IPC)", "Url": "/dyngs/INEbase/..."},
  "Nombre": "Nacional. Índice general. Índice. ",
  "Decimales": 3,
  "Periodicidad": {"Nombre": "Mensual", "Codigo": "M"},
  "Publicacion": {"Nombre": "Índice de Precios de Consumo", "Periodicidad": {...},
                  "Operacion": [...], "PubFechaAct": {"Id": 12626, "Nombre": "... Avance. Julio 2026",
                  "Fecha": "2026-07-30T09:00:00.000+02:00", "T3_Periodo": "M07", "Anyo": 2026}},
  "Clasificacion": {"Nombre": "Base 2021 (IPC)", "Fecha": "2022-01-31T00:00:00.000+01:00"},
  "Escala": {"Nombre": " ", "Factor": "1E0", "Codigo": null},
  "Unidad": {"Nombre": "Índice", "Codigo": null, "Abrev": null}
}
```
`PubFechaAct` = última actualización de la serie. `Clasificacion` = versión/base (cuidado con series "ver.1"/"ver.2" por cambios de base).

### Operación
```json
{"Id": 25, "Cod_IOE": "30138", "Nombre": "Índice de Precios de Consumo (IPC)", "Codigo": "IPC",
 "Url": "/dyngs/INEbase/operacion.htm?c=..."}
```

### Tabla (`TABLAS_OPERACION` con `tip=A`)
```json
{"Id": 24077, "Nombre": "Índice general nacional. Series desde enero de 1961", "Codigo": "NAC",
 "T3_Periodicidad": "Mensual", "T3_Publicacion": "Índice de Precios de Consumo",
 "T3_Periodo_ini": "ene.", "Anyo_Periodo_ini": "1961",
 "FechaRef_fin": "null", "Ultima_Modificacion": "2026-07-15T09:00:00.000+02:00"}
```
⚠️ `FechaRef_fin` puede ser el **string `"null"`** (tabla al día). Sin `tip=A`, `Ultima_Modificacion` es epoch ms.

### Variables / valores
```json
{"Id": 3, "Nombre": "Tipo de dato", "Codigo": ""}
{"Id": 304092, "Variable": {"Id": 762, "Nombre": "Grupos ECOICOP", "Codigo": ""},
 "Nombre": "Índice general", "Codigo": "00"}
```
`VALORES_VARIABLE` usa `FK_Variable` en vez de objeto `Variable` (salvo `det`). `VALORES_GRUPOSTABLA` puede incluir `Nota`. `VALORES_HIJOS` con `det=2` incluye `JerarquiaPadres`.

### Metadatos de series de tabla pc-axis/tpx (`SERIES_TABLA?tip=M`)
```json
{"FK_Operacion": 22, "Nombre": "TOTAL EDADES, TOTAL, Ambos sexos", "Decimales": 0,
 "MetaData": [{"T3_Variable": "Sexo", "Nombre": "Ambos sexos", "Codigo": "ambossexos"}]}
```
`T3_Variable` + `Codigo` son los que se usan en `tv` alfanumérico.

## 5. Comportamientos verificados y límites

1. **`DATOS_SERIE` sin `nult` ni `date` → 404.** Es obligatorio uno de los dos.
2. **CSV/XLSX/px**: exportan la **tabla completa**; ignoran `nult`/`date`/`tip`; `tv` → 400. Disponibles para Tempus3 y tpx (tpx requiere prefijo `/tpx/` en la ruta: `/wstempus/csv/ES/DATOS_TABLA/tpx/{id}`). Las pc-axis no tienen exportación (204). `DATOS_SERIE` no tiene CSV (404).
3. **Codificación CSV**: el contenido real es **UTF-8 con BOM** aunque `Content-Type` diga `ISO-8859-15`. Decimales con coma. Cabecera = variables de la tabla; formato largo; periodo `2025M12`.
4. **Errores**: 404 → HTML (no JSON); parámetros inválidos suelen devolver 404 o ignorarse (`det=9` ignorado). No hay cabeceras de rate-limit; uso público sin clave.
5. **Tamaños**: `SERIES_OPERACION/IPC?page=1` ≈ 2,3 MB (det=0) y ≈ 10,7 MB (det=2). `DATOS_TABLA/50902?nult=1&tip=A` ≈ 14 KB. `SERIES_TABLA/50913` ≈ 250 KB. Planifica `nult`/`date`/`tv`/`search`.
6. **`OPERACIONES_DISPONIBLES`** tiene 112 elementos (una sola página; `page=2` → `[]`).
7. **Valores `null`** en `Data` (típico en tpx: periodos "avance" no publicados para todas las series) no son errores.
8. **`Notas`** de las series pueden contener URLs con códigos históricos de serie (p. ej. `IPC206446`); no confundir con el código vigente.
9. **Idioma EN** traduce nombres y `T3_TipoDato` ("Final value" vs "Definitivo"); códigos y estructura idénticos.
10. **Cache**: `jsCache` es un espejo equivalente para `SERIES_TABLA` (verificado: misma respuesta).
