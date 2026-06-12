# start-pc-server-host.ps1 — Start PC Server on Windows host
#
# Usage:
#   .\scripts\start-pc-server-host.ps1
#   .\scripts\start-pc-server-host.ps1 -Port 50052
#   .\scripts\start-pc-server-host.ps1 -Bind "127.0.0.1"

param(
    [int]$Port = 50052,
    [string]$Bind = "0.0.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS PC Server — Windows Host" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if pc-server is already running
$existing = Get-Process -Name "aegis-pc-server" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[WARN] PC Server already running (PID: $($existing.Id))" -ForegroundColor Yellow
    $confirm = Read-Host "Kill existing process? (y/N)"
    if ($confirm -eq "y") {
        Stop-Process -Id $existing.Id -Force
        Start-Sleep -Seconds 1
    } else {
        Write-Host "Aborted."
        exit 0
    }
}

# Build pc-server
Write-Host "[1/3] Building pc-server..." -ForegroundColor Green
Set-Location "$PSScriptRoot\..\pc-server"
cargo build --release 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  Build OK" -ForegroundColor Gray

# Check port availability
Write-Host "[2/3] Checking port $Port..." -ForegroundColor Green
$portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[ERROR] Port $Port is already in use!" -ForegroundColor Red
    Write-Host "  PID: $($portInUse.OwningProcess)" -ForegroundColor Gray
    exit 1
}
Write-Host "  Port $Port available" -ForegroundColor Gray

# Start pc-server
Write-Host "[3/3] Starting pc-server..." -ForegroundColor Green
Write-Host ""
Write-Host "  Bind:    $Bind`:$Port" -ForegroundColor White
Write-Host "  Health:  $Bind`:$Port (send 'health')" -ForegroundColor White
Write-Host ""
Write-Host "  Docker connection:" -ForegroundColor Yellow
Write-Host "    host.docker.internal:$Port" -ForegroundColor White
Write-Host ""
Write-Host "  Firewall note:" -ForegroundColor Yellow
Write-Host "    If Docker cannot connect, run as Admin:" -ForegroundColor Gray
Write-Host "    New-NetFirewallRule -DisplayName 'AEGIS PC Server' `"
Write-Host "      -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Run pc-server
$releasePath = "$PSScriptRoot\..\pc-server\target\release\aegis-pc-server.exe"
if (Test-Path $releasePath) {
    & $releasePath --port $Port --bind $Bind
} else {
    # Fallback to debug build
    $debugPath = "$PSScriptRoot\..\pc-server\target\debug\aegis-pc-server.exe"
    if (Test-Path $debugPath) {
        & $debugPath --port $Port --bind $Bind
    } else {
        Write-Host "[ERROR] pc-server binary not found. Run 'cargo build' in pc-server/" -ForegroundColor Red
        exit 1
    }
}
