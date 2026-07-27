# GENERATED: protocol=2.1.0 source_sha256=23388e1cde7d1ee06fa89ea360d39bacaff33753e14cdc39893e1449b07bdda1; edit ~/.agentic/orchestrator and run sync_runtime.py.
function Get-CodexOutputSchemaCompatibilityErrors {
    [CmdletBinding()]
    param([Parameter(Mandatory)][object]$Schema)

    $errors = [System.Collections.Generic.List[string]]::new()
    $allowedKeywords = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($keyword in @(
        '$schema', '$id', '$defs', '$ref', 'title', 'description', 'type', 'enum', 'const', 'anyOf',
        'properties', 'required', 'additionalProperties', 'items', 'pattern', 'format', 'minLength',
        'maxLength', 'multipleOf', 'maximum', 'exclusiveMaximum', 'minimum', 'exclusiveMinimum',
        'minItems', 'maxItems'
    )) { [void]$allowedKeywords.Add($keyword) }

    function Visit-SchemaNode {
        param([Parameter(Mandatory)][object]$Node, [Parameter(Mandatory)][string]$Path, [switch]$Root)

        if ($Node -isnot [pscustomobject]) {
            [void]$errors.Add("$Path must be a JSON object")
            return
        }

        $propertyNames = @($Node.PSObject.Properties.Name)
        foreach ($name in $propertyNames) {
            if (-not $allowedKeywords.Contains($name)) {
                [void]$errors.Add("$Path uses unsupported Structured Outputs keyword '$name'")
            }
        }

        if ($Root) {
            if ([string]$Node.type -ne 'object') { [void]$errors.Add('The root schema type must be object') }
            if ('anyOf' -in $propertyNames) { [void]$errors.Add('The root schema must not use anyOf') }
        }

        if ('properties' -in $propertyNames) {
            if ($Node.properties -isnot [pscustomobject]) {
                [void]$errors.Add("$Path.properties must be a JSON object")
            }
            else {
                $defined = @($Node.properties.PSObject.Properties.Name)
                $required = @($Node.required)
                if ('required' -notin $propertyNames) {
                    [void]$errors.Add("$Path must require every declared property")
                }
                foreach ($name in $defined) {
                    if ($name -notin $required) { [void]$errors.Add("$Path property '$name' is not required") }
                    Visit-SchemaNode -Node $Node.properties.$name -Path "$Path.properties.$name"
                }
                foreach ($name in $required) {
                    if ($name -notin $defined) { [void]$errors.Add("$Path requires undefined property '$name'") }
                }
                if ('additionalProperties' -notin $propertyNames -or $Node.additionalProperties -ne $false) {
                    [void]$errors.Add("$Path must set additionalProperties to false")
                }
            }
        }

        if ('$defs' -in $propertyNames) {
            if ($Node.'$defs' -isnot [pscustomobject]) {
                [void]$errors.Add("$Path.`$defs must be a JSON object")
            }
            else {
                foreach ($definition in @($Node.'$defs'.PSObject.Properties)) {
                    Visit-SchemaNode -Node $definition.Value -Path "$Path.`$defs.$($definition.Name)"
                }
            }
        }
        if ('items' -in $propertyNames) { Visit-SchemaNode -Node $Node.items -Path "$Path.items" }
        if ('anyOf' -in $propertyNames) {
            $index = 0
            foreach ($variant in @($Node.anyOf)) {
                Visit-SchemaNode -Node $variant -Path "$Path.anyOf[$index]"
                $index++
            }
        }
    }

    Visit-SchemaNode -Node $Schema -Path '$' -Root
    return @($errors)
}

function Assert-CodexOutputSchemaCompatibility {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$SchemaPath)

    if (-not (Test-Path -LiteralPath $SchemaPath -PathType Leaf)) {
        throw "Output schema is unavailable: $SchemaPath"
    }
    try { $schema = Get-Content -Raw -LiteralPath $SchemaPath | ConvertFrom-Json -Depth 100 }
    catch { throw "Output schema is not valid JSON: $($_.Exception.Message)" }
    $errors = @(Get-CodexOutputSchemaCompatibilityErrors -Schema $schema)
    if ($errors.Count -gt 0) {
        throw "Output schema is incompatible with Codex Structured Outputs: $($errors -join '; ')"
    }
}

