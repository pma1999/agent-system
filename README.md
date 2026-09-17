# Configuracion global de OpenCode

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
conservando preferencias locales. Las credenciales y la configuracion personalizada de
`oh-my-opencode-slim.json` son locales y no se sincronizan.

Para actualizar posteriormente desde cualquier PC:

```powershell
pwsh -NoProfile -File "$HOME/.claude/install.ps1"
```

## Flujo predeterminado

`oh-my-opencode-slim` proporciona el agente predeterminado `orchestrator` y sus especialistas
`oracle`, `council`, `librarian`, `explorer`, `designer`, `fixer` y `observer`. La instalacion se
registra sin fijar version en `opencode.jsonc`, por lo que carga la ultima version compatible del
paquete.

La configuracion local restaurada vive en `oh-my-opencode-slim.json`:

- preset activo `hybrid-optimal`;
- presets alternativos `openai-optimal` y `opencode-go-optimal`;
- Observer habilitado y enrutado automaticamente para imagenes;
- Council `quality-price` con perfiles pragmatist, architect y critic;
- multiplexer automatico con layout `main-vertical` y panel principal al 60%;
- skills y MCP asignados por agente, con `websearch` moderno habilitado para Librarian.

No existe un `AGENTS.md` global ni los antiguos agentes inline `consult`, `diff-review` y `review`,
sus prompts o el comando `/review`.

## Orquestador alternativo conservado

`orquestador` es un sistema independiente y opcional, distinto del `orchestrator` de OMO. Se
selecciona manualmente en OpenCode cuando se necesita su flujo de discovery, planificacion,
implementacion BDD por olas y revision independiente. No es el agente predeterminado.

El sistema conservado vive en:

- `agents/orquestador.md` - agente padre seleccionable;
- `skills/opencode-orchestrator/SKILL.md` - triage, artefactos, aprobaciones, olas y recuperacion;
- `agents/codebase-explorer.md` - mapa inicial del repositorio;
- `agents/integration-researcher.md` - contrato externo verificado;
- `agents/implementation-planner.md` - diseno y briefs ejecutables;
- `agents/root-cause-debugger.md` - diagnostico causal sin implementar;
- `agents/task-implementer-bdd.md` - especialista que escribe codigo de produccion;
- `agents/implementation-reviewer.md` - revision independiente por tarea o final;
- `agents/advisor.md` - consultor read-only de segundo criterio (GPT-5.6 Sol);
- `plugin/advisor-context.ts` - inyecta el transcript completo del consultante en cada consulta
  a `advisor`.

`subagent_depth` se mantiene en `2`. Los especialistas solo pueden consultar `advisor` via la
task tool; todo lo demas queda denegado, por lo que no existe recursion accidental. La skill
Claude `orchestrator` sigue denegada para evitar activar el runtime equivocado. OMO tiene
denegada `opencode-orchestrator`; esa skill queda disponible solo para el `orquestador`
conservado.

## Configuracion

`templates/opencode.jsonc` instala por merge los MCP sincronizados, el plugin OMO, LSP y los ajustes
necesarios para conservar el orquestador alternativo. MCP con autenticacion, rutas locales y otras
preferencias de maquina permanecen solo en el `opencode.jsonc` runtime.

MCP Playwright esta desactivado globalmente para ahorrar contexto y se habilita en `build` y en los
agentes conservados que lo declaran. OMO controla los permisos de sus propios agentes.

## Modelos

| Componente | Modelo | Variante | Proveedor |
| --- | --- | --- | --- |
| OMO `orchestrator`, `explorer`, `librarian`, `designer`, `fixer` | DeepSeek V4 Flash | `max` | OpenCode Go |
| OMO `oracle` | DeepSeek V4 Pro | `max` | OpenCode Go |
| OMO `council` | DeepSeek V4 Pro | `max` | OpenCode Go |
| OMO `observer` | MiMo V2.5 | - | OpenCode Go |
| `orquestador` | DeepSeek V4 Flash | `max` | OpenCode Go |
| `codebase-explorer` / `task-implementer-bdd` | DeepSeek V4 Flash | `max` | OpenCode Go |
| `implementation-planner` | GPT-5.6 Sol | `high` | OpenAI OAuth |
| `advisor` | GPT-5.6 Sol | `high` | OpenAI OAuth |
| `integration-researcher` / `root-cause-debugger` / `implementation-reviewer` | GPT-5.6 Luna | `max` | OpenAI OAuth |

## WSL

OpenCode en WSL lee configuracion y skills externas desde el home de Linux. Puentes de una sola vez:

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
