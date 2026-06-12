# test-pc-host.ps1 - Test PC Server on Windows host

param(
    [string]$PcHost = "localhost",
    [int]$PcPort = 50052
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "AEGIS PC Server - Host Test" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

function Send-PcCommand($HostName, $Port, $Command) {
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

# Test 1: Health
Write-Host "[1/8] Health check..." -ForegroundColor Green
$health = Send-PcCommand $PcHost $PcPort "health"
if ($health) {
    Write-Host "  [PASS] Health: OK" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No health response" -ForegroundColor Red
    $failed++
}

# Test 2: OS Info
Write-Host "[2/8] OS Info..." -ForegroundColor Green
$osInfo = Send-PcCommand $PcHost $PcPort "os_info"
if ($osInfo) {
    Write-Host "  [PASS] OS Info received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No OS info" -ForegroundColor Red
    $failed++
}

# Test 3: Screen Size
Write-Host "[3/8] Screen size..." -ForegroundColor Green
$screenSize = Send-PcCommand $PcHost $PcPort "screen_size"
if ($screenSize) {
    Write-Host "  [PASS] Screen size received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No screen size" -ForegroundColor Red
    $failed++
}

# Test 4: Screenshot
Write-Host "[4/8] Screenshot..." -ForegroundColor Green
$screenshot = Send-PcCommand $PcHost $PcPort "screenshot"
if ($screenshot) {
    Write-Host "  [PASS] Screenshot received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No screenshot" -ForegroundColor Red
    $failed++
}

# Test 5: Active Window
Write-Host "[5/8] Active window..." -ForegroundColor Green
$activeWindow = Send-PcCommand $PcHost $PcPort "active_window"
if ($activeWindow) {
    Write-Host "  [PASS] Active window received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No active window" -ForegroundColor Red
    $failed++
}

# Test 6: Window List
Write-Host "[6/8] Window list..." -ForegroundColor Green
$windows = Send-PcCommand $PcHost $PcPort "windows"
if ($windows) {
    Write-Host "  [PASS] Window list received" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No window list" -ForegroundColor Red
    $failed++
}

# Test 7: Show Overlay
Write-Host "[7/8] Show overlay..." -ForegroundColor Green
$overlay = Send-PcCommand $PcHost $PcPort "show_overlay AEGIS Test"
if ($overlay) {
    Write-Host "  [PASS] Overlay shown" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No overlay response" -ForegroundColor Red
    $failed++
}

# Test 8: Mouse Click (approval required)
Write-Host "[8/8] Mouse click (approval required)..." -ForegroundColor Green
$click = Send-PcCommand $PcHost $PcPort "mouse_click"
if ($click -and $click -match "approval_required") {
    Write-Host "  [PASS] Approval required returned" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  [FAIL] No approval response" -ForegroundColor Red
    $failed++
}

# Summary
Write-Host ""
Write-Host "===========================" -ForegroundColor Cyan
Write-Host "  Results: $passed passed, $failed failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""

exit $failed
