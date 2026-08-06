# Sistema global de ingenieria para OpenCode

Checkout sincronizado en `~/.config/opencode` mediante la rama `opencode` de
`pma1999/agent-system`. El instalador es `~/.claude/install.ps1` y tambien puede ejecutarse mediante
la skill `sync-agent-system`.

## Instalar o actualizar en otro PC

Primera instalacion en Windows (requiere PowerShell 7, Git, Node LTS y acceso autenticado al repo
privado, por ejemplo mediante `gh auth login`):

```powershell
git clone https://github.com/pma1999/agent-system.git "$env:TEMP\agent-system"
pwsh -NoProfile -File "$env:TEMP\agent-system\install.ps1"
```

El instalador prepara conjuntamente `~/.claude`, `~/.codex` y `~/.config/opencode`, conserva copias
de seguridad de los archivos preexistentes que pudiera sustituir y fusiona las plantillas
conservando preferencias locales. Solo aplica migraciones concretas necesarias para el sistema,
como elevar `subagent_depth` de `1` a `2`. Para actualizar posteriormente desde cualquier PC:

```powershell
pwsh -NoProfile -File "$HOME/.claude/install.ps1"
```

Las credenciales no se sincronizan. Hay que iniciar sesion en OpenCode y sus proveedores de modelos
en cada maquina. Si OpenCode se ejecuta en WSL, aplica tambien los puentes de la seccion WSL.

## Flujo predeterminado

El agente predeterminado es explicitamente `build`. Su politica vive en `AGENTS.md`: trabajo
directo, verificacion con las herramientas del proyecto y delegacion acotada a `explore`,
`diff-review` y `consult`. Restaurar el sistema multiagente no cambia ese comportamiento.

- `explore` - exploracion integrada, fijada al modelo principal y con 25 pasos.
- `diff-review` - revision limpia del diff; verifica sin modificar codigo ni estado de git.
- `consult` - consulta puntual a un modelo mas fuerte; verifica sin modificar codigo.
- `review` - respaldo del comando `/review`; revisa cambios sin tocarlos.
- `prompts/` - contratos de `diff-review`, `consult` y `review`.

Los agentes de revision pueden usar terminal y escribir sondas solo bajo `/tmp/opencode/`, con
limpieza obligatoria. No pueden modificar el proyecto, cambiar git, instalar paquetes, usar
`sudo` ni ejecutar formateadores in-place.

## Orquestador opcional

`orquestador` es un agente padre opcional, nunca el predeterminado. Se activa de dos formas:

1. El usuario lo selecciona directamente en el selector de agentes de OpenCode.
2. `build` propone delegarle una tarea genuinamente compleja y el usuario aprueba el `task`.

La segunda ruta envia `Invocation: delegated-by-build`. `orquestador` conserva la propiedad del
trabajo y, cuando necesita aprobacion o una decision de producto, devuelve
`STATUS: NEEDS_USER_DECISION`; `build` pregunta al usuario y reanuda el mismo `task_id`.

No se usa para cambios pequenos. Esta pensado para varias olas de implementacion, refactors
amplios entre subsistemas, contratos publicos acoplados, diagnosticos dificiles y cambios
transversales de migracion o seguridad.

El sistema vive en:

- `agents/orquestador.md` - agente padre seleccionable y delegable.
- `skills/opencode-orchestrator/SKILL.md` - triage, artefactos, aprobaciones, olas, revisiones y
  recuperacion ante bloqueos.
- `agents/codebase-explorer.md` - mapa inicial del repositorio.
- `agents/integration-researcher.md` - contrato externo verificado.
- `agents/implementation-planner.md` - diseno y briefs ejecutables.
- `agents/root-cause-debugger.md` - diagnostico causal sin implementar.
- `agents/task-implementer-bdd.md` - unico especialista que escribe codigo de produccion.
- `agents/implementation-reviewer.md` - revision independiente por tarea o final.

`subagent_depth` vale `2` para permitir `build -> orquestador -> especialista`. Todos los
especialistas tienen `task: deny`, por lo que no existe un tercer nivel ni recursion accidental.
`build` no puede cargar la skill multiagente, no puede invocar directamente a los especialistas y
su permiso para invocar `orquestador` es `ask`. El padre y los especialistas sin codigo solo pueden
editar `plans/**` y `/tmp/opencode/**`; `task-implementer-bdd` conserva la escritura de produccion.

## Configuracion

MCP Playwright esta desactivado globalmente para ahorrar contexto y se habilita solo en los
agentes que lo necesitan. La skill Claude `orchestrator` sigue denegada para evitar activar el
runtime equivocado; la skill propia de OpenCode es `opencode-orchestrator`.

`templates/opencode.jsonc` instala valores sincronizados mediante merge aditivo y migraciones
obligatorias acotadas. MCP con autenticacion, rutas locales y preferencias de maquina permanecen
solo en el `opencode.jsonc` runtime.

## Modelos

| Componente | Modelo | Variante | Proveedor |
| --- | --- | --- | --- |
| `build` / principal | DeepSeek V4 Flash | `max` | OpenCode Go |
| `small_model` | DeepSeek V4 Flash Free | - | OpenCode |
| `explore` | DeepSeek V4 Flash | `max` | OpenCode Go |
| `diff-review` | GPT-5.6 Luna | `max` | OpenAI OAuth |
| `consult` | GPT-5.6 Sol | `xhigh` | OpenAI OAuth |
| `review` | DeepSeek V4 Flash (default) | `max` | OpenCode Go |
| `orquestador` | DeepSeek V4 Flash | `max` | OpenCode Go |
| `codebase-explorer` / `task-implementer-bdd` | DeepSeek V4 Flash | `max` | OpenCode Go |
| `implementation-planner` | GPT-5.6 Sol | `xhigh` | OpenAI OAuth |
| `integration-researcher` / `root-cause-debugger` / `implementation-reviewer` | GPT-5.6 Luna | `max` | OpenAI OAuth |

## WSL

OpenCode en WSL lee configuración y skills externas desde el home de Linux. Puentes de una sola vez:

```bash
ln -s /mnt/c/Users/<usuario-windows>/.config/opencode ~/.config/opencode
mkdir -p ~/.claude
ln -s /mnt/c/Users/<usuario-windows>/.claude/skills ~/.claude/skills
npx -y @playwright/mcp@latest install-browser chromium
sudo npx -y playwright@latest install-deps chrome-for-testing
```

El enlace de skills expone globalmente `sync-agent-system`, las skills frontend, documentacion y
demas utilidades compatibles sin copiarlas. Los permisos separan la skill Claude `orchestrator`
de la skill OpenCode `opencode-orchestrator`.
