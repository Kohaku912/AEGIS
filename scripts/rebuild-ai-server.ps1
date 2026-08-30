# Rebuild the AI Server image from source. This is the canonical deploy path.
# Partial docker cp into a running container is emergency-only and causes drift.
#
# Usage:
#   .\scripts\rebuild-ai-server.ps1
#   .\scripts\rebuild-ai-server.ps1 -NoCache

param(
    [switch]$NoCache
)

$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

$rev = "unknown"
try {
    $rev = (git rev-parse --short HEAD).Trim()
} catch {
    $rev = "unknown"
}

$env:AEGIS_SOURCE_REVISION = $rev
Write-Host "Building ai-server revision $rev"

$buildArgs = @("compose", "build", "--build-arg", "AEGIS_SOURCE_REVISION=$rev", "ai-server")
if ($NoCache) {
    $buildArgs = @("compose", "build", "--no-cache", "--build-arg", "AEGIS_SOURCE_REVISION=$rev", "ai-server")
}
docker @buildArgs
if ($LASTEXITCODE -ne 0) {
    throw "docker compose build failed"
}

docker compose up -d --force-recreate --no-deps ai-server
if ($LASTEXITCODE -ne 0) {
    throw "docker compose up failed"
}

Write-Host "ai-server recreated at revision $rev"
Write-Host "Partial docker cp is emergency-only; do not leave a patched container as the source of truth."
