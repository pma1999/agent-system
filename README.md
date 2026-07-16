# agent-system, rama codex (~/.codex)

Mitad Codex del sistema multiagéntico personal: `AGENTS.md`, skill `orchestrator` (SKILL + references + scripts), 6 agentes especialistas (TOML) y `templates/config.toml` (claves del sistema, fusionadas aditivamente en el `config.toml` local).

Es la rama **`codex`** del repo único `github.com/pma1999/agent-system` (la rama `master` es `~/.claude` y contiene el instalador y el README completo). **No se gestiona a mano**:

```powershell
pwsh -File "$HOME/.claude/install.ps1"          # instalar/actualizar ambas carpetas
pwsh -File "$HOME/.claude/install.ps1" -Push    # publicar cambios de ambas
```
