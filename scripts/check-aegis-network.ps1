# check-aegis-network.ps1 — Check AEGIS network connectivity
#
# Usage:
#   .\scripts\check-aegis-network.ps1

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "AEGIS Network Check" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Docker:" -ForegroundColor Yellow
try {
    $dockerVersion = docker version --format '{{.Server.Version}}' 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Docker $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Docker not running" -ForegroundColor Red
    }
} catch {
    Write-Host "  [FAIL] Docker not available" -ForegroundColor Red
}

Write-Host ""

# Check Docker Compose
Write-Host "Docker Compose:" -ForegroundColor Yellow
try {
    $composeVersion = docker compose version --short 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Docker Compose $composeVersion" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Docker Compose not available" -ForegroundColor Red
    }
} catch {
    Write-Host "  [FAIL] Docker Compose not available" -ForegroundColor Red
}

Write-Host ""

# Check .env
Write-Host "Environment:" -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\..\.env") {
    Write-Host "  [OK] .env exists" -ForegroundColor Green
    $envContent = Get-Content "$PSScriptRoot\..\.env"
    $apiKey = $envContent | Where-Object { $_ -match "OPENAI_API_KEY=" }
    if ($apiKey -and $apiKey -notmatch "sk-your-") {
        Write-Host "  [OK] API key configured" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] API key not configured" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [WARN] .env not found (copy from .env.example)" -ForegroundColor Yellow
}

Write-Host ""

# Check ports
Write-Host "Ports:" -ForegroundColor Yellow
$ports = @(
    @{Port=50051; Name="AI Server"},
    @{Port=50052; Name="PC Server"},
    @{Port=50053; Name="Browser Server"},
    @{Port=8090;  Name="Dashboard"},
)

foreach ($p in $ports) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", $p.Port)
        $tcp.Close()
        Write-Host "  [OPEN]  $($p.Port) - $($p.Name)" -ForegroundColor Green
    } catch {
        Write-Host "  [----]  $($p.Port) - $($p.Name)" -ForegroundColor Gray
    }
}

Write-Host ""

# Check host.docker.internal
Write-Host "Docker Host Connectivity:" -ForegroundColor Yellow
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("host.docker.internal", 50052)
    $tcp.Close()
    Write-Host "  [OK] host.docker.internal:50052 reachable" -ForegroundColor Green
} catch {
    Write-Host "  [INFO] host.docker.internal:50052 not reachable (start PC Server)" -ForegroundColor Gray
}

Write-Host ""
