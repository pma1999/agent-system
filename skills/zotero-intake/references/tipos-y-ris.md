# Tipo de ítem y plantillas RIS

Todo lo que hay aquí está extraído del traductor `RIS.js` que Zotero 7 usa realmente para
importar, no de la especificación RIS genérica. Donde ambos discrepan, manda esto.

## Índice

1. [Árbol de decisión del tipo de ítem](#1-árbol-de-decisión-del-tipo-de-ítem)
2. [Tabla TY ↔ tipo de Zotero](#2-tabla-ty--tipo-de-zotero)
3. [Etiquetas válidas para cualquier tipo](#3-etiquetas-válidas-para-cualquier-tipo)
4. [Etiquetas que cambian de significado según el tipo](#4-etiquetas-que-cambian-de-significado-según-el-tipo)
5. [Plantillas por tipo](#5-plantillas-por-tipo)
6. [Lo que RIS no puede expresar](#6-lo-que-ris-no-puede-expresar)

---

## 1. Árbol de decisión del tipo de ítem

Pregunta en este orden y para en la primera que dé sí.

**¿Son datos, no un texto?** (tabla, encuesta, serie, código de un repositorio de datos:
Zenodo, Dataverse, ICPSR, figshare, Dryad, OSF, portal estadístico oficial)
→ `dataset`. Si es software ejecutable en vez de datos → `computerProgram`.

**¿Está depositado en un servidor de preprints y aún no ha pasado revisión?** (arXiv, SSRN,
OSF Preprints, SocArXiv, bioRxiv, RePEc como working paper de serie académica)
→ `preprint`. Ojo: si ya salió publicado en revista, la versión de registro es el
`journalArticle`; usa el preprint solo si el usuario cita expresamente esa versión.

**¿Lo publica una institución bajo su propio sello, fuera de una revista?** (banco central,
ministerio, OCDE, OIT, FMI, Banco Mundial, Comisión Europea, think tank, universidad como
editora de una serie de working papers)
→ `report`. Este es el gran cajón de la literatura gris y el error más común es meterlo en
`journalArticle`.

**¿Es una tesis o TFM?** → `thesis`.

**¿Salió en actas de un congreso?** → `conferencePaper`. Si solo fue una ponencia sin actas
→ `presentation`.

**¿Es un capítulo dentro de un libro con editores?** → `bookSection`.

**¿Es un libro completo?** → `book`.

**¿Salió en una revista con volumen/número?** → `journalArticle`. Si es prensa generalista
→ `newspaperArticle`; si es revista divulgativa → `magazineArticle`.

**¿Es una página web sin equivalente impreso?** → `webpage`. Es el último recurso: una
página web que en realidad presenta un informe descargable es un `report`, no un `webpage`.

### Señales de que es `report` y no `journalArticle`

- La cabecera del PDF dice "Working Paper", "Discussion Paper", "Policy Brief",
  "Occasional Paper", "Staff Report", "Technical Report", "Documento de Trabajo".
- Tiene un número de serie propio del organismo (`WP/24/117`, `No. 2024/03`).
- No hay volumen ni número de revista, pero sí una serie institucional.
- El DOI, si lo hay, lo registró el propio organismo.

Crossref y muchos agregadores devuelven `journal-article` para estos documentos. **No les
hagas caso**: manda la naturaleza de la fuente.

---

## 2. Tabla TY ↔ tipo de Zotero

Lo que Zotero **exporta**, y por tanto lo que debes escribir para que reimporte idéntico:

| Tipo de Zotero | `TY` |
|---|---|
| journalArticle | `JOUR` |
| bookSection | `CHAP` |
| book | `BOOK` |
| report | `RPRT` |
| dataset | `DATA` |
| thesis | `THES` |
| conferencePaper | `CONF` |
| magazineArticle | `MGZN` |
| newspaperArticle | `NEWS` |
| blogPost | `BLOG` |
| webpage | `ELEC` |
| computerProgram | `COMP` |
| manuscript | `MANSCPT` |
| presentation | `SLIDE` |
| map | `MAP` |
| audioRecording | `SOUND` |
| videoRecording | `VIDEO` |
| film | `MPCT` |
| artwork | `ART` |
| patent | `PAT` |
| case | `CASE` |
| statute | `STAT` |
| bill | `BILL` |
| hearing | `HEAR` |
| letter | `PCOMM` |
| dictionaryEntry | `DICT` |
| encyclopediaArticle | `ENCYC` |

Equivalencias adicionales que Zotero **acepta al importar** (útiles si auditas un RIS ajeno):
`GOVDOC` y `STAND` → `report`; `DBASE` → `dataset`; `EJOUR`, `JFULL`, `ABST` y `GEN` →
`journalArticle`; `ECHAP` → `bookSection`; `EBOOK`, `EDBOOK`, `CLSWK`, `SER` → `book`;
`CPAPER` → `conferencePaper`; `WEB` → `webpage`; `INPR`, `UNPD`, `PAMP`, `UNBILL` →
`manuscript`.

Un `TY` desconocido cae en `journalArticle`. Por eso una etiqueta mal escrita no da error:
da un ítem silenciosamente mal tipado.

---

## 3. Etiquetas válidas para cualquier tipo

| RIS | Campo de Zotero | Notas |
|---|---|---|
| `TI` | title | |
| `AU` | autor | `Apellido, Nombre`. Sin coma → autor institucional (campo único) |
| `A2` | editor / seriesEditor / recipient | depende del tipo, ver §4 |
| `A4` | translator (o contributor en `CONF`/`DATA`) | |
| `AB` | abstractNote | admite varias líneas; se conservan los saltos |
| `DO` | DOI | Zotero lo limpia solo; da `10.xxxx/yyyy` sin `https://doi.org/` |
| `KW` | tags | una etiqueta por línea `KW`; también admite separación por `;` |
| `LA` | language | ISO 639: `spa`, `eng`, `fra`, `deu` |
| `UR` | url | |
| `Y2` | accessDate | |
| `ST` | shortTitle | |
| `DP` | libraryCatalog | |
| `DB` | archive | |
| `AN` | archiveLocation | |
| `CN` | callNumber | |
| `J2` | journalAbbreviation | |
| `N1` | nota hija | crea una nota adjunta al ítem |
| `L1` | adjunto PDF | URL **directa al PDF** (se descarga) o ruta absoluta local |
| `L2` | adjunto HTML | captura, título "Full Text (HTML)" |
| `L4` | otro adjunto | |
| `PY` | date (solo año) | |
| `DA` | date (completa) | `AAAA/MM/DD`; parciales: `2024/06//` |
| `ER` | fin de registro | obligatorio, línea `ER  - ` |

También se importan, aunque Zotero no los exporte así: `N2` → abstractNote, `EP` → página
final, `CR` → rights, `JF` → publicationTitle, `JA`/`JO` → journalAbbreviation,
`ED` → editor, `M2` → extra.

---

## 4. Etiquetas que cambian de significado según el tipo

Esta tabla es la razón de ser de este fichero. Una etiqueta usada fuera de su tipo **no da
error**: Zotero la descarta a una nota y el campo queda vacío.

### `PB`
| Tipo | Significado |
|---|---|
| book, bookSection, conferencePaper | publisher |
| **report** | **institution** |
| **dataset** | **repository** |
| **thesis** | **university** |
| computerProgram | company |
| audioRecording | label |
| film | distributor |

### `T2`
| Tipo | Significado |
|---|---|
| journalArticle, magazineArticle, newspaperArticle | publicationTitle |
| **bookSection** | **bookTitle** |
| **conferencePaper** | **conferenceName** |
| **report**, computerProgram, map | **seriesTitle** |
| book | series |
| webpage | websiteTitle |
| blogPost | blogTitle |
| presentation | meetingName |

### `SN`
| Tipo | Significado |
|---|---|
| journalArticle, magazineArticle, newspaperArticle | ISSN |
| book, bookSection, conferencePaper | ISBN |
| **report** | **reportNumber** |
| patent | patentNumber |

### `M3`
| Tipo | Significado |
|---|---|
| **report** | **reportType** ("Working Paper", "Policy Brief"…) |
| **thesis** | **thesisType** ("Tesis doctoral", "PhD thesis"…) |
| webpage, blogPost | websiteType |
| manuscript | manuscriptType |
| presentation | presentationType |

### `ET`
| Tipo | Significado |
|---|---|
| casi todos | edition |
| **dataset**, computerProgram | **versionNumber** |

### `CY`
| Tipo | Significado |
|---|---|
| casi todos | place |
| **dataset** | **repositoryLocation** |
| conferencePaper | *no usar* — el lugar va en `C1` |

### `SP` / `EP`
| Tipo | Significado |
|---|---|
| journalArticle, bookSection, conferencePaper | páginas (`SP` inicial, `EP` final) |
| book, thesis, manuscript | `SP` = numPages |

### Otras específicas
| RIS | Tipo | Campo |
|---|---|---|
| `C1` | conferencePaper | place |
| `C3` | conferencePaper | proceedingsTitle |
| `T3` | journalArticle, bookSection, conferencePaper | series |
| `SV` | bookSection | seriesNumber |
| `M1` | book | seriesNumber |
| `IS` | bookSection | numberOfVolumes |
| `NV` | dataset | identifier |
| `C2` | bookSection | bookAuthor |
| `A2` | journalArticle, bookSection, conferencePaper | editor |
| `A2` | book, report | seriesEditor |
| `A3` | book | editor |
| `A3` | thesis | contributor |

**No válidos y por tanto descartados:** `VL`/`IS` en `report`, `dataset`, `webpage` o
`thesis`. Si tienes un número de serie de informe, va en `SN`, no en `VL`.

---

## 5. Plantillas por tipo

Rellena y borra las líneas que no tengas. Nunca dejes una etiqueta con valor inventado.

### journalArticle
```
TY  - JOUR
AU  - Apellido, Nombre
AU  - Apellido2, Nombre2
TI  - Título exacto del artículo
T2  - Nombre completo de la revista
VL  - 12
IS  - 3
SP  - 145
EP  - 168
PY  - 2024
DA  - 2024/06/15
DO  - 10.1234/ejemplo.2024.001
SN  - 1234-5678
LA  - eng
AB  - Resumen en idioma original.
UR  - https://…
L1  - https://…/articulo.pdf
ER  - 
```

### report (informe, working paper, policy brief)
```
TY  - RPRT
AU  - Organisation for Economic Co-operation and Development
TI  - Título exacto del informe
PB  - Nombre del organismo que lo publica
CY  - París
T2  - Nombre de la serie
SN  - No. 2024/03
M3  - Working Paper
PY  - 2024
DA  - 2024/03//
DO  - 10.1234/ejemplo
LA  - eng
AB  - Resumen o sumario ejecutivo.
UR  - https://…
L1  - https://…/informe.pdf
ER  - 
```
`PB` = institución, `SN` = número de informe, `M3` = tipo de informe, `T2` = serie.
Sin `VL` ni `IS`.

### dataset
```
TY  - DATA
AU  - Apellido, Nombre
TI  - Título exacto del conjunto de datos
PB  - Zenodo
CY  - Ginebra
ET  - v2.1
PY  - 2024
DA  - 2024/05/20
DO  - 10.5281/zenodo.1234567
LA  - eng
AB  - Descripción del conjunto de datos.
UR  - https://doi.org/10.5281/zenodo.1234567
ER  - 
```
`PB` = repositorio, `CY` = ubicación del repositorio, `ET` = versión, `NV` = identificador
interno si lo hay. Sin `VL` ni `IS`. Cita **siempre la versión concreta** que se usó: un
dataset sin versión es irreproducible.

### thesis
```
TY  - THES
AU  - Apellido, Nombre
TI  - Título exacto de la tesis
PB  - Universidad Complutense de Madrid
CY  - Madrid
M3  - Tesis doctoral
SP  - 312
PY  - 2023
DA  - 2023/09//
LA  - spa
AB  - Resumen.
UR  - https://…
L1  - https://…/tesis.pdf
ER  - 
```

### conferencePaper
```
TY  - CONF
AU  - Apellido, Nombre
TI  - Título de la comunicación
T2  - Nombre del congreso
C3  - Título de las actas
C1  - Pontevedra
PB  - Editorial de las actas
SP  - 891
EP  - 893
PY  - 2024
DA  - 2024/06/18
SN  - 978-84-1188-045-9
DO  - 10.1234/ejemplo
LA  - eng
AB  - Resumen.
UR  - https://…
ER  - 
```
El lugar va en `C1`, **no** en `CY`.

### bookSection
```
TY  - CHAP
AU  - Apellido, Nombre
A2  - ApellidoEditor, NombreEditor
TI  - Título del capítulo
T2  - Título del libro
PB  - Editorial
CY  - Barcelona
SP  - 45
EP  - 72
PY  - 2022
SN  - 978-84-000-0000-0
LA  - spa
AB  - Resumen.
ER  - 
```

### book
```
TY  - BOOK
AU  - Apellido, Nombre
TI  - Título del libro
PB  - Editorial
CY  - Madrid
ET  - 2ª ed.
SP  - 428
PY  - 2021
SN  - 978-84-000-0000-0
LA  - spa
AB  - Resumen.
ER  - 
```

### webpage
```
TY  - ELEC
AU  - Nombre del organismo
TI  - Título de la página
T2  - Nombre del sitio web
PY  - 2025
DA  - 2025/02/10
Y2  - 2026/08/30
LA  - spa
UR  - https://…
ER  - 
```
`Y2` es la fecha de consulta. Sin `VL`.

---

## 6. Lo que RIS no puede expresar

- **`preprint`.** No existe en el mapa de tipos de RIS. Un preprint importado por RIS acaba
  como `journalArticle`. Opciones, en orden: (a) darlo de alta por DOI o ID de arXiv, que sí
  produce el tipo correcto; (b) importar el RIS y cambiar el tipo a mano en Zotero;
  (c) alta manual. Nunca entregues un RIS de preprint sin advertirlo.
- **Adjunto como enlace en vez de fichero.** `L1` siempre descarga. Para enlazar sin
  descargar, el usuario tiene que usar el menú de adjuntar enlace web.
- **La colección de destino.** El RIS no la lleva: el ítem entra en la biblioteca y colección
  **seleccionadas en ese momento** en Zotero. Por eso el primer paso de toda importación es
  seleccionar el destino.
- **Autores institucionales con coma en el nombre.** Zotero parte por la primera coma.
  Reescribe `Banco de España, Servicio de Estudios` como `Banco de España Servicio de
  Estudios` o usa solo `Banco de España`.