function Assert-SpecialistTerminalResult {
    [CmdletBinding()]
    param([Parameter(Mandatory)][object]$Result)

    $required = @('status', 'summary', 'artifact_paths', 'verification', 'changed', 'needs', 'finding_ids')
    $actual = @($Result.PSObject.Properties.Name)
    foreach ($name in $required) {
        if ($name -notin $actual) { throw "required field '$name' is missing" }
    }
    foreach ($name in $actual) {
        if ($name -notin $required) { throw "unexpected field '$name' is present" }
    }

    $allowedStatuses = @('DONE', 'DONE_WITH_CONCERNS', 'APPROVED', 'CHANGES_REQUIRED', 'BLOCKED', 'NEEDS_CONTEXT', 'PACK_GAP')
    if ($Result.status -isnot [string] -or ([string]$Result.status).Trim() -notin $allowedStatuses) {
        throw "status '$($Result.status)' is invalid"
    }
    if ($Result.summary -isnot [string]) { throw 'summary must be a string' }

    foreach ($field in @('artifact_paths', 'verification', 'changed', 'needs', 'finding_ids')) {
        $value = $Result.$field
        if ($null -eq $value -or $value -is [string] -or $value -isnot [System.Collections.IEnumerable]) {
            throw "$field must be an array of strings"
        }
        foreach ($item in @($value)) {
            if ($item -isnot [string]) { throw "$field must contain only strings" }
        }
    }

    foreach ($findingId in @($Result.finding_ids)) {
        if (([string]$findingId).Trim() -notmatch '^RC-[0-9]{2,}$') { throw "finding_ids contains invalid value '$findingId'" }
    }
}

function Normalize-SpecialistTerminalResult {
    [CmdletBinding()]
    param([Parameter(Mandatory)][object]$Result)

    # Validate first so normalization never invents a missing field or hides a
    # malformed result. Whitespace and duplicate list entries are harmless and
    # are normalized deterministically instead of wasting a resume turn.
    Assert-SpecialistTerminalResult -Result $Result
    $normalized = [ordered]@{
        status = ([string]$Result.status).Trim()
        summary = ([string]$Result.summary).Trim()
    }
    foreach ($field in @('artifact_paths', 'verification', 'changed', 'needs', 'finding_ids')) {
        $seen = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        $values = [System.Collections.Generic.List[string]]::new()
        foreach ($item in @($Result.$field)) {
            $value = ([string]$item).Trim()
            if ($value.Length -gt 0 -and $seen.Add($value)) { [void]$values.Add($value) }
        }
        $normalized[$field] = @($values)
    }
    [pscustomobject]$normalized
}

function Resolve-SpecialistArtifactPath {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$Workspace)
    $expanded = [Environment]::ExpandEnvironmentVariables($Path)
    if ([System.IO.Path]::IsPathFullyQualified($expanded)) {
        return [System.IO.Path]::GetFullPath($expanded)
    }
    [System.IO.Path]::GetFullPath((Join-Path ([System.IO.Path]::GetFullPath($Workspace)) $expanded))
}

function Assert-SpecialistMarkdownHeadings {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string[]]$Headings,
        [Parameter(Mandatory)][string]$Label
    )
    $text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    foreach ($heading in $Headings) {
        if ($text -notmatch "(?m)^##\s+$([regex]::Escape($heading))\s*$") {
            throw "$Label is missing required heading '$heading': $Path"
        }
    }
}

