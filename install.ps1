#Requires -Version 7.0
<#
.SYNOPSIS
  Installer/updater/publisher for the personal multi-agent system (~/.claude + ~/.codex + ~/.config/opencode).

.DESCRIPTION
  Idempotent. Three uses:
    install.ps1                    # fresh install OR pull latest onto this machine
    install.ps1 -Push              # commit & push local changes from this machine
    install.ps1 -Push -Message "x" # same, with a custom commit message

  Layout: ONE private repo (github.com/pma1999/agent-system) with three branches —
  master mirrors ~/.claude (installer + README at its root), codex mirrors ~/.codex,
  opencode mirrors ~/.config/opencode.

  What it does in pull mode, per directory (~/.claude, ~/.codex and ~/.config/opencode):
    1. git init + remote origin if missing, core.autocrlf=false, identity.
    2. Fresh machine: backs up any existing files that the repo would overwrite to
       backup-preinstall-<timestamp>/, then checks out the branch. Existing machine:
       fast-forward pull (refuses politely if you have uncommitted tracked changes).
    3. Additive config merge — never overwrites existing values:
       - templates/settings.json  -> ~/.claude/settings.json (fill missing keys, union arrays)
       - templates/config.toml    -> ~/.codex/config.toml    (prepend missing top-level keys,
         append missing [tables], insert missing keys into existing tables)
       - templates/opencode.jsonc -> ~/.config/opencode/opencode.jsonc (fill missing keys,
         union arrays; pure-JSON template so PowerShell can parse it)
    4. Re-applies the local Codex plugin patch (node patches/codex-plugin-agent-patch.mjs)
       if the plugin cache exists; otherwise tells you to launch Claude Code once first.

  Machine state is never synced: credentials, sessions, sqlite, logs, plugin caches,
  project trust, hooks you add locally to settings.json, memory, real opencode.json(c)
  values, opencode plugin deps (node_modules).
#>
[CmdletBinding()]
param(
    [switch]$Push,
    [string]$Message = "sync: agent system update",
    [string]$GitHubUser = "pma1999",
    # One repo, three branches: master = ~/.claude, codex = ~/.codex, opencode = ~/.config/opencode.
    [string]$Remote,
    [switch]$SkipRepatch,
    # Root that contains .claude/.codex — override only for testing the installer itself.
    [string]$HomeDir = $HOME
)

$ErrorActionPreference = 'Stop'
if (-not $Remote) { $Remote = "https://github.com/$GitHubUser/agent-system.git" }

$repos = @(
    [pscustomobject]@{ Name = '.claude';          Dir = Join-Path $HomeDir '.claude';          Remote = $Remote; Branch = 'master'   },
    [pscustomobject]@{ Name = '.codex';           Dir = Join-Path $HomeDir '.codex';           Remote = $Remote; Branch = 'codex'    },
    [pscustomobject]@{ Name = '.config/opencode'; Dir = Join-Path $HomeDir '.config\opencode'; Remote = $Remote; Branch = 'opencode' }
)

function Write-Step { param([string]$Text) Write-Host "==> $Text" -ForegroundColor Cyan }
function Write-Info { param([string]$Text) Write-Host "    $Text" }
function Write-Warn2 { param([string]$Text) Write-Host "    ! $Text" -ForegroundColor Yellow }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git no está en PATH. Instálalo (winget install Git.Git) y reintenta."
}
$hasNode = [bool](Get-Command node -ErrorAction SilentlyContinue)
if (-not $hasNode) { Write-Warn2 "node no está en PATH: el parche del plugin Codex no podrá aplicarse (winget install OpenJS.NodeJS.LTS)." }

function Initialize-Repo {
    param([pscustomobject]$Repo)
    New-Item -ItemType Directory -Force -Path $Repo.Dir | Out-Null
    if (-not (Test-Path (Join-Path $Repo.Dir '.git'))) {
        git -C $Repo.Dir init --initial-branch=$($Repo.Branch) *> $null
        Write-Info "repo git inicializado (rama $($Repo.Branch))"
    }
    git -C $Repo.Dir config core.autocrlf false
    if (-not (git -C $Repo.Dir config user.name))  { git -C $Repo.Dir config user.name  $GitHubUser }
    if (-not (git -C $Repo.Dir config user.email)) { git -C $Repo.Dir config user.email "$GitHubUser@users.noreply.github.com" }
    $origin = git -C $Repo.Dir remote get-url origin 2>$null
    if (-not $origin) {
        git -C $Repo.Dir remote add origin $Repo.Remote
        Write-Info "remote origin -> $($Repo.Remote)"
    }
    elseif ($origin -ne $Repo.Remote) {
        Write-Info "remote origin ya configurado ($origin); se respeta"
    }
}

