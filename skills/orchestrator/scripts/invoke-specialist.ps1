[CmdletBinding(DefaultParameterSetName = 'Start')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Start')]
    [Parameter(Mandatory, ParameterSetName = 'Resume')]
    [ValidatePattern('^[a-z0-9][a-z0-9-]*$')]
    [string]$Agent,

    [Parameter(Mandatory, ParameterSetName = 'Start')]
    [Parameter(Mandatory, ParameterSetName = 'Resume')]
    [ValidateSet('gpt-5.6-sol', 'gpt-5.6-terra', 'gpt-5.6-luna')]
    [string]$Model,

    [Parameter(Mandatory, ParameterSetName = 'Start')]
    [Parameter(Mandatory, ParameterSetName = 'Resume')]
    [ValidateSet('low', 'medium', 'high', 'xhigh', 'max')]
    [string]$ReasoningEffort,

    [Parameter(Mandatory, ParameterSetName = 'Start')]
    [Parameter(Mandatory, ParameterSetName = 'Resume')]
    [string]$Prompt,

    [Parameter(Mandatory, ParameterSetName = 'Start')]
    [string]$Workspace,

    [Parameter(Mandatory, ParameterSetName = 'Resume')]
    [ValidatePattern('^[0-9a-fA-F-]{36}$')]
    [string]$SessionId,

    [Parameter(ParameterSetName = 'Start')]
    [ValidateSet('read-only', 'workspace-write', 'danger-full-access')]
    [string]$Sandbox = 'workspace-write',

    [Parameter(ParameterSetName = 'Start')]
    [ValidateSet('untrusted', 'on-request', 'never')]
    [string]$Approval = 'never',

    [Parameter(Mandatory, ParameterSetName = 'Wait')]
    [switch]$Wait,

    [Parameter(Mandatory, ParameterSetName = 'Status')]
    [switch]$Status,

    [Parameter(Mandatory, ParameterSetName = 'List')]
    [switch]$List,

    [Parameter(Mandatory, ParameterSetName = 'Cleanup')]
    [switch]$Cleanup,

    [Parameter(Mandatory, ParameterSetName = 'Wait')]
    [Parameter(Mandatory, ParameterSetName = 'Status')]
    [Parameter(Mandatory, ParameterSetName = 'Cleanup')]
    [ValidatePattern('^[0-9a-fA-F-]{36}$')]
    [string]$JobId,

    [Parameter(ParameterSetName = 'Wait')]
    [Parameter(ParameterSetName = 'Status')]
    [ValidateRange(0, 100)]
    [int]$TailErrorLines = 20
)

$ErrorActionPreference = 'Stop'

$codexHome = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$jobsRoot = Join-Path $codexHome '.orchestrator\jobs'
$workerPath = Join-Path $PSScriptRoot 'invoke-specialist-worker.ps1'

function Write-JsonAtomically {
    param(
        [Parameter(Mandatory)]
        [object]$Value,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $temporaryPath = "$Path.$([guid]::NewGuid().ToString('N')).tmp"
    $json = $Value | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText(
        $temporaryPath,
        $json,
        [System.Text.UTF8Encoding]::new($false)
    )
    Move-Item -LiteralPath $temporaryPath -Destination $Path -Force
}

function Get-JobDirectory {
    param(
        [Parameter(Mandatory)]
        [string]$Id
    )

    $parsedId = [guid]::ParseExact($Id, 'D').ToString('D')
    $resolvedRoot = [System.IO.Path]::GetFullPath($jobsRoot).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $resolvedJob = [System.IO.Path]::GetFullPath((Join-Path $resolvedRoot $parsedId))
    if ([System.IO.Path]::GetDirectoryName($resolvedJob) -ne $resolvedRoot) {
        throw "Job path escapes the orchestrator jobs directory: $Id"
    }
    $resolvedJob
}

function Read-JsonFile {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -DateKind String
}

function Test-RecordedProcess {
    param(
        [Parameter(Mandatory)]
        [object]$Launch
    )

    $process = Get-Process -Id ([int]$Launch.process_id) -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        return $null
    }

    if ($Launch.process_started_at) {
        try {
            $recordedStart = [DateTimeOffset]::Parse([string]$Launch.process_started_at).UtcDateTime
            $actualStart = $process.StartTime.ToUniversalTime()
            if ([Math]::Abs(($actualStart - $recordedStart).TotalSeconds) -gt 2) {
                return $null
            }
        }
        catch {
            return $null
        }
    }
    $process
}

