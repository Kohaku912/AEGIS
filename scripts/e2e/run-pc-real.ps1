param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$PcHost = "127.0.0.1",
    [int]$PcPort = 50052,
    [switch]$RealActions
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
foreach ($cmd in @("health", "screenshot", "active_window", "show_overlay AEGIS E2E")) {
    $cStart = Get-Date
    try {
        $response = Send-PcCommand $cmd
        if (-not $response) { throw "empty response" }
        $checks += @{ id = "pc_$($cmd.Split(' ')[0])"; name = "PC $cmd"; status = "pass"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @($response.Substring(0, [Math]::Min(120, $response.Length))); error = ""; report_path = "" }
    } catch {
        $checks += @{ id = "pc_$($cmd.Split(' ')[0])"; name = "PC $cmd"; status = "fail"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @(); error = $_.Exception.Message; report_path = "" }
    }
}
if ($RealActions -or $env:AEGIS_PC_REAL_ACTIONS_REQUIRED -eq "1") {
    foreach ($cmd in @("mouse_move 10 10", "press_hotkey ctrl+shift+f12")) {
        $cStart = Get-Date
        try {
            $response = Send-PcCommand $cmd
            if (-not $response -or $response -match "\[MOCK\]") { throw "real action did not execute as real output" }
            $checks += @{ id = "pc_real_action"; name = "PC real action $cmd"; status = "pass"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @($response); error = ""; report_path = "" }
        } catch {
            $checks += @{ id = "pc_real_action"; name = "PC real action $cmd"; status = "fail"; duration_ms = [int]((Get-Date)-$cStart).TotalMilliseconds; evidence = @(); error = $_.Exception.Message; report_path = "" }
        }
    }
}
$status = if (($checks | Where-Object { $_.status -ne "pass" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{ id = "pc_real"; name = "PC real observe/action"; status = $status; duration_ms = [int]((Get-Date)-$start).TotalMilliseconds; evidence = @("$ReportDir/pc-real.json"); error = ""; report_path = "$ReportDir/pc-real.json"; checks = $checks }
$result | ConvertTo-Json -Depth 10 | Set-Content "$ReportDir/pc-real.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