function Sync-RepoPull {
    param([pscustomobject]$Repo)
    Write-Step "Sincronizando $($Repo.Name)"
    Initialize-Repo -Repo $Repo

    $branch = $Repo.Branch
    git -C $Repo.Dir fetch origin $branch --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warn2 "no se pudo hacer fetch de origin ($($Repo.Remote), rama $branch)."
        Write-Warn2 "¿Repo remoto creado y git autenticado? (gh auth login / credenciales git). Se continúa sin pull."
        return
    }

    git -C $Repo.Dir rev-parse --verify HEAD *> $null
    $hasHead = ($LASTEXITCODE -eq 0)
    if ($hasHead) {
        $dirty = git -C $Repo.Dir status --porcelain --untracked-files=no
        if ($dirty) {
            Write-Warn2 "hay cambios locales sin commitear en ficheros versionados; pull omitido."
            Write-Warn2 "Publica con: install.ps1 -Push  (o revisa 'git -C $($Repo.Dir) status')."
            return
        }
        $before = git -C $Repo.Dir rev-parse HEAD
        git -C $Repo.Dir merge --ff-only "origin/$branch" --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Warn2 "el historial local y el remoto han divergido; resuélvelo a mano:"
            Write-Warn2 "  git -C $($Repo.Dir) pull --rebase origin $branch"
            return
        }
        $after = git -C $Repo.Dir rev-parse HEAD
        if ($before -eq $after) { Write-Info "ya estaba al día ($($after.Substring(0,7)))" }
        else { Write-Info "actualizado $($before.Substring(0,7)) -> $($after.Substring(0,7))" }
    }
    else {
        # Fresh machine: materialize the repo into a possibly non-empty directory.
        $tracked = git -C $Repo.Dir ls-tree -r --name-only "origin/$branch"
        $conflicts = @($tracked | Where-Object { Test-Path (Join-Path $Repo.Dir $_) })
        if ($conflicts.Count -gt 0) {
            $backup = Join-Path $Repo.Dir ("backup-preinstall-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
            foreach ($rel in $conflicts) {
                $src = Join-Path $Repo.Dir $rel
                $dst = Join-Path $backup $rel
                New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
                Copy-Item -LiteralPath $src -Destination $dst -Force
            }
            Write-Info "copia de seguridad de $($conflicts.Count) fichero(s) preexistente(s) en $backup"
        }
        git -C $Repo.Dir checkout -f -B $branch "origin/$branch" --quiet
        Write-Info "instalado en $($Repo.Dir) ($((git -C $Repo.Dir rev-parse --short HEAD)))"
    }
    git -C $Repo.Dir branch --set-upstream-to="origin/$branch" $branch *> $null
}

function Sync-RepoPush {
    param([pscustomobject]$Repo)
    Write-Step "Publicando $($Repo.Name)"
    Initialize-Repo -Repo $Repo
    git -C $Repo.Dir add -A
    $status = git -C $Repo.Dir status --porcelain
    if ($status) {
        git -C $Repo.Dir commit -m $Message --quiet
        Write-Info "commit: $Message"
    }
    else {
        Write-Info "sin cambios locales"
    }
    git -C $Repo.Dir push -u origin $($Repo.Branch) --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Warn2 "push falló. ¿Repo remoto creado ($($Repo.Remote)) y autenticación git/gh lista?"
    }
    else {
        Write-Info "push OK -> $($Repo.Remote) (rama $($Repo.Branch))"
    }
}

# ---------- additive config merges ----------

function Merge-Hashtable {
    # Fill-missing merge: adds keys absent in Target; recurses into nested maps;
    # unions arrays (adds template entries missing from target). Never overwrites scalars.
    param($Target, $Template, [ref]$Changed)
    foreach ($key in $Template.Keys) {
        if (-not $Target.Contains($key)) {
            $Target[$key] = $Template[$key]
            $Changed.Value = $true
        }
        elseif ($Target[$key] -is [System.Collections.IDictionary] -and $Template[$key] -is [System.Collections.IDictionary]) {
            Merge-Hashtable -Target $Target[$key] -Template $Template[$key] -Changed $Changed
        }
        elseif ($Target[$key] -is [System.Collections.IList] -and $Template[$key] -is [System.Collections.IList]) {
            $missing = @($Template[$key] | Where-Object { $Target[$key] -notcontains $_ })
            if ($missing.Count -gt 0) {
                $Target[$key] = @($Target[$key]) + $missing
                $Changed.Value = $true
            }
        }
        # scalar present in both -> target wins, always
    }
}

