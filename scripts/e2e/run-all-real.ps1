param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [switch]$Rebuild,
    [switch]$SkipPc,
    [switch]$SkipAndroid,
    [switch]$RealPcActions,
    [string]$AndroidHost = "192.168.50.175",
    [string]$AndroidTailscaleHost = ""
)
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$steps = @()
function Run-Step($Id, $Script, $ArgsList) {
    $start = Get-Date
    Write-Host "== $Id ==" -ForegroundColor Cyan
    & powershell -ExecutionPolicy Bypass -File $Script @ArgsList
    $exit = $LASTEXITCODE
    $script:steps += @{ id = $Id; status = $(if ($exit -eq 0) { "pass" } else { "fail" }); duration_ms = [int]((Get-Date)-$start).TotalMilliseconds; exit_code = $exit }
}
$dockerArgs = @("-ReportDir", $ReportDir)
if ($Rebuild) { $dockerArgs += "-Rebuild" }
Run-Step "docker" "scripts/e2e/run-docker-core.ps1" $dockerArgs
Run-Step "managers" "scripts/e2e/run-manager-e2e.ps1" @("-ReportDir", $ReportDir)
Run-Step "browser" "scripts/e2e/run-browser-real.ps1" @("-ReportDir", $ReportDir)
Run-Step "dev" "scripts/e2e/run-dev-real.ps1" @("-ReportDir", $ReportDir)
if (-not $SkipPc) {
    $pcArgs = @("-ReportDir", $ReportDir)
    if ($RealPcActions) { $pcArgs += "-RealActions" }
    Run-Step "pc" "scripts/e2e/run-pc-real.ps1" $pcArgs
}
if (-not $SkipAndroid) {
    $androidArgs = @("-ReportDir", $ReportDir, "-HostAddress", $AndroidHost)
    if ($AndroidTailscaleHost) { $androidArgs += @("-TailscaleHost", $AndroidTailscaleHost, "-RequireOnline") }
    Run-Step "android" "scripts/e2e/run-android-real.ps1" $androidArgs
}
Run-Step "readiness" "scripts/e2e/run-readiness-report.ps1" @("-ReportDir", $ReportDir)
$steps | ConvertTo-Json -Depth 6 | Set-Content "$ReportDir/run-all-steps.json" -Encoding utf8
if (($steps | Where-Object { $_.status -eq "fail" }).Count -eq 0) { exit 0 } else { exit 1 }
