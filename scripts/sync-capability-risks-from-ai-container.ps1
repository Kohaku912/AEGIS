param(
    [switch]$Apply,
    [string]$Service = "ai-server",
    [string]$ContainerCapabilitiesPath = "/app/capabilities",
    [string]$HostCapabilitiesPath = "ai-server/capabilities"
)

$ErrorActionPreference = "Stop"

function Read-JsonFile($Path) {
    if (!(Test-Path -LiteralPath $Path)) {
        return $null
    }
    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Write-JsonFile($Path, $Data) {
    $json = $Data | ConvertTo-Json -Depth 50
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json + "`n", $utf8NoBom)
}

function Get-RelativePathCompat($BasePath, $ChildPath) {
    $baseFull = [System.IO.Path]::GetFullPath($BasePath).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $childFull = [System.IO.Path]::GetFullPath($ChildPath)
    $baseUri = New-Object System.Uri($baseFull)
    $childUri = New-Object System.Uri($childFull)
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($childUri).ToString()).Replace('/', [System.IO.Path]::DirectorySeparatorChar)
}

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$hostRoot = Resolve-Path (Join-Path $root $HostCapabilitiesPath)
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-container-capabilities-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

try {
    docker compose cp "${Service}:${ContainerCapabilitiesPath}/." $tempRoot | Out-Null

    $changes = @()
    Get-ChildItem -LiteralPath $tempRoot -Filter "*.json" -Recurse | ForEach-Object {
        $relative = Get-RelativePathCompat $tempRoot $_.FullName
        $hostFile = Join-Path $hostRoot $relative
        $containerJson = Read-JsonFile $_.FullName
        $hostJson = Read-JsonFile $hostFile
        if ($null -eq $containerJson -or $null -eq $hostJson) {
            return
        }
        $containerRisk = $containerJson.risk
        $hostRisk = $hostJson.risk
        if ($null -eq $containerRisk -or $null -eq $hostRisk) {
            return
        }
        $containerLevel = [string]$containerRisk.level
        $hostLevel = [string]$hostRisk.level
        $containerApproval = [bool]$containerRisk.requires_approval
        $hostApproval = [bool]$hostRisk.requires_approval
        if ($containerLevel -ne $hostLevel -or $containerApproval -ne $hostApproval) {
            $changes += [pscustomobject]@{
                file = $relative
                host_level = $hostLevel
                container_level = $containerLevel
                host_requires_approval = $hostApproval
                container_requires_approval = $containerApproval
            }
            if ($Apply) {
                $hostJson.risk.level = $containerLevel
                $hostJson.risk.requires_approval = $containerApproval
                Write-JsonFile $hostFile $hostJson
            }
        }
    }

    $changes | Format-Table -AutoSize
    if (!$Apply -and $changes.Count -gt 0) {
        Write-Host "Run again with -Apply to copy only risk.level and risk.requires_approval to host manifests." -ForegroundColor Yellow
    }
    if ($changes.Count -eq 0) {
        Write-Host "No capability risk differences found." -ForegroundColor Green
    }
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
