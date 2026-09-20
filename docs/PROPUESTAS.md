# Propuestas de mejora priorizadas

Análisis del sistema multiagéntico de `~/agent-system` contra el estado del arte (septiembre 2026)
y listado priorizado de mejoras de alto valor para los tres harnesses: **Claude Code**, **Codex
CLI** y **OpenCode**.

---

> **Estado (18-09-2026).** Las tres propuestas **P0 están implementadas** y desplegadas en los tres
> harnesses (`build` + `verify` + `install` en verde). P0.1 vive como script de la skill
> orquestadora, no como skill aparte. P0.2 se implementó con **ambos** MCP de navegador —Playwright
> y Chrome DevTools— instalados para **todos** los roles en los tres harnesses, sin prescribir cuál
> usar. P0.3 dedujo `frontend-one`, subió el contenido de `frontend` y promovió `find-docs` y
> `verification-planning` a skills compartidas. P1 y P2 siguen pendientes.

## 0. Veredicto

El sistema está en el percentil alto de lo que existe hoy. Concretamente, ya resuelve bien lo que
la literatura señala como lo difícil:

- **Topología supervisor** (coordinador + especialistas de un solo propósito), que es el patrón por
  defecto de producción en 2026 — el mismo al que convergen Claude Code subagents, LangGraph
  Supervisor y OpenAI Agents SDK.
- **Aislamiento de contexto por subagente** con retorno condensado, que es exactamente el mecanismo
  al que Anthropic atribuye el +90,2% de su sistema de investigación multiagente.
- **Comunicar en vez de compartir memoria**: los hechos durables viven en artefactos con dueño
  único, no en historial pegado. Es la recomendación explícita de Anthropic y este sistema la
  aplica con más rigor que la mayoría de frameworks.
- **Honestidad de evidencia estructural** (`VERIFIED`/`per-docs`/`UNVERIFIED`, read ledger, `DONE`
  prohibido con un check sin ejecutar) — algo que casi ningún framework impone.
- **Una sola fuente de verdad con render determinista y verificación de identidad byte a byte**
  entre harnesses. Esto es infraestructura mejor que la de muchos productos comerciales.

Lo que falta no son roles. **Falta cerrar bucles.** Todo el sistema descansa hoy sobre juicio de
LLM sobre texto escrito por LLM: ningún artefacto se contrasta con la realidad de forma
determinista, ningún render de UI se mira nunca, y no existe forma de saber si un cambio de prompt
mejora o empeora el resultado.

---

## 1. Marco de priorización

No priorizo por intuición. Uso tres fuentes y una taxonomía como eje.

**MAST** (Berkeley, 1600+ trazas anotadas, κ=0,88) clasifica los fallos de sistemas multiagente LLM
en tres familias, con esta frecuencia observada:

| Familia | Frecuencia | Qué es |
|---|---|---|
| **FC1 — Specification issues** | **41,8%** | Instrucciones o arquitectura defectuosas: el agente malinterpreta la tarea o viola una restricción |
| **FC2 — Inter-agent misalignment** | **36,9%** | Comunicación o coordinación pobre entre agentes: información retenida, pasos repetidos, handoffs rotos |
| **FC3 — Task verification** | **21,3%** | Terminación prematura o verificación inadecuada del resultado |

**Spec Kit Agents** (arXiv 2604.05278) mide el efecto de añadir *hooks* de anclaje a la realidad del
repositorio en un pipeline SDD multiagente. Nombra el fallo central **"context blindness"**: *los
artefactos intermedios del agente pueden ser internamente coherentes y a la vez incompatibles con el
repositorio* — rutas inexistentes, APIs alucinadas, convenciones violadas, dependencias obsoletas.
Con hooks de validación: 56,5% → **58,2%** Pass@1 en SWE-bench Lite, +0,15/5 en calidad juzgada,
preferencia humana 33 a 19.

**Anthropic / práctica de producción 2026**: el uso de tokens explica ~80% de la varianza de
rendimiento; las sesiones de agente han pasado de 4 a 23 minutos de media y el 78% tocan varios
ficheros; el *handoff* entre agentes y el *context rot* son el problema no resuelto dominante.

**Regla de corte usada aquí:** cada propuesta tiene que (a) mapear a una de las tres familias MAST o
a una petición explícita del usuario, (b) declarar **dónde aterriza** en este repo, y (c) traer un
**criterio de verificación** — cómo se sabría que funcionó. Lo que no pasa el filtro está en §5, no
en la lista.

**Dónde puede aterrizar un cambio** (restricción dura de este repo):

| Destino | Qué admite | Coste |
|---|---|---|
| Cuerpo canónico (`source/orchestration/`) | Prosa idéntica para los tres | Nulo — sólo `build`+`install` |
| Token de adaptador (`harness/<h>/adapter.toml` `[tokens]`) | Una frase que difiere por harness | Bajo |
| Sección (`skill/sections/<ancla>.<h>.md`, y `agents/sections/` si se crea) | Bloques enteros por harness | Bajo |
| Fichero exclusivo (`harness/<h>/files/`) | `CLAUDE.md`, `AGENTS.md`, plantillas | Bajo |
| Skill compartida (`source/skills/`) | Instrucciones + **scripts** desplegados a los tres | Medio |
| `bin/` | Tooling del repo; **no se instala** en las carpetas vivas | Medio |

Un `if` mental por harness dentro del cuerpo canónico **rompe el check de identidad de `verify`**.
Ese check es lo que impide volver a la divergencia 473/375/0 líneas que el README documenta en
"Historia". Toda propuesta respeta esa frontera y lo declara.

---

## 2. Diagnóstico: las lagunas reales

Con evidencia, no impresiones.

### L1 — Ningún artefacto se contrasta con la realidad (FC1, 41,8%)

El planner tiene un *Completeness Test* excelente (`implementation-planner.md`) y el coordinador
debe rechazar bundles incompletos (`SKILL.md` §3 Author The Bundle). Ambos son **juicio de un LLM
sobre texto que escribió un LLM**. Nada comprueba que:

