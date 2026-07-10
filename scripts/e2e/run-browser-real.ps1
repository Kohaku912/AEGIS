param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$BrowserBase = "http://127.0.0.1:50053"
)
$ErrorActionPreference = "Continue"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$checks = @()
foreach ($url in @("$BrowserBase/health", "$BrowserBase/observe")) {
    $cStart = Get-Date
    try {
        $res = Invoke-WebRequest -UseBasicParsing -TimeoutSec 15 $url
        $checks += @{ id = "browser"; name = $url; status = $(if ($res.StatusCode -lt 500) { "pass" } else { "fail" }); duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @($url); error = ""; report_path = "" }
    } catch {
        $checks += @{ id = "browser"; name = $url; status = "fail"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @($url); error = $_.Exception.Message; report_path = "" }
    }
}
$status = if (($checks | Where-Object { $_.status -ne "pass" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{ id = "browser_real"; name = "Browser real service"; status = $status; duration_ms = [int]((Get-Date)-$start).TotalMilliseconds; evidence = @("$ReportDir/browser-real.json"); error = ""; report_path = "$ReportDir/browser-real.json"; checks = $checks }
$result | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/browser-real.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