function Assert-SpecialistArtifacts {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object]$Result,
        [Parameter(Mandatory)][string]$Agent,
        [Parameter(Mandatory)][string]$Workspace,
        [string[]]$RequiredArtifacts = @()
    )

    $resolvedWorkspace = [System.IO.Path]::GetFullPath($Workspace)
    $declaredPaths = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($declared in @($Result.artifact_paths)) {
        if ([string]::IsNullOrWhiteSpace([string]$declared)) { throw 'artifact_paths contains an empty path' }
        $resolved = Resolve-SpecialistArtifactPath -Path ([string]$declared) -Workspace $resolvedWorkspace
        [void]$declaredPaths.Add($resolved)
        if (-not (Test-Path -LiteralPath $resolved)) {
            throw "declared artifact does not exist: $declared"
        }
        if (Test-Path -LiteralPath $resolved -PathType Leaf) {
            if ((Get-Item -LiteralPath $resolved).Length -eq 0) { throw "declared artifact is empty: $declared" }
        }
        elseif (-not (Get-ChildItem -LiteralPath $resolved -Force | Select-Object -First 1)) {
            throw "declared artifact directory is empty: $declared"
        }
    }

    foreach ($required in @($RequiredArtifacts)) {
        if ([string]::IsNullOrWhiteSpace([string]$required)) { throw 'required_artifacts contains an empty path' }
        $resolvedRequired = Resolve-SpecialistArtifactPath -Path ([string]$required) -Workspace $resolvedWorkspace
        if (-not $declaredPaths.Contains($resolvedRequired)) {
            throw "required artifact was not declared by ${Agent}: $required"
        }
        if (-not (Test-Path -LiteralPath $resolvedRequired -PathType Leaf)) {
            throw "required artifact is missing or is not a file: $required"
        }
        if ((Get-Item -LiteralPath $resolvedRequired).Length -eq 0) {
            throw "required artifact is empty: $required"
        }
        if ($Agent -eq 'codebase-explorer') {
            Assert-SpecialistMarkdownHeadings -Path $resolvedRequired -Label 'context map' -Headings @(
                'Objective', 'Index / CodeGraph Status', 'Relevant Areas', 'Behavior / Data Flow',
                'Existing Patterns to Reuse', 'Tests and Verification Entry Points',
                'Internal Integration / Data Contracts', 'Named Risks', 'Open Unknowns'
            )
        }
        elseif ($Agent -eq 'integration-researcher') {
            Assert-SpecialistMarkdownHeadings -Path $resolvedRequired -Label 'integration recipe' -Headings @(
                'Objective', 'Version and Sources', 'Chosen Approach', 'Contract',
                'Minimal Repo-Idiomatic Snippet', 'Setup', 'Verification Strategy',
                'Fact Evidence', 'Risks / Unknowns'
            )
        }
        elseif ($Agent -eq 'task-implementer-bdd') {
            Assert-SpecialistMarkdownHeadings -Path $resolvedRequired -Label 'task report' -Headings @(
                'Owner', 'Status', 'Outcome', 'Acceptance Criteria', 'Files Changed',
                'Symbol / Contract Changes', 'Verification', 'Read Ledger', 'Effect Cleanup',
                'Decisions', 'Concerns', 'Remediation History'
            )
        }
        elseif ($Agent -eq 'implementation-reviewer') {
            Assert-SpecialistMarkdownHeadings -Path $resolvedRequired -Label 'review' -Headings @(
                'Reviewer Owner', 'Verdict', 'Functional Verification', 'Specification Compliance',
                'Code Quality', 'Named Risk Checks', 'Required Changes', 'Remediation History',
                'Evidence', 'Limitations'
            )
        }
    }

    $artifactOwners = @(
        'codebase-explorer',
        'integration-researcher',
        'implementation-planner',
        'implementation-planner-claude-host',
        'task-implementer-bdd',
        'implementation-reviewer'
    )
    $completedStatuses = @('DONE', 'DONE_WITH_CONCERNS', 'APPROVED', 'CHANGES_REQUIRED')
    if ($Agent -in $artifactOwners -and ([string]$Result.status) -in $completedStatuses -and @($Result.artifact_paths).Count -eq 0) {
        throw "$Agent returned $($Result.status) without its required artifact"
    }
}