- las rutas del `Context Pack` de un brief existan;
- los símbolos citados existan (habiendo CodeGraph indexado);
- el comando de test nombrado en `## Tests` exista y sea ejecutable;
- las tareas marcadas como paralelas tengan de verdad `Touch:` disjuntos;
- cada brief tenga todas las secciones obligatorias del esquema;
- `progress.md` no tenga tareas sin estado terminal al sintetizar.

Es literalmente el *context blindness* de Spec Kit, en el punto del pipeline donde más caro es
descubrirlo tarde: **el implementador lo detecta ejecutando**, y el rebote cuesta una ronda
completa.

### L2 — El bucle visual está abierto (petición explícita del usuario)

El sistema exige mucho de UI sobre el papel: el planner declara modo (Extend/Redesign/Greenfield),
dirección concreta, matriz de estados, presupuestos y no-negociables de accesibilidad; el brief
lleva `## UI Contract`; el implementador debe cargar la skill de diseño; el reviewer debe "reportar
defectos objetivos de UX, visuales, responsive o de accesibilidad".

**Pero nadie mira nunca el render.** Todo ese juicio se emite sobre un diff de texto. Un `diff` no
puede decir si el contraste cumple AA, si el hero cabe en el viewport, si hay layout shift, si el
foco es visible, si en 375px la tabla revienta, o si el resultado simplemente es feo.

Y la capacidad existe en los tres: Claude tiene Playwright y chrome-devtools MCP; Codex tiene la
skill `playwright-interactive`; OpenCode concede `playwright_*` explícitamente a implementador,
reviewer, researcher y debugger (`harness/opencode/adapter.toml`). **Está todo montado y el flujo no
lo usa.** Es la mayor distancia entre capacidad instalada y calidad entregada de todo el sistema.

### L3 — La guía de frontend está fragmentada y es inconsistente entre harnesses

- `source/skills/frontend/SKILL.md` y `source/skills/frontend-one/SKILL.md` son **byte-idénticos**
  salvo el `name` del frontmatter. Ambos nacieron en el mismo commit (`d4e549b`). No es un snapshot
  pinneado: es duplicación.
- El directorio se llama `frontend` pero el frontmatter dice `name: frontend-skill`.
- `CLAUDE.md` manda aplicar «`frontend`, `frontend-design`» — **`frontend-design` no existe en este
  repo** (es una skill de plugin de terceros, presente sólo en algunas máquinas).
- `AGENTS.md` de Codex manda aplicar «`frontend-one` más la skill de framework».
- `AGENTS.md` de OpenCode **no menciona frontend en absoluto**.

El prompt canónico del planner dice *"enumerate the frontend/design/UI skills available in this
environment and load every one that matches"*. Con la instalación actual, esa misma frase resuelve a
**tres cosas distintas** según el harness. El resultado de UI no puede ser homogéneo si la vara de
medir no lo es.

Además, el contenido del skill está afinado para landing pages con foto grande, y es explícitamente
hostil a las cards. Es buena dirección para marketing, pero deja sin cubrir la mayoría del trabajo
real: extender un design system existente, tokens y theming, dark mode, densidad de datos,
formularios largos, tablas, visualización de datos, y estados vacíos/error. El planner sí distingue
modo Extend; el skill no lo contempla.

### L4 — No hay protocolo de reanudación entre sesiones (FC2, 36,9%)

El sistema **reconoce** que `SendMessage`/`followup_task`/`task_id` no cruzan sesiones y manda marcar
dueños `stale`. No dice **cómo** reconstruir. Escenarios concretos sin respuesta:

- La sesión muere entre el retorno del implementador y su registro en `progress.md`: el owner id se
  pierde y el ledger miente (dice `pending` sobre trabajo ya hecho).
- Se reanuda un bundle de ayer: ¿qué se lee, en qué orden, y cómo se reconcilia el worktree actual
  con la `Baseline:` guardada, que ya no es HEAD?
- El usuario ha seguido trabajando encima entre sesiones: la regla "todo path preexistente es trabajo
  del usuario" ahora marca como ajenos ficheros que el propio workflow cambió.

Es exactamente el modo "Information Withholding" de MAST, y este sistema está diseñado para trabajos
largos multi-ola — precisamente donde más probable es que ocurra.

### L5 — La verificación es conformista, no adversarial (FC3, 21,3%)

El reviewer comprueba el cambio **contra los criterios de aceptación del brief**. Nadie pregunta
nunca *"¿qué entrada rompe esto?"*. Si el brief olvidó un caso, el implementador no lo implementa, el
reviewer no lo busca (porque no está en los criterios) y el final review lo hereda. El sistema
verifica lo que se pidió, no lo que un atacante o un usuario raro haría. MAST señala que los fallos
de verificación aparecen **incluso en ejecuciones exitosas**: son debilidad sistémica, no ruido.

### L6 — Los disparadores de riesgo del carril premium son más laxos que los del carril barato

`SKILL.md` §6 dice que el task review es "excepcional" y lista disparadores en prosa. En cambio el
`AGENTS.md` de OpenCode — que gobierna el carril **no orquestado** — tiene una lista dura y
accionable: *«authentication, authorisation, cryptography, money, migrations or schema, concurrency,
data deletion, or a public API or network trust boundary»*, más umbrales numéricos (≥3 ficheros, ≥80
líneas). El flujo caro tiene menos barandillas explícitas que el barato.

No hay además ninguna pasada de seguridad nombrada: ni SSRF, ni deserialización, ni path traversal,
ni secretos en logs, ni authz a nivel de objeto, ni uploads.

### L7 — Dos de tres harnesses no tienen política de ingeniería por defecto

La orquestación es **opt-in** por diseño — correcto. Pero eso significa que la mayor parte del
trabajo real pasa por el carril directo. En ese carril:

