param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [switch]$Rebuild,
    [switch]$IncludeDev,
    [switch]$IncludeRoom
)
$ErrorActionPreference = "Stop"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$evidence = @()
$status = "pass"
$errorMessage = ""
function Wait-HttpOk([string]$Url, [int]$Attempts = 24, [int]$DelaySec = 3) {
    $lastError = ""
    for ($i = 0; $i -lt $Attempts; $i++) {
        try {
            $res = Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 $Url
            if ($res.StatusCode -lt 400) { return $res }
            $lastError = "HTTP $($res.StatusCode)"
        } catch {
            $lastError = $_.Exception.Message
        }
        Start-Sleep -Seconds $DelaySec
    }
    throw "Timed out waiting for $Url. Last error: $lastError"
}

try {
    $compose = @("compose", "-f", "docker-compose.yml", "-f", "docker-compose.production.yml")
    $services = @("ai-server", "browser-server")
    if ($IncludeDev) { $compose += @("--profile", "dev"); $services += "dev-server" }
    if ($IncludeRoom) { $compose += @("--profile", "room"); $services += "room-server" }
    if ($Rebuild) { docker @compose build @services | Out-File "$ReportDir/docker-build.log" -Encoding utf8 }
    docker @compose up -d @services | Out-File "$ReportDir/docker-up.log" -Encoding utf8
    $evidence += "$ReportDir/docker-up.log"
    $dashboard = Wait-HttpOk "http://127.0.0.1:8090/health"
    $evidence += "http://127.0.0.1:8090/health"
    docker @compose ps --format json | Set-Content "$ReportDir/docker-ps.json" -Encoding utf8
    $evidence += "$ReportDir/docker-ps.json"
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
