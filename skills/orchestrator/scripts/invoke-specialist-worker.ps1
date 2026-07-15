[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$RequestPath
)

$ErrorActionPreference = 'Stop'
$startedAt = [DateTimeOffset]::UtcNow
$exitCode = 1
$jobDirectory = Split-Path -Parent (Resolve-Path -LiteralPath $RequestPath).Path
$resultPath = Join-Path $jobDirectory 'result.json'

function Write-WorkerResult {
    param(
        [Parameter(Mandatory)]
        [int]$Code
    )

    $value = [pscustomobject]@{
        schema_version = 1
        exit_code      = $Code
        started_at     = $startedAt.ToString('o')
        completed_at   = [DateTimeOffset]::UtcNow.ToString('o')
    }
    $temporaryPath = "$resultPath.$([guid]::NewGuid().ToString('N')).tmp"
    [System.IO.File]::WriteAllText(
        $temporaryPath,
        ($value | ConvertTo-Json -Depth 5),
        [System.Text.UTF8Encoding]::new($false)
    )
    Move-Item -LiteralPath $temporaryPath -Destination $resultPath -Force
}

try {
    $request = Get-Content -Raw -LiteralPath $RequestPath | ConvertFrom-Json
    if ([int]$request.schema_version -ne 1) {
        throw "Unsupported specialist request schema: $($request.schema_version)"
    }
    if (-not (Test-Path -LiteralPath ([string]$request.codex_executable) -PathType Leaf)) {
        throw "Codex executable is unavailable: $($request.codex_executable)"
    }

    $env:CODEX_HOME = [string]$request.codex_home
    $eventsPath = [string]$request.events_path
    $stderrPath = [string]$request.stderr_path
    $arguments = @($request.arguments | ForEach-Object { [string]$_ })
    & ([string]$request.codex_executable) @arguments 1>> $eventsPath 2>> $stderrPath
    $exitCode = if ($null -eq $LASTEXITCODE) { 0 } else { [int]$LASTEXITCODE }
}
catch {
    $stderrPath = if ($request -and $request.stderr_path) {
        [string]$request.stderr_path
    }
    else {
        Join-Path $jobDirectory 'stderr.log'
    }
    [System.IO.File]::AppendAllText(
        $stderrPath,
        $_.Exception.ToString() + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )
    $exitCode = 1
}
finally {
    Write-WorkerResult -Code $exitCode
}

exit $exitCode
