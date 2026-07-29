# Configuración global de soporte para OpenCode

Checkout sincronizado en `~/.config/opencode` mediante la rama `opencode` de `pma1999/agent-system`. El instalador es `~/.claude/install.ps1` y también puede ejecutarse mediante la skill `sync-agent-system`.

Esta rama **no contiene un sistema multiagente personalizado**: OpenCode utiliza sus agentes integrados. Se conservan únicamente:

- `AGENTS.md` — reglas de documentación Context7.
- `templates/opencode.jsonc` — merge aditivo de los MCP `codegraph` y `playwright`.
- MCP Playwright globalmente desactivado para ahorrar contexto y habilitado en el agente integrado `build`.
- Compatibilidad con las skills globales de `~/.claude/skills`; la skill Claude `orchestrator` está denegada en OpenCode para no activar el sistema del runtime equivocado.

## WSL

OpenCode en WSL lee configuración y skills externas desde el home de Linux. Puentes de una sola vez:

```bash
ln -s /mnt/c/Users/<usuario-windows>/.config/opencode ~/.config/opencode
mkdir -p ~/.claude
ln -s /mnt/c/Users/<usuario-windows>/.claude/skills ~/.claude/skills
npx -y @playwright/mcp@latest install-browser chromium
sudo npx -y playwright@latest install-deps chrome-for-testing
```

El enlace de skills expone globalmente `sync-agent-system`, las skills frontend, documentación y demás utilidades compatibles sin copiarlas. La configuración de permisos oculta y deniega únicamente la skill Claude `orchestrator`.