function Get-RecordedTaskState {
    param(
        [Parameter(Mandatory)]
        [object]$Launch
    )

    if (-not $Launch.task_name) {
        return $null
    }
    $task = Get-ScheduledTask -TaskName ([string]$Launch.task_name) -ErrorAction SilentlyContinue
    if ($null -eq $task) {
        return [pscustomobject]@{
            state = 'interrupted'
            task  = $null
        }
    }
    if ([string]$task.State -eq 'Running') {
        return [pscustomobject]@{
            state = 'running'
            task  = $task
        }
    }

    $taskInfo = Get-ScheduledTaskInfo -TaskName ([string]$Launch.task_name)
    $launchedAt = [DateTimeOffset]::Parse([string]$Launch.launched_at).UtcDateTime
    $lastRunUtc = $taskInfo.LastRunTime.ToUniversalTime()
    $state = if ($lastRunUtc -ge $launchedAt.AddSeconds(-2)) {
        'interrupted'
    }
    else {
        'starting'
    }
    [pscustomobject]@{
        state = $state
        task  = $task
    }
}

function Get-EventSummary {
    param(
        [Parameter(Mandatory)]
        [string]$EventsPath
    )

    $eventCount = 0
    $sessionId = $null
    $lastEventType = $null
    $lastAgentMessage = $null
    if (Test-Path -LiteralPath $EventsPath -PathType Leaf) {
        foreach ($line in Get-Content -LiteralPath $EventsPath) {
            if ([string]::IsNullOrWhiteSpace($line)) {
                continue
            }
            try {
                $event = $line | ConvertFrom-Json
            }
            catch {
                continue
            }
            $eventCount++
            $lastEventType = [string]$event.type
            if ($event.type -eq 'thread.started' -and $event.thread_id) {
                $sessionId = [string]$event.thread_id
            }
            if (
                $event.type -eq 'item.completed' -and
                $event.item.type -eq 'agent_message' -and
                $event.item.text
            ) {
                $lastAgentMessage = [string]$event.item.text
            }
        }
    }

    [pscustomobject]@{
        event_count       = $eventCount
        session_id        = $sessionId
        last_event_type   = $lastEventType
        last_agent_message = $lastAgentMessage
    }
}

