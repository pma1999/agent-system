---
name: zotero-intake
description: 'Convierte cualquier fuente bibliográfica en un alta perfecta, verificada y lista para copiar-pegar en Zotero. Usa esta skill SIEMPRE que el usuario comparta o mencione un paper, artículo, informe, working paper, dataset, tesis, capítulo, preprint, ponencia, página web, DOI, ISBN, ID de arXiv o URL de un repositorio y quiera meterlo, añadirlo, guardarlo, darlo de alta, citarlo o referenciarlo en Zotero — también cuando solo diga "añade esto a Zotero", "cómo cito esto", "mete este PDF en mi biblioteca", "pásame el RIS/BibTeX de esto" o pegue una referencia suelta que haya que normalizar. Aplícala aunque el usuario no diga "Zotero" explícitamente si el contexto es gestionar su biblioteca de referencias. Verifica los metadatos contra fuentes autorizadas (Crossref, DataCite, OpenAlex, arXiv, PubMed, la web del organismo emisor) antes de producir nada, elige el tipo de ítem correcto y entrega la vía más rápida y segura: identificador, fichero RIS generado o pasos manuales.'
---

# Alta de fuentes en Zotero

Un alta mediocre en Zotero no se nota el día que la haces: se nota dos años después,
cuando la bibliografía final sale con el tipo de ítem equivocado, el informe citado como
si fuera artículo de revista, o el dataset sin versión ni repositorio. Arreglarlo entonces
cuesta muchísimo; hacerlo bien ahora cuesta dos minutos. Por eso esta skill invierte en
**verificar antes de escribir** y en entregar algo que el usuario pueda pegar sin pensar.

Todo lo que produzcas va **en español**, salvo los metadatos de la fuente (título, resumen,
editorial, nombres), que se conservan **exactamente** en su idioma original. Traducir un
título rompe la cita.

## Regla que gobierna todo lo demás: no inventes campos

Si no has verificado un dato, no lo pongas. Un campo ausente es un hueco que el usuario
rellena en diez segundos; un campo inventado es un error que sobrevive a la tesis. Cuando
dudes entre omitir y adivinar, omite y dilo en el apartado de avisos.

## Paso 0 — Lee el destino y reconoce tu entorno

**Empieza leyendo `references/biblioteca-usuario.md`**, siempre, en cualquier modo. Ahí está
en qué biblioteca y colección concretas entra el material, y equivocarse de biblioteca es el
fallo más caro de todos: los pasos que entregues tienen que nombrar el destino explícitamente
o el usuario importará donde no toca.

Tus capacidades cambian además según dónde se ejecute esta skill. Detéctalo antes de prometer
nada:

| Entorno | Cómo lo sabes | Qué puedes ofrecer |
|---|---|---|
| **Web** (claude.ai, ChatGPT sin sandbox) | No tienes shell ni escritura de ficheros | Bloque para copiar-pegar + pasos. Es el modo por defecto y siempre debe funcionar |
| **Fichero** | Puedes escribir ficheros o adjuntar descargas | Además, genera un `.ris` real que el usuario importa con un doble clic |
| **Local** | Tienes shell **y** Zotero corre en este mismo PC | Además, comprueba duplicados y normaliza etiquetas antes de entregar |

En modo Local, ejecuta `python scripts/zotero_probe.py --check` antes de nada. Si Zotero no
responde, degrada a modo Fichero sin dramatizar: dilo en una línea y sigue.

**No escribas nunca en la biblioteca del usuario por iniciativa propia.** El entregable es
asesor: el usuario ejecuta el alta. Solo actúa si lo pide de forma explícita e inequívoca
("añádelo tú"), y aun entonces confirma el destino antes.

## Paso 1 — Verifica los metadatos contra la fuente autorizada

Esta es la parte que separa un alta perfecta de una plausible. Nunca construyas la
referencia a partir de lo que aparente el PDF ni de lo que recuerdes: los PDF llevan
portadas de preprint desactualizadas, las páginas de repositorio copian mal los volúmenes y
las citas que circulan por ahí arrastran erratas.

