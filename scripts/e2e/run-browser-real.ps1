param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$BrowserBase = "http://127.0.0.1:50053"
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

foreach ($url in @("$BrowserBase/health", "$BrowserBase/observe")) {
    $cStart = Get-Date
    try {
        $res = Invoke-WebRequest -UseBasicParsing -TimeoutSec 15 $url
        Add-Check "browser_http" $url $(if ($res.StatusCode -lt 500) { "pass" } else { "fail" }) @($url) "" $cStart
    } catch {
        Add-Check "browser_http" $url "fail" @($url) $_.Exception.Message $cStart
    }
}
$browseStart = Get-Date
try {
    $html = "<!doctype html><html><head><title>AEGIS Browser E2E</title></head><body><main id='probe'><h1>Browser verification probe</h1><p>AEGIS_BROWSER_E2E_TEXT</p></main></body></html>"
    $dataUrl = "data:text/html;charset=utf-8,$([uri]::EscapeDataString($html))"
    $body = @{
        url = $dataUrl
        selector = "#probe"
        expect_text = "AEGIS_BROWSER_E2E_TEXT"
    } | ConvertTo-Json -Depth 4
    $browse = Invoke-RestMethod -Method Post -Uri "$BrowserBase/browse" -ContentType "application/json" -Body $body -TimeoutSec 45
    $browse | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/browser-dom-verification.json" -Encoding utf8
    $verification = $browse.verification
    $passed = $browse.ok -eq $true -and $verification.passed -eq $true -and $verification.selector_found -eq $true -and $verification.text_found -eq $true
    if ($passed) {
        Add-Check "browser_dom_verification" "Browser DOM selector/text/http verification" "pass" @("$ReportDir/browser-dom-verification.json") "" $browseStart
    } else {
        Add-Check "browser_dom_verification" "Browser DOM selector/text/http verification" "fail" @("$ReportDir/browser-dom-verification.json") "DOM verification did not pass" $browseStart
    }
} catch {
    Add-Check "browser_dom_verification" "Browser DOM selector/text/http verification" "fail" @("$ReportDir/browser-dom-verification.json") $_.Exception.Message $browseStart
}
$status = if (($checks | Where-Object { $_.status -ne "pass" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{ id = "browser_real"; name = "Browser real service"; status = $status; duration_ms = [int]((Get-Date)-$start).TotalMilliseconds; evidence = @("$ReportDir/browser-real.json"); error = ""; report_path = "$ReportDir/browser-real.json"; checks = $checks }
$result | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/browser-real.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
