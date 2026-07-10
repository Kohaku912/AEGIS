param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$DashboardBase = "http://127.0.0.1:8090"
)
$ErrorActionPreference = "Continue"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$checks = @()
function Add-Check($Id, $Name, $Url) {
    $cStart = Get-Date
    try {
        $res = Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 $Url
        $ok = $res.StatusCode -lt 400
        $script:checks += @{
            id = $Id; name = $Name; status = $(if ($ok) { "pass" } else { "fail" })
            duration_ms = [int]((Get-Date) - $cStart).TotalMilliseconds
            evidence = @($Url); error = $(if ($ok) { "" } else { "HTTP $($res.StatusCode)" })
            report_path = ""
        }
    } catch {
        $script:checks += @{
            id = $Id; name = $Name; status = "fail"
            duration_ms = [int]((Get-Date) - $cStart).TotalMilliseconds
            evidence = @($Url); error = $_.Exception.Message; report_path = ""
        }
    }
}
Add-Check "runtime_health" "Dashboard health" "$DashboardBase/health"
Add-Check "servers" "StatusManager servers" "$DashboardBase/api/servers"
Add-Check "tasks" "TaskManager API" "$DashboardBase/api/tasks"
Add-Check "events" "EventManager API" "$DashboardBase/api/events"
Add-Check "audit" "AuditManager API" "$DashboardBase/api/audit"
Add-Check "notifications" "NotificationManager API" "$DashboardBase/api/notifications"
Add-Check "approvals" "ApprovalManager API" "$DashboardBase/api/approvals"
Add-Check "capabilities" "CapabilityCatalog API" "$DashboardBase/api/capabilities/overrides"
Add-Check "llm_usage" "LLMUsage API" "$DashboardBase/api/llm-usage/summary?period=24h"
Add-Check "presentations" "Presentation API" "$DashboardBase/api/presentations?limit=5"
$status = if (($checks | Where-Object { $_.status -ne "pass" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{
    id = "manager_e2e"; name = "Manager API E2E"; status = $status
    duration_ms = [int]((Get-Date) - $start).TotalMilliseconds
    evidence = @("$ReportDir/manager-e2e.json"); error = ""; report_path = "$ReportDir/manager-e2e.json"
    checks = $checks
}
$result | ConvertTo-Json -Depth 10 | Set-Content "$ReportDir/manager-e2e.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
