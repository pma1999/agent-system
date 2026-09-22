# Sistema multiagéntico personal

Un único sistema de orquestación de ingeniería de software, instalado en tres harnesses —**Claude
Code**, **Codex CLI** y **OpenCode**— con **prompts idénticos** y una capa de adaptación pequeña,
declarada y auditable.

Este repo es la **única fuente de verdad**. `~/.claude`, `~/.codex` y `~/.config/opencode` son
destinos de despliegue: lo que hay ahí se genera desde aquí.

```
source/  +  harness/        ->      rendered/       ->     carpetas vivas
cuerpos canónicos           build   lo que se        install   ~/.claude
+ adaptadores por harness           instalará                  ~/.codex
                                    (commiteado)               ~/.config/opencode
```

## El sistema en un párrafo

Un coordinador concreta el resultado pedido y elige el siguiente especialista por la evidencia
que falta, reevaluando después de cada retorno. Los carriles (Directo, Quick, Plan → Implementar
→ Revisar, o Debug) organizan la entrega; no imponen una secuencia fija. Delega en explorador de código,
investigador de integraciones, planificador, depurador de causa raíz, implementador BDD y revisor
independiente, más un `advisor` de solo lectura para las decisiones difíciles. Nadie pega historial
en el chat: los hechos duraderos viven en un bundle de artefactos Markdown bajo `plans/<slug>/`, con
un dueño por artefacto y un `progress.md` como libro mayor. Las dudas que pueden cambiar la solución
se resuelven antes de avanzar; una credencial, acceso o decisión del usuario pendiente bloquea el
trabajo dependiente. Ver [docs/DISENO.md](docs/DISENO.md).

## Tabla de adaptadores

Esto es lo único que puede diferir entre harnesses. Todo lo demás del prompt es literalmente el
mismo texto, y `verify` lo demuestra en cada ejecución.

| Concepto | `claude` | `codex` | `opencode` |
|---|---|---|---|
| `ORCH_SKILL` | `orchestrator` | `orchestrator` | `opencode-orchestrator` |
| `WORKFLOW` | `orchestrator` | `orchestrator` | `orquestador` |
| `PARENT` | `thread` | `thread` | `orquestador` |
| `COORDINATOR_INTRO` | el hilo principal de Claude Code | el hilo Codex de nivel superior | el agente `orquestador` |
| `SPAWN` | tool `Agent` con `subagent_type` | `spawn_agent` (`agent_type`, `fork_turns="none"`) | tool `task` con `subagent_type` |
| `RESUME` | `SendMessage` al id del agente | `followup_task` | `task` con el `task_id` |
| `OWNER_ID` | agent id | agent id | `task_id` |
| `ASK_USER` | tool `AskUserQuestion` | pregunta directa en el hilo | tool `question` |
| `ADVISOR_DELEGATION` | tool nativa `advisor()` | subagente vía `spawn_agent` + `fork_turns="all"` | subagente vía `task` + plugin `advisor-context` |
| `ROSTER_ADVISOR` | fila "tool nativa" | fila de despacho | fila de despacho |
| `PROVENANCE` | `engine=claude-code \| model=opus` | `engine=codex \| model=gpt-6-sol` | `engine=opencode \| model=muse-spark-1.3` |
| `MODEL_PIN` | perfil por rol en cada fichero | perfil por rol en cada TOML | roster entero a muse-spark-1.3/xhigh |
| `MODEL` / `EFFORT` | por rol, en `[agents.<rol>]` | idem, se renderiza como `model_reasoning_effort` | idem, se renderiza como `variant` |
| `BUNDLE_LINT` | `python ~/.claude/skills/orchestrator/scripts/bundle_lint.py` | `python ~/.codex/skills/orchestrator/scripts/bundle_lint.py` | `python ~/.config/opencode/skills/opencode-orchestrator/scripts/bundle_lint.py` |

**Bloques exclusivos** (secciones enteras, no tokens; viven en
`source/orchestration/skill/sections/`):

| Ancla | claude | codex | opencode |
|---|---|---|---|
| `invocation` | hilo principal, opt-in | hilo Codex, `$orchestrator` | directo o `delegated-by-build`, `subagent_depth: 2` |
| `dispatch` | Agent + SendMessage | spawn/followup/wait + estado wait-only | task + task_id |
| `advisor` | brief antes de la llamada, sin reanudación | fork del hilo | plugin de inyección de transcripción |
| `outbound-status` | — | — | `NEEDS_USER_DECISION` hacia `build` |
| `user-decision` | — | — | bloque de handoff a `build` |

