param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$HostAddress = "192.168.50.41",
    [int]$Port = 50051,
    [string]$TailscaleHost = "",
    [string]$StatusUrl = "",
    [switch]$TryUsbReverse,
    [switch]$RequireOnline,
    [switch]$TestWifiOff,
    [switch]$ScreenOff,
    [switch]$RestartAiServer,
    [switch]$RestartAndroidApp
)
$argsList = @("-ExecutionPolicy", "Bypass", "-File", "scripts/test-android-real.ps1", "-HostAddress", $HostAddress, "-Port", "$Port", "-ReportDir", $ReportDir)
if ($TailscaleHost) { $argsList += @("-TailscaleHost", $TailscaleHost) }
if ($StatusUrl) { $argsList += @("-StatusUrl", $StatusUrl) }
if ($TryUsbReverse) { $argsList += "-TryUsbReverse" }
if ($RequireOnline) { $argsList += "-RequireOnline" }
if ($TestWifiOff) { $argsList += "-TestWifiOff" }
if ($ScreenOff) { $argsList += "-ScreenOff" }
if ($RestartAiServer) { $argsList += "-RestartAiServer" }
if ($RestartAndroidApp) { $argsList += "-RestartAndroidApp" }
& powershell @argsList
exit $LASTEXITCODE