function Merge-ClaudeSettings {
    $templatePath = Join-Path $HomeDir '.claude\templates\settings.json'
    $targetPath   = Join-Path $HomeDir '.claude\settings.json'
    if (-not (Test-Path $templatePath)) { return }
    Write-Step "settings.json (merge aditivo)"
    if (-not (Test-Path $targetPath)) {
        Copy-Item -LiteralPath $templatePath -Destination $targetPath
        Write-Info "creado desde plantilla"
        return
    }
    $target   = Get-Content -Raw -LiteralPath $targetPath   | ConvertFrom-Json -AsHashtable -Depth 30
    $template = Get-Content -Raw -LiteralPath $templatePath | ConvertFrom-Json -AsHashtable -Depth 30
    $changed = $false
    Merge-Hashtable -Target $target -Template $template -Changed ([ref]$changed)
    if ($changed) {
        $json = $target | ConvertTo-Json -Depth 30
        [System.IO.File]::WriteAllText($targetPath, $json, [System.Text.UTF8Encoding]::new($false))
        Write-Info "claves del sistema añadidas (los valores existentes no se tocan)"
    }
    else {
        Write-Info "sin cambios necesarios"
    }
}

function Merge-CodexConfig {
    $templatePath = Join-Path $HomeDir '.codex\templates\config.toml'
    $targetPath   = Join-Path $HomeDir '.codex\config.toml'
    if (-not (Test-Path $templatePath)) { return }
    Write-Step "config.toml (merge aditivo)"
    if (-not (Test-Path $targetPath)) {
        $body = (Get-Content -LiteralPath $templatePath | Where-Object { $_ -notmatch '^\s*#' }) -join "`n"
        [System.IO.File]::WriteAllText($targetPath, $body.Trim() + "`n", [System.Text.UTF8Encoding]::new($false))
        Write-Info "creado desde plantilla"
        return
    }

    $template = (Get-Content -Raw -LiteralPath $templatePath) -replace "`r`n", "`n"
    $templateLines = $template -split "`n" | Where-Object { $_ -notmatch '^\s*#' }
    $target = (Get-Content -Raw -LiteralPath $targetPath) -replace "`r`n", "`n"

    # Partition template into top-level key lines and [table] blocks.
    $topKeys = [System.Collections.Generic.List[string]]::new()
    $blocks = [ordered]@{}   # header -> list of body lines
    $currentHeader = $null
    foreach ($line in $templateLines) {
        if ($line -match '^\s*\[(?<h>[^\]]+)\]\s*$') {
            $currentHeader = $Matches.h
            $blocks[$currentHeader] = [System.Collections.Generic.List[string]]::new()
        }
        elseif ($null -eq $currentHeader) {
            if ($line -match '^\s*[\w."''-]+\s*=') { $topKeys.Add($line.Trim()) }
        }
        else {
            if ($line.Trim()) { $blocks[$currentHeader].Add($line.Trim()) }
        }
    }

    $changed = $false

    # 1. Missing top-level keys -> prepend at the very top (before any [table]).
    $prepend = [System.Collections.Generic.List[string]]::new()
    foreach ($kv in $topKeys) {
        $key = ($kv -split '=', 2)[0].Trim()
        if ($target -notmatch "(?m)^\s*$([regex]::Escape($key))\s*=") { $prepend.Add($kv) }
    }
    if ($prepend.Count -gt 0) {
        $target = ($prepend -join "`n") + "`n" + $target
        $changed = $true
        Write-Info "añadidas claves top-level: $(($prepend | ForEach-Object { ($_ -split '=',2)[0].Trim() }) -join ', ')"
    }

    # 2. Tables: append whole block if header missing; else insert missing keys after header.
    foreach ($header in $blocks.Keys) {
        $headerPattern = "(?m)^\s*\[$([regex]::Escape($header))\]\s*$"
        if ($target -notmatch $headerPattern) {
            $target = $target.TrimEnd() + "`n`n[" + $header + "]`n" + (($blocks[$header]) -join "`n") + "`n"
            $changed = $true
            Write-Info "añadida tabla [$header]"
        }
        else {
            # Region = from header to next header or EOF.
            $regionMatch = [regex]::Match($target, $headerPattern + "(?<body>[\s\S]*?)(?=(?m)^\s*\[|\z)")
            $body = $regionMatch.Groups['body'].Value
            $missing = @($blocks[$header] | Where-Object {
                    $k = ($_ -split '=', 2)[0].Trim()
                    $body -notmatch "(?m)^\s*$([regex]::Escape($k))\s*="
                })
            if ($missing.Count -gt 0) {
                $rx = [regex]::new($headerPattern)
                $headerLine = $rx.Match($target).Value
                $replacement = ($headerLine + "`n" + ($missing -join "`n")).Replace('$', '$$')
                $target = $rx.Replace($target, $replacement, 1)
                $changed = $true
                Write-Info "añadidas claves en [$header]: $(($missing | ForEach-Object { ($_ -split '=',2)[0].Trim() }) -join ', ')"
            }
        }
    }

    if ($changed) {
        [System.IO.File]::WriteAllText($targetPath, $target.TrimEnd() + "`n", [System.Text.UTF8Encoding]::new($false))
    }
    else {
        Write-Info "sin cambios necesarios"
    }
}

