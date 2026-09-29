# test-ai-server.ps1 - Run the ai-server test suite plus the egress constraint checks.
#
# The egress suite guards AEGIS's single constraint: the user's information must
# never leave the local environment. Three checks run here, all mandatory:
#
#   1. The full ai-server suite.
#   2. The egress suite with --require-egress-tests=N. This is the retired
#      --fail-on-empty discipline: a rename, a marker typo, or a narrowed -k
#      expression can leave the egress selection empty while pytest reports the
#      rest of the suite as passing, so the constraint silently stops being
#      checked. The floor makes that a hard failure.
#   3. The mutation check. The egress suite must FAIL when the gate is
#      deliberately disabled; a suite that has never been observed failing is an
#      assumption, not a control.
#
# Usage:
#   .\scripts\test-ai-server.ps1
#   .\scripts\test-ai-server.ps1 -EgressFloor 160
#   .\scripts\test-ai-server.ps1 -SkipMutation      # faster local iteration
#
# If your shell blocks script execution (the default on many Windows installs),
# run it through a bypass:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-ai-server.ps1

param(
    [int]$EgressFloor = 160,
    [switch]$SkipMutation
)

$ErrorActionPreference = "Continue"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$AiServer = Join-Path $RepoRoot "ai-server"
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$MutationScript = Join-Path $AiServer "scripts\verify_egress_tests_catch_regression.py"

if (-not (Test-Path $Python)) {
    Write-Host "Python not found at $Python" -ForegroundColor Red
    Write-Host "Create the venv first (see ai-server/README or docs/)." -ForegroundColor Red
    exit 1
}

# The WorkBuddy safe-delete shim turns Path.unlink() into SystemExit(1) during
# pytest teardown. Disable it for test runs.
$env:CODEBUDDY_SAFE_DELETE_ENABLED = "0"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AEGIS ai-server test suite" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Push-Location $AiServer

$failed = @()

# ── 1. Full suite ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[1/3] Full ai-server suite ..." -ForegroundColor Green
& $Python -m pytest tests/ -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] full suite exited $LASTEXITCODE" -ForegroundColor Red
    $failed += "full suite"
} else {
    Write-Host "  [PASS] full suite" -ForegroundColor Green
}

# ── 2. Egress suite with the --fail-on-empty floor ───────────────────────────
Write-Host ""
Write-Host "[2/3] Egress suite (-m egress --require-egress-tests=$EgressFloor) ..." -ForegroundColor Green
& $Python -m pytest -m egress --require-egress-tests=$EgressFloor -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] the egress suite failed or fell below the floor of $EgressFloor" -ForegroundColor Red
    $failed += "egress suite (floor $EgressFloor)"
} else {
    Write-Host "  [PASS] egress suite" -ForegroundColor Green
}

# ── 3. Mutation check ────────────────────────────────────────────────────────
if ($SkipMutation) {
    Write-Host ""
    Write-Host "[3/3] Mutation check ... SKIPPED (-SkipMutation)" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[3/3] Mutation check (the egress suite must fail when the gate is broken) ..." -ForegroundColor Green
    & $Python $MutationScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [FAIL] the egress suite does not catch a disabled gate" -ForegroundColor Red
        $failed += "mutation check"
    } else {
        Write-Host "  [PASS] mutation check" -ForegroundColor Green
    }
}

Pop-Location

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
if ($failed.Count -eq 0) {
    Write-Host "  ALL CHECKS PASSED" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    exit 0
}

Write-Host "  FAILED: $($failed -join ', ')" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Cyan
exit 1
