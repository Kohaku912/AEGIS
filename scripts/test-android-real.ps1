param(
    [string]$HostAddress = "192.168.50.175",
    [int]$Port = 50051,
    [switch]$TryUsbReverse,
    [string]$TailscaleHost = "",
    [string]$ReportDir = "data/reports/e2e/latest",
    [switch]$RequireOnline
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$start = Get-Date
$checks = @()

function Add-Check($Id, $Name, $Status, $Evidence, $ErrorMessage = "") {
    $script:checks += @{
        id = $Id
        name = $Name
        status = $Status
        duration_ms = 0
        evidence = @($Evidence)
        error = $ErrorMessage
        report_path = ""
    }
}

function Get-NetworkType {
    try {
        $wifi = adb shell dumpsys wifi | Select-String -Pattern "Wi-Fi is|mNetworkInfo|Supplicant state" | Select-Object -First 5
        $telephony = adb shell dumpsys telephony.registry | Select-String -Pattern "mServiceState|mDataConnectionState|mSignalStrength" | Select-Object -First 5
        return @{ wifi = ($wifi -join "`n"); telephony = ($telephony -join "`n") }
    } catch {
        return @{ error = $_.Exception.Message }
    }
}

Write-Host "== ADB device =="
adb devices -l
Add-Check "adb_device" "ADB device visible" "pass" "adb devices -l"

Write-Host "`n== Installed AEGIS app =="
adb shell pm list packages | Select-String -Pattern "aegis" -CaseSensitive:$false
Add-Check "android_app_installed" "AEGIS app installed" "pass" "pm list packages"

if ($TryUsbReverse) {
    Write-Host "`n== USB reverse =="
    adb reverse tcp:$Port tcp:$Port
    adb reverse --list
    $HostAddress = "127.0.0.1"
}
if ($TailscaleHost) {
    $HostAddress = $TailscaleHost
}
$network = Get-NetworkType
$network | ConvertTo-Json -Depth 6 | Set-Content "$ReportDir/android-network.json" -Encoding utf8

Write-Host "`n== Launch Android app =="
adb shell am force-stop com.aegis.android
adb shell am start -n com.aegis.android/.MainActivity --es host $HostAddress --ei port $Port --ez auto_connect true

Write-Host "`n== Poll Android status =="
$online = $false
$lastStatus = ""
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 3
    $status = curl.exe -s http://127.0.0.1:8090/api/android/status
    $lastStatus = $status
    Write-Host $status
    if ($status -match '"online"\s*:\s*true') {
        $online = $true
        break
    }
}
Set-Content "$ReportDir/android-status.json" -Value $lastStatus -Encoding utf8
if ($online) {
    Add-Check "android_online" "Android Dashboard online" "pass" "$ReportDir/android-status.json"
} else {
    Add-Check "android_online" "Android Dashboard online" $(if ($RequireOnline) { "fail" } else { "warn" }) "$ReportDir/android-status.json" "Android did not become online"
}

$summary = @{
    id = "android_real"
    name = "Android real connectivity"
    status = $(if (($checks | Where-Object { $_.status -eq "fail" }).Count -eq 0) { "pass" } else { "fail" })
    duration_ms = [int]((Get-Date) - $start).TotalMilliseconds
    evidence = @("$ReportDir/android-status.json", "$ReportDir/android-network.json")
    error = ""
    report_path = "$ReportDir/android-real.json"
    host = $HostAddress
    port = $Port
    usb_reverse = [bool]$TryUsbReverse
    tailscale = [bool]$TailscaleHost
    reconnect_count = $null
    heartbeat_failure_count = $null
    checks = $checks
}
$summary | ConvertTo-Json -Depth 10 | Set-Content "$ReportDir/android-real.json" -Encoding utf8

Write-Host "`nRun local pytest with:"
Write-Host "cd ai-server; `$env:AEGIS_ANDROID_LOCAL='1'; `$env:AEGIS_ANDROID_TEST_HOST='$HostAddress'; uv run pytest -m android_local -q"

if ($summary.status -eq "pass") { exit 0 } else { exit 1 }