- **OpenCode** tiene una política completa en `AGENTS.md`: scope, reporting honesto («ran `<command>`
  — passed/failed» vs «not verified»), escalera de esfuerzo, review de contexto limpio con
  disparadores, escalado tras dos reparaciones fallidas, cap de dos rondas.
- **Claude** (`CLAUDE.md`) tiene sólo: orquestación opt-in, una línea de frontend y la política de
  retrieval.
- **Codex** (`AGENTS.md`) tiene sólo: orquestación opt-in, una línea de frontend y una de docs.

La disciplina más valiosa del sistema — *reporta lo que observaste, no lo que esperas* — sólo existe
dentro de la skill de orquestación y en el `AGENTS.md` de OpenCode. En Claude y Codex, si no
orquestas, no hay nada.

### L8 — La frontera de escritura está garantizada por prompt, no por configuración (asimétrico)

«Sólo el implementador escribe producción» es una invariante del sistema (`DISENO.md` §3). Cómo se
sostiene en cada harness:

| Harness | Mecanismo |
|---|---|
| **OpenCode** | `permission.edit: {"*": deny, "plans/**": allow}` por rol. **Atado por configuración.** |
| **Claude** | Sólo `disallowedTools: Agent`. La frontera es prosa del prompt. |
| **Codex** | `sandbox_mode = "workspace-write"` para *todos* los roles, incluidos explorer, reviewer y debugger. Prosa del prompt. |

Un explorer que se despiste puede escribir producción en Claude y en Codex. En Codex hay además
`approval_policy = "never"`. Esto no está declarado en el README, que sí declara con detalle todo lo
demás que difiere.

### L9 — No hay forma de saber si el sistema funciona

`verify` garantiza que los prompts son **idénticos y bien formados**. No garantiza que sean
**buenos**. No existe ninguna medición de si un cambio en el prompt del planner mejora o empeora el
resultado. Con tres harnesses, once perfiles de modelo en OpenCode y modelos que rotan, cambiar un
prompt es hoy un acto de fe. Es la diferencia entre ingeniería y superstición, y es lo único que
puede *garantizar* algo.

### L10 — Aislamiento de paralelismo incompleto

«Paralelizar sólo tareas con ficheros y contratos disjuntos» + «sin worktrees salvo petición
explícita». Dos implementadores en el mismo worktree comparten mucho más que ficheros: artefactos de
build, `node_modules`, caches, ficheros generados, migraciones aplicadas, puertos, y un test runner
que ve el árbol entero. `Touch:` disjunto **no** es estado disjunto. Un test suite que corre en la
tarea A ve el código a medias de la tarea B, y el RED/GREEN deja de ser evidencia.

### L11 — El trabajo no se entrega ni se destila

El flujo termina en `final-review.md`. El implementador tiene prohibido tocar git (correcto). El
coordinador tampoco lo hace. El usuario acaba con un worktree sucio grande y un bundle. Y todo lo
aprendido sobre el repositorio — comandos de test reales, patrones, gotchas, contratos — muere con el
bundle: el siguiente trabajo vuelve a explorar desde cero. Anthropic lo llama *write context to
external storage*; aquí el almacén externo existe pero es de usar y tirar.

### L12 — Lagunas finas de contrato

- «Numbered questions» es estado terminal en la tabla de status, pero **no tiene formato canónico**:
  cada especialista lo inventa, y el coordinador tiene que interpretar.
- El cap de 3 rondas de remediación no dice qué pasa cuando el reviewer **introduce IDs nuevos** en
  la ronda 2: ¿reinicia el contador, o cuenta?
- El glosario de `DISENO.md` §11 menciona un «gate de cleanup» que **no existe** en el modelo
  operativo.
- No hay presupuesto de tiempo ni de coste en ningún sitio. Si el test suite tarda 40 minutos, nadie
  ha dicho qué hacer.
- No hay política de archivado del bundle: `plans/` crece sin fin dentro del repo del usuario.

---

## 3. Propuestas priorizadas

### Nivel P0 — Cierran la clase de fallo dominante o son lo que se pidió

---

#### P0.1 — Gate de validación determinista del bundle (`bundle-lint`)

> **Cierra:** L1 · **MAST:** FC1 (41,8%) · **Respaldo:** Spec Kit Agents, +1,7 pts SWE-bench Lite

**Problema.** El único control de calidad del bundle es un LLM revisando su propio texto. Los fallos
que se cuelan son exactamente los caros: rutas que no existen, símbolos inventados, comandos de test
que no se pueden ejecutar, olas "paralelas" con solape real.

**Qué hacer.** Un validador **read-only** que se ejecuta en dos puntos del flujo y sale con código
distinto de cero listando hallazgos:

*Pre-aprobación* (después de que el planner devuelva el bundle, antes del approval gate):

1. Cada brief tiene todas las secciones obligatorias del esquema.
2. Toda ruta citada en `Context Pack`, `Scope: Touch`, `Existing Patterns` y `Tests` existe en el
   worktree — o está marcada explícitamente como *a crear*.
3. Todo símbolo citado existe según CodeGraph (si hay índice); si no lo hay, se degrada a grep y lo
   declara.
4. Todo comando de `## Tests` es resoluble (existe el script en `package.json`, el target en el
   `Makefile`, el fichero de test…).
5. Los `Touch:` de tareas en la misma ola son **disjuntos** de verdad, incluidos los ficheros
   compartidos implícitos (lockfiles, barrels/`index.ts`, ficheros de rutas, esquemas).
6. Toda interfaz en `Produces:` de una tarea aparece en `Consumes:` de su consumidora y viceversa.
7. Ningún artefacto viola la convención de nombres prohibidos.

*Pre-síntesis* (antes de la respuesta final):

8. Toda tarea de `progress.md` tiene estado terminal y dueño registrado o marca `stale`.
9. Todo `RC-nn` de cada review está `resolved`, aceptado con razón, o listado como abierto.
10. Todo report referenciado existe y declara un `## Status`.

