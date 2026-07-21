param(
    [string]$ReportDir = "data/reports/e2e/fix-instruction-latest",
    [string]$PcHost = "127.0.0.1",
    [string]$BrowserBase = "http://127.0.0.1:50053",
    [switch]$RequireAndroid,
    [switch]$RequireAgoraReplyId
)

$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$steps = @()

function Invoke-Probe {
    param([string]$Id, [scriptblock]$Action, [string]$ReportPath)
    $started = Get-Date
    & $Action
    $code = $LASTEXITCODE
    $status = if ($code -eq 0) { "pass" } else { "fail" }
    if (Test-Path $ReportPath) {
        try {
            $reported = Get-Content $ReportPath -Raw -Encoding utf8 | ConvertFrom-Json
            if ($reported.status) { $status = [string]$reported.status }
        } catch {
            $status = "fail"
        }
    }
    $script:steps += @{
        id = $Id
        status = $status
        exit_code = $code
        duration_ms = [int]((Get-Date) - $started).TotalMilliseconds
        report_path = $ReportPath
    }
}

$agoraReport = Join-Path $ReportDir "agora-real.json"
Invoke-Probe "agora" {
    $argsList = @("scripts/e2e/agora-real-probe.py", "--report", $agoraReport)
    if ($RequireAgoraReplyId) { $argsList += "--require-reply-id" }
    & "ai-server/.venv/Scripts/python.exe" @argsList
} $agoraReport

$pcReport = Join-Path $ReportDir "pc-real.json"
Invoke-Probe "pc" {
    & powershell -ExecutionPolicy Bypass -File scripts/e2e/run-pc-real.ps1 `
        -ReportDir $ReportDir -PcHost $PcHost
} $pcReport

$browserReport = Join-Path $ReportDir "browser-real.json"
Invoke-Probe "browser" {
    & powershell -ExecutionPolicy Bypass -File scripts/e2e/run-browser-real.ps1 `
        -ReportDir $ReportDir -BrowserBase $BrowserBase
} $browserReport

$androidReport = Join-Path $ReportDir "android-real.json"
$deviceLines = @(& adb devices -l 2>$null | Select-Object -Skip 1 | Where-Object { $_.Trim() })
if ($deviceLines.Count -gt 0) {
    Invoke-Probe "android" {
        & powershell -ExecutionPolicy Bypass -File scripts/e2e/run-android-real.ps1 `
            -ReportDir $ReportDir -TryUsbReverse -RequireOnline
    } $androidReport
} else {
    $steps += @{
        id = "android"
        status = if ($RequireAndroid) { "fail" } else { "pending" }
        exit_code = if ($RequireAndroid) { 1 } else { 0 }
        duration_ms = 0
        report_path = $androidReport
        reason = "No authorized ADB device is currently visible."
    }
}

$blocking = @($steps | Where-Object { $_.status -eq "fail" })
$overall = if ($blocking.Count -gt 0) { "fail" } elseif (($steps | Where-Object { $_.status -in @("partial", "pending") }).Count -gt 0) { "partial" } else { "pass" }
$summary = @{
    overall_status = $overall
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    checks = $steps
    blockers = @($blocking | ForEach-Object { $_.id })
}
$summary | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $ReportDir "summary.json") -Encoding utf8
$summary | ConvertTo-Json -Depth 8
if ($overall -eq "fail") { exit 1 } else { exit 0 }
