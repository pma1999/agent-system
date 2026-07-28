# Rama `opencode` — sistema multiagente para OpenCode

Checkout en `~/.config/opencode`. Documentación completa del sistema (instalación, sync, qué se versiona) en la rama `master` (`~/.claude/README.md`). El instalador/sync es `~/.claude/install.ps1` (o la skill `/sync-agent-system`).

## Contenido

- `AGENTS.md` — reglas globales de OpenCode: orquestador obligatorio, barra frontend, doctrina de retrieval (glob/grep/codegraph), Context7 CLI.
- `agents/` — los 6 especialistas (subagentes OpenCode, herramienta `task` deshabilitada en todos):
  - `implementation-planner`, `integration-researcher`, `root-cause-debugger` → `opencode-go/glm-5.2` con `reasoningEffort: max`
  - `codebase-explorer`, `task-implementer-bdd`, `implementation-reviewer` → `opencode-go/deepseek-v4-flash` con `reasoningEffort: max`
- `skills/opencode-orchestrator/` — la skill orquestadora (motor único nativo: dispatch vía herramienta `task`, reanudación por `task_id`, segunda diagnosis con instancia independiente ante diagnósticos atascados). Nombre distinto de `orchestrator` a propósito: OpenCode también descubre `~/.claude/skills/` y los nombres de skill deben ser únicos.
- `templates/opencode.jsonc` — claves del sistema (MCP `codegraph`) fusionadas aditivamente en el `opencode.jsonc` real por `install.ps1`. JSON puro sin comentarios a propósito (el merge lo parsea con PowerShell).

## WSL

OpenCode en WSL lee `~/.config/opencode` del home de Linux. Puentéalo con un symlink al checkout de Windows:

```bash
ln -s /mnt/c/Users/<usuario-windows>/.config/opencode ~/.config/opencode
```
