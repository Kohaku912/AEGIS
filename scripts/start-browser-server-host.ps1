# start-browser-server-host.ps1 - Start Browser Server on Windows host
#
# Usage:
#   .\scripts\start-browser-server-host.ps1
#   .\scripts\start-browser-server-host.ps1 -Port 50053
#   .\scripts\start-browser-server-host.ps1 -InstallDeps

param(
    [int]$Port = 50053,
    [string]$Bind = "0.0.0.0",
    [switch]$InstallDeps
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot\.."
$serverRoot = Join-Path $repoRoot "browser-server"
$venvPython = Join-Path $serverRoot ".venv\Scripts\python.exe"
$logOut = Join-Path $serverRoot "startup_browser.out.log"
$logErr = Join-Path $serverRoot "startup_browser.err.log"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS Browser Server - Windows Host" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $serverRoot

if (-not (Test-Path $venvPython)) {
    Write-Host "[1/5] Creating browser-server .venv..." -ForegroundColor Green
    python -m venv .venv
} else {
    Write-Host "[1/5] .venv exists" -ForegroundColor Gray
}

if ($InstallDeps) {
    Write-Host "[2/5] Installing dependencies..." -ForegroundColor Green
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -e . pytest
    & $venvPython -m playwright install chromium
} else {
    Write-Host "[2/5] Skipping dependency install (use -InstallDeps to refresh)" -ForegroundColor Gray
}

Write-Host "[3/5] Checking dependency health..." -ForegroundColor Green
$env:PYTHONPATH = "src"
$health = & $venvPython -c "from aegis_browser.main import get_runtime_health; import json; print(json.dumps(get_runtime_health(), ensure_ascii=False))"
Write-Host "  $health" -ForegroundColor Gray

Write-Host "[4/5] Checking port $Port..." -ForegroundColor Green
$portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[ERROR] Port $Port is already in use by PID $($portInUse.OwningProcess)" -ForegroundColor Red
    exit 1
}

Write-Host "[5/5] Starting browser-server..." -ForegroundColor Green
$env:AEGIS_GRPC_PORT = "$Port"
$env:AEGIS_GRPC_HOST = "$Bind"
Start-Process -FilePath $venvPython `
    -ArgumentList "-m aegis_browser.main" `
    -WorkingDirectory $serverRoot `
    -RedirectStandardOutput $logOut `
    -RedirectStandardError $logErr `
    -WindowStyle Hidden

Start-Sleep -Seconds 3
$started = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $started) {
    Write-Host "[ERROR] Browser Server did not start. See $logErr" -ForegroundColor Red
    exit 1
}

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 5
    Write-Host "  Health: $($response.status) / mode=$($response.mode)" -ForegroundColor Gray
} catch {
    Write-Host "[WARN] Server is listening but /health failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Browser Server started on $Bind`:$Port" -ForegroundColor Green
