param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$HostAddress = "192.168.50.175",
    [int]$Port = 50051,
    [string]$TailscaleHost = "",
    [switch]$TryUsbReverse,
    [switch]$RequireOnline
)
$argsList = @("-ExecutionPolicy", "Bypass", "-File", "scripts/test-android-real.ps1", "-HostAddress", $HostAddress, "-Port", "$Port", "-ReportDir", $ReportDir)
if ($TailscaleHost) { $argsList += @("-TailscaleHost", $TailscaleHost) }
if ($TryUsbReverse) { $argsList += "-TryUsbReverse" }
if ($RequireOnline) { $argsList += "-RequireOnline" }
& powershell @argsList
exit $LASTEXITCODE
