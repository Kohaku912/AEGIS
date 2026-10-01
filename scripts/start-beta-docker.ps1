# start-beta-docker.ps1 - Start AEGIS Docker services
#
# Usage:
#   .\scripts\start-beta-docker.ps1
#   .\scripts\start-beta-docker.ps1 -Build
#
# Note: dev-server was deleted in Phase 9 and is not part of this topology. It used to be
# passed to `docker compose build/up` here, which made every invocation fail with
# "no such service: dev-server".

param(
    [switch]$Build,
    [switch]$Logs
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS Docker Environment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "$PSScriptRoot\..\.env")) {
    Write-Host "[WARN] .env not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\..\.env.example" "$PSScriptRoot\..\.env"
    Write-Host "  Edit .env with your API key, then run again." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/3] Checking Docker..." -ForegroundColor Green
docker version | Out-Null
Write-Host "  Docker OK" -ForegroundColor Gray

Set-Location "$PSScriptRoot\.."

if ($Build) {
    Write-Host "[2/3] Building images..." -ForegroundColor Green
    docker compose build ai-server browser-server room-server 2>&1 |
        ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "[2/3] Skipping build (use -Build to build)" -ForegroundColor Gray
}

Write-Host "[3/3] Starting services..." -ForegroundColor Green
docker compose up -d ai-server browser-server room-server

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS Docker Started" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  AI Dashboard:   http://0.0.0.0:8090" -ForegroundColor White
Write-Host "  AI Chat:        http://0.0.0.0:8090/chat" -ForegroundColor White
Write-Host "  AI gRPC:        0.0.0.0:50051" -ForegroundColor White
Write-Host "  Browser Server: http://0.0.0.0:50053" -ForegroundColor White
Write-Host "  Room Server:    gRPC 0.0.0.0:50055" -ForegroundColor White
Write-Host ""
Write-Host "  PC Server remains host-native: host.docker.internal:50052" -ForegroundColor Yellow
Write-Host ""

if ($Logs) {
    docker compose logs -f ai-server browser-server room-server
}
