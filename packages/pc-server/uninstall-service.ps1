param(
    [switch]$RemoveFiles,
    [string]$InstallDir = "$env:ProgramFiles\AEGIS\pc-server"
)
$ErrorActionPreference = "Continue"
$serviceName = "AegisPcServer"
if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
    Stop-Service $serviceName -ErrorAction SilentlyContinue
    sc.exe delete $serviceName | Out-Null
}
Get-NetFirewallRule -DisplayName "AEGIS PC Server*" -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
if ($RemoveFiles -and (Test-Path $InstallDir)) {
    Remove-Item -LiteralPath $InstallDir -Recurse -Force
}
Write-Host "Uninstalled $serviceName"
