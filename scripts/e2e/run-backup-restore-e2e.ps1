param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$DataVolume = "",
    [string]$ReportsVolume = ""
)

$ErrorActionPreference = "Stop"
$started = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$backupDir = Join-Path $ReportDir "backup-restore"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

function Resolve-ComposeVolume([string]$Key, [string]$Explicit) {
    if ($Explicit) { return $Explicit }
    $resolved = docker compose config --volumes | Where-Object { $_ -eq $Key } | Select-Object -First 1
    if (-not $resolved) { throw "Compose volume '$Key' is not defined" }
    $project = Split-Path -Leaf (Get-Location)
    return "$($project.ToLower())_$Key"
}

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

$restoreVolume = "aegis-restore-check-$([guid]::NewGuid().ToString('N').Substring(0, 10))"
try {
    $dataVolumeName = Resolve-ComposeVolume "aegis-data" $DataVolume
    $reportsVolumeName = Resolve-ComposeVolume "aegis-reports" $ReportsVolume
    foreach ($volume in @($dataVolumeName, $reportsVolumeName)) {
        if (-not (docker volume inspect $volume 2>$null)) { throw "Docker volume '$volume' does not exist" }
    }

    $absoluteBackupDir = (Resolve-Path $backupDir).Path
    docker run --rm -v "${dataVolumeName}:/source:ro" -v "${absoluteBackupDir}:/backup" alpine:3.20 `
        sh -c "cd /source && tar czf /backup/aegis-critical-data.tar.gz auth settings readiness" | Out-Null
    docker run --rm -v "${reportsVolumeName}:/source:ro" -v "${absoluteBackupDir}:/backup" alpine:3.20 `
        tar czf /backup/aegis-reports.tar.gz -C /source . | Out-Null
    Add-Check "backup_archives_created" "pass" @(
        "$backupDir/aegis-critical-data.tar.gz",
        "$backupDir/aegis-reports.tar.gz"
    )

    docker volume create $restoreVolume | Out-Null
    docker run --rm -v "${restoreVolume}:/restore" -v "${absoluteBackupDir}:/backup:ro" alpine:3.20 `
        tar xzf /backup/aegis-critical-data.tar.gz -C /restore | Out-Null
    $listing = docker run --rm -v "${restoreVolume}:/restore:ro" alpine:3.20 `
        sh -c "find /restore -mindepth 1 -maxdepth 3 -type f | head -n 50"
    $listing | Set-Content (Join-Path $backupDir "restored-files.txt") -Encoding utf8
    if (-not $listing) { throw "Restored data volume is empty" }
    Add-Check "restore_to_isolated_volume" "pass" @("$backupDir/restored-files.txt")
} catch {
    Add-Check "backup_restore" "fail" @($backupDir) $_.Exception.Message
} finally {
    if (docker volume inspect $restoreVolume 2>$null) {
        docker volume rm $restoreVolume | Out-Null
    }
}

$status = if (($checks | Where-Object status -eq "fail").Count) { "fail" } else { "pass" }
$result = @{
    id = "backup_restore"
    name = "Docker volume backup and isolated restore"
    status = $status
    duration_ms = [int]((Get-Date) - $started).TotalMilliseconds
    evidence = @($backupDir)
    error = (($checks | Where-Object status -eq "fail" | ForEach-Object error) -join "; ")
    report_path = "$ReportDir/backup-restore.json"
    scope = "critical durable state; full-volume backup remains the Ubuntu runbook operation"
    checks = $checks
}
$result | ConvertTo-Json -Depth 8 | Set-Content "$ReportDir/backup-restore.json" -Encoding utf8
if ($status -eq "pass") { exit 0 }
exit 1