Orden de preferencia, parando en cuanto obtengas un registro completo:

1. **Hay DOI** → resuélvelo y usa ese registro como verdad. Crossref para literatura
   publicada, DataCite para datasets y repositorios.
2. **Hay otro identificador** (arXiv, PMID, ISBN, handle, OpenAlex ID) → resuélvelo en su
   servicio nativo.
3. **No hay identificador** (típico en literatura gris: informes de organismos, documentos
   de trabajo, notas de política) → la **web oficial del organismo emisor** es la fuente
   autorizada. La ficha de la propia institución manda sobre cualquier agregador.
4. **Nada de lo anterior** → reconstruye con lo que aporte el usuario y marca cada campo
   dudoso en avisos.

El detalle operativo de cada servicio (endpoints, qué campo mirar, trampas conocidas) está
en `references/fuentes-metadatos.md`. Léelo cuando trabajes con un tipo de fuente que no
domines o cuando un registro venga incompleto.

Contrasta además **dos cosas que casi siempre vienen mal**:

- **Versión.** ¿Preprint, versión aceptada o versión publicada? Cambia el tipo de ítem y a
  veces el año. Si el usuario te pasa un PDF de repositorio, lo más probable es que no sea
  la versión de registro.
- **Autoría institucional.** Muchos informes no tienen autores personales aunque el PDF
  liste colaboradores. Si el organismo firma, el autor es el organismo.

## Paso 2 — Elige el tipo de ítem de Zotero

Aquí se pierden más altas que en ningún otro sitio. Los tres errores caros:

- Un **working paper / informe de organismo** guardado como `journalArticle`. Es `report`,
  con institución, número y tipo de informe.
- Un **preprint** guardado como `journalArticle`. Es `preprint`, con su repositorio.
- Un **dataset** guardado como `document` o `webpage`. Es `dataset`, con repositorio,
  versión y DOI.

`references/tipos-y-ris.md` tiene el árbol de decisión completo y la plantilla RIS de cada
tipo. Consúltalo siempre que la fuente no sea un artículo de revista evidente.

## Paso 3 — Elige la vía de alta

Escoge **una** y di en una línea por qué. Más rápido y menos manipulable siempre gana.

**Vía A — Identificador** (preferente siempre que exista y resuelva).
Zotero descarga los metadatos canónicos él mismo, así que acierta tipos que otros formatos
no saben expresar —`preprint` y `dataset` entre ellos— y no hay nada que el usuario pueda
pegar mal. Basta un DOI, un ID de arXiv, un PMID o un ISBN.

**Vía B — Fichero o bloque RIS** (cuando no hay identificador que resuelva, o el registro
oficial está incompleto y hay que corregirlo).
Tú construyes el RIS ya auditado. Si el editor ofrece su propia exportación, tómala como
punto de partida pero **revísala**: las exportaciones de editorial traen tipos mal puestos y
resúmenes truncados con frecuencia.

**Vía C — Manual** (cuando ni identificador ni RIS pueden expresar el ítem correctamente).
El caso claro es un **preprint sin DOI**: el importador RIS de Zotero no tiene tipo preprint
y lo convertiría en artículo de revista. Antes que entregar un ítem con el tipo equivocado,
entrega los campos uno a uno.

Si el usuario pide expresamente una vía concreta, dásela aunque no sea la que elegirías, y
menciona en una línea qué pierde.

## Paso 4 — Construye el entregable

### Vía A
Da el identificador **solo**, en su forma limpia (`10.1093/oxrep/grz002`, no la URL
envolvente). Zotero acepta varios a la vez, uno por línea.

### Vía B: reglas del RIS que hay que respetar

El importador de Zotero es estricto y silencioso: cuando algo no encaja lo deja caer en una
nota y no avisa. Estas reglas evitan justamente eso.

- **Formato de línea:** `XX  - valor`, con **dos espacios** antes del guion. El fichero
  empieza por `TY  - ` y cada registro cierra con `ER  - `.