**Frontera de escritura.** Solo el implementador escribe producción. Quién lo garantiza difiere y
conviene saberlo: en **opencode** está atado por configuración (`permission.edit` por rol, con
`plans/**` permitido); en **claude** y **codex** la frontera es prosa del prompt — `disallowedTools:
Agent` y `sandbox_mode = "workspace-write"` no la imponen. Los roles read-only necesitan escribir su
artefacto bajo `plans/**`, así que una denegación total de escritura los rompería.

**Navegador.** Los tres instalan **Playwright MCP** y **Chrome DevTools MCP**, disponibles para todos
los roles. Ninguno es el por defecto: cada agente mira las tools que tiene y elige. En claude viven
en `~/.claude.json` (es donde Claude guarda los MCP de usuario, no en `settings.json`); en codex y
opencode, en sus plantillas de config.

Los MCP de navegador se configuran para guardar evidencias fuera de la carpeta del proyecto:
Playwright usa `--allow-unrestricted-file-access` y Chrome DevTools
`--allow-unrestricted-paths`. Este ultimo se aplica cuando el cliente no negocia MCP roots;
si el cliente comunica roots, Chrome DevTools sigue respetandolas. Los permisos del sistema
operativo siguen vigentes. Tras sincronizar, reinicia los clientes para recargar los MCP.
`install` migra tambien los argumentos existentes de los paquetes oficiales `@latest`,
sin duplicar flags ni modificar versiones fijadas o una opcion explicita `--flag=false`.
En Windows, usa rutas nativas o el temporal real del sistema: `/tmp` se resuelve a `C:\tmp`.
La regresion de esta migracion se comprueba con `python bin/test_browser_paths.py`.

Dos detalles comprobados en ejecucion, no deducidos:

- En **codex** el servidor se llama `chrome_devtools`, sin guion, a proposito: un id citado seria
  TOML valido pero un servidor MCP que el runtime no acepta no da error, se ignora en silencio.
- En **opencode** (que corre bajo WSL) `chrome-devtools-mcp` busca Google Chrome estable en
  `/opt/google/chrome/chrome`, que ahi no existe: conecta igual y **falla en la primera llamada**.
  Por eso su comando lleva `--executable-path /snap/bin/chromium`, igual que ya hacia playwright.
  Verificado despachando un `codebase-explorer` que invoco `playwright_browser_navigate` y
  `chrome-devtools_navigate_page` contra una pagina real. El implementador adjunta capturas y snapshot de
accesibilidad a su report cuando el brief lleva `UI Contract`, y el reviewer juzga el render antes
que el diff.

**Ficheros exclusivos de un harness** (`harness/<h>/files/`): `CLAUDE.md` (claude);
`AGENTS.md` y `skills/orchestrator/agents/openai.yaml` (codex); `AGENTS.md` y
`plugin/advisor-context.ts` (opencode). El agente padre `orquestador` no es un fichero literal:
es un rol mas del roster, declarado solo para opencode, para que `models` pueda fijar su modelo.

**Roles.** Los seis especialistas existen en los tres. `advisor` existe como subagente sólo en Codex
y OpenCode: **Claude Code tiene `advisor` como tool nativa**, disponible tanto para el hilo
principal como para cada especialista, así que allí no hace falta el fichero de agente. El agente
padre `orquestador` existe sólo en OpenCode; en Claude y Codex orquesta el hilo principal, al que
`CLAUDE.md` / `AGENTS.md` le dicen que cargue la skill cuando el usuario pida orquestar.

## Dónde va un cambio

Nunca edites las carpetas vivas: `install` las sobrescribe y `verify` canta la deriva.

| Lo que quieres cambiar | Fichero a editar |
|---|---|
| El prompt de un especialista, para los tres | `source/orchestration/agents/<rol>.md` |
| El modelo operativo de orquestación | `source/orchestration/skill/SKILL.md` |
| Algo cierto sólo en un harness | `source/orchestration/skill/sections/<ancla>.<harness>.md` |
| Añadir/quitar un rol, o su descripción | `source/orchestration/roles.toml` |
| El modelo o el effort de un rol | `agentsys models` (no edites el adaptador a mano) |
| Permisos, colores, nombres de tool, sandbox | `harness/<h>/adapter.toml` |
| Una skill compartida por los tres | `source/skills/<skill>/` |
| El validador del bundle | `source/orchestration/skill/scripts/bundle_lint.py` |
| Una skill de un solo harness | `harness/<h>/files/skills/<skill>/` |
| `CLAUDE.md`, `AGENTS.md`, plantillas, parches, reglas | `harness/<h>/files/` |

Si te descubres copiando el mismo texto en dos adaptadores, ese texto pertenece al cuerpo canónico.
Si te descubres poniendo un `if` mental por harness dentro del cuerpo canónico, eso es un token o
una sección.

