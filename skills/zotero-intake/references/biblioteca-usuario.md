# Configuración concreta de esta biblioteca

Todo lo de aquí está leído de la instalación real, no supuesto. Si el usuario cambia su
montaje, actualiza este fichero.

## Destino

**Biblioteca:** grupo **`Tesis_RBU`** (ID de grupo `6139303`).
**No** "Mi biblioteca": ahí solo hay material residual. Prácticamente todo el corpus de la
tesis vive en el grupo, y mover ítems entre biblioteca personal y de grupo después no es
limpio (cambian las claves y se pierden relaciones). Si el paso 1 no dice explícitamente
"selecciona `Tesis_RBU`", el usuario acabará importando en el sitio equivocado.

**Colección:** siempre **`00_Inbox`**. Es la decisión del usuario: todo entra por el Inbox y
él lo clasifica después en el cribado. No propongas otra colección salvo que te lo pida.

Circuito completo, por si necesitas nombrarlo:

```
00_Inbox  →  01_Screening  →  02_Incluidos_A
                           →  03_Contexto_B
                           →  04_Excluidos
99_Anexos   (material de apoyo, fuera del circuito de cribado)
```

## Entorno

- Zotero 7 en Windows, interfaz en **español (es-ES)**.
- Directorio de datos: `C:\Users\PcVIP\Zotero`.
- Estilo de citación por defecto: **APA**.
- Complementos activos: **Better BibTeX**, **Zoplicate** (gestión de duplicados) y **SciPDF**.

## Etiquetas de menú en español

Úsalas literalmente en los pasos. Están sacadas de los ficheros de idioma de esta
instalación.

| Acción | Ruta exacta |
|---|---|
| Alta por identificador | Botón de la varita (barra de herramientas) → **Añadir por identificador** |
| Importar un fichero `.ris` | **Archivo → Importar...** |
| Importar desde texto copiado | **Archivo → Importar desde el portapapeles** |
| Nuevo ítem manual | Botón **+** de la barra → tipo de elemento |
| Adjuntar un PDF del disco | Clic derecho en el ítem → **Añadir adjunto → Archivo** |
| Adjuntar enlace a un fichero | Clic derecho → **Añadir adjunto → Archivo enlazado** |
| Adjuntar un enlace web | Clic derecho → **Añadir adjunto → Enlace web** |
| Que Zotero busque el PDF | Clic derecho en el ítem → **Buscar texto completo** |
| Crear ítem a partir de un PDF suelto | Clic derecho en el PDF → **Crear elemento contenedor...** |
| Rellenar metadatos desde un PDF | Clic derecho en el PDF → **Recuperar metadatos** |
| Ver duplicados | Panel izquierdo → **Elementos duplicados** |
| Nueva colección | **Nueva colección...** |

**El destino se fija antes de importar.** Ni el RIS ni el portapapeles llevan colección: el
ítem cae en lo que esté seleccionado en ese momento. Por eso el paso 1 de toda importación es
siempre *seleccionar `Tesis_RBU → 00_Inbox` en el panel izquierdo*.

## Clave de cita (Better BibTeX)

Formato configurado: `auth.lower + shorttitle(3, 3) + year`

Algoritmo, validado contra 30 claves reales de esta biblioteca:

1. **`auth.lower`** — apellido del primer autor, en minúsculas, sin diacríticos, sin espacios
   ni apóstrofos. Los guiones **se conservan**.
2. **`shorttitle(3, 3)`** — del título: se descartan las palabras vacías inglesas
   (*the, of, and, a, an, in, on, for, to, toward(s), via, or, at, as…*) y las de menos de 3
   caracteres; se toman las **3 primeras** que queden; se les quita la puntuación interna
   (los guiones desaparecen y las partes se unen); se pone la inicial de cada una en
   mayúscula y se concatenan.
3. **`year`** — año de publicación.
4. Si la clave ya existe, Better BibTeX añade un sufijo `a`, `b`, `c`…

Ejemplos reales de esta biblioteca:

| Autor | Título | Clave |
|---|---|---|
| McKay | *The future of social security policy: Women, work and a citizens' basic income* | `mckayFutureSocialSecurity2005` |
| Román de Lara | *Implications of universal basic income for climate goals* | `romandelaraImplicationsUniversalBasic2024` |
| Marín Cánovas | *Universal Basic Income and Inequality…* | `marincanovasUniversalBasicIncome2020` |
| Büchs | *Challenges for the degrowth transition: The debate about wellbeing* | `buchsChallengesDegrowthTransition2019` |
| Krzywdzinski | *Toward a Socioeconomic Company-Level Theory of Automation at Work* | `krzywdzinskiSocioeconomicCompanyLevelTheory2022` |
| Zeyer-Gliozzo | *Returns to formal, non-formal, and informal further training…* | `zeyer-gliozzoReturnsFormalNonformal2024` |
| Heikkinen | *(De)growth and welfare in an equilibrium model…* | `heikkinenDegrowthWelfareEquilibrium2015` |
| Moreno Fernández | *The Spanish "via media" to the development of the welfare state* | `morenofernandezSpanishMediaDevelopment1992` |

Fíjate en los casos difíciles: `Company-Level` → `CompanyLevel` (guion fuera, mayúscula
interna conservada); `non-formal` → `Nonformal`; `(De)growth` → `Degrowth`; `via` se descarta
por ser palabra vacía; `Toward` también.

Como la clave depende del título y del autor, **cámbialos antes de citar**: si el usuario
corrige el título después de haber citado, la clave cambia y las citas se rompen.

## Etiquetas: el casing importa

Esta biblioteca arrastra variantes de mayúsculas de la misma etiqueta, heredadas de
importaciones RIS masivas:

```
Social Policy (305)  /  social policy (257)
human (277)  /  Human (275)  /  Humans (156)
Welfare State (193)  /  welfare state (162)  /  Welfare-State (121)
```

Cada `KW` nuevo con un casing distinto empeora el problema y fragmenta las búsquedas por
etiqueta. Por eso, por defecto, **no metas etiquetas temáticas en el RIS**: propónselas al
usuario para que las añada desde el autocompletado de Zotero, que reutiliza las que ya
existen. Si estás en modo Local, `scripts/zotero_probe.py --tags "welfare"` te dice qué
variantes existen y cuál es la mayoritaria; usa esa forma exacta y entonces sí puedes
incluirla en `KW`.

## Contexto temático

La tesis va sobre **renta básica universal**, en diálogo con estado de bienestar, política
social, decrecimiento, automatización y futuro del trabajo, opinión pública y merecimiento
(*deservingness*). Te sirve para juzgar si una fuente es central o periférica y para proponer
etiquetas sensatas — pero recuerda que el destino es `00_Inbox` en todos los casos.
