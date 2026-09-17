# Verificación de metadatos

Cómo obtener el registro autorizado de cada tipo de fuente. Todos los endpoints de aquí se
comprobaron funcionando; si alguno falla, búscalo en la web antes de dar el dato por
imposible — nunca lo rellenes de memoria.

Cuando una API pida identificarte, usa una cabecera
`User-Agent: <algo>/1.0 (mailto:tu@correo)`. Crossref da prioridad a quien lo hace.

## Índice

1. [Con DOI](#1-con-doi)
2. [Con otro identificador](#2-con-otro-identificador)
3. [Sin identificador: literatura gris](#3-sin-identificador-literatura-gris)
4. [Buscar el PDF en acceso abierto](#4-buscar-el-pdf-en-acceso-abierto)
5. [Trampas conocidas](#5-trampas-conocidas)

---

## 1. Con DOI

**Content negotiation es la vía canónica.** Un solo endpoint sirve para Crossref y DataCite,
porque `doi.org` redirige a la agencia que registró el DOI:

```
curl -LH "Accept: application/vnd.citationstyles.csl+json" https://doi.org/10.1093/oxrep/grz002
```

Devuelve CSL-JSON: `type`, `title`, `author`, `container-title`, `volume`, `issue`, `page`,
`issued`, `publisher`, `abstract`, `ISSN`. Es lo mismo que consume Zotero cuando resuelves un
DOI con "Añadir por identificador", así que si esto trae el registro bien, la Vía A funcionará.

Alternativas cuando necesites campos que CSL no expone:

- **Crossref** — `https://api.crossref.org/works/{doi}`
  Más rico: `type`, `subtype`, `institution`, `abstract` (en JATS), `funder`, `license`,
  `relation`. Mira `type` para distinguir `posted-content` (preprint) de `journal-article`, y
  `institution` para detectar informes.
- **DataCite** — `https://api.datacite.org/dois/{doi}`
  Para datasets y repositorios. Los campos que necesitas para un ítem `dataset`:
  `attributes.publisher` (repositorio), `attributes.version`, `attributes.publicationYear`,
  `attributes.types.resourceTypeGeneral`, `attributes.descriptions`.
  `relatedIdentifiers` con `IsVersionOf` te dice si estás ante una versión concreta o el DOI
  paraguas de todas las versiones — importante: cita la versión concreta.
- **OpenAlex** — `https://api.openalex.org/works/doi:{doi}`
  Bueno para desambiguar: da `type`, `primary_location.source` (revista o repositorio),
  `open_access.oa_url` (¡PDF libre!), `best_oa_location`, y las versiones alternativas del
  mismo trabajo en `locations`. Sin clave y sin límite práctico.
- **Semantic Scholar** — `https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,year,venue,abstract,openAccessPdf,externalIds`
  Útil sobre todo por `openAccessPdf` y por `externalIds` (te da el arXiv ID y el PMID a
  partir del DOI).

---

## 2. Con otro identificador

**arXiv** — `http://export.arxiv.org/api/query?id_list=2401.00001`
Atom XML. Fíjate en `<published>` (v1) frente a `<updated>` (última versión), y en
`arxiv:doi` / `arxiv:journal_ref`: si están, el trabajo **ya se publicó** y probablemente
debas dar de alta el artículo de revista, no el preprint.

**PubMed** — `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json`
Para el registro completo con resumen, `efetch.fcgi` con `retmode=xml`.

**ISBN** — `https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data`
OpenLibrary flojea con libros no anglosajones. Para publicaciones españolas, la ficha del
ISBN del Ministerio de Cultura y los catálogos de la BNE o de la propia editorial son más
fiables. Zotero también acepta ISBN directamente en "Añadir por identificador" y consulta
varios catálogos nacionales, así que en libros la Vía A suele ganar.

**Handle / URN** (repositorios institucionales) — resuélvelo (`https://hdl.handle.net/{handle}`)
y usa la ficha del repositorio como fuente.

---

## 3. Sin identificador: literatura gris

Es el caso más frecuente en informes de organismos y el que peor resuelven los agregadores.
**La web oficial del emisor manda.** Ve a la ficha del documento en el sitio del organismo y
saca de ahí: título exacto, autoría (personal o institucional), serie, número, mes y año,
lugar y URL directa al PDF.

Sitios de referencia por emisor:

| Emisor | Dónde mirar |
|---|---|
| OCDE | `oecd.org/publications`, iLibrary — traen DOI propio y número de working paper |
| FMI | `imf.org/en/Publications` — la serie y el `WP/AA/NNN` están en la portada |
| Banco Mundial | `openknowledge.worldbank.org` — handle + PDF abierto |
| OIT / ILO | `ilo.org/publications` |
| Comisión Europea | `op.europa.eu` (Publications Office) — trae ISBN y número de catálogo |
| Eurostat / INE | ficha del conjunto de datos, no la tabla: necesitas versión y fecha |
| Bancos centrales | serie de working papers propia, con número |
| Think tanks | la ficha del informe; ojo con las reediciones sin cambio de fecha |
| RePEc / EconPapers | `ideas.repec.org` — buen agregador de working papers en economía |

Si el organismo publica el documento en varias lenguas, da de alta **la versión que el
usuario va a citar** y anota la otra en el campo Extra.

---

## 4. Buscar el PDF en acceso abierto

Merece la pena porque un ítem sin texto completo no sirve para trabajar. Por orden:

1. **OpenAlex** `open_access.oa_url` o `best_oa_location.pdf_url` — ya lo tienes si
   consultaste OpenAlex en el paso anterior.
2. **Unpaywall** — `https://api.unpaywall.org/v2/{doi}?email=tu@correo`
   `best_oa_location.url_for_pdf` es la URL directa. Requiere el parámetro `email`.
3. **Semantic Scholar** `openAccessPdf.url`.
4. **arXiv** — `https://arxiv.org/pdf/{id}` es siempre directa.
5. **Repositorio institucional del autor** o **web del organismo**, para literatura gris.

Comprueba que la URL apunta **al PDF** y no a la landing page: debe terminar en `.pdf` o
servir `application/pdf`. Una landing page en `L1` no adjunta nada.

Al comprobarlo, **manda una cabecera `User-Agent` de navegador**. Muchos sitios
institucionales (Drupal, Cloudflare) devuelven `403` a una petición con el agente por defecto
de un script, y esa negativa no dice nada sobre la URL: Zotero se identifica como navegador y
la descargará sin problema. Un `403` con agente de script no es motivo para descartar un
enlace; un `404`, o un `Content-Type` que sea HTML, sí.

Si solo hay versión de pago, no busques atajos: indícalo y ofrece el paso de adjuntar el
enlace, o el botón de Zotero para buscar el PDF disponible, que respeta los accesos
institucionales del usuario.

---

## 5. Trampas conocidas

- **Crossref llama `journal-article` a muchos informes.** Su `type` describe cómo se registró
  el DOI, no qué es el documento. Si la portada dice "Working Paper" y hay número de serie,
  es un `report`.
- **`posted-content` en Crossref = preprint.** Mira también `subtype`.
- **Resúmenes en JATS.** Crossref devuelve el `abstract` con etiquetas `<jats:p>`. Límpialas
  antes de meterlas en `AB`.
- **DOI de concepto frente a DOI de versión** en Zenodo y similares. El DOI "de concepto"
  apunta siempre a la última versión y por tanto no es citable de forma estable. Usa el DOI de
  la versión concreta y rellena `ET` con esa versión.
- **Fechas discrepantes.** *Online first* frente a número impreso: usa la de la versión de
  registro que se cita, y si difieren de forma relevante anótalo en Extra.
- **Nombres con partículas** (`de`, `van`, `van der`, `Ben`). Van dentro del apellido:
  `AU  - Van Parijs, Philippe`, `AU  - Román de Lara, María Victoria`. Partirlos mal rompe
  tanto la cita como la clave de Better BibTeX.
- **Nombres compuestos españoles.** Dos apellidos son **un solo apellido** a efectos de
  Zotero: `AU  - Marín Cánovas, José`.
- **Títulos con mayúsculas de estilo editorial** (`THE FUTURE OF WORK`). Normalízalos a la
  capitalización real del documento; Zotero no lo hace solo y la cita saldrá gritando.
