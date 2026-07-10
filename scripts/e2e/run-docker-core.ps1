param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [switch]$Rebuild
)
$ErrorActionPreference = "Stop"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$evidence = @()
$status = "pass"
$errorMessage = ""
try {
    if ($Rebuild) { docker compose build ai-server browser-server room-server dev-server | Out-File "$ReportDir/docker-build.log" -Encoding utf8 }
    docker compose up -d ai-server browser-server room-server dev-server | Out-File "$ReportDir/docker-up.log" -Encoding utf8
    $evidence += "$ReportDir/docker-up.log"
    Start-Sleep -Seconds 5
    $dashboard = Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 "http://127.0.0.1:8090/health"
    if ($dashboard.StatusCode -ge 400) { throw "Dashboard health returned $($dashboard.StatusCode)" }
    $evidence += "http://127.0.0.1:8090/health"
} catch {
    $status = "fail"
    $errorMessage = $_.Exception.Message
}
$result = @{
    id = "docker_core"
    name = "Docker core services"
    status = $status
    duration_ms = [int]((Get-Date) - $start).TotalMilliseconds
    evidence = $evidence
    error = $errorMessage
    report_path = "$ReportDir/docker-core.json"
}
$result | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/docker-core.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