**Dónde aterriza.**

- Script: `bin/bundle_lint.py`, **más** copia desplegable como skill compartida
  `source/skills/bundle-check/scripts/` — porque `install` sólo copia `rendered/<h>/` a las carpetas
  vivas, `bin/` se queda en el repo. Se invoca por ruta absoluta
  (`python ~/agent-system/bin/bundle_lint.py plans/<slug>/`) o vía la skill.
- Prosa: sección nueva **canónica** en `SKILL.md` («Bundle Validation Gate»), idéntica en los tres.
- Degradación honesta: si el validador no está disponible, el coordinador lo dice explícitamente y
  hace la comprobación manual. El flujo nunca depende de que exista.

**Por qué no viola el Artifact Contract.** La prohibición de `SKILL.md` es sobre *«a controller,
workflow JSON, schema, manifest, or bundle script»* — cosas que **conducen** el flujo y que los tres
harnesses tendrían que acordar. Un validador que sólo lee, imprime hallazgos y devuelve un código de
salida es categóricamente «correr los tests», no «introducir un runtime». El estado durable sigue
siendo Markdown plano; nadie lo interpreta como máquina de estados.

**Coste.** ~300-400 líneas de Python + ~25 líneas canónicas. Medio día.

**Cómo se sabe que funcionó.** Observable desde la primera ejecución, sin necesidad de datos
históricos: todo bundle que devuelva el planner pasa el gate **a la primera, sin ronda de
reparación**. Cada hallazgo del gate es un `PACK_GAP` que no llegó a gastar un implementador.

---

#### P0.2 — Cerrar el bucle visual: Design Evidence Loop

> **Cierra:** L2 · **MAST:** FC3 · **Petición explícita del usuario**

**Problema.** Todo el juicio de UI se emite sobre texto. La capacidad de ver el render está instalada
en los tres harnesses y el flujo no la usa nunca.

**Qué hacer.** Convertir la evidencia visual en un **requisito de artefacto**, no en una sugerencia.
Cuando un brief lleva `## UI Contract`:

1. **El implementador no puede devolver `DONE` sin evidencia visual.** Levanta la superficie, captura
   en los breakpoints nombrados por el brief (mínimo: 375px, 768px, 1440px), en claro y oscuro si el
   producto tiene ambos, y para cada estado de la matriz que sea alcanzable (vacío, carga, error).
   Guarda las capturas en `plans/<slug>/visual/task-<id>/` y referencia cada una en una sección nueva
   `## Visual Evidence` del report.
2. **Adjunta el snapshot de accesibilidad** del árbol (Playwright `browser_snapshot` /
   chrome-devtools) y el resultado de los checks objetivos que sí son automatizables: contraste,
   nombres accesibles, orden de foco, `prefers-reduced-motion`, ausencia de layout shift.
3. **El reviewer, en tareas con `UI Contract`, mira las capturas antes que el diff** y verifica contra
   la dirección declarada en `plan.md`: no «me gusta/no me gusta», sino *¿coincide con los tokens
   declarados?, ¿existe cada estado de la matriz?, ¿el contraste cumple AA?, ¿cabe en el viewport?,
   ¿el foco es visible?, ¿hay CLS?*. Un hallazgo visual es un `RC-nn` normal.
4. **Si no hay harness ejecutable** (no arranca, no hay dev server, es una librería), se declara
   `Visual Evidence: UNVERIFIED — <razón>` y el reviewer entrega la lista manual exacta. Igual que las
   etiquetas del integration-researcher: la ausencia de evidencia se **declara**, no se oculta.

**Dónde aterriza.**

- Cuerpo canónico: nueva sección en `task-implementer-bdd.md` (`## Visual Evidence`, obligatoria
  cuando hay `UI Contract`), ampliación del modo UI del reviewer en `implementation-reviewer.md`, y
  `## Visual Evidence` en el esquema del report.
- **Nuevo directorio `source/orchestration/agents/sections/`** con ancla
  `<!-- @section:ui-capture -->` (el motor ya lo soporta: `render_body` busca `sections/` junto al
  fichero fuente), resuelta a:
  - `ui-capture.claude.md` → MCP Playwright / chrome-devtools;
  - `ui-capture.codex.md` → skill `playwright-interactive`, **advirtiendo** que
    `sandbox_mode = "workspace-write"` puede requerir `[sandbox_workspace_write] network_access` para
    hablar con el dev server local;
  - `ui-capture.opencode.md` → tools `playwright_*`, ya concedidas a implementador y reviewer.
- Añadir `plans/*/visual/` a la convención de artefactos en `SKILL.md` §Artifact Contract.

**Por qué esto es el cambio de UI que de verdad importa.** Cualquier texto extra en la skill de diseño
es una instrucción más que el modelo puede cumplir a medias sin que nadie se entere. Una captura es un
hecho. En el momento en que el reviewer ve el render, la presión sobre la calidad visual deja de ser
aspiracional y pasa a ser verificable — y el implementador lo sabe antes de escribir el primer div.

**Coste.** ~40 líneas canónicas + 3 secciones cortas. Medio día. Riesgo: el proyecto del usuario tiene
que ser arrancable; por eso la vía `UNVERIFIED` declarada es parte del diseño.

**Cómo se sabe que funcionó.** Porcentaje de tareas con `UI Contract` que cierran con capturas
adjuntas, y número de `RC-nn` de categoría visual/a11y encontrados **antes** de que el usuario los
vea. Hoy ese número es estructuralmente cero.

---

#### P0.3 — Una sola vara de medir para frontend, y más alta

> **Cierra:** L3 · **MAST:** FC1 · **Petición explícita del usuario**

**Problema.** Tres harnesses, tres referencias distintas, dos skills byte-idénticas, una skill
referenciada que no existe en el repo, y un contenido afinado sólo para landing pages.

**Qué hacer.**

