# test-beta-real.ps1 - Test AEGIS Beta real integration

param(
    [string]$PcHost = "localhost",
    [int]$PcPort = 50052,
    [string]$AiHost = "localhost",
    [int]$AiPort = 50051,
    [int]$BrowserPort = 50053,
    [switch]$SkipBrowser
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "AEGIS Beta - Real Integration Test" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

function Test-TcpConnection($HostName, $Port, $Name) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect($HostName, $Port)
        $tcp.Close()
        Write-Host "  [PASS] $Name ($HostName`:$Port)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  [FAIL] $Name ($HostName`:$Port)" -ForegroundColor Red
        return $false
    }
}

function Send-TcpCommand($HostName, $Port, $Command) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect($HostName, $Port)
        $stream = $tcp.GetStream()
        $writer = New-Object System.IO.StreamWriter($stream)
        $reader = New-Object System.IO.StreamReader($stream)
        $writer.WriteLine($Command)
        $writer.Flush()
        $stream.ReadTimeout = 10000
        $response = $reader.ReadLine()
        $tcp.Close()
        return $response
    } catch {
        return $null
    }
}

# Test 1: AI Server
Write-Host "[1/7] AI Server health..." -ForegroundColor Green
if (Test-TcpConnection $AiHost $AiPort "AI Server") { $passed++ } else { $failed++ }

# Test 2: Browser Server
Write-Host "[2/7] Browser Server health..." -ForegroundColor Green
if (Test-TcpConnection $AiHost $BrowserPort "Browser Server") { $passed++ } else { $failed++ }

# Test 3: PC Server
Write-Host "[3/7] PC Server health..." -ForegroundColor Green
if (Test-TcpConnection $PcHost $PcPort "PC Server") { $passed++ } else { $failed++ }

# Test 4: PC Server health check
Write-Host "[4/7] PC Server health check..." -ForegroundColor Green
$health = Send-TcpCommand $PcHost $PcPort "health"
if ($health) {
    Write-Host "  [PASS] Health response received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No health response" -ForegroundColor Red
    $failed++
}

# Test 5: PC Server screenshot
Write-Host "[5/7] PC Server screenshot..." -ForegroundColor Green
$screenshot = Send-TcpCommand $PcHost $PcPort "screenshot"
if ($screenshot) {
    Write-Host "  [PASS] Screenshot received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No screenshot response" -ForegroundColor Red
    $failed++
}

# Test 6: PC Server active window
Write-Host "[6/7] PC Server active window..." -ForegroundColor Green
$window = Send-TcpCommand $PcHost $PcPort "active_window"
if ($window) {
    Write-Host "  [PASS] Active window received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No active window response" -ForegroundColor Red
    $failed++
}

# Test 7: Browser Server check
if (-not $SkipBrowser) {
    Write-Host "[7/7] Browser Server check..." -ForegroundColor Green
    $browserHealth = Send-TcpCommand $AiHost $BrowserPort "health"
    if ($browserHealth) {
        Write-Host "  [PASS] Browser Server responded" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "  [INFO] Browser Server not responding" -ForegroundColor Yellow
    }
} else {
    Write-Host "[7/7] Browser Server skipped" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "  Results: $passed passed, $failed failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

if ($failed -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed." -ForegroundColor Yellow
}

exit $failed
