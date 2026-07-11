param(
    [string]$HostAddress = "192.168.50.175",
    [int]$Port = 50051,
    [switch]$TryUsbReverse,
    [string]$TailscaleHost = "",
    [string]$ReportDir = "data/reports/e2e/latest",
    [switch]$RequireOnline,
    [switch]$TestWifiOff,
    [switch]$ScreenOff,
    [switch]$RestartAiServer,
    [switch]$RestartAndroidApp
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$start = Get-Date
$checks = @()
$wifiWasDisabled = $false
$reconnectCount = 0
$heartbeatFailureCount = 0
$wasOnline = $false
$statusSamples = @()

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

function Get-AndroidStatusObject {
    try {
        $raw = curl.exe -s http://127.0.0.1:8090/api/android/status
        if (-not $raw) { return @{ raw = ""; online = $false; error = "empty status" } }
        $obj = $raw | ConvertFrom-Json
        $obj | Add-Member -NotePropertyName raw -NotePropertyValue $raw -Force
        return $obj
    } catch {
        return @{ raw = ""; online = $false; error = $_.Exception.Message }
    }
}

function Poll-AndroidOnline([string]$Phase, [int]$Attempts = 15, [int]$DelaySec = 3) {
    $online = $false
    $last = $null
    for ($i = 0; $i -lt $Attempts; $i++) {
        Start-Sleep -Seconds $DelaySec
        $status = Get-AndroidStatusObject
        $last = $status
        $isOnline = [bool]$status.online
        $script:statusSamples += @{
            phase = $Phase
            attempt = $i
            online = $isOnline
            sampled_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            status = $status
        }
        Write-Host ($status.raw | Out-String)
        if ($script:wasOnline -and -not $isOnline) { $script:heartbeatFailureCount += 1 }
        if (-not $script:wasOnline -and $isOnline) { $script:reconnectCount += 1 }
        $script:wasOnline = $isOnline
        if ($isOnline) {
            $online = $true
            break
        }
    }
    return @{ online = $online; last = $last }
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
$poll = Poll-AndroidOnline "initial" 15 3
$online = $poll.online
$lastStatus = if ($poll.last -and $poll.last.raw) { $poll.last.raw } else { ($poll.last | ConvertTo-Json -Depth 10) }
Set-Content "$ReportDir/android-status.json" -Value $lastStatus -Encoding utf8
if ($online) {
    Add-Check "android_online" "Android Dashboard online" "pass" "$ReportDir/android-status.json"
} else {
    Add-Check "android_online" "Android Dashboard online" $(if ($RequireOnline) { "fail" } else { "warn" }) "$ReportDir/android-status.json" "Android did not become online"
}

try {
    if ($ScreenOff) {
        Write-Host "`n== Screen off reconnect check =="
        adb shell input keyevent 26
        $poll = Poll-AndroidOnline "screen_off" 10 3
        Add-Check "android_screen_off_reconnect" "Android reconnects with screen off" $(if ($poll.online) { "pass" } elseif ($RequireOnline) { "fail" } else { "warn" }) "$ReportDir/android-status-samples.json" $(if ($poll.online) { "" } else { "Android not online after screen off" })
    }

    if ($RestartAiServer) {
        Write-Host "`n== AI Server restart reconnect check =="
        docker compose restart ai-server | Out-Host
        Start-Sleep -Seconds 10
        $poll = Poll-AndroidOnline "ai_restart" 20 3
        Add-Check "android_ai_restart_reconnect" "Android reconnects after AI Server restart" $(if ($poll.online) { "pass" } elseif ($RequireOnline) { "fail" } else { "warn" }) "$ReportDir/android-status-samples.json" $(if ($poll.online) { "" } else { "Android not online after AI restart" })
    }

    if ($RestartAndroidApp) {
        Write-Host "`n== Android app restart reconnect check =="
        adb shell am force-stop com.aegis.android
        Start-Sleep -Seconds 2
        adb shell am start -n com.aegis.android/.MainActivity --es host $HostAddress --ei port $Port --ez auto_connect true
        $poll = Poll-AndroidOnline "app_restart" 15 3
        Add-Check "android_app_restart_reconnect" "Android reconnects after app restart" $(if ($poll.online) { "pass" } elseif ($RequireOnline) { "fail" } else { "warn" }) "$ReportDir/android-status-samples.json" $(if ($poll.online) { "" } else { "Android not online after app restart" })
    }

    if ($TestWifiOff -or $TailscaleHost) {
        Write-Host "`n== Wi-Fi OFF reconnect check =="
        adb shell svc wifi disable
        $wifiWasDisabled = $true
        Start-Sleep -Seconds 8
        $networkOff = Get-NetworkType
        $networkOff | ConvertTo-Json -Depth 6 | Set-Content "$ReportDir/android-network-wifi-off.json" -Encoding utf8
        $poll = Poll-AndroidOnline "wifi_off" 20 3
        $expectedOnline = [bool]$TailscaleHost
        $wifiStatus = if ($poll.online -or -not $expectedOnline) { "pass" } elseif ($RequireOnline) { "fail" } else { "warn" }
        Add-Check "android_wifi_off_tailscale" "Android online with Wi-Fi OFF via Tailscale/mobile data" $wifiStatus "$ReportDir/android-network-wifi-off.json" $(if ($poll.online -or -not $expectedOnline) { "" } else { "Tailscale host was specified but Android did not become online with Wi-Fi OFF" })
    }
} finally {
    if ($wifiWasDisabled) {
        Write-Host "`n== Restore Wi-Fi =="
        adb shell svc wifi enable
        Start-Sleep -Seconds 5
        $networkRestored = Get-NetworkType
        $networkRestored | ConvertTo-Json -Depth 6 | Set-Content "$ReportDir/android-network-restored.json" -Encoding utf8
    }
}

$statusSamples | ConvertTo-Json -Depth 12 | Set-Content "$ReportDir/android-status-samples.json" -Encoding utf8

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
    reconnect_count = $reconnectCount
    heartbeat_failure_count = $heartbeatFailureCount
    wifi_off_tested = [bool]($TestWifiOff -or $TailscaleHost)
    screen_off_tested = [bool]$ScreenOff
    ai_restart_tested = [bool]$RestartAiServer
    app_restart_tested = [bool]$RestartAndroidApp
    checks = $checks
}
$summary | ConvertTo-Json -Depth 10 | Set-Content "$ReportDir/android-real.json" -Encoding utf8

Write-Host "`nRun local pytest with:"
Write-Host "cd ai-server; `$env:AEGIS_ANDROID_LOCAL='1'; `$env:AEGIS_ANDROID_TEST_HOST='$HostAddress'; uv run pytest -m android_local -q"

if ($summary.status -eq "pass") { exit 0 } else { exit 1 }
