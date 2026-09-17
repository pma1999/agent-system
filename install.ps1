<#
.SYNOPSIS
  Redireccion. El instalador antiguo de tres ramas ya no existe.

  Esta carpeta es un destino de despliegue, no un repositorio. El sistema se
  instala y se actualiza desde la fuente canonica:

      ~/agent-system     (repo pma1999/agent-system, rama main)

  Si el repo no esta clonado todavia en esta maquina:

      git clone https://github.com/pma1999/agent-system.git "$HOME/agent-system"

  Ver ~/agent-system/docs/INSTALACION.md para la migracion completa.
#>
$repo = Join-Path $HOME 'agent-system'
Write-Host ''
Write-Host '  Este install.ps1 esta retirado.' -ForegroundColor Yellow
Write-Host '  El sistema se gestiona desde la fuente canonica, no desde ~/.claude.'
Write-Host ''
if (Test-Path (Join-Path $repo 'bin/install.ps1')) {
  Write-Host "  Usa:  pwsh -NoProfile -File `"$repo/bin/install.ps1`""
} else {
  Write-Host "  Clona primero el repo canonico:"
  Write-Host "    git clone https://github.com/pma1999/agent-system.git `"$repo`""
  Write-Host "    pwsh -NoProfile -File `"$repo/bin/install.ps1`""
}
Write-Host ''
Write-Host "  Migracion desde el sistema antiguo: $repo/docs/INSTALACION.md"
Write-Host ''
exit 1
