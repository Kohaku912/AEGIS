param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$HostAddress = "192.168.50.41",
    [int]$Port = 50051
)

$ErrorActionPreference = "Stop"
$started = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$checks = @()

function Add-Check([string]$Id, [string]$Status, [string[]]$Evidence, [string]$ErrorMessage = "") {
    $script:checks += @{
        id = $Id
        name = $Id.Replace("_", " ")
        status = $Status
        duration_ms = 0
        evidence = $Evidence
        error = $ErrorMessage
        report_path = ""
    }
}

function Capture-State([string]$Name) {
    $remoteXml = "/sdcard/aegis-$Name.xml"
    $remotePng = "/sdcard/aegis-$Name.png"
    adb shell uiautomator dump $remoteXml | Out-Null
    adb shell screencap -p $remotePng | Out-Null
    adb pull $remoteXml "$ReportDir/android-ui-$Name.xml" | Out-Null
    adb pull $remotePng "$ReportDir/android-ui-$Name.png" | Out-Null
    [xml]$tree = Get-Content "$ReportDir/android-ui-$Name.xml" -Raw
    return @($tree.SelectNodes('//node[@text!=""]') | ForEach-Object { $_.text })
}

$originalFontScale = (adb shell settings get system font_scale).Trim()
$originalAccelerometer = (adb shell settings get system accelerometer_rotation).Trim()
$originalRotation = (adb shell settings get system user_rotation).Trim()

try {
    adb shell settings put system accelerometer_rotation 0
    adb shell settings put system user_rotation 0
    adb shell settings put system font_scale 2.0
    adb shell am force-stop com.aegis.android
    adb shell am start -n com.aegis.android/.MainActivity --es host $HostAddress --ei port $Port --ez auto_connect true | Out-Null
    Start-Sleep -Seconds 6
    $portraitText = Capture-State "portrait-font-200"
    if ($portraitText -contains "Home" -and $portraitText -contains "More" -and $portraitText -contains "Connected to ${HostAddress}:${Port}") {
        Add-Check "android_portrait_font_200" "pass" @("$ReportDir/android-ui-portrait-font-200.xml", "$ReportDir/android-ui-portrait-font-200.png")
    } else {
        Add-Check "android_portrait_font_200" "fail" @("$ReportDir/android-ui-portrait-font-200.xml") "Required phone navigation or connection text is not visible"
    }

    adb shell settings put system user_rotation 1
    Start-Sleep -Seconds 5
    $landscapeText = Capture-State "landscape-font-200"
    if ($landscapeText -contains "Home" -and $landscapeText -contains "More") {
        Add-Check "android_landscape_font_200" "pass" @("$ReportDir/android-ui-landscape-font-200.xml", "$ReportDir/android-ui-landscape-font-200.png")
    } else {
        Add-Check "android_landscape_font_200" "fail" @("$ReportDir/android-ui-landscape-font-200.xml") "Accessible compact navigation is not visible"
    }
} catch {
    Add-Check "android_ui_real" "fail" @($ReportDir) $_.Exception.Message
} finally {
    adb shell settings put system font_scale $originalFontScale
    adb shell settings put system user_rotation $originalRotation
    adb shell settings put system accelerometer_rotation $originalAccelerometer
    adb shell am force-stop com.aegis.android
    adb shell am start -n com.aegis.android/.MainActivity --es host $HostAddress --ei port $Port --ez auto_connect true | Out-Null
}

$status = if (($checks | Where-Object status -eq "fail").Count) { "fail" } else { "pass" }
$result = @{
    id = "android_ui_real"
    name = "Android responsive UI real-device E2E"
    status = $status
    duration_ms = [int]((Get-Date) - $started).TotalMilliseconds
    evidence = @("$ReportDir/android-ui-portrait-font-200.png", "$ReportDir/android-ui-landscape-font-200.png")
    error = (($checks | Where-Object status -eq "fail" | ForEach-Object error) -join "; ")
    report_path = "$ReportDir/android-ui-real.json"
    original_settings_restored = $true
    tablet_policy_test = "AegisMobileUiModelTest.navigationUsesRailForTabletWidths"
    checks = $checks
}
$result | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/android-ui-real.json" -Encoding utf8
if ($status -eq "pass") { exit 0 }
exit 1
