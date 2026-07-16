# codex-config (~/.codex)

Mitad Codex del sistema multiagéntico personal: `AGENTS.md`, skill `orchestrator` (SKILL + references + scripts), 6 agentes especialistas (TOML) y `templates/config.toml` (claves del sistema, fusionadas aditivamente en el `config.toml` local).

**No se gestiona a mano**: la instalación, actualización y publicación de este repo las hace `~/.claude/install.ps1` (repo hermano `github.com/pma1999/claude-config`, que contiene el instalador y el README completo).

```powershell
pwsh -File "$HOME/.claude/install.ps1"          # instalar/actualizar ambos
pwsh -File "$HOME/.claude/install.ps1" -Push    # publicar cambios de ambos
```
