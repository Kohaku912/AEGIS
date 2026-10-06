# test-all-suites.ps1 - Run every Python test suite, so that none of them can drift unnoticed.
#
# Why this exists: scripts/test-ai-server.ps1 guards the single constraint (the egress
# gate) but runs only the ai-server suite. The SDK suite once sat at 6 failures while
# every ai-server run was green, because nothing ran it. A suite that is not run is not
# a control - the failure was real and nobody saw it.
#
# Checks run, in order:
#
#   1. scripts/test-ai-server.ps1 - the constraint gate: the full suite, the egress
#      suite with --require-egress-tests, and the mutation check. Delegated, so that the
#      constraint gate keeps its own identity and its own exit code.
#   2. aegis-sdk-python   - the SDK a third-party server would be built with.
#   3. room-server
#   4. browser-server
#
# Counts are deliberately not listed here: a count in a comment is a claim that rots. These
# suites are checked by exit code only. Expected totals live in PROJECT_STATUS_REVIEW.md and
# in the aegis-verify-and-test skill.
#
# web-ui (vitest / playwright) is deliberately NOT included: it needs a node toolchain
# and, for playwright, browser binaries plus a dev server. Run those separately.
#
# Usage:
#   .\scripts\test-all-suites.ps1
#   .\scripts\test-all-suites.ps1 -SkipAiServer     # only the three small suites
#   .\scripts\test-all-suites.ps1 -SkipMutation     # forwarded to the constraint gate
#
# If your shell blocks script execution (the default on many Windows installs), run it
# through a bypass:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-all-suites.ps1

param(
    [switch]$SkipAiServer,
    [switch]$SkipMutation
)

$ErrorActionPreference = "Continue"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Python not found at $Python" -ForegroundColor Red
    Write-Host "Create the venv first (see ai-server/README or docs/)." -ForegroundColor Red
    exit 1
}

# The WorkBuddy safe-delete shim turns Path.unlink() into SystemExit(1) during pytest
# teardown. Disable it for test runs.
$env:CODEBUDDY_SAFE_DELETE_ENABLED = "0"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AEGIS all-suite run" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$failed = @()

# ── The verdict carries its denominator ──────────────────────────────────────
# `-SkipAiServer` runs 3 of the 4 checks, and a bare "ALL CHECKS PASSED" is the *same
# string* a full run prints -- so a reduced run cannot be told from a complete one by
# reading the last line, which is the line CI and the run records actually quote. `$ran`
# and `$skipped` are counted (each check appends its own name), never inferred, and the
# census is reconciled before the verdict is printed: a future edit that adds a check
# without touching `$checksTotal` says so instead of printing a denominator it made up.
# `-SkipMutation` is forwarded into the delegated gate, where it reduces the gate's own
# census from 4 to 3; that is a *second* reduction the outer verdict must not hide, so it
# is named in the verdict even though it is not one of this script's own four checks.
$checksTotal = 4
$ran = @()
$skipped = @()

# -- 1. The constraint gate (delegated) --------------------------------------
if ($SkipAiServer) {
    Write-Host ""
    Write-Host "[1/4] ai-server constraint gate ... SKIPPED (-SkipAiServer)" -ForegroundColor Yellow
    $skipped += "ai-server constraint gate"
} else {
    Write-Host ""
    Write-Host "[1/4] ai-server constraint gate ..." -ForegroundColor Green
    $GateScript = Join-Path $PSScriptRoot "test-ai-server.ps1"
    $GateArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $GateScript)
    if ($SkipMutation) { $GateArgs += "-SkipMutation" }
    # A separate process, so that the gate's own `exit 1` cannot end this script.
    & powershell @GateArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [FAIL] ai-server constraint gate exited $LASTEXITCODE" -ForegroundColor Red
        $failed += "ai-server constraint gate"
    } else {
        Write-Host "  [PASS] ai-server constraint gate" -ForegroundColor Green
    }
    $ran += "ai-server constraint gate"
}

# -- 2..4. The suites that used to be nobody's job ---------------------------
# The exit code travels in a script-scoped variable rather than as the function's
# return value, so that the caller cannot accidentally capture pytest's stdout together
# with the boolean.
$script:SuiteExitCode = 0

function Invoke-PythonSuite {
    param(
        [string]$RelativeDir,
        [string]$RelativePythonPath
    )
    Push-Location (Join-Path $RepoRoot $RelativeDir)
    $PreviousPythonPath = $env:PYTHONPATH
    $env:PYTHONPATH = $RelativePythonPath
    & $Python -m pytest -q -p no:cacheprovider
    $script:SuiteExitCode = $LASTEXITCODE
    $env:PYTHONPATH = $PreviousPythonPath
    Pop-Location
}

$Suites = @(
    @{ Label = "aegis-sdk-python"; Dir = "packages\aegis-sdk-python"; Path = "..\..\ai-server\src"; Step = "[2/4]" },
    @{ Label = "room-server";      Dir = "room-server";                Path = "src";                  Step = "[3/4]" },
    @{ Label = "browser-server";   Dir = "browser-server";             Path = "src";                  Step = "[4/4]" }
)

foreach ($Suite in $Suites) {
    Write-Host ""
    Write-Host "$($Suite.Step) $($Suite.Label) suite ..." -ForegroundColor Green
    Invoke-PythonSuite -RelativeDir $Suite.Dir -RelativePythonPath $Suite.Path
    if ($script:SuiteExitCode -eq 0) {
        Write-Host "  [PASS] $($Suite.Label)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $($Suite.Label) exited $script:SuiteExitCode" -ForegroundColor Red
        $failed += $Suite.Label
    }
    $ran += $Suite.Label
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
$checksAccounted = $ran.Count + $skipped.Count
if ($checksAccounted -ne $checksTotal) {
    Write-Host "  CENSUS MISMATCH: $checksAccounted of $checksTotal checks accounted for" -ForegroundColor Red
    Write-Host "  ran: $($ran -join ', ')" -ForegroundColor Red
    Write-Host "  skipped: $($skipped -join ', ')" -ForegroundColor Red
    Write-Host '  A check was added or removed without updating $checksTotal.' -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Cyan
    exit 1
}
# A reduced run must not print the same last line a complete run prints: the verdict is
# the line CI and the run records quote, so the denominator goes into it, and any reason
# the run is reduced is named beside it. The numerator is the checks that *ran*, not the
# checks accounted for -- "4/4 PASSED (1 skipped)" would contradict itself.
$reduction = @()
if ($skipped.Count -gt 0) { $reduction += "skipped: $($skipped -join ', ')" }
if ($SkipMutation -and -not $SkipAiServer) { $reduction += "gate ran with -SkipMutation" }
if ($failed.Count -eq 0) {
    if ($reduction.Count -gt 0) {
        Write-Host "  ALL $($ran.Count)/$checksTotal CHECKS PASSED ($($reduction -join '; '))" -ForegroundColor Yellow
    } else {
        Write-Host "  ALL $($ran.Count)/$checksTotal CHECKS PASSED" -ForegroundColor Green
    }
    Write-Host "============================================================" -ForegroundColor Cyan
    exit 0
}

Write-Host "  FAILED: $($failed -join ', ') ($($ran.Count)/$checksTotal checks ran)" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Cyan
exit 1
