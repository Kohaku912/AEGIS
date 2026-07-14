param(
    [string]$ReportDir = "data/reports/e2e/latest"
)

$ErrorActionPreference = "Continue"
$started = Get-Date
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$reportPath = Join-Path $root $ReportDir
New-Item -ItemType Directory -Force -Path $reportPath | Out-Null

Push-Location (Join-Path $root "web-ui")
try {
    $output = & npx playwright test -g "72-hour-equivalent stream" 2>&1
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
$output | Set-Content -Encoding UTF8 (Join-Path $reportPath "display-soak-playwright.log")

$summary = [ordered]@{
    id = "display_soak"
    name = "Display 72-hour-equivalent event accumulation"
    status = if ($exitCode -eq 0) { "pass" } else { "fail" }
    duration_seconds = [int]((Get-Date) - $started).TotalSeconds
    equivalent_duration_seconds = 72 * 60 * 60
    sample_count = 8640
    sample_interval_equivalent_seconds = 30
    failure_count = if ($exitCode -eq 0) { 0 } else { 1 }
    memory_growth_limit_bytes = 96 * 1024 * 1024
    evidence = @(
        "$ReportDir/display-soak-playwright.log",
        "web-ui/tests/display.spec.ts"
    )
    error = if ($exitCode -eq 0) { "" } else { ($output | Select-Object -Last 20) -join "`n" }
    report_path = "$ReportDir/display_soak_summary.json"
}
$summary | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $reportPath "display_soak_summary.json")
if ($exitCode -eq 0) { exit 0 }
exit 1
