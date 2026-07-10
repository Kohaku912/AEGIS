param(
    [string]$InstallDir = "$env:ProgramFiles\AEGIS\pc-server",
    [int]$Port = 50052,
    [string]$Bind = "0.0.0.0",
    [switch]$EnableRealPcActions
)
$ErrorActionPreference = "Stop"
$serviceName = "AegisPcServer"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path "$env:ProgramData\AEGIS\pc-server\logs" | Out-Null
$source = Join-Path $PSScriptRoot "aegis-pc-server.exe"
if (-not (Test-Path $source)) { $source = "pc-server/target/release/aegis-pc-server.exe" }
if (-not (Test-Path $source)) { throw "aegis-pc-server.exe not found" }
Copy-Item $source "$InstallDir\aegis-pc-server.exe" -Force
$args = "--bind $Bind --port $Port"
if ($EnableRealPcActions) { $args += " --enable-real-pc-actions" }
$binPath = "`"$InstallDir\aegis-pc-server.exe`" $args"
if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
    Stop-Service $serviceName -ErrorAction SilentlyContinue
    sc.exe delete $serviceName | Out-Null
}
New-Service -Name $serviceName -BinaryPathName $binPath -DisplayName "AEGIS PC Server" -StartupType Automatic
New-NetFirewallRule -DisplayName "AEGIS PC Server $Port" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port -ErrorAction SilentlyContinue | Out-Null
Start-Service $serviceName
Write-Host "Installed and started $serviceName on $Bind`:$Port"