function Get-SpecialistJobStatus {
    param(
        [Parameter(Mandatory)]
        [string]$Id,

        [int]$ErrorTail = 20
    )

    $jobDirectory = Get-JobDirectory -Id $Id
    if (-not (Test-Path -LiteralPath $jobDirectory -PathType Container)) {
        throw "Unknown specialist job: $Id"
    }

    $requestPath = Join-Path $jobDirectory 'request.json'
    $launchPath = Join-Path $jobDirectory 'launch.json'
    $resultPath = Join-Path $jobDirectory 'result.json'
    $eventsPath = Join-Path $jobDirectory 'events.jsonl'
    $stderrPath = Join-Path $jobDirectory 'stderr.log'
    $request = Read-JsonFile -Path $requestPath
    $launch = Read-JsonFile -Path $launchPath
    $result = Read-JsonFile -Path $resultPath
    $taskState = if ($launch -and $launch.task_name) {
        Get-RecordedTaskState -Launch $launch
    }
    else {
        $null
    }
    $process = if ($launch -and $launch.process_id) {
        Test-RecordedProcess -Launch $launch
    }
    else {
        $null
    }
    $eventSummary = Get-EventSummary -EventsPath $eventsPath

    $state = if ($result) {
        if ([int]$result.exit_code -eq 0) { 'completed' } else { 'failed' }
    }
    elseif ($taskState) {
        $taskState.state
    }
    elseif ($process) {
        'running'
    }
    elseif (-not $launch) {
        'starting'
    }
    else {
        'interrupted'
    }

    $stderrTail = @()
    if ($ErrorTail -gt 0 -and (Test-Path -LiteralPath $stderrPath -PathType Leaf)) {
        $stderrTail = @(Get-Content -LiteralPath $stderrPath -Tail $ErrorTail)
    }
    [pscustomobject]@{
        schema_version     = 1
        job_id             = ([guid]::ParseExact($Id, 'D').ToString('D'))
        state              = $state
        process_id         = if ($launch -and $launch.process_id) { [int]$launch.process_id } else { $null }
        task_name          = if ($launch -and $launch.task_name) { [string]$launch.task_name } else { $null }
        session_id         = $eventSummary.session_id
        agent              = if ($request) { [string]$request.agent } else { $null }
        model              = if ($request) { [string]$request.model } else { $null }
        reasoning_effort   = if ($request) { [string]$request.reasoning_effort } else { $null }
        mode               = if ($request) { [string]$request.mode } else { $null }
        started_at         = if ($request) { [string]$request.started_at } else { $null }
        completed_at       = if ($result) { [string]$result.completed_at } else { $null }
        exit_code          = if ($result) { [int]$result.exit_code } else { $null }
        event_count        = $eventSummary.event_count
        last_event_type    = $eventSummary.last_event_type
        last_agent_message = $eventSummary.last_agent_message
        stderr_tail        = $stderrTail
        job_directory      = $jobDirectory
        events_path        = $eventsPath
        stderr_path        = $stderrPath
        result_path        = $resultPath
    }
}

function Write-OutputJson {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object]$Value
    )

    [Console]::Out.WriteLine(
        (ConvertTo-Json -InputObject $Value -Depth 20 -Compress)
    )
}

function Resolve-CodexLauncher {
    $application = Get-Command codex -CommandType Application -ErrorAction Stop |
        Select-Object -First 1

    if (-not $IsWindows -or [System.IO.Path]::GetExtension($application.Source) -notin @('.cmd', '.bat')) {
        return [pscustomobject]@{
            kind             = 'application'
            executable       = $application.Source
            prefix_arguments = @()
            source           = $application.Source
        }
    }

    # npm's codex.cmd passes every argument through cmd.exe, whose 8191-character
    # command-line limit is too small for long custom-agent instructions. Resolve
    # the official JavaScript launcher used by that shim and invoke it with Node
    # directly. The launcher still selects and configures the packaged native
    # Codex binary exactly as the supported shim does.
    $shimDirectory = Split-Path -Parent $application.Source
    $shimText = Get-Content -Raw -LiteralPath $application.Source
    $launcherMatch = [regex]::Match(
        $shimText,
        '(?i)%dp0%\\(?<relative>[^"\r\n]*codex\.js)'
    )
    $javascriptLauncher = if ($launcherMatch.Success) {
        Join-Path $shimDirectory $launcherMatch.Groups['relative'].Value
    }
    else {
        Join-Path $shimDirectory 'node_modules\@openai\codex\bin\codex.js'
    }
    if (-not (Test-Path -LiteralPath $javascriptLauncher -PathType Leaf)) {
        throw "Unable to resolve the Codex JavaScript launcher from $($application.Source)"
    }

    $bundledNode = Join-Path $shimDirectory 'node.exe'
    $nodeExecutable = if (Test-Path -LiteralPath $bundledNode -PathType Leaf) {
        $bundledNode
    }
    else {
        (Get-Command node -CommandType Application -ErrorAction Stop |
            Select-Object -First 1).Source
    }

    [pscustomobject]@{
        kind             = 'node-js'
        executable       = $nodeExecutable
        prefix_arguments = @($javascriptLauncher)
        source           = $application.Source
    }
}