## Ciclo de trabajo

```bash
cd ~/agent-system
python bin/agentsys.py build      # source/ + harness/  ->  rendered/
python bin/agentsys.py verify     # las cuatro comprobaciones
python bin/agentsys.py install    # rendered/  ->  carpetas vivas
python bin/agentsys.py publish -m "resumen real del cambio"
```

En Windows, `pwsh -NoProfile -File "$HOME/agent-system/bin/install.ps1"` hace pull + build +
install + verify de una vez.

Otros comandos: `status` (resumen corto), `adopt` (recupera al canon un cambio hecho a mano en una
carpeta viva), `install --dry-run`, `install --force`, `install --retire-legacy`.

**Desde WSL**, `~` es el home de Linux pero Claude Code y Codex leen el de Windows. `agentsys` lo
detecta y avisa; pásale `--home /mnt/c/Users/<usuario>` (o `AGENTSYS_HOME`) si de verdad quieres
lanzarlo desde ahí. Ver [docs/INSTALACION.md](docs/INSTALACION.md).

## Modelos

El modelo y el effort de cada rol viven en `harness/<h>/adapter.toml`, en claves estructuradas
(`[agents.<rol>]` -> `model`, `effort`), y el frontmatter los referencia con `{{MODEL}}` y
`{{EFFORT}}`. Un **perfil** es un fichero pequeño que fija esos dos valores para todo el roster:

```
harness/<h>/model-profiles/<nombre>.toml
```

```bash
python bin/agentsys.py models list                              # perfiles de los tres; * = el vigente
python bin/agentsys.py models show ox-alpha-free-max --harness opencode
python bin/agentsys.py models apply ox-alpha-free-max --harness opencode
python bin/agentsys.py models set --harness claude --model opus --effort xhigh
python bin/agentsys.py models set --harness codex --model gpt-6-sol --role implementation-planner
python bin/agentsys.py models save mi-perfil --harness opencode -m "por que lo guardo"
```

`apply` y `set` reescriben el adaptador y vuelven a renderizar; después hace falta `install`.

**Por qué está apartado por harness.** OpenCode tiene muchos más modelos disponibles y cambia con
frecuencia — de ahí sus once perfiles. Claude y Codex cambian poco y arrancan con un único perfil
`actual`. El mecanismo es el mismo; lo que no se comparte son los perfiles, porque un nombre de
modelo no significa nada fuera de su harness.

**`--scope`, sólo relevante en OpenCode.** `oh-my-opencode-slim` (OMO) es *otro* sistema de agentes
—el flujo por defecto de OpenCode, con su propio `orchestrator`, `oracle`, `librarian`— y su config
es estado local de cada máquina que no viaja en el repo. Por eso:

| `--scope` | Qué toca |
|---|---|
| `ours` (por defecto) | sólo el roster del orquestador |
| `omo` | sólo los agentes del preset activo de `oh-my-opencode-slim.json` |
| `both` | los dos |

Con `--omo-preset <nombre>` se apunta a un preset distinto del activo.

## El gate de validación del bundle

`source/orchestration/skill/scripts/bundle_lint.py` viaja **dentro de la skill orquestadora**, así
que los tres harnesses lo instalan en la misma ruta relativa y el token `{{BUNDLE_LINT}}` resuelve el
comando exacto de cada uno. Es de solo lectura: lee los artefactos Markdown, los contrasta con el
worktree, imprime hallazgos `BL-nn` y devuelve un código de salida. No conduce el flujo ni edita
nada, así que no es el "bundle controller" que el modelo operativo prohíbe — es correr los tests del
bundle.

```bash
python <ruta>/bundle_lint.py plans/<slug> --phase pre-approval    # antes de pedir aprobación
python <ruta>/bundle_lint.py plans/<slug> --phase pre-synthesis   # antes de la respuesta final
```

Caza lo que el juicio de un LLM sobre su propio texto no caza: rutas y símbolos que no existen,
comandos de test que no se pueden ejecutar, briefs a los que les falta una sección del esquema,
tareas de la misma ola tocando el mismo fichero, nombres de artefacto prohibidos, tareas de UI sin
evidencia visual, filas del ledger sin estado terminal, hallazgos `RC-nn` abiertos. Solo es
`BLOCKER` lo que es demostrablemente falso; el resto queda en `WARN`/`INFO`. Si falta el script o el
intérprete, el coordinador lo dice y hace las mismas comprobaciones a mano.

## Qué garantiza `verify`

1. **Render determinista.** `rendered/` es exactamente lo que produce `source/ + harness/`. Detecta
   cualquier edición hecha directamente sobre la salida.