- **UTF-8 sin BOM.**
- **Autores:** `AU  - Apellido, Nombre`. Sin coma → Zotero lo trata como **autor
  institucional** de un solo campo, que es justo lo que quieres para
  `AU  - Organisation for Economic Co-operation and Development`. Cuidado: si el nombre del
  organismo lleva coma, Zotero partirá por ella y creará un apellido falso — reescríbelo sin
  coma.
- **Las etiquetas cambian de significado según el tipo.** `PB` es editorial en un libro,
  **institución** en un `RPRT`, **repositorio** en un `DATA` y **universidad** en un `THES`.
  Usa la tabla de `references/tipos-y-ris.md`: una etiqueta que no sea válida para ese tipo
  se pierde en una nota.
- **Fechas:** `PY  - 2024` y `DA  - 2024/06/15` (mes y día opcionales: `DA  - 2024/06//`).
- **Resumen:** `AB  - `, en idioma original, sin recortar.
- **PDF incluido:** `L1  - https://…/fichero.pdf` hace que Zotero **descargue y adjunte el
  PDF** al importar el fichero desde disco. Es la diferencia entre un ítem y un ítem
  utilizable, así que inclúyelo siempre que tengas una URL **directa y legal** al PDF. `L2`
  para captura HTML. Para *enlazar* sin descargar (informes vivos, portales de datos), omite
  `L1` y usa el paso manual de adjuntar enlace web.
- **Si el RIS lleva `L1`, los pasos deben decir "guarda el `.ris` y usa Archivo →
  Importar...", nunca "Importar desde el portapapeles."** La descarga del adjunto está
  comprobada en la ruta de importación de fichero; por el portapapeles no. Cuando no haya
  `L1`, el portapapeles es cómodo y perfectamente válido.
- **Nunca escribas una URL en `L1` que no hayas abierto.** Esta es la regla más importante de
  toda la sección, porque su fallo es invisible: si la URL no existe, Zotero se la come sin
  decir nada y el usuario acaba con un ítem sin PDF creyendo que lo tiene. La URL se **copia
  del `href` real** de la página del editor o del repositorio; jamás se deduce del patrón de
  otra URL parecida ni se completa de memoria — un guion en vez de un guion bajo ya es un 404.
  Si no puedes abrir la URL para comprobarla, **omite `L1`** y entrega en su lugar el paso de
  adjuntar el PDF a mano: un ítem al que le falta el adjunto es un inconveniente, pero uno que
  miente sobre tenerlo es un error.
- **Idioma:** `LA  - spa` / `LA  - eng` (ISO 639).

**Etiquetas temáticas (`KW`): por defecto, no las metas.** Una biblioteca madura arrastra
variantes de mayúsculas de la misma etiqueta, y cada `KW` con un casing nuevo agrava el
problema. Propón las etiquetas en el apartado de verificación para que el usuario las elija
desde el autocompletado de Zotero, que reutiliza las existentes. En modo Local,
`scripts/zotero_probe.py --tags "<término>"` te da la forma que ya existe: entonces sí,
inclúyelas en `KW` con ese casing exacto.

En modo Fichero, escribe el `.ris` en disco y **valídalo** con
`python scripts/validate_ris.py <fichero>` antes de entregarlo. Comprueba el formato de línea,
el `TY`/`ER`, que cada etiqueta sea válida para ese tipo, y —lo que más te va a salvar— que
las URLs de `L1`/`UR` respondan y sirvan lo que dicen servir. No entregues un fichero que no
salga con cero errores.

Si no puedes ejecutar el validador, comprueba a mano esas cuatro cosas; la de las URLs no es
opcional por no tener el script.

### Vía C
Da los campos en una tabla `Campo de Zotero → valor exacto`, en el orden en que aparecen en
el panel derecho de Zotero, para que el usuario los recorra sin saltar.

## Paso 5 — Cierra el alta

Un ítem importado no está terminado. Añade siempre:

