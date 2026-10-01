# test-ai-server.ps1 - Run the ai-server test suite plus the egress constraint checks.
#
# The egress suite guards AEGIS's single constraint: **unpermitted** user information
# must never leave the local environment (re-scoped 2026-09-30 — outbound connections,
# and disclosure the user permits, are allowed). Four checks run here, all mandatory:
#
#   1. Ruff, scoped to F821 (undefined name). This is the only check that is not
#      dynamic, and it runs first because it is sub-second while the suite is minutes.
#      It is scoped deliberately — see the block below.
#   2. The full ai-server suite.
#   3. The egress suite with --require-egress-tests=N. This is the retired
#      --fail-on-empty discipline: a rename, a marker typo, or a narrowed -k
#      expression can leave the egress selection empty while pytest reports the
#      rest of the suite as passing, so the constraint silently stops being
#      checked. The floor makes that a hard failure.
#   4. The mutation check. The egress suite must FAIL when the gate is
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

# ── 1. Ruff, scoped to F821 ──────────────────────────────────────────────────
# Deliberately `--select F821`, not a wholesale `ruff check`. The declared rule set
# in pyproject.toml (E, F, I, N, W, UP) has 994 outstanding findings across src/, so
# an unscoped gate would fail on its first run and be switched off again. F821 is the
# one rule that is BOTH zero-debt across src/ and tests/ AND demonstrated to catch what
# pytest cannot: a live path that passed the entire suite green while calling an
# undefined name (`_create_autonomous_loop` passing `confirmation_store`, a local of
# the separate `_build_runtime`). ruff was the only tool that saw it, and ruff was not
# in CI. Widening this scope is a follow-up, not a prerequisite — see DELEGATION.md §4.
Write-Host ""
Write-Host "[1/4] Ruff F821 (undefined names) ..." -ForegroundColor Green
# Non-vacuity guard, for the same reason the egress floor exists. Measured: `ruff check
# <missing path>` **exits 0** and only warns ("Failed to lint ...: os error 2"), so a
# renamed or moved directory would leave this check reporting [PASS] while linting nothing.
# Assert the surface first, then lint it.
$ruffTargets = @("src", "tests")
$missingTargets = @($ruffTargets | Where-Object { -not (Test-Path $_) })
$lintableFiles = @(Get-ChildItem -Path $ruffTargets -Recurse -Filter *.py -ErrorAction SilentlyContinue)
if ($missingTargets.Count -gt 0 -or $lintableFiles.Count -eq 0) {
    Write-Host "  [FAIL] ruff has no surface to lint (missing: $($missingTargets -join ', '); .py files found: $($lintableFiles.Count))" -ForegroundColor Red
    $failed += "ruff F821 (no surface)"
} else {
    & $Python -m ruff check src tests --select F821
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [FAIL] ruff found an undefined name" -ForegroundColor Red
        $failed += "ruff F821"
    } else {
        Write-Host "  [PASS] ruff F821 ($($lintableFiles.Count) files)" -ForegroundColor Green
    }
}

# ── 2. Full suite ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[2/4] Full ai-server suite ..." -ForegroundColor Green
& $Python -m pytest tests/ -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] full suite exited $LASTEXITCODE" -ForegroundColor Red
    $failed += "full suite"
} else {
    Write-Host "  [PASS] full suite" -ForegroundColor Green
}

# ── 3. Egress suite with the --fail-on-empty floor ───────────────────────────
Write-Host ""
Write-Host "[3/4] Egress suite (-m egress --require-egress-tests=$EgressFloor) ..." -ForegroundColor Green
& $Python -m pytest -m egress --require-egress-tests=$EgressFloor -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] the egress suite failed or fell below the floor of $EgressFloor" -ForegroundColor Red
    $failed += "egress suite (floor $EgressFloor)"
} else {
    Write-Host "  [PASS] egress suite" -ForegroundColor Green
}

# ── 4. Mutation check ────────────────────────────────────────────────────────
if ($SkipMutation) {
    Write-Host ""
    Write-Host "[4/4] Mutation check ... SKIPPED (-SkipMutation)" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[4/4] Mutation check (the egress suite must fail when the gate is broken) ..." -ForegroundColor Green
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