2. **Identidad de prompts.** Para cada rol presente en ≥2 harnesses, y para la skill, en dos
   direcciones. *Ida:* se renderiza el cuerpo con los tokens marcados con un centinela, se quitan
   los bloques de `sections/` y se exige igualdad byte a byte contra el canónico. *Vuelta:* se coge
   lo realmente renderizado en `rendered/`, se le quita el envoltorio del harness y las secciones, y
   se revierte la sustitución de tokens, exigiendo otra vez el canónico. La vuelta es la que caza un
   valor de token que colisione con la prosa: si el mismo texto es a la vez token y palabra del
   prompt, la inversa sobre-sustituye y el check falla. Es intencionado — ese valor es ambiguo.
   (Dos tokens con el mismo valor en un harness sí se permiten: se normalizan por valor.)
3. **Envoltorio: esquema y roster.** Cada harness recibe sólo claves y valores que entiende: alias
   de modelo, `effort` y color dentro de rango, ningún especialista con la tool `Agent`, el advisor
   en `read-only`, el `name` coincidiendo con el fichero, la skill con el nombre esperado, el roster
   cuadrado y ningún artefacto con nombre prohibido. Un valor fuera de rango no da error en el
   runtime: se ignora en silencio, que es peor. `build` además aborta si un cuerpo contiene `'''` o
   acaba en `\`, que romperían el `developer_instructions` de Codex.
4. **Deriva.** Las carpetas vivas coinciden con `rendered/`.

## Seguridad del despliegue

- `install` guarda copia con marca de tiempo de **cada** fichero que reemplaza en
  `~/.agent-system-backups/<fecha>/`.
- Mantiene un manifiesto (`.agent-system-manifest.json`) en cada carpeta viva. Un fichero que
  existe, difiere y **nunca estuvo gestionado** no se toca: se reporta y hace falta `--force`.
- Los ficheros que gestionábamos y ya no se generan se retiran al backup, no se borran.
- Las plantillas de configuración se fusionan de forma **aditiva**: se añaden las claves del sistema
  que falten y jamás se sobrescribe un valor existente. Las excepciones declaradas son subir
  `subagent_depth` a 2 en OpenCode y añadir los permisos de rutas de los MCP de navegador
  oficiales `@latest` descritos arriba. Los comentarios y el
  formato del fichero del usuario se conservan, así que una clave **anidada** que falte dentro de un
  bloque que ya existe no se inserta: se reporta por su ruta con `REVISA A MANO` para que la añadas
  tú. Silenciarla sería peor que pedírtela.
- `publish` usa lista explícita de ficheros. Nunca `git add -A`, así que ni el estado de máquina ni
  las skills de plugin sincronizadas desde claude.ai pueden acabar en el repo.

## Qué se sincroniza y qué no

| Se sincroniza | Local de cada máquina |
|---|---|
| Prompts de orquestación y agentes | credenciales, sesiones, historial, transcripciones |
| Skills (compartidas y por harness) | `settings.json`, `config.toml`, `opencode.jsonc` reales |
| `CLAUDE.md`, `AGENTS.md` | caches de plugin, sqlite, logs, memoria automática |
| Plantillas de configuración, parches, reglas | `skills/synced/`, `plugins/synced/` (skills de terceros) |

## Estructura

```
README.md                 este documento
docs/DISENO.md            el modelo operativo, agnóstico de harness
docs/MANTENIMIENTO.md     invariantes, flujo de cambio, definition of done
docs/INSTALACION.md       PC nuevo, WSL, problemas típicos
docs/HARNESS-OPENCODE.md  manual concreto de la instalación OpenCode
source/orchestration/     roles.toml, skill/SKILL.md + sections/ + scripts/, agents/<rol>.md
source/skills/            skills desplegadas en los tres harnesses
harness/<h>/adapter.toml  tokens, modelo/effort y envoltorio por rol, frontmatter de la skill
harness/<h>/model-profiles/ perfiles de modelos de ese harness
harness/<h>/files/        ficheros literales sólo de ese harness
rendered/<h>/             salida determinista, commiteada
bin/agentsys.py           build | verify | status | install | adopt | publish
bin/install.ps1           atajo de Windows
```

## Historia

Antes de esta unificación el sistema vivía en tres ramas (`master`, `codex`, `opencode`) cuyos
working trees eran las propias carpetas de configuración, y los prompts se editaban a mano tres
veces. Divergieron: la skill orquestadora llegó a tener 473 líneas en OpenCode, 375 en Codex y cero
en Claude, donde había sido borrada. Esas ramas se conservan congeladas como historia, junto con los
tags `pre-unificacion-20260917-*` y `orchestrator-system-v1`. La ruta de restauración está en
`~/agent-system-backup-20260917/RESTORE.md`.
