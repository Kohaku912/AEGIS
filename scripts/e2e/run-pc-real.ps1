param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$PcHost = "127.0.0.1",
    [int]$PcPort = 50052,
    [switch]$RealActions,
    [switch]$InstallService,
    [switch]$UninstallAfter,
    [string]$ServiceInstallDir = "$env:ProgramFiles\AEGIS\pc-server",
    [string]$Bind = "127.0.0.1",
    [string]$AllowedRemoteAddress = ""
)
$ErrorActionPreference = "Continue"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
function Send-PcCommand([string]$Command) {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.ReceiveTimeout = 8000
    $tcp.Connect($PcHost, $PcPort)
    $stream = $tcp.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $reader = New-Object System.IO.StreamReader($stream)
    $writer.WriteLine($Command); $writer.Flush()
    $line = $reader.ReadLine()
    $tcp.Close()
    return $line
}
$checks = @()
function Add-Check($Id, $Name, $Status, $Evidence, $ErrorMessage = "", $StartedAt = $null) {
    $duration = 0
    if ($StartedAt) { $duration = [int]((Get-Date)-$StartedAt).TotalMilliseconds }
    $script:checks += @{ id = $Id; name = $Name; status = $Status; duration_ms = $duration; evidence = @($Evidence); error = $ErrorMessage; report_path = "" }
}

if ($InstallService) {
    $svcStart = Get-Date
    try {
        $args = @("-ExecutionPolicy", "Bypass", "-File", "scripts/pc/install-service.ps1", "-InstallDir", $ServiceInstallDir, "-Port", "$PcPort", "-Bind", $Bind)
        if ($AllowedRemoteAddress) { $args += @("-AllowedRemoteAddress", $AllowedRemoteAddress) }
        if ($RealActions -or $env:AEGIS_PC_REAL_ACTIONS_REQUIRED -eq "1") { $args += "-EnableRealPcActions" }
        $output = & powershell.exe @args 2>&1
        $output | Set-Content "$ReportDir/pc-service-install.log" -Encoding utf8
        Start-Sleep -Seconds 3
        $svc = Get-Service AegisPcServer -ErrorAction Stop
        if ($svc.Status -ne "Running") { throw "service status is $($svc.Status)" }
        Add-Check "pc_service_install_start" "PC service install and start" "pass" "$ReportDir/pc-service-install.log" "" $svcStart
    } catch {
        Add-Check "pc_service_install_start" "PC service install and start" "fail" "$ReportDir/pc-service-install.log" $_.Exception.Message $svcStart
    }
}

foreach ($cmd in @("health", "screenshot", "active_window", "show_overlay AEGIS E2E")) {
    $cStart = Get-Date
    try {
        $response = Send-PcCommand $cmd
        if (-not $response) { throw "empty response" }
        Add-Check "pc_$($cmd.Split(' ')[0])" "PC $cmd" "pass" $response.Substring(0, [Math]::Min(120, $response.Length)) "" $cStart
    } catch {
        Add-Check "pc_$($cmd.Split(' ')[0])" "PC $cmd" "fail" "" $_.Exception.Message $cStart
    }
}
if ($RealActions -or $env:AEGIS_PC_REAL_ACTIONS_REQUIRED -eq "1") {
    foreach ($cmd in @("mouse_move 10 10", "press_hotkey ctrl+shift+f12")) {
        $cStart = Get-Date
        try {
            $response = Send-PcCommand $cmd
            if (-not $response -or $response -match "\[MOCK\]") { throw "real action did not execute as real output" }
            Add-Check "pc_real_action" "PC real action $cmd" "pass" $response "" $cStart
        } catch {
            Add-Check "pc_real_action" "PC real action $cmd" "fail" "" $_.Exception.Message $cStart
        }
    }
}
if ($InstallService) {
    $restartStart = Get-Date
    try {
        Restart-Service AegisPcServer -Force -ErrorAction Stop
        Start-Sleep -Seconds 3
        $response = Send-PcCommand "health"
        if (-not $response) { throw "empty health response after restart" }
        Add-Check "pc_service_restart" "PC service restart and health" "pass" $response "" $restartStart
    } catch {
        Add-Check "pc_service_restart" "PC service restart and health" "fail" "" $_.Exception.Message $restartStart
    }
}

$logDir = "$env:ProgramData\AEGIS\pc-server\logs"
if (Test-Path $logDir) {
    Get-ChildItem $logDir -File -ErrorAction SilentlyContinue | Select-Object Name, Length, LastWriteTime |
        ConvertTo-Json -Depth 4 | Set-Content "$ReportDir/pc-service-logs.json" -Encoding utf8
    Add-Check "pc_service_logs" "PC service log directory recorded" "pass" "$ReportDir/pc-service-logs.json"
} else {
    Add-Check "pc_service_logs" "PC service log directory recorded" $(if ($InstallService) { "fail" } else { "warn" }) $logDir "Log directory not found"
}

if ($InstallService -and $UninstallAfter) {
    $uninstallStart = Get-Date
    try {
        $output = & powershell.exe -ExecutionPolicy Bypass -File scripts/pc/uninstall-service.ps1 -InstallDir $ServiceInstallDir 2>&1
        $output | Set-Content "$ReportDir/pc-service-uninstall.log" -Encoding utf8
        if (Get-Service AegisPcServer -ErrorAction SilentlyContinue) { throw "service still exists after uninstall" }
        Add-Check "pc_service_uninstall" "PC service uninstall" "pass" "$ReportDir/pc-service-uninstall.log" "" $uninstallStart
    } catch {
        Add-Check "pc_service_uninstall" "PC service uninstall" "fail" "$ReportDir/pc-service-uninstall.log" $_.Exception.Message $uninstallStart
    }
}
$status = if (($checks | Where-Object { $_.status -eq "fail" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{
    id = "pc_real"
    name = "PC service observe/action"
    status = $status
    duration_ms = [int]((Get-Date)-$start).TotalMilliseconds
    evidence = @("$ReportDir/pc-real.json", "$ReportDir/pc-service-logs.json")
    error = ""
    report_path = "$ReportDir/pc-real.json"
    service_install_tested = [bool]$InstallService
    real_actions_tested = [bool]($RealActions -or $env:AEGIS_PC_REAL_ACTIONS_REQUIRED -eq "1")
    bind = $Bind
    allowed_remote_address = $AllowedRemoteAddress
    log_dir = $logDir
    reboot_autostart_manual_check = "After install, reboot Windows and verify Get-Service AegisPcServer is Running, then run this script without -InstallService."
    installer_next_step = "NSIS is the default consumer installer path; MSI/WiX remains the enterprise packaging candidate."
    checks = $checks
}
$result | ConvertTo-Json -Depth 10 | Set-Content "$ReportDir/pc-real.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
