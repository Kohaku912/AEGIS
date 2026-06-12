# start-beta-docker.ps1 — Start AEGIS Beta Docker environment
#
# Usage:
#   .\scripts\start-beta-docker.ps1
#   .\scripts\start-beta-docker.ps1 -Build

param(
    [switch]$Build,
    [switch]$Logs
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS Beta — Docker Environment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check .env
if (-not (Test-Path "$PSScriptRoot\..\.env")) {
    Write-Host "[WARN] .env not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\..\.env.example" "$PSScriptRoot\..\.env"
    Write-Host "  Edit .env with your API key, then run again." -ForegroundColor Yellow
    exit 1
}

# Check Docker
Write-Host "[1/3] Checking Docker..." -ForegroundColor Green
try {
    docker version | Out-Null
    Write-Host "  Docker OK" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Docker is not running!" -ForegroundColor Red
    exit 1
}

# Build if requested
if ($Build) {
    Write-Host "[2/3] Building images..." -ForegroundColor Green
    Set-Location "$PSScriptRoot\.."
    docker compose --profile beta build 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "[2/3] Skipping build (use -Build to build)" -ForegroundColor Gray
}

# Start services
Write-Host "[3/3] Starting Beta services..." -ForegroundColor Green
Set-Location "$PSScriptRoot\.."
docker compose --profile beta up -d

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS Beta Started" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Services:" -ForegroundColor White
Write-Host "    AI Server:      http://127.0.0.1:8090 (Dashboard)" -ForegroundColor White
Write-Host "    AI Server:      http://127.0.0.1:8091 (Web Chat)" -ForegroundColor White
Write-Host "    Browser Server: http://127.0.0.1:50053" -ForegroundColor White
Write-Host ""
Write-Host "  PC Server (external):" -ForegroundColor Yellow
Write-Host "    Start with: .\scripts\start-pc-server-host.ps1" -ForegroundColor White
Write-Host ""
Write-Host "  Test:" -ForegroundColor Yellow
Write-Host "    .\scripts\test-beta-real.ps1" -ForegroundColor White
Write-Host ""

if ($Logs) {
    docker compose --profile beta logs -f
}
