# start-docker-real.ps1 - Build and start AEGIS Docker services
#
# Usage:
#   .\scripts\start-docker-real.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS Docker - Real Integration" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "$PSScriptRoot\..\.env")) {
    Write-Host "[WARN] .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\..\.env.example" "$PSScriptRoot\..\.env"
    Write-Host "  Please edit .env with your API key before continuing." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/4] Checking Docker..." -ForegroundColor Green
docker version | Out-Null
Write-Host "  Docker OK" -ForegroundColor Gray

Write-Host "[2/4] Checking host-native PC server target..." -ForegroundColor Green
$pcPort = if ($env:PC_SERVER_PORT) { $env:PC_SERVER_PORT } else { "50052" }
Write-Host "  PC Server expected at host.docker.internal:$pcPort" -ForegroundColor Gray

Set-Location "$PSScriptRoot\.."

Write-Host "[3/4] Building Docker images..." -ForegroundColor Green
docker compose build ai-server browser-server room-server dev-server 2>&1 |
    ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host "[4/4] Starting services..." -ForegroundColor Green
docker compose up -d ai-server browser-server room-server dev-server

Write-Host ""
Write-Host "  AI Dashboard:   http://0.0.0.0:8090" -ForegroundColor White
Write-Host "  AI Web Chat:    http://0.0.0.0:8091" -ForegroundColor White
Write-Host "  AI gRPC:        0.0.0.0:50051" -ForegroundColor White
Write-Host "  Browser Server: http://0.0.0.0:50053" -ForegroundColor White
Write-Host "  Room Server:    gRPC 0.0.0.0:50055" -ForegroundColor White
Write-Host "  Dev Server:     gRPC 0.0.0.0:50056" -ForegroundColor White
Write-Host ""
