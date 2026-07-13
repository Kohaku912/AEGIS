param(
    [string]$BaseUrl = "http://127.0.0.1:8090",
    [int]$DurationMinutes = 4320,
    [int]$DurationSeconds = 0,
    [string]$ReportDir = "data/reports/e2e/latest"
)

$ErrorActionPreference = "Stop"
$started = Get-Date
$duration = if ($DurationSeconds -gt 0) {
    [TimeSpan]::FromSeconds($DurationSeconds)
} else {
    [TimeSpan]::FromMinutes($DurationMinutes)
}
$deadline = $started.Add($duration)
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$reportPath = Join-Path $root $ReportDir
New-Item -ItemType Directory -Force -Path $reportPath | Out-Null

$samples = New-Object System.Collections.Generic.List[object]
$failures = 0

while ((Get-Date) -lt $deadline) {
    $sampleStarted = Get-Date
    try {
        $overview = Invoke-RestMethod -Method Get -Uri "$BaseUrl/display/overview" -TimeoutSec 10
        $samples.Add([pscustomobject]@{
            checked_at = $sampleStarted.ToString("o")
            ok = $true
            schema_version = $overview.schema_version
            phase = $overview.display_scene.data.phase
            display_queue_count = $overview.display_queue.data.count
            activity_count = $overview.activity.data.count
            stale = $overview.freshness.stale
        })
    } catch {
        $failures += 1
        $samples.Add([pscustomobject]@{
            checked_at = $sampleStarted.ToString("o")
            ok = $false
            error = $_.Exception.Message
        })
    }
    Start-Sleep -Seconds 30
}

$summary = [pscustomobject]@{
    id = "display_soak"
    name = "Display 72-hour stability probe"
    status = if ($failures -eq 0) { "PASS" } else { "FAIL" }
    started_at = $started.ToString("o")
    finished_at = (Get-Date).ToString("o")
    duration_seconds = [int]((Get-Date) - $started).TotalSeconds
    sample_count = $samples.Count
    failure_count = $failures
    evidence = @("GET $BaseUrl/display/overview", "schema/display_queue/activity/freshness sampled")
}

$summary | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $reportPath "display_soak_summary.json")
$samples | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $reportPath "display_soak_samples.json")

if ($failures -gt 0) {
    Write-Error "Display soak failed with $failures failures."
}

Write-Host "Display soak completed: $($summary.status), samples=$($samples.Count), failures=$failures"
