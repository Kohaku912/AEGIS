param(
    [string]$ReportDir = "data/reports/e2e/latest"
)

$ErrorActionPreference = "Continue"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$checks = @()

function Add-Check {
    param(
        [string]$Id,
        [string]$Name,
        [string]$Status,
        [array]$Evidence,
        [string]$Error,
        [datetime]$Started
    )
    $script:checks += @{
        id = $Id
        name = $Name
        status = $Status
        duration_ms = [int]((Get-Date)-$Started).TotalMilliseconds
        evidence = $Evidence
        error = $Error
        report_path = ""
    }
}

function Exec-Ai {
    param([string]$Command)
    return docker compose exec -T ai-server sh -lc $Command
}

function Wait-AiContainer {
    param([int]$TimeoutSec = 60)
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $id = docker compose ps -q ai-server 2>$null
        if ($LASTEXITCODE -eq 0 -and $id) {
            $state = docker inspect -f "{{.State.Running}}" $id 2>$null
            if ($state -eq "true") { return $true }
        }
        Start-Sleep -Seconds 2
    }
    return $false
}

$sentinelPath = "/app/data/readiness/persistence-sentinel.txt"
$sentinel = "aegis-persistence-" + [guid]::NewGuid().ToString("N")

$writeStart = Get-Date
try {
    Exec-Ai "mkdir -p /app/data/readiness /app/data/auth /app/data/memory /app/data/reports && printf '%s' '$sentinel' > $sentinelPath"
    $readBack = Exec-Ai "cat $sentinelPath"
    if (($readBack | Out-String).Trim() -eq $sentinel) {
        Add-Check "persistence_write" "Write sentinel to Docker data volume" "pass" @($sentinelPath) "" $writeStart
    } else {
        Add-Check "persistence_write" "Write sentinel to Docker data volume" "fail" @($sentinelPath) "Sentinel readback mismatch" $writeStart
    }
} catch {
    Add-Check "persistence_write" "Write sentinel to Docker data volume" "fail" @($sentinelPath) $_.Exception.Message $writeStart
}

$restartStart = Get-Date
try {
    docker compose restart ai-server | Out-Null
    if (-not (Wait-AiContainer 90)) { throw "ai-server did not return to running state after restart" }
    $afterRestart = Exec-Ai "cat $sentinelPath"
    if (($afterRestart | Out-String).Trim() -eq $sentinel) {
        Add-Check "persistence_restart" "Data volume survives docker compose restart" "pass" @($sentinelPath) "" $restartStart
    } else {
        Add-Check "persistence_restart" "Data volume survives docker compose restart" "fail" @($sentinelPath) "Sentinel missing after restart" $restartStart
    }
} catch {
    Add-Check "persistence_restart" "Data volume survives docker compose restart" "fail" @($sentinelPath) $_.Exception.Message $restartStart
}

$recreateStart = Get-Date
try {
    docker compose up -d --no-deps --force-recreate ai-server | Out-Null
    if (-not (Wait-AiContainer 120)) { throw "ai-server did not return to running state after force recreate" }
    $afterRecreate = Exec-Ai "cat $sentinelPath"
    if (($afterRecreate | Out-String).Trim() -eq $sentinel) {
        Add-Check "persistence_recreate" "Data volume survives container recreate" "pass" @($sentinelPath) "" $recreateStart
    } else {
        Add-Check "persistence_recreate" "Data volume survives container recreate" "fail" @($sentinelPath) "Sentinel missing after recreate" $recreateStart
    }
} catch {
    Add-Check "persistence_recreate" "Data volume survives container recreate" "fail" @($sentinelPath) $_.Exception.Message $recreateStart
}

$requiredPathsStart = Get-Date
try {
    $pathProbe = Exec-Ai "python - <<'PY'
from pathlib import Path
required = ['/app/data/auth', '/app/data/memory', '/app/data/reports', '/app/data/settings']
print('\\n'.join(f'{path}:{Path(path).exists()}' for path in required))
PY"
    $pathProbe | Set-Content "$ReportDir/persistence-paths.txt" -Encoding utf8
    $missing = @($pathProbe | Where-Object { $_ -match ":False$" })
    if ($missing.Count -eq 0) {
        Add-Check "persistence_required_paths" "Auth/memory/reports/settings paths exist in data volume" "pass" @("$ReportDir/persistence-paths.txt") "" $requiredPathsStart
    } else {
        Add-Check "persistence_required_paths" "Auth/memory/reports/settings paths exist in data volume" "fail" @("$ReportDir/persistence-paths.txt") "Missing paths: $($missing -join ', ')" $requiredPathsStart
    }
} catch {
    Add-Check "persistence_required_paths" "Auth/memory/reports/settings paths exist in data volume" "fail" @("$ReportDir/persistence-paths.txt") $_.Exception.Message $requiredPathsStart
}

$status = if (($checks | Where-Object { $_.status -ne "pass" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{
    id = "docker_persistence"
    name = "Docker restart/recreate persistence"
    status = $status
    duration_ms = [int]((Get-Date)-$start).TotalMilliseconds
    evidence = @("$ReportDir/docker-persistence.json", "$ReportDir/persistence-paths.txt")
    error = ""
    report_path = "$ReportDir/docker-persistence.json"
    checks = $checks
}
$result | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/docker-persistence.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
