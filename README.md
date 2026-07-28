# Rama `opencode` — sistema multiagente para OpenCode

Checkout en `~/.config/opencode`. Documentación completa del sistema (instalación, sync, qué se versiona) en la rama `master` (`~/.claude/README.md`). El instalador/sync es `~/.claude/install.ps1` (o la skill `/sync-agent-system`).

## Contenido

- `AGENTS.md` — reglas globales de OpenCode: orquestador obligatorio, barra frontend, doctrina de retrieval (glob/grep/codegraph), Context7 CLI.
- `agents/` — los 6 especialistas (subagentes OpenCode, `task` deshabilitada y `edit` habilitada explícitamente en todos: OpenCode usa el permiso `edit` también para la herramienta `write`, necesaria para mapas/recetas/planes/diagnósticos/reports/reviews; los prompts de roles no-productivos limitan esa escritura a sus artifacts):
  - `implementation-planner` → `openai/gpt-5.6-sol` con `reasoningEffort: xhigh`
  - `integration-researcher`, `root-cause-debugger`, `implementation-reviewer` → `openai/gpt-5.6-luna` con `reasoningEffort: max`
  - `codebase-explorer`, `task-implementer-bdd` → `opencode-go/deepseek-v4-flash` con `reasoningEffort: max`
- `skills/opencode-orchestrator/` — la skill orquestadora (motor único nativo: dispatch vía herramienta `task`, reanudación por `task_id`, segunda diagnosis con instancia independiente ante diagnósticos atascados). OpenCode puede descubrir la skill Claude `orchestrator` mediante compatibilidad, pero `permission.skill` la oculta y deniega; `opencode-orchestrator` queda explícitamente permitida y `AGENTS.md` obliga a usarla.
- `templates/opencode.jsonc` — claves del sistema fusionadas aditivamente en el `opencode.jsonc` real por `install.ps1`: MCP `codegraph` global y MCP `playwright` headless, deshabilitado globalmente pero habilitado en implementer, reviewer, integration-researcher y debugger para no inflar el contexto de los demás agentes. JSON puro sin comentarios a propósito (el merge lo parsea con PowerShell).

## WSL

OpenCode en WSL lee configuración y skills externas desde el home de Linux. Puentéalos una sola vez al origen sincronizado de Windows:

```bash
ln -s /mnt/c/Users/<usuario-windows>/.config/opencode ~/.config/opencode
mkdir -p ~/.claude
ln -s /mnt/c/Users/<usuario-windows>/.claude/skills ~/.claude/skills
npx -y @playwright/mcp@latest install-browser chromium
sudo npx -y playwright@latest install-deps chrome-for-testing
```

El segundo enlace hace globales en cualquier proyecto WSL las skills sincronizadas (`sync-agent-system`, `frontend`, `frontend-one`, `find-docs`, etc.) sin copiarlas. La skill Claude `orchestrator` queda oculta y denegada por configuración; solo `opencode-orchestrator` se anuncia al agente. Los dos últimos comandos instalan Chromium y sus dependencias Linux para Playwright; requieren `sudo` una sola vez por distro WSL.
