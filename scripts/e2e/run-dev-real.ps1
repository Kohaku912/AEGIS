param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [int]$DevPort = 50056,
    [switch]$ManageDocker
)
$ErrorActionPreference = "Continue"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$checks = @()
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$managed = $false
if ($ManageDocker) {
    Push-Location $root
    try {
        docker compose -f docker-compose.yml -f docker-compose.production.yml --profile dev up -d dev-server | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Failed to start dev-server profile" }
        $managed = $true
    } catch {
        $checks += @{ id = "dev_profile_start"; name = "Dev profile starts on demand"; status = "fail"; duration_ms = 0; evidence = @("docker compose --profile dev up"); error = $_.Exception.Message; report_path = "" }
    } finally {
        Pop-Location
    }
}
$cStart = Get-Date
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("127.0.0.1", $DevPort)
    $tcp.Close()
    $checks += @{ id = "dev_tcp"; name = "Dev Server TCP"; status = "pass"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @("127.0.0.1:$DevPort"); error = ""; report_path = "" }
} catch {
    $checks += @{ id = "dev_tcp"; name = "Dev Server TCP"; status = "fail"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @("127.0.0.1:$DevPort"); error = $_.Exception.Message; report_path = "" }
}
$probeStart = Get-Date
try {
    $python = Join-Path $root "ai-server\.venv\Scripts\python.exe"
    if (-not (Test-Path $python)) { $python = "python" }
    $probeOutput = & $python (Join-Path $PSScriptRoot "dev-real-probe.py") "127.0.0.1" $DevPort
    if ($LASTEXITCODE -ne 0) { throw "Dev gRPC probe failed: $probeOutput" }
    $probeOutput | Set-Content "$ReportDir/dev-real-probe.json" -Encoding utf8
    $probe = $probeOutput | ConvertFrom-Json
    $checks += @{ id = "dev_readonly_operations"; name = "Dev health/repo status/diff"; status = "pass"; duration_ms = [int]((Get-Date)-$probeStart).TotalMilliseconds; evidence = @("$ReportDir/dev-real-probe.json"); error = ""; report_path = "" }
} catch {
    $checks += @{ id = "dev_readonly_operations"; name = "Dev health/repo status/diff"; status = "fail"; duration_ms = [int]((Get-Date)-$probeStart).TotalMilliseconds; evidence = @("$ReportDir/dev-real-probe.json"); error = $_.Exception.Message; report_path = "" }
}
if ($managed) {
    Push-Location $root
    try { docker compose -f docker-compose.yml -f docker-compose.production.yml --profile dev stop dev-server | Out-Null } finally { Pop-Location }
}
$status = if (($checks | Where-Object { $_.status -ne "pass" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{ id = "dev_real"; name = "Dev real service"; status = $status; duration_ms = [int]((Get-Date)-$start).TotalMilliseconds; evidence = @("$ReportDir/dev-real.json"); error = ""; report_path = "$ReportDir/dev-real.json"; checks = $checks }
$result | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/dev-real.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
