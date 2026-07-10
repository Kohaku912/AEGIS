param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [int]$DevPort = 50056
)
$ErrorActionPreference = "Continue"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$checks = @()
$cStart = Get-Date
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("127.0.0.1", $DevPort)
    $tcp.Close()
    $checks += @{ id = "dev_tcp"; name = "Dev Server TCP"; status = "pass"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @("127.0.0.1:$DevPort"); error = ""; report_path = "" }
} catch {
    $checks += @{ id = "dev_tcp"; name = "Dev Server TCP"; status = "fail"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @("127.0.0.1:$DevPort"); error = $_.Exception.Message; report_path = "" }
}
$status = if (($checks | Where-Object { $_.status -ne "pass" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{ id = "dev_real"; name = "Dev real service"; status = $status; duration_ms = [int]((Get-Date)-$start).TotalMilliseconds; evidence = @("$ReportDir/dev-real.json"); error = ""; report_path = "$ReportDir/dev-real.json"; checks = $checks }
$result | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/dev-real.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