- **Destino:** biblioteca y colección concretas, nombradas. Si el usuario tiene un destino
  fijo configurado está en `references/biblioteca-usuario.md`; léelo al empezar.
- **Adjunto:** si el PDF no viaja en el RIS, el paso explícito para adjuntarlo. Busca
  activamente una **versión de acceso abierto legal** (repositorio institucional, arXiv, web
  del organismo, Unpaywall) y da la URL directa. Si no la hay, dilo y ofrece el paso de
  adjuntar enlace en vez de fichero.
- **Verificación:** tabla corta de los campos que suelen entrar mal en ese tipo concreto,
  con el valor que el usuario debería ver. No repitas todo el registro: solo lo frágil.
- **Clave de cita** que generará Better BibTeX, si el usuario lo usa. Algoritmo y formato
  configurado en `references/biblioteca-usuario.md`.
- **Avisos**, solo si los hay: posible duplicado, versión ambigua, metadatos oficiales
  incompletos, campo que has dejado vacío a propósito.

## Formato de salida

Usa esta estructura. Es corta a propósito: el usuario quiere ejecutar, no leer.

```
## Qué es
[Una línea: qué es la fuente y qué tipo de ítem de Zotero le corresponde, con el porqué si
no es obvio.]

## Vía: [A identificador | B RIS | C manual]
[Una línea justificándola.]

## Pasos
1. …
2. …

## Para copiar
[Un único bloque de código: el identificador, o el RIS completo. Se omite en Vía C.]

## Adjunto
[URL directa al PDF de acceso abierto, o el paso para adjuntarlo/enlazarlo.]

## Comprueba después de importar
| Campo | Debe quedar |
|---|---|
| … | … |

Clave de cita: `…`

## Avisos
[Solo si los hay. Si no, omite el apartado entero.]
```

Los nombres de menú van **exactamente** como aparecen en el Zotero del usuario, en su idioma
de interfaz. Las etiquetas en español están en `references/biblioteca-usuario.md`.

## Errores que arruinan un alta

- Entregar `TY  - JOUR` para algo que no es artículo de revista porque el registro de
  Crossref lo llamaba así. Crossref clasifica muchos informes como artículo: manda lo que la
  fuente **es**, no cómo la etiquetó el agregador.
- Rellenar `IS`/`VL` en un `RPRT` o un `DATA`: no son campos válidos ahí y se pierden.
- Poner el número de informe en `M1`. Va en `SN`.
- Dar la URL de la landing page en `L1`. `L1` necesita la URL **directa al PDF** o no
  adjuntará nada.
- Deducir la URL del PDF a partir de otra parecida. Los sitios institucionales mezclan guiones
  y guiones bajos sin criterio (`..._no_remunerado.pdf` frente a `..._no-remunerado.pdf`), y
  el fallo no se ve: el ítem entra bien y el PDF simplemente no aparece. Copia el `href`.
- Traducir el título o el resumen. Nunca.
- Añadir el ítem sin mirar si ya está. En bibliotecas grandes el duplicado es el fallo más
  frecuente: en modo Local compruébalo, y en los demás recuérdaselo al usuario en una línea.

## Ficheros de apoyo

- `references/tipos-y-ris.md` — árbol de decisión de tipo de ítem, mapa completo etiqueta
  RIS ↔ campo de Zotero por tipo, y plantillas listas para rellenar. Léelo siempre que la
  fuente no sea un artículo de revista evidente.
- `references/fuentes-metadatos.md` — cómo verificar en Crossref, DataCite, OpenAlex, arXiv,
  PubMed, Unpaywall, ISBN y literatura gris; trampas de cada uno.
- `references/biblioteca-usuario.md` — configuración concreta del usuario: bibliotecas,
  colección de destino, idioma de interfaz, formato de clave Better BibTeX. Léelo al empezar
  en cualquier modo.
- `scripts/validate_ris.py` — valida un `.ris` contra el importador de Zotero. Solo stdlib.
- `scripts/zotero_probe.py` — modo Local: Zotero activo, duplicados y casing de etiquetas.
