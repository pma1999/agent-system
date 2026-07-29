# Sistema multiagéntico personal (~/.claude + ~/.codex) + soporte OpenCode

Configuración versionada del sistema de orquestación multiagente para **Claude Code** y **Codex CLI**: `CLAUDE.md`/`AGENTS.md`, skill `orchestrator` (+ referencias), agentes especialistas por lado, parches del plugin Codex y plantillas de configuración. La rama OpenCode conserva únicamente soporte compartido (Context7, MCP y skills compatibles), sin orquestador ni agentes personalizados. **Un único repo privado** con tres ramas:

- `github.com/pma1999/agent-system`, rama **`master`** → se instala en `~/.claude` (esta rama; incluye el instalador)
- misma URL, rama **`codex`** → se instala en `~/.codex`
- misma URL, rama **`opencode`** → se instala en `~/.config/opencode`

`install.ps1` gestiona **las tres carpetas** a la vez; tú solo tratas con un repo.

## Instalar en un PC nuevo (cualquier usuario)

Requisitos: PowerShell 7 (`winget install Microsoft.PowerShell`), git (`winget install Git.Git`), Node LTS (`winget install OpenJS.NodeJS.LTS`), y acceso al repo privado (lo más cómodo: `winget install GitHub.cli` + `gh auth login`, que configura las credenciales de git). Claude Code y Codex CLI se instalan aparte como siempre.

```powershell
git clone https://github.com/pma1999/agent-system.git "$env:TEMP\agent-system"
pwsh -File "$env:TEMP\agent-system\install.ps1"
```

El instalador convierte `~/.claude`, `~/.codex` y `~/.config/opencode` en clones de los repos (haciendo copia de seguridad en `backup-preinstall-<fecha>/` de cualquier fichero previo que fuera a sobrescribir), fusiona las plantillas de configuración y aplica el parche del plugin si ya existe. Después:

1. Abre `claude` — inicia sesión si hace falta; en el primer arranque instala los plugins de `settings.json`.
2. Ejecuta `/repatch-codex` dentro de Claude Code (si el instalador dejó el parche pendiente por no existir aún el plugin).
3. `codex login` si vas a usar el lado Codex.
4. `opencode` ya queda configurado; si lo usas **dentro de WSL**, enlaza su home a la carpeta de Windows (ver sección OpenCode abajo).

## Actualizar (en cualquier PC, en cualquier momento)

```powershell
pwsh -File "$HOME/.claude/install.ps1"
```

O, dentro de Claude Code: `/sync-agent-system`.

## Publicar cambios hechos en este PC

```powershell
pwsh -File "$HOME/.claude/install.ps1" -Push -Message "descripcion del cambio"
```

O `/sync-agent-system push`. Commitea y sube las tres ramas. Si otro PC publicó antes, haz primero un update; si git avisa de divergencia: `git -C $HOME\.claude pull --rebase origin master` (en `.codex`: `... pull --rebase origin codex`; en `.config/opencode`: `... pull --rebase origin opencode`).

## Qué se sincroniza y qué no

| Se sincroniza (versionado) | Local de cada máquina (nunca se sube) |
|---|---|
| `CLAUDE.md`, `AGENTS.md` | credenciales (`.credentials.json`, `auth.json`), sesiones, historial |
| `agents/`, `skills/`, `rules/`, `patches/`, `plans/`, `statusline.py` | `settings.json` y `config.toml` reales (estado de máquina: hooks locales, trust de proyectos, runtimes) |
| `templates/settings.json`, `templates/config.toml` (claves del sistema) | caches de plugins, sqlite, logs, memoria auto de Claude |
| rama `opencode`: `AGENTS.md`, `README.md`, `templates/opencode.jsonc` | `opencode.jsonc`/`opencode.json` reales, `node_modules`, estado de OpenCode |

Las plantillas se fusionan **aditivamente**: añaden las claves del sistema que falten (modelo, permisos codegraph, plugins habilitados, marketplaces, MCP codegraph, multi_agent…) y **jamás** sobrescriben un valor existente. Los ajustes propios de cada máquina (p. ej. hooks extra en `settings.json`, trust de proyectos en `config.toml`, modelo por defecto en `opencode.jsonc`) sobreviven a cada update.

## OpenCode (`~/.config/opencode`, rama `opencode`)

OpenCode utiliza sus agentes integrados; esta rama no contiene un sistema multiagente personalizado:

- **`AGENTS.md` global** — conserva únicamente las reglas de documentación Context7.
- **Sin agentes ni orquestador personalizados** — no hay routing de modelos, bundles, artefactos ni pipeline personalizado.
- **Skills compatibles** — el enlace `~/.claude/skills` expone las skills generales sincronizadas; `permission.skill` deniega la skill Claude `orchestrator` para no activar el runtime equivocado.
- **`templates/opencode.jsonc`** — MCP `codegraph` global y MCP `playwright` headless habilitado para el agente integrado `build` (merge aditivo; JSON puro sin comentarios para que PowerShell lo parsee).

En **WSL**, OpenCode lee configuración y skills externas desde el home de Linux. Puentes de una sola vez:

```bash
# una sola vez por máquina WSL (haz backup antes si existe)
mv ~/.config/opencode ~/.config/opencode.backup-$(date +%Y%m%d) 2>/dev/null
ln -s /mnt/c/Users/<usuario-windows>/.config/opencode ~/.config/opencode
mkdir -p ~/.claude
ln -s /mnt/c/Users/<usuario-windows>/.claude/skills ~/.claude/skills
npx -y @playwright/mcp@latest install-browser chromium
sudo npx -y playwright@latest install-deps chrome-for-testing
```

El enlace de skills expone globalmente en cualquier proyecto WSL `sync-agent-system`, `frontend`, `frontend-one`, `find-docs` y las demás skills sincronizadas, sin copiarlas. `permission.skill` deniega la skill Claude `orchestrator`, evitando que se anuncie o invoque en OpenCode. Los dos últimos comandos preparan Chromium headless y sus dependencias Linux una sola vez por distro WSL.

Y el sync desde WSL se lanza con el PowerShell de Windows: `pwsh.exe -NoProfile -File 'C:\Users\<usuario-windows>\.claude\install.ps1'`.

## Problemas típicos

- **`fetch` falla** → repo privado sin credenciales: `gh auth login` (o configura un PAT en el credential manager).
- **El plugin Codex "no conoce" `--agent` o `max`** → una actualización del plugin borró el parche: `/repatch-codex`.
- **Drift entre los gemelos .md/.toml de los agentes** → `node "$HOME/.claude/patches/agent-parity-check.mjs"`.
- **Pull rechazado por cambios locales** → decide: publícalos (`-Push`) o descártalos (`git -C $HOME\.claude checkout -- <fichero>`).
