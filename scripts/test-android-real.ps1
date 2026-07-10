param(
    [string]$HostAddress = "192.168.50.175",
    [int]$Port = 50051,
    [switch]$TryUsbReverse
)

$ErrorActionPreference = "Stop"

Write-Host "== ADB device =="
adb devices -l

Write-Host "`n== Installed AEGIS app =="
adb shell pm list packages | Select-String -Pattern "aegis" -CaseSensitive:$false

if ($TryUsbReverse) {
    Write-Host "`n== USB reverse =="
    adb reverse tcp:$Port tcp:$Port
    adb reverse --list
    $HostAddress = "127.0.0.1"
}

Write-Host "`n== Launch Android app =="
adb shell am force-stop com.aegis.android
adb shell am start -n com.aegis.android/.MainActivity --es host $HostAddress --ei port $Port --ez auto_connect true

Write-Host "`n== Poll Android status =="
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 3
    $status = curl.exe -s http://127.0.0.1:8090/api/android/status
    Write-Host $status
    if ($status -match '"online"\s*:\s*true') {
        break
    }
}

Write-Host "`nRun local pytest with:"
Write-Host "cd ai-server; `$env:AEGIS_ANDROID_LOCAL='1'; `$env:AEGIS_ANDROID_TEST_HOST='$HostAddress'; uv run pytest -m android_local -q"