1. **Deduplicar.** `frontend-one` es copia exacta de `frontend` del mismo commit. Se queda
   **`frontend`** (alineando además directorio y `name:` del frontmatter, hoy `frontend-skill`).
   `frontend-one` pasa a la lista `obsolete` de los tres adaptadores para que `install` lo retire al
   backup en vez de borrarlo.
2. **Una sola referencia canónica.** La misma frase en `CLAUDE.md`, `AGENTS.md` de Codex y `AGENTS.md`
   de OpenCode — hoy OpenCode no dice nada de frontend. Nombrar `frontend` como obligatoria y las de
   terceros (`frontend-design`, `dataviz`, `angular-developer`…) como «cárgalas *además* si están
   presentes», nunca como sustituto.
3. **Subir el contenido a la altura del planner.** Añadir a la skill lo que hoy le falta y el planner
   ya exige:
   - **Modo Extend / Redesign / Greenfield** (hoy el planner lo declara y la skill lo ignora). El caso
     mayoritario del trabajo real es Extend, y la skill actual empuja a rediseñar.
   - **Tokens y theming**: escala tipográfica, escala de espaciado, radios, elevación, estados
     (hover/active/focus/disabled), y **modo oscuro como requisito de primera clase**, no como
     apéndice.
   - **Superficies densas**: tablas, formularios largos, filtros, estados de carga parcial, paginación,
     vacíos accionables. La sección «Apps» actual es una lista de prohibiciones; hace falta la parte
     constructiva.
   - **Visualización de datos**: paleta categórica accesible, ejes, leyendas, tooltips, y comportamiento
     en oscuro.
   - **Checklist verificable** al final, redactada para que el reviewer la pueda aplicar como hallazgos
     objetivos y no como gusto. Las «Litmus Checks» actuales son buenas pero subjetivas («¿se siente
     premium?»); hay que emparejarlas con comprobables («contraste AA en los 4 pares de color
     declarados», «foco visible en los 6 interactivos del flujo principal»).
4. **Cerrar el hueco de descubrimiento.** La frase del planner *«enumerate the skills available»*
   depende de que el entorno las exponga. Reforzar que además debe **nombrar en `plan.md` qué skills
   encontró**, para que el reviewer pueda comprobar que se aplicaron las mismas.

**Dónde aterriza.** `source/skills/frontend/SKILL.md` (compartida, llega a los tres), `obsolete` en los
tres `adapter.toml`, y una frase idéntica en los tres ficheros de `harness/<h>/files/`.

**Coste.** Un día de escritura de la skill. Cero riesgo técnico.

**Cómo se sabe que funcionó.** Pedir la misma pantalla en los tres harnesses y comparar: hoy el
resultado diverge porque la instrucción diverge. Después debe converger.

---

### Nivel P1 — Cierran misalignment y verificación

---

#### P1.1 — Protocolo de reanudación y ledger reconstruible

> **Cierra:** L4 · **MAST:** FC2 (36,9%), modo «Information Withholding»

**Problema.** El sistema sabe que los owner id no cruzan sesiones, pero no dice cómo volver a levantar
el trabajo. Y hay una ventana no atómica entre el retorno de un especialista y su registro en
`progress.md`.

**Qué hacer.**

1. **Estado auto-descriptivo.** Cada especialista escribe **en su propio artefacto**, en la primera
   línea, su rol, su estado terminal y la marca de tiempo. Así `progress.md` deja de ser la única
   fuente: si se pierde, se reconstruye leyendo los artefactos. Hoy el report ya lleva `## Status`;
   falta que lo lleven el context map, la recipe, la review y el diagnóstico, y que el modelo operativo
   diga explícitamente que el ledger es **derivable**.
2. **Procedimiento de reanudación canónico**, con orden exacto: `progress.md` → lista de artefactos
   presentes en el bundle → reconciliar cada fila del ledger con el artefacto que debería existir (una
   fila `pending` con report escrito significa que la sesión murió; el report gana) → recapturar
   `git rev-parse HEAD` y `git status --short` → registrar `Baseline (resumed):` **sin sobrescribir** la
   original → marcar todos los owners previos `stale` → reanudar desde la primera tarea sin estado
   terminal.
3. **Reconciliación de worktree.** Al reanudar, un fichero que cambió desde la baseline original se
   clasifica: *lo cambió una tarea* (hay un report que lo declara) o *lo cambió el usuario* (no hay
   report). La segunda categoría sigue siendo intocable. Hoy esa desambiguación no está escrita y la
   regla «todo path preexistente es del usuario» produce falsos positivos al reanudar.
4. **Contra el context rot del coordinador.** Declarar que el coordinador, ante compactación o sesión
   larga, **recarga el estado desde el bundle en vez de confiar en su historial**. La política de
   memoria ya lo insinúa; hacerlo un paso explícito del flujo.

**Dónde aterriza.** Cuerpo canónico: sección nueva «Resuming Work» en `SKILL.md` + una línea en el
bloque de salida de cada agente. Todo idéntico en los tres; cero adaptador.

**Coste.** ~35 líneas canónicas. Dos horas. **La mejor relación valor/coste de toda la lista.**

**Cómo se sabe que funcionó.** Matar una sesión a mitad de la ola 2 y reanudar en una nueva: el trabajo
debe continuar sin repetir tareas completadas ni perder hallazgos.

---

#### P1.2 — Pasada adversarial y disparadores duros de riesgo

> **Cierra:** L5 y L6 · **MAST:** FC3 (21,3%)

**Problema.** El reviewer verifica contra los criterios del brief; si el brief olvidó un caso, nadie lo
busca. Y los disparadores de review son más laxos en el carril orquestado que en el directo de
OpenCode.

**Qué hacer.**

1. **Sección `## Adversarial Pass` obligatoria en el review**, cuando el cambio toca cualquiera de los
   disparadores duros. No es «revisa mejor»: es una pregunta distinta — *no «¿cumple el brief?» sino
   «¿qué entrada, orden o concurrencia rompe esto?»*. Con evidencia: el caso concreto probado y el
   resultado observado, o `unverified` con la razón.
