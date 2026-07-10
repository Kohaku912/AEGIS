param(
    [string]$OutputDir = "packages/pc-server",
    [switch]$Release
)
$ErrorActionPreference = "Stop"
$profile = if ($Release) { "release" } else { "debug" }
Push-Location pc-server
if ($Release) { cargo build --release } else { cargo build }
Pop-Location
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$binary = "pc-server/target/$profile/aegis-pc-server.exe"
if (-not (Test-Path $binary)) { throw "Missing $binary" }
Copy-Item $binary "$OutputDir/aegis-pc-server.exe" -Force
@"
port=50052
bind=0.0.0.0
enable_real_pc_actions=false
"@ | Set-Content "$OutputDir/aegis-pc-server.example.conf" -Encoding utf8
Copy-Item scripts/pc/install-service.ps1 "$OutputDir/install-service.ps1" -Force
Copy-Item scripts/pc/uninstall-service.ps1 "$OutputDir/uninstall-service.ps1" -Force
@"
# AEGIS PC Server portable package

Run as administrator:

```powershell
.\install-service.ps1
```

Real mouse/keyboard actions are disabled unless the service is installed with
`-EnableRealPcActions` and AEGIS approval policy allows the action.
"@ | Set-Content "$OutputDir/README.md" -Encoding utf8
Compress-Archive -Path "$OutputDir/*" -DestinationPath "$OutputDir/aegis-pc-server-portable.zip" -Force
Write-Host "Portable package: $OutputDir/aegis-pc-server-portable.zip"
