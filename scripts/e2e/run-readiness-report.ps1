param(
    [string]$ReportDir = "data/reports/e2e/latest"
)
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$start = Get-Date
$checks = @()
foreach ($file in Get-ChildItem -Path $ReportDir -Filter "*.json" -File -ErrorAction SilentlyContinue) {
    if ($file.Name -eq "summary.json") { continue }
    try {
        $json = Get-Content $file.FullName -Raw | ConvertFrom-Json
        if ($json.id -and $json.status) {
            $checks += $json
        }
    } catch {}
}
$audit = & python scripts/audit-production-readiness.py --report-dir data/reports 2>&1
$auditExit = $LASTEXITCODE
$blockerPath = "data/reports/production_blockers.json"
$blockers = @()
if (Test-Path $blockerPath) {
    try { $blockers = @((Get-Content $blockerPath -Raw | ConvertFrom-Json).blockers) } catch { $blockers = @(@{ classification = "production_blocker"; reason = $_.Exception.Message }) }
}
$checks += @{
    id = "production_readiness_audit"
    name = "Production readiness audit"
    status = $(if ($auditExit -eq 0) { "pass" } else { "fail" })
    duration_ms = 0
    evidence = @($blockerPath)
    error = ($audit -join "`n")
    report_path = $blockerPath
}
$required = @("docker_core", "manager_e2e", "pc_real", "android_real", "browser_real", "dev_real", "production_readiness_audit")
$missing = @()
foreach ($id in $required) {
    if (-not ($checks | Where-Object { $_.id -eq $id })) { $missing += $id }
}
$failed = @($checks | Where-Object { $_.status -eq "fail" })
$overall = if ($failed.Count -eq 0 -and $missing.Count -eq 0 -and $blockers.Count -eq 0) { "pass" } else { "fail" }
$summary = @{
    overall_status = $overall
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    duration_ms = [int]((Get-Date) - $start).TotalMilliseconds
    environment = @{
        runtime_mode = $env:AEGIS_RUNTIME_MODE
        pc_real_actions_required = $env:AEGIS_PC_REAL_ACTIONS_REQUIRED
    }
    checks = $checks
    blockers = $blockers
    missing_checks = $missing
    summary = @{
        production_blocker = $blockers.Count
        checks_total = $checks.Count
        checks_failed = $failed.Count
        missing = $missing.Count
    }
}
$summary | ConvertTo-Json -Depth 12 | Set-Content "$ReportDir/summary.json" -Encoding utf8
$md = @(
    "# AEGIS E2E Readiness Summary",
    "",
    "- overall_status: $overall",
    "- production_blocker: $($blockers.Count)",
    "- failed_checks: $($failed.Count)",
    "- missing_checks: $($missing.Count)",
    "",
    "| Status | Check | Error |",
    "|---|---|---|"
)
foreach ($check in $checks) {
    $err = ($check.error | Out-String).Trim().Replace("|", "\|")
    $md += "| $($check.status) | $($check.name) | ``$err`` |"
}
Set-Content "$ReportDir/summary.md" -Value ($md -join "`n") -Encoding utf8
if ($overall -eq "pass") { exit 0 } else { exit 1 }
