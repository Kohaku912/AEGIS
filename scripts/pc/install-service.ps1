param(
    [string]$InstallDir = "$env:ProgramFiles\AEGIS\pc-server",
    [int]$Port = 50052,
    [string]$Bind = "127.0.0.1",
    [switch]$EnableRealPcActions
)
$ErrorActionPreference = "Stop"
$serviceName = "AegisPcServer"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$LogDir = "$env:ProgramData\AEGIS\pc-server\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$source = Join-Path $PSScriptRoot "aegis-pc-server.exe"
if (-not (Test-Path $source)) { $source = "pc-server/target/release/aegis-pc-server.exe" }
if (-not (Test-Path $source)) { throw "aegis-pc-server.exe not found" }
Copy-Item $source "$InstallDir\aegis-pc-server.exe" -Force
$args = "--bind $Bind --port $Port"
if ($EnableRealPcActions) { $args += " --enable-real-pc-actions" }
$wrapper = Join-Path $InstallDir "run-pc-server-service.ps1"
@"
`$ErrorActionPreference = "Stop"
`$logDir = "$LogDir"
New-Item -ItemType Directory -Force -Path `$logDir | Out-Null
`$stdout = Join-Path `$logDir "stdout.log"
`$stderr = Join-Path `$logDir "stderr.log"
& "$InstallDir\aegis-pc-server.exe" $args 1>>`$stdout 2>>`$stderr
"@ | Set-Content $wrapper -Encoding utf8
$binPath = "`"$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe`" -NoProfile -ExecutionPolicy Bypass -File `"$wrapper`""
if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
    Stop-Service $serviceName -ErrorAction SilentlyContinue
    sc.exe delete $serviceName | Out-Null
}
New-Service -Name $serviceName -BinaryPathName $binPath -DisplayName "AEGIS PC Server" -StartupType Automatic
sc.exe description $serviceName "AEGIS PC Server. Logs: $LogDir. Production bind default: 127.0.0.1." | Out-Null
New-NetFirewallRule -DisplayName "AEGIS PC Server $Port" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port -ErrorAction SilentlyContinue | Out-Null
Start-Service $serviceName
Write-Host "Installed and started $serviceName on $Bind`:$Port"
Write-Host "Logs: $LogDir"