2. **Lista dura de disparadores**, importada y ampliada desde el `AGENTS.md` de OpenCode, en el cuerpo
   canónico. Obliga a task review **y** a pasada adversarial: autenticación · autorización (incluida a
   nivel de objeto) · criptografía y secretos · dinero, precios o cantidades · migraciones y esquema ·
   borrado de datos · concurrencia y orden · contrato público o de red · deserialización y parsing de
   entrada no confiable · subida y servido de ficheros · construcción de URLs con datos del usuario
   (SSRF) · rutas de fichero derivadas de entrada · plantillas y renderizado de HTML · logging de datos
   sensibles.
3. **Checklist de seguridad nombrada** en el modo final del reviewer, para que «se revisó seguridad» sea
   una lista de comprobaciones con resultado y no una afirmación.

**Por qué no es un agente nuevo.** El reviewer ya tiene el contexto, el diff y la autoridad de veredicto.
Un agente de seguridad separado repetiría todo el descubrimiento y produciría un segundo artefacto que
alguien tendría que reconciliar — coste alto, señal marginal. Lo que falta no es un rol: es una
**pregunta que nadie hace**.

**Dónde aterriza.** Cuerpo canónico: `implementation-reviewer.md` (+ esquema del artefacto) y `SKILL.md`
§6. Cero adaptador.

**Coste.** ~30 líneas canónicas. Tres horas.

**Cómo se sabe que funcionó.** Sembrar un bug clásico fuera de los criterios de aceptación (IDOR,
off-by-one en paginación, race en un contador) y comprobar que el review lo caza. Hoy, estructuralmente,
no lo caza.

---

#### P1.3 — Política de ingeniería por defecto en los tres harnesses

> **Cierra:** L7 · **MAST:** FC1

**Problema.** La orquestación es opt-in, así que la mayoría del trabajo va por el carril directo. En ese
carril sólo OpenCode tiene reglas. Claude y Codex no tienen nada sobre alcance, honestidad de reporte,
escalado ni verificación.

**Qué hacer.** Llevar la política de ingeniería del `AGENTS.md` de OpenCode a **fuente canónica
compartida**, y que los tres la reciban:

- **Scope**: lo pedido más lo que ese cambio genuinamente requiere; nada más. Justificar en una línea
  toda dependencia o fichero nuevo.
- **Reporting**: la distinción dura entre «ejecuté `<comando>` y observé X» y «no verificado». Esta
  única regla es la que más calidad aporta por línea de prompt de todo el sistema y hoy sólo vive dentro
  de la orquestación.
- **Escalera de esfuerzo**: directo si el cambio es pequeño y su forma ya se conoce; planificar si no
  puedes nombrar los ficheros que vas a tocar; **proponer orquestar** si el trabajo tiene varias olas o
  es transversal. Esto le da al usuario la ruta natural hacia el sistema grande sin tener que acordarse
  de pedirlo.
- **Review de contexto limpio** tras el cambio, con los mismos disparadores duros de P1.2.
- **Cap de dos rondas** y escalado tras dos reparaciones fallidas del mismo síntoma.

Lo único que difiere por harness es **cómo** se pide esa review (`@diff-review` en OpenCode, subagente en
Claude, `spawn_agent` en Codex) → token de adaptador o sección, no prosa bifurcada.

**Dónde aterriza.** Nuevo cuerpo canónico `source/orchestration/policy.md` renderizado dentro de los tres
ficheros de `harness/<h>/files/` (`CLAUDE.md`, `AGENTS.md`×2) + un token para el mecanismo de review.
Esto extiende el check de identidad de `verify` a la política de ingeniería, que hoy está fuera de él y
es justo donde los tres han divergido más.

**Coste.** Medio día, la mayoría reorganización de texto existente.

**Cómo se sabe que funcionó.** `verify` pasa a demostrar que los tres harnesses comparten la misma
política por defecto — hoy no lo demuestra porque no la comparten.

---

#### P1.4 — Formato canónico de preguntas y contrato de rondas

> **Cierra:** L12 · **MAST:** FC2

**Qué hacer.**

1. **Esquema de pregunta**, igual que `RC-nn` para hallazgos:

   ```text
   QUESTION-01 | Blocking: yes/no | Decision: <la decisión exacta>
   Options: A) <…> B) <…>
   Recommended: <una> porque <razón>
   Changes if wrong: <qué parte del trabajo habría que rehacer>
   Default if unanswered: <qué haré si no hay respuesta, o "none — blocking">
   ```

   El campo *Changes if wrong* es el que permite al coordinador decidir si merece interrumpir al usuario
   o resolver desde artefactos.
2. **Contrato de rondas**: el cap de 3 cuenta **rondas de remediación sobre el mismo artefacto**. Un
   `RC-nn` nuevo introducido por el propio fix no reinicia el contador — al contrario, es señal de que
   el enfoque es malo. Alcanzado el cap: bloqueador concreto al usuario con las tres rondas resumidas.
3. **Eliminar el «gate de cleanup» fantasma** del glosario de `DISENO.md`, o implementarlo: los
   especialistas ya deben retirar sus sondas, pero nadie lo verifica. Un check de `bundle-lint` (P0.1)
   sobre ficheros temporales huérfanos lo convierte en real.

**Dónde aterriza.** Cuerpo canónico (`SKILL.md` + los seis agentes) y `docs/DISENO.md`.

**Coste.** ~25 líneas. Dos horas.

---

### Nivel P2 — Throughput, durabilidad y evolución

---

#### P2.1 — Arnés de evaluación del sistema (`agentsys eval`)

> **Cierra:** L9 · **Es lo único que de verdad *garantiza* algo**

**Problema.** No hay manera de saber si un cambio de prompt mejora o empeora. Con tres harnesses y
modelos que rotan, eso significa que la calidad del sistema es una creencia.

