<#
.SYNOPSIS
  Atajo de Windows para el sistema multiagentico. Todo el trabajo lo hace
  bin/agentsys.py; este fichero solo existe por comodidad y memoria muscular.

.EXAMPLE
  pwsh -NoProfile -File "$HOME/agent-system/bin/install.ps1"
  pwsh -NoProfile -File "$HOME/agent-system/bin/install.ps1" -Publish -Message "..."
#>
param(
  [switch]$Publish,
  [string]$Message,
  [switch]$Force,
  [switch]$DryRun,
  [switch]$RetireLegacy
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$py = (Get-Command python -ErrorAction SilentlyContinue) ?? (Get-Command python3 -ErrorAction SilentlyContinue)
if (-not $py) { throw "Python 3.11+ no encontrado en PATH (winget install Python.Python.3.13)" }
$agentsys = Join-Path $PSScriptRoot 'agentsys.py'

function Invoke-AgentSys { & $py.Source $agentsys @args; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }

if ($Publish) {
  if (-not $Message) { throw "-Publish requiere -Message con un resumen real del cambio" }
  Invoke-AgentSys publish -m $Message
  exit 0
}

git -C $repo pull --ff-only 2>&1 | Write-Host
Invoke-AgentSys build
$installArgs = @('install')
if ($Force)        { $installArgs += '--force' }
if ($DryRun)       { $installArgs += '--dry-run' }
if ($RetireLegacy) { $installArgs += '--retire-legacy' }
Invoke-AgentSys @installArgs
Invoke-AgentSys verify
