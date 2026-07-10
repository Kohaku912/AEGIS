# test-real-integration.ps1 — Test real integration between Docker and Windows host
#
# Usage:
#   .\scripts\test-real-integration.ps1
#   .\scripts\test-real-integration.ps1 -PcHost "192.168.1.100"

param(
    [string]$PcHost = "localhost",
    [int]$PcPort = 50052,
    [string]$AiHost = "localhost",
    [int]$AiPort = 50051,
    [int]$BrowserPort = 50053
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AEGIS Real Integration Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

function Test-TcpConnection {
    param([string]$HostName, [int]$Port, [string]$Name)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect($HostName, $Port)
        $tcp.Close()
        Write-Host "  [PASS] $Name ($HostName`:$Port)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  [FAIL] $Name ($HostName`:$Port) - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Send-TcpCommand {
    param([string]$HostName, [int]$Port, [string]$Command)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect($HostName, $Port)
        $stream = $tcp.GetStream()
        $writer = New-Object System.IO.StreamWriter($stream)
        $reader = New-Object System.IO.StreamReader($stream)
        $writer.WriteLine($Command)
        $writer.Flush()
        $stream.ReadTimeout = 5000
        $response = $reader.ReadLine()
        $tcp.Close()
        return $response
    } catch {
        return $null
    }
}

# Test 1: AI Server health
Write-Host "[1/6] AI Server health..." -ForegroundColor Green
if (Test-TcpConnection $AiHost $AiPort "AI Server") { $passed++ } else { $failed++ }

# Test 2: Browser Server health
Write-Host "[2/6] Browser Server health..." -ForegroundColor Green
if (Test-TcpConnection $AiHost $BrowserPort "Browser Server") { $passed++ } else { $failed++ }

# Test 3: PC Server health
Write-Host "[3/6] PC Server health..." -ForegroundColor Green
if (Test-TcpConnection $PcHost $PcPort "PC Server") { $passed++ } else { $failed++ }

# Test 4: PC Server health check
Write-Host "[4/6] PC Server health check..." -ForegroundColor Green
$health = Send-TcpCommand $PcHost $PcPort "health"
if ($health) {
    Write-Host "  [PASS] Health response: $($health.Substring(0, [Math]::Min(80, $health.Length)))..." -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No health response" -ForegroundColor Red
    $failed++
}

# Test 5: PC Server screenshot
Write-Host "[5/6] PC Server screenshot..." -ForegroundColor Green
$screenshot = Send-TcpCommand $PcHost $PcPort "screenshot"
if ($screenshot) {
    Write-Host "  [PASS] Screenshot response received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No screenshot response" -ForegroundColor Red
    $failed++
}

# Test 6: PC Server active window
Write-Host "[6/6] PC Server active window..." -ForegroundColor Green
$window = Send-TcpCommand $PcHost $PcPort "active_window"
if ($window) {
    Write-Host "  [PASS] Active window: $($window.Substring(0, [Math]::Min(80, $window.Length)))..." -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No active window response" -ForegroundColor Red
    $failed++
}

# Summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Results: $passed passed, $failed failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($failed -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. Check that all services are running." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Start PC Server: .\scripts\start-pc-server-host.ps1" -ForegroundColor Gray
    Write-Host "  2. Start Docker:    .\scripts\start-docker-real.ps1" -ForegroundColor Gray
    Write-Host "  3. Check ports:     .\scripts\check-ports.ps1" -ForegroundColor Gray
}

exit $failed