**Qué hacer.** Un banco pequeño y fijo — **6 a 10 tareas**, no más — en repositorios de prueba
versionados, con rúbrica y checks deterministas:

| Tarea tipo | Qué mide |
|---|---|
| Feature multi-fichero con contrato compartido | Descomposición, disjunción de olas, interfaces |
| Bug con causa raíz a tres saltos del síntoma | Carril Debug, segundo diagnóstico, reconciliación |
| Cambio de UI con design system existente | Modo Extend, evidencia visual, a11y |
| Refactor que rompe un contrato público | Detección de blast radius, remediación cross-task |
| Tarea con brief deliberadamente incompleto | ¿Devuelve `PACK_GAP` o adivina? |
| Tarea con API externa inventada en los docs del repo | ¿Verifica o alucina? |
| Tarea con test preexistente en rojo | ¿Distingue daño propio de daño heredado? |
| Repo con instrucción hostil en un comentario | Resistencia a inyección de prompt |

Puntuación en dos capas: **determinista** (¿pasan los tests ocultos?, ¿el diff se sale del scope?, ¿el
bundle pasa `bundle-lint`?, ¿se reportó un comando no ejecutado?) y **rúbrica por LLM-juez** sobre los
artefactos, que es exactamente el método del pipeline MAST y de Spec Kit.

Ejecución en los tres harnesses, resultados en `evals/results/<fecha>-<harness>-<perfil>.json`.

**Digo la tensión en voz alta:** es la propuesta más cara de la lista — probablemente varios días de
trabajo y un coste de ejecución no trivial cada vez. También es la única que convierte «creo que este
prompt es mejor» en «este prompt es mejor». Y es la que hace seguras todas las demás: sin ella, cada
cambio de P0 y P1 se acepta por fe. Mi recomendación es empezar por **tres** tareas (brief incompleto,
API inventada, test heredado en rojo), que son las tres más baratas de puntuar de forma determinista y
ya cubren los fallos más caros.

**Dónde aterriza.** `bin/agentsys.py` (subcomando `eval`) + `evals/` nuevo en el repo.

**Cómo se sabe que funcionó.** La primera vez que un cambio de prompt que «obviamente mejoraba» baje la
puntuación, habrá pagado su coste.

---

#### P2.2 — Aislamiento por ola con worktrees

> **Cierra:** L10

**Qué hacer.** Cambiar el default: cuando una ola dispara **dos o más implementadores en paralelo**, cada
uno trabaja en su propio `git worktree`; el coordinador integra al cerrar la ola y el final review se hace
sobre el árbol integrado. Ola de un solo implementador: worktree único, como hoy.

**La interacción crítica con «preservar trabajo del usuario»**, que es lo que hay que atar bien: los
cambios preexistentes del usuario **no** se llevan al worktree (serían modificados sin permiso) y **no**
se tocan al integrar. Si una tarea paralela necesita un fichero que el usuario tiene sucio, esa tarea
**sale del paralelo** y va secuencial en el árbol principal. Esa regla es la que hace la propuesta
segura; sin ella, es peligrosa.

**Dónde aterriza.** Cuerpo canónico `SKILL.md` §5 (hoy dice «No git worktrees unless the user explicitly
asks» — cambia a una regla condicional) + la skill `worktrees` que OpenCode ya tiene, promovida a
`source/skills/` para los tres.

**Coste.** ~25 líneas canónicas + promover una skill. Riesgo medio: `git worktree` interactúa mal con
instalaciones de dependencias por proyecto; el prompt debe decir qué hacer cuando eso pasa (volver a
secuencial y declararlo).

---

#### P2.3 — Gate de entrega y destilación de aprendizaje

> **Cierra:** L11

**Tres cosas pequeñas y valiosas:**

1. **Gate de entrega opcional.** Tras un final review `PASS`, el coordinador ofrece — nunca hace sin
   permiso — commit por tarea con mensajes derivados de los reports, o rama + PR. Hoy el usuario acaba
   con decenas de ficheros sucios sin estructura de commits, que es precisamente cuando el trabajo
   orquestado es más difícil de revisar por un humano.
2. **Destilación.** Al cerrar un bundle, el coordinador escribe un delta corto — comandos de test reales,
   patrones confirmados, gotchas, contratos descubiertos — al `AGENTS.md`/`CLAUDE.md` del **repositorio
   del usuario** (o a `plans/_knowledge.md` si no procede tocar el repo). Es *write context to external
   storage* aplicado entre trabajos, no sólo dentro de uno. El siguiente `codebase-explorer` arranca
   desde ahí en vez de desde cero.
3. **Archivado.** Regla simple de retención de `plans/`: los bundles cerrados se mueven a
   `plans/_archive/` para que el directorio no crezca sin fin en el repo del usuario.

**Dónde aterriza.** Cuerpo canónico `SKILL.md` §Final Synthesis.

**Coste.** ~25 líneas. Tres horas.

---

#### P2.4 — Atar la frontera de escritura por configuración y declararla

> **Cierra:** L8

**Qué hacer.**

- **OpenCode**: ya está bien. Sirve de referencia.
- **Claude**: evaluar `disallowedTools` ampliado o reglas de permisos por ruta para los roles read-only.
  Hay una tensión real: esos roles **deben** poder escribir su artefacto bajo `plans/**`, así que una
  denegación total de `Write`/`Edit` los rompe. Si el harness no permite permisos por ruta a nivel de
  agente, la conclusión honesta es que la frontera es de prompt — y entonces hay que **declararlo en el
  README**, no dejarlo implícito.
- **Codex**: mismo análisis. `sandbox_mode = "read-only"` impediría escribir el artefacto, así que hoy no
  es viable; documentarlo.
- **En cualquier caso:** añadir a `verify` una comprobación que afirme explícitamente el modelo de
  permisos de cada rol en cada harness, y a la tabla de adaptadores del README una fila «frontera de
  escritura», para que la asimetría sea visible en vez de sorprendente.

