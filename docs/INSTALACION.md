# Instalación

## Requisitos

- **Python 3.11+** (`winget install Python.Python.3.13`) — `agentsys` sólo usa la biblioteca
  estándar; `tomllib` viene incluido desde 3.11.
- **git** (`winget install Git.Git`).
- Acceso al repo: lo más cómodo es `winget install GitHub.cli` + `gh auth login`, que además deja
  configuradas las credenciales de git.
- Claude Code, Codex CLI y OpenCode se instalan aparte, como siempre.
- PowerShell 7 (`winget install Microsoft.PowerShell`) sólo si quieres usar el atajo `install.ps1`.

## PC nuevo

```bash
git clone https://github.com/pma1999/agent-system.git ~/agent-system
cd ~/agent-system
python bin/agentsys.py install
python bin/agentsys.py verify
```

`install` crea lo que falte, respalda lo que reemplace en `~/.agent-system-backups/<fecha>/` y
fusiona de forma aditiva las plantillas de configuración en los ficheros reales de la máquina.

Después:

1. Abre `claude` una vez: inicia sesión si hace falta e instala los plugins de `settings.json`.
2. Ejecuta `/repatch-codex` dentro de Claude Code si el parche del plugin de Codex quedó pendiente
   por no existir todavía la caché del plugin.
3. `codex login` si vas a usar el lado Codex.
4. OpenCode queda configurado. Si lo usas **dentro de WSL**, enlaza los directorios (abajo).

## Migrar un PC que ya tenía el sistema antiguo

Los PCs antiguos tienen `~/.claude`, `~/.codex` y `~/.config/opencode` como checkouts de las ramas
`master` / `codex` / `opencode`. El nuevo sistema los trata como destinos de despliegue.

```bash
# 1. no pierdas nada que sólo exista en ese PC
cd ~/.claude          && git status --porcelain
cd ~/.codex           && git status --porcelain
cd ~/.config/opencode && git status --porcelain
# publica o guarda aparte cualquier cambio local antes de seguir

# 2. instala el canon
git clone https://github.com/pma1999/agent-system.git ~/agent-system
cd ~/agent-system
python bin/agentsys.py install --dry-run     # revisa la lista, sobre todo los "rechazados"
python bin/agentsys.py install

# 3. desactiva los checkouts antiguos para que nadie vuelva a publicar por ahí
python bin/agentsys.py install --retire-legacy
```

`--retire-legacy` renombra el `.git` de cada carpeta viva a `.git.legacy-agent-system-<fecha>`. No
borra nada: para revertir, basta renombrarlo de vuelta.

Durante la migración, `install` considera "gestionado" todo lo que el checkout antiguo tuviera
trackeado, así que lo sobrescribe con normalidad. Lo que **no** estuviera en git y difiera aparece
como **rechazado** y no se toca hasta que decidas.

## OpenCode dentro de WSL

OpenCode lee su configuración y las skills externas desde el home de Linux. Una sola vez por
distribución:

```bash
# haz backup si ya existe
mv ~/.config/opencode ~/.config/opencode.backup-$(date +%Y%m%d) 2>/dev/null
ln -s /mnt/c/Users/<usuario-windows>/.config/opencode ~/.config/opencode
mkdir -p ~/.claude
ln -s /mnt/c/Users/<usuario-windows>/.claude/skills ~/.claude/skills
npx -y @playwright/mcp@latest install-browser chromium
sudo npx -y playwright@latest install-deps chrome-for-testing
```

El enlace de skills expone globalmente en cualquier proyecto WSL las skills sincronizadas sin
copiarlas. `permission.skill` en la configuración de OpenCode deniega la skill `orchestrator` de
Claude, de modo que el runtime equivocado ni se anuncia ni se puede invocar.

**Ejecuta `install` desde Windows.** Bajo WSL, `~` es el home de Linux, pero Claude Code y Codex
corren en Windows y leen sus carpetas del home de Windows: un `install` sin más desplegaría en
`/home/<tu-usuario>/` y no serviría de nada. `agentsys` lo detecta y avisa.

Si necesitas lanzarlo desde WSL — por ejemplo porque sólo trabajas con OpenCode ahí — dile el home
de Windows explícitamente:

```bash
cd /mnt/c/Users/<usuario-windows>/agent-system
python3 bin/agentsys.py install --home /mnt/c/Users/<usuario-windows>
python3 bin/agentsys.py verify  --home /mnt/c/Users/<usuario-windows>
```

También vale la variable `AGENTSYS_HOME`. Para OpenCode da igual cuál uses: `~/.config/opencode` en
WSL es un enlace a la carpeta de Windows, así que ambos caminos llegan al mismo sitio.

## Problemas típicos

**`fetch` o `push` falla.** Repo privado sin credenciales: `gh auth login`, o configura un PAT en el
credential manager.

**`install` dice "rechazados".** Esos ficheros existen, difieren de lo generado y nunca estuvieron
gestionados por este sistema. Míralos: si son tuyos y los quieres conservar, cópialos aparte o
pásalos al canon con `agentsys adopt`; si quieres que los sustituya lo generado, repite con
`--force`.

**`install` dice "REVISA A MANO".** Faltan claves del sistema dentro de un bloque que tu fichero de
configuración ya tenía. El merge no las inserta para no destrozar tus comentarios. Ábrelo y añádelas
a mano; la ruta exacta viene en el mensaje. La que más importa es
`permission.skill.orchestrator: "deny"` en OpenCode: sin ella, la skill `orchestrator` de Claude
--- visible en OpenCode a través del enlace `~/.claude/skills` --- se anunciaría en el runtime
equivocado.

**`verify` dice "Identidad de prompts" fallando.** Los tres harnesses han dejado de compartir un
solo cuerpo. El diff que imprime dice exactamente dónde. Se arregla en el canónico
(`source/orchestration/`), nunca en un harness suelto.

**`verify` dice "Render determinista" fallando.** Alguien editó `rendered/` a mano. `build` lo
regenera; si el cambio era intencionado, llévalo al canónico primero.

**Deriva que no desaparece.** Comprueba que no quede un checkout antiguo escribiendo encima:
`agentsys status` marca `[checkout legacy activo]`.

**El plugin de Codex "no conoce" `--agent` o `max`.** Una actualización del plugin borró el parche:
`/repatch-codex` dentro de Claude Code.

**Recuperar algo que `install` reemplazó.** Está en `~/.agent-system-backups/<fecha>/<harness>/` con
la misma ruta relativa.

## Restaurar el sistema anterior a la unificación

En el remoto: tags `pre-unificacion-20260917-master`, `-codex` y `-opencode`, más
`orchestrator-system-v1` (última versión del sistema del lado Claude antes de que lo borraran).
Copia completa fuera del repo, con bundles y ficheros planos, en
`~/agent-system-backup-20260917/` — ver su `RESTORE.md`.
