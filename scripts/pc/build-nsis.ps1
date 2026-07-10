param(
    [string]$NsisPath = "makensis.exe"
)
$ErrorActionPreference = "Stop"
powershell -ExecutionPolicy Bypass -File scripts/pc/build-portable.ps1 -Release
& $NsisPath pc-server/installer/aegis-pc-server.nsi