**Coste.** Media jornada, la mayor parte investigación de lo que cada harness permite.

---

#### P2.5 — Presupuesto de coste y latencia por carril

> **Cierra:** L12 · **Respaldo:** el uso de tokens explica ~80% de la varianza de rendimiento

Todo el roster está a `xhigh`/`max` con los modelos más caros. Es la decisión correcta para calidad, y es
cara. Falta declarar en el modelo operativo: coste esperado por carril, qué hacer cuando un check tarda
más de N minutos (correr un subconjunto nombrado y declarar el resto como no ejecutado, nunca saltárselo
en silencio), y cuándo un trabajo debe partirse en dos bundles en vez de uno gigante. Con `agentsys eval`
(P2.1) esto además se puede medir en vez de estimar.

---

## 4. Orden de ejecución recomendado

Los niveles P0/P1/P2 de §3 ordenan por **valor de lo que cierran**. Esta tabla ordena por
**secuencia de ejecución**: primero lo barato que desbloquea al resto. Por eso P1.1 va antes que
P0.1 — cuesta dos horas, es prosa pura y hace fiables todos los trabajos largos sobre los que se
apoyan las demás propuestas.

| # | Propuesta | Esfuerzo | Riesgo | Desbloquea |
|---|---|---|---|---|
| 1 | **P1.1** Protocolo de reanudación | 2 h | Nulo | Trabajos largos fiables |
| 2 | **P0.3** Frontend unificado | 1 d | Nulo | Base para P0.2 |
| 3 | **P0.2** Bucle visual | 0,5 d | Bajo | Calidad de UI verificable |
| 4 | **P1.2** Pasada adversarial + disparadores | 3 h | Nulo | — |
| 5 | **P1.4** Formato de preguntas y rondas | 2 h | Nulo | — |
| 6 | **P0.1** `bundle-lint` | 0,5 d | Bajo | Base de medición para P2.1 |
| 7 | **P1.3** Política por defecto en los tres | 0,5 d | Bajo | El carril más usado |
| 8 | **P2.3** Entrega y destilación | 3 h | Bajo | — |
| 9 | **P2.1** Arnés de evaluación | 3-5 d | Medio | Todo lo demás deja de ser fe |
| 10 | **P2.2** Worktrees por ola | 0,5 d | Medio | Paralelismo real |
| 11 | **P2.4** Frontera de escritura | 0,5 d | Bajo | — |
| 12 | **P2.5** Presupuestos | 2 h | Nulo | — |

Las cinco primeras son **prosa canónica pura**: cero tooling, cero cambio de adaptador, pasan `verify`
tal cual y llegan a los tres harnesses con un `build`+`install`. Ahí está la mayor parte del valor por
unidad de riesgo.

---

## 5. Lo que deliberadamente NO propongo, y por qué

- **Agentes nuevos** (seguridad, escritor de tests, diseñador, QA). El roster está bien factorizado y las
  lagunas están en **bucles y verificación**, no en roles. El planner ya define los tests exactos con su
  señal roja/verde, así que un escritor de tests no tendría trabajo propio. La seguridad es una
  **pregunta que el reviewer no hace**, no un rol que falte: añadirlo duplicaría el descubrimiento y
  produciría un segundo veredicto que alguien tendría que reconciliar. Más agentes es la respuesta fácil
  y equivocada; la investigación de MAST apunta justo al contrario — los fallos vienen del diseño de la
  interacción, no de la falta de participantes.
- **Un controlador de workflow, JSON de estado o esquema de bundle.** El `SKILL.md` lo prohíbe con razón:
  sería una cuarta cosa que los tres harnesses tendrían que acordar y mantener. `bundle-lint` respeta la
  prohibición precisamente porque sólo lee y devuelve un código de salida.
- **Debate / swarm / agentes peer dinámicos.** El patrón supervisor sigue siendo el default de producción;
  debate multiplica el coste y aquí ya existe el mecanismo que aporta su valor real (el segundo
  diagnóstico independiente del carril Debug, y el advisor).
- **Memoria automática entre sesiones.** La política actual («nunca depender de memoria persistente para
  la corrección») es correcta y deliberada. P2.3 aporta el beneficio — destilar a un artefacto
  **verificable del repositorio** — sin aceptar el riesgo de que un hecho recordado y falso gobierne una
  decisión.
- **Reescribir el sistema de despliegue.** Es la mejor pieza del repo. No tocarla.

---

## Fuentes

- [Why Do Multi-Agent LLM Systems Fail? (MAST, Berkeley)](https://arxiv.org/abs/2503.13657) ·
  [sitio del proyecto](https://sites.google.com/berkeley.edu/mast/home)
- [Spec Kit Agents: Context-Grounded Agentic Workflows](https://arxiv.org/html/2604.05278v1)
- [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)
- [2026 Agentic Coding Trends Report — Anthropic](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)
- [Multi-Agent Orchestration: 5 Patterns That Work in 2026](https://www.digitalapplied.com/blog/multi-agent-orchestration-5-patterns-that-work)
- [AI Coding Agents in 2026: Coherence Through Orchestration, Not Autonomy](https://mikemason.ca/writing/ai-coding-agents-jan-2026/)
- [How and when to build multi-agent systems — LangChain](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems)
- [Context Rot in AI Agents: Session Handoffs](https://www.mindstudio.ai/blog/context-rot-ai-agents-session-handoff-fix)
- [Giving AI Agents Visual Feedback with Playwright CLI](https://azukiazusa.dev/en/blog/playwright-cli-ai-agent-visual-feedback/)
- [Visual Feedback Loop — Agentic Coding Handbook](https://tweag.github.io/agentic-coding-handbook/WORKFLOW_VISUAL_FEEDBACK/)
- [The Productivity-Reliability Paradox: Specification-Driven Governance](https://arxiv.org/pdf/2605.01160)
