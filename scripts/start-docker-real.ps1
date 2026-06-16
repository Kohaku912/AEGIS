# start-docker-real.ps1 — Start Docker services for real integration testing
#
# Usage:
#   .\scripts\start-docker-real.ps1
#   .\scripts\start-docker-real.ps1 -Profile "real-browser"

param(
    [string]$Profile = "pc-host",
    [switch]$RealBrowser,
    [switch]$FullLocal
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS Docker — Real Integration" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Determine profiles
$profiles = @($Profile)
if ($RealBrowser) { $profiles += "real-browser" }
if ($FullLocal) { $profiles += "full-local" }

$profileArgs = ($profiles | ForEach-Object { "--profile $_" }) -join " "

# Check .env
if (-not (Test-Path "$PSScriptRoot\..\.env")) {
    Write-Host "[WARN] .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\..\.env.example" "$PSScriptRoot\..\.env"
    Write-Host "  Please edit .env with your API key before continuing." -ForegroundColor Yellow
    Write-Host "  Then run this script again." -ForegroundColor Yellow
    exit 1
}

# Check Docker
Write-Host "[1/4] Checking Docker..." -ForegroundColor Green
try {
    docker version | Out-Null
    Write-Host "  Docker OK" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Docker is not running!" -ForegroundColor Red
    exit 1
}

# Check host.docker.internal connectivity
Write-Host "[2/4] Checking host.docker.internal..." -ForegroundColor Green
$pcPort = if ($env:PC_SERVER_PORT) { $env:PC_SERVER_PORT } else { "50052" }
Write-Host "  PC Server expected at host.docker.internal:$pcPort" -ForegroundColor Gray
Write-Host "  (Start pc-server separately with start-pc-server-host.ps1)" -ForegroundColor Gray

# Build images
Write-Host "[3/4] Building Docker images..." -ForegroundColor Green
Set-Location "$PSScriptRoot\.."
Invoke-Expression "docker compose $profileArgs build 2>&1" | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

# Start services
Write-Host "[4/4] Starting services..." -ForegroundColor Green
Write-Host ""
Write-Host "  Profiles: $($profiles -join ', ')" -ForegroundColor White
Write-Host ""
Write-Host "  Services:" -ForegroundColor White
Write-Host "    AI Server:      http://0.0.0.0:8090 (Dashboard)" -ForegroundColor White
Write-Host "    AI Server:      http://0.0.0.0:8091 (Web Chat)" -ForegroundColor White
Write-Host "    Browser Server: http://0.0.0.0:50053" -ForegroundColor White
Write-Host ""
Write-Host "  PC Server (external):" -ForegroundColor Yellow
Write-Host "    Start with: .\scripts\start-pc-server-host.ps1" -ForegroundColor White
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Invoke-Expression "docker compose $profileArgs up -d"
