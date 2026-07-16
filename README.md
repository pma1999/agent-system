# Sistema multiagéntico personal (~/.claude + ~/.codex)

Configuración versionada del sistema de orquestación multiagente para **Claude Code** y **Codex CLI**: `CLAUDE.md`/`AGENTS.md`, skill `orchestrator` (+ referencias), 6 agentes especialistas por lado, parches del plugin Codex y plantillas de configuración. Dos repos privados espejo:

- `github.com/pma1999/claude-config` → se instala en `~/.claude` (este repo; incluye el instalador)
- `github.com/pma1999/codex-config` → se instala en `~/.codex`

`install.ps1` gestiona **los dos** a la vez.

## Instalar en un PC nuevo (cualquier usuario)

Requisitos: PowerShell 7 (`winget install Microsoft.PowerShell`), git (`winget install Git.Git`), Node LTS (`winget install OpenJS.NodeJS.LTS`), y acceso al repo privado (lo más cómodo: `winget install GitHub.cli` + `gh auth login`, que configura las credenciales de git). Claude Code y Codex CLI se instalan aparte como siempre.

```powershell
git clone https://github.com/pma1999/claude-config.git "$env:TEMP\claude-config"
pwsh -File "$env:TEMP\claude-config\install.ps1"
```

El instalador convierte `~/.claude` y `~/.codex` en clones de los repos (haciendo copia de seguridad en `backup-preinstall-<fecha>/` de cualquier fichero previo que fuera a sobrescribir), fusiona las plantillas de configuración y aplica el parche del plugin si ya existe. Después:

1. Abre `claude` — inicia sesión si hace falta; en el primer arranque instala los plugins de `settings.json`.
2. Ejecuta `/repatch-codex` dentro de Claude Code (si el instalador dejó el parche pendiente por no existir aún el plugin).
3. `codex login` si vas a usar el lado Codex.

## Actualizar (en cualquier PC, en cualquier momento)

```powershell
pwsh -File "$HOME/.claude/install.ps1"
```

O, dentro de Claude Code: `/sync-agent-system`.

## Publicar cambios hechos en este PC

```powershell
pwsh -File "$HOME/.claude/install.ps1" -Push -Message "descripcion del cambio"
```

O `/sync-agent-system push`. Commitea y sube los dos repos. Si otro PC publicó antes, haz primero un update; si git avisa de divergencia: `git -C $HOME\.claude pull --rebase origin master` (ídem `.codex`).

## Qué se sincroniza y qué no

| Se sincroniza (versionado) | Local de cada máquina (nunca se sube) |
|---|---|
| `CLAUDE.md`, `AGENTS.md` | credenciales (`.credentials.json`, `auth.json`), sesiones, historial |
| `agents/`, `skills/`, `rules/`, `patches/`, `plans/`, `statusline.py` | `settings.json` y `config.toml` reales (estado de máquina: hooks locales, trust de proyectos, runtimes) |
| `templates/settings.json`, `templates/config.toml` (claves del sistema) | caches de plugins, sqlite, logs, memoria auto de Claude |

Las plantillas se fusionan **aditivamente**: añaden las claves del sistema que falten (modelo, permisos codegraph, plugins habilitados, marketplaces, MCP codegraph, multi_agent…) y **jamás** sobrescriben un valor existente. Los ajustes propios de cada máquina (p. ej. hooks extra en `settings.json`, trust de proyectos en `config.toml`) sobreviven a cada update.

## Problemas típicos

- **`fetch` falla** → repo privado sin credenciales: `gh auth login` (o configura un PAT en el credential manager).
- **El plugin Codex "no conoce" `--agent` o `max`** → una actualización del plugin borró el parche: `/repatch-codex`.
- **Drift entre los gemelos .md/.toml de los agentes** → `node "$HOME/.claude/patches/agent-parity-check.mjs"`.
- **Pull rechazado por cambios locales** → decide: publícalos (`-Push`) o descártalos (`git -C $HOME\.claude checkout -- <fichero>`).