function Merge-OpenCodeConfig {
    $templatePath = Join-Path $HomeDir '.config\opencode\templates\opencode.jsonc'
    $targetJsonc  = Join-Path $HomeDir '.config\opencode\opencode.jsonc'
    $targetJson   = Join-Path $HomeDir '.config\opencode\opencode.json'
    if (-not (Test-Path $templatePath)) { return }
    Write-Step "opencode.jsonc (merge aditivo)"
    $targetPath = $null
    if (Test-Path $targetJsonc) { $targetPath = $targetJsonc }
    elseif (Test-Path $targetJson) { $targetPath = $targetJson }
    if (-not $targetPath) {
        Copy-Item -LiteralPath $templatePath -Destination $targetJsonc
        Write-Info "creado desde plantilla"
        return
    }
    try {
        $target   = Get-Content -Raw -LiteralPath $targetPath   | ConvertFrom-Json -AsHashtable -Depth 30 -ErrorAction Stop
        $template = Get-Content -Raw -LiteralPath $templatePath | ConvertFrom-Json -AsHashtable -Depth 30 -ErrorAction Stop
    }
    catch {
        Write-Warn2 "no se pudo parsear $targetPath (¿comentarios JSONC a mano?). Fusiona manualmente desde templates/opencode.jsonc."
        return
    }
    $changed = $false
    Merge-Hashtable -Target $target -Template $template -Changed ([ref]$changed)
    if ($changed) {
        $json = $target | ConvertTo-Json -Depth 30
        [System.IO.File]::WriteAllText($targetPath, $json, [System.Text.UTF8Encoding]::new($false))
        Write-Info "claves del sistema añadidas (los valores existentes no se tocan)"
    }
    else {
        Write-Info "sin cambios necesarios"
    }
}

function Invoke-Repatch {
    if ($SkipRepatch) { return }
    Write-Step "Parche del plugin Codex"
    $patcher = Join-Path $HomeDir '.claude\patches\codex-plugin-agent-patch.mjs'
    $pluginCache = Join-Path $HomeDir '.claude\plugins\cache\openai-codex\codex'
    if (-not (Test-Path $patcher)) { Write-Warn2 "patcher no encontrado ($patcher)"; return }
    if (-not $hasNode) { Write-Warn2 "sin node; ejecuta luego: node `"$patcher`""; return }
    if (-not (Test-Path $pluginCache)) {
        Write-Warn2 "el plugin codex aún no está instalado en esta máquina."
        Write-Warn2 "Abre Claude Code una vez (instala los plugins de settings.json) y luego ejecuta /repatch-codex."
        return
    }
    $patchOutput = & node $patcher 2>&1
    $patchOutput | ForEach-Object { Write-Info $_ }
    if ($LASTEXITCODE -ne 0) { Write-Warn2 "el patcher devolvió error; revisa la salida y /repatch-codex." }
}

# ---------- run ----------

if ($Push) {
    foreach ($repo in $repos) { Sync-RepoPush -Repo $repo }
    Write-Host ""
    Write-Host "Publicado. En los demás PCs: pwsh -File `"`$HOME/.claude/install.ps1`"" -ForegroundColor Green
}
else {
    foreach ($repo in $repos) { Sync-RepoPull -Repo $repo }
    Merge-ClaudeSettings
    Merge-CodexConfig
    Merge-OpenCodeConfig
    Invoke-Repatch
    Write-Host ""
    Write-Host "Listo. Pasos manuales si es la primera vez en esta máquina:" -ForegroundColor Green
    Write-Host "  1. claude  (inicia sesión si hace falta; instala plugins en el primer arranque)"
    Write-Host "  2. /repatch-codex dentro de Claude Code si el paso del parche quedó pendiente"
    Write-Host "  3. codex login  (si usarás el lado Codex)"
    Write-Host "  4. opencode: la config ya queda en ~/.config/opencode; en WSL enlázala (ver README, sección OpenCode)"
}