function ConvertTo-WindowsCommandLineArgument {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyString()]
        [string]$Value
    )

    if ($Value.Length -gt 0 -and $Value -notmatch '[\s"]') {
        return $Value
    }

    $builder = [System.Text.StringBuilder]::new()
    [void]$builder.Append('"')
    $backslashes = 0
    foreach ($character in $Value.ToCharArray()) {
        if ($character -eq '\') {
            $backslashes++
            continue
        }
        if ($character -eq '"') {
            [void]$builder.Append(('\' * (($backslashes * 2) + 1)))
            [void]$builder.Append('"')
        }
        else {
            if ($backslashes -gt 0) {
                [void]$builder.Append(('\' * $backslashes))
            }
            [void]$builder.Append($character)
        }
        $backslashes = 0
    }
    if ($backslashes -gt 0) {
        [void]$builder.Append(('\' * ($backslashes * 2)))
    }
    [void]$builder.Append('"')
    $builder.ToString()
}

function Assert-WindowsCommandLineFits {
    param(
        [Parameter(Mandatory)]
        [string]$Executable,

        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    if (-not $IsWindows) {
        return
    }
    $parts = @(
        ConvertTo-WindowsCommandLineArgument -Value $Executable
    ) + @(
        $Arguments | ForEach-Object {
            ConvertTo-WindowsCommandLineArgument -Value $_
        }
    )
    $length = ($parts -join ' ').Length + 1 # terminating NUL
    if ($length -gt 32767) {
        throw "Codex invocation requires $length command-line characters; Windows CreateProcess supports at most 32767. Shorten the selected agent profile or move its instructions to a file-backed Codex configuration surface."
    }
}

New-Item -ItemType Directory -Force -Path $jobsRoot | Out-Null

switch ($PSCmdlet.ParameterSetName) {
    'Wait' {
        while ($true) {
            $jobStatus = Get-SpecialistJobStatus -Id $JobId -ErrorTail $TailErrorLines
            if ($jobStatus.state -notin @('starting', 'running')) {
                Write-OutputJson -Value $jobStatus
                exit $(if ($jobStatus.state -eq 'completed') { 0 } else { 1 })
            }

            $launch = Read-JsonFile -Path (Join-Path $jobStatus.job_directory 'launch.json')
            if ($launch.task_name) {
                $watcher = [System.IO.FileSystemWatcher]::new(
                    $jobStatus.job_directory,
                    'result.json'
                )
                $watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName
                $watcher.EnableRaisingEvents = $true
                try {
                    if (-not (Test-Path -LiteralPath $jobStatus.result_path -PathType Leaf)) {
                        $changes = [System.IO.WatcherChangeTypes]::Created -bor
                            [System.IO.WatcherChangeTypes]::Renamed
                        $watcher.WaitForChanged($changes) | Out-Null
                    }
                }
                finally {
                    $watcher.Dispose()
                }
            }
            else {
                $process = if ($launch) { Test-RecordedProcess -Launch $launch } else { $null }
                if ($process) {
                    $process.WaitForExit()
                }
                else {
                    Start-Sleep -Milliseconds 100
                }
            }
        }
    }
    'Status' {
        Write-OutputJson -Value (Get-SpecialistJobStatus -Id $JobId -ErrorTail $TailErrorLines)
        exit 0
    }
    'List' {
        $jobs = @(
            Get-ChildItem -LiteralPath $jobsRoot -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match '^[0-9a-fA-F-]{36}$' } |
                ForEach-Object {
                    try {
                        Get-SpecialistJobStatus -Id $_.Name -ErrorTail 0
                    }
                    catch {
                        [pscustomobject]@{
                            schema_version = 1
                            job_id         = $_.Name
                            state          = 'invalid'
                            error          = $_.Exception.Message
                        }
                    }
                }
        )
        Write-OutputJson -Value $jobs
        exit 0
    }
    'Cleanup' {
        $jobStatus = Get-SpecialistJobStatus -Id $JobId -ErrorTail 0
        if ($jobStatus.state -in @('starting', 'running')) {
            throw "Specialist job is still active: $JobId"
        }
        $launch = Read-JsonFile -Path (Join-Path $jobStatus.job_directory 'launch.json')
        if ($launch -and $launch.task_name) {
            Unregister-ScheduledTask -TaskName ([string]$launch.task_name) -Confirm:$false -ErrorAction SilentlyContinue
        }
        $jobDirectory = Get-JobDirectory -Id $JobId
        Remove-Item -LiteralPath $jobDirectory -Recurse -Force
        Write-OutputJson -Value ([pscustomobject]@{
            schema_version = 1
            job_id         = ([guid]::ParseExact($JobId, 'D').ToString('D'))
            state          = 'cleaned'
            previous_state = $jobStatus.state
            cleaned_at     = [DateTimeOffset]::UtcNow.ToString('o')
        })
        exit 0
    }
}

$approvedPairs = @(
    'gpt-5.6-luna/low',
    'gpt-5.6-luna/medium',
    'gpt-5.6-luna/high',
    'gpt-5.6-luna/xhigh',
    'gpt-5.6-luna/max',
    'gpt-5.6-sol/medium',
    'gpt-5.6-sol/high',
    'gpt-5.6-sol/xhigh',
    'gpt-5.6-sol/max'
)
$pair = "$Model/$ReasoningEffort"
if ($pair -notin $approvedPairs) {
    throw "Unapproved model/reasoning pair: $pair"
}
if ($Agent -eq 'implementation-planner' -and $pair -ne 'gpt-5.6-sol/xhigh') {
    throw 'implementation-planner must use gpt-5.6-sol/xhigh'
}

$agentsDir = Join-Path $codexHome 'agents'
$agentFile = Join-Path $agentsDir "$Agent.toml"
$resolvedAgentsDir = [System.IO.Path]::GetFullPath($agentsDir).TrimEnd('\')
$resolvedAgentFile = [System.IO.Path]::GetFullPath($agentFile)
if ((Split-Path -Parent $resolvedAgentFile).TrimEnd('\') -ne $resolvedAgentsDir) {
    throw "Agent path escapes the configured agents directory: $Agent"
}
if (-not (Test-Path -LiteralPath $resolvedAgentFile -PathType Leaf)) {
    throw "Unknown agent profile: $Agent"
}
if (-not (Test-Path -LiteralPath $workerPath -PathType Leaf)) {
    throw "Missing specialist worker: $workerPath"
}

$agentToml = Get-Content -Raw -LiteralPath $resolvedAgentFile
$match = [regex]::Match(
    $agentToml,
    "(?ms)^developer_instructions\s*=\s*'''(.*?)'''\s*$"
)
if (-not $match.Success -or [string]::IsNullOrWhiteSpace($match.Groups[1].Value)) {
    throw "Agent profile has no non-empty developer_instructions: $resolvedAgentFile"
}

$developerInstructions = [System.Text.Json.JsonSerializer]::Serialize(
    [object]$match.Groups[1].Value,
    [System.Text.Json.JsonSerializerOptions]::new()
)
$commonArgs = @(
    '-m', $Model,
    '-c', "model_reasoning_effort=$ReasoningEffort",
    '-c', "developer_instructions=$developerInstructions",
    '--strict-config',
    '--skip-git-repo-check',
    '--json'
)

if ($PSCmdlet.ParameterSetName -eq 'Start') {
    $resolvedWorkspace = (Resolve-Path -LiteralPath $Workspace).Path
    $codexArgs = @(
        '-a', $Approval,
        'exec'
    ) + $commonArgs + @(
        '-s', $Sandbox,
        '-C', $resolvedWorkspace,
        $Prompt
    )
    $mode = 'start'
}
else {
    $codexArgs = @(
        'exec', 'resume'
    ) + $commonArgs + @(
        $SessionId,
        $Prompt
    )
    $mode = 'resume'
}

$codexLauncher = Resolve-CodexLauncher
$codexInvocationArguments = @($codexLauncher.prefix_arguments) + $codexArgs
Assert-WindowsCommandLineFits `
    -Executable ([string]$codexLauncher.executable) `
    -Arguments $codexInvocationArguments
$jobIdValue = [guid]::NewGuid().ToString('D')
$jobDirectory = Get-JobDirectory -Id $jobIdValue
New-Item -ItemType Directory -Path $jobDirectory | Out-Null
$requestPath = Join-Path $jobDirectory 'request.json'
$launchPath = Join-Path $jobDirectory 'launch.json'
$eventsPath = Join-Path $jobDirectory 'events.jsonl'
$stderrPath = Join-Path $jobDirectory 'stderr.log'
$request = [pscustomobject]@{
    schema_version   = 1
    job_id           = $jobIdValue
    mode             = $mode
    agent            = $Agent
    model            = $Model
    reasoning_effort = $ReasoningEffort
    session_id       = if ($mode -eq 'resume') { $SessionId } else { $null }
    started_at       = [DateTimeOffset]::UtcNow.ToString('o')
    codex_executable = $codexLauncher.executable
    codex_launcher    = $codexLauncher.kind
    codex_source      = $codexLauncher.source
    codex_home       = $codexHome
    events_path      = $eventsPath
    stderr_path      = $stderrPath
    arguments        = $codexInvocationArguments
}
Write-JsonAtomically -Value $request -Path $requestPath

$pwshPath = Join-Path $PSHOME 'pwsh.exe'
$taskName = $null
$processId = $null
$process = $null
$launchError = $null
try {
    if ($IsWindows) {
        $escapeCommandLineValue = {
            param([string]$Value)
            if ($Value.Contains('"')) {
                throw "Command-line path contains an unsupported quote: $Value"
            }
            '"' + $Value + '"'
        }
        $workerArguments = @(
            '-NoLogo',
            '-NoProfile',
            '-NonInteractive',
            '-ExecutionPolicy',
            'Bypass',
            '-WindowStyle',
            'Hidden',
            '-File',
            (& $escapeCommandLineValue $workerPath),
            '-RequestPath',
            (& $escapeCommandLineValue $requestPath)
        ) -join ' '
        $taskName = "CodexOrchestrator-$jobIdValue"
        $action = New-ScheduledTaskAction -Execute $pwshPath -Argument $workerArguments -WorkingDirectory $codexHome
        $settings = New-ScheduledTaskSettingsSet `
            -ExecutionTimeLimit ([TimeSpan]::Zero) `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -Hidden
        $principal = New-ScheduledTaskPrincipal `
            -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) `
            -LogonType Interactive `
            -RunLevel Limited
        Register-ScheduledTask `
            -TaskName $taskName `
            -Action $action `
            -Settings $settings `
            -Principal $principal | Out-Null
        Start-ScheduledTask -TaskName $taskName
    }
    else {
        $process = Start-Process -FilePath $pwshPath -ArgumentList @(
            '-NoLogo',
            '-NoProfile',
            '-NonInteractive',
            '-File',
            $workerPath,
            '-RequestPath',
            $requestPath
        ) -WorkingDirectory $codexHome -PassThru
        $processId = $process.Id
    }
}
catch {
    $launchError = $_
    if ($taskName) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        $taskName = $null
    }
}
$launch = [pscustomobject]@{
    schema_version     = 1
    job_id             = $jobIdValue
    process_id         = $processId
    task_name          = if ($IsWindows) { $taskName } else { $null }
    process_started_at = if ($process) {
        $process.StartTime.ToUniversalTime().ToString('o')
    }
    else {
        $null
    }
    launched_at        = [DateTimeOffset]::UtcNow.ToString('o')
}
Write-JsonAtomically -Value $launch -Path $launchPath
if ($launchError) {
    [System.IO.File]::AppendAllText(
        $stderrPath,
        $launchError.Exception.ToString() + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )
    Write-JsonAtomically -Value ([pscustomobject]@{
        schema_version = 1
        exit_code      = 1
        started_at     = $request.started_at
        completed_at   = [DateTimeOffset]::UtcNow.ToString('o')
    }) -Path (Join-Path $jobDirectory 'result.json')
    Write-OutputJson -Value (Get-SpecialistJobStatus -Id $jobIdValue -ErrorTail 20)
    exit 1
}
Write-OutputJson -Value (Get-SpecialistJobStatus -Id $jobIdValue -ErrorTail 0)
