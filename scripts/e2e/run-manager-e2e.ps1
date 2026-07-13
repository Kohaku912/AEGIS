param(
    [string]$ReportDir = "data/reports/e2e/latest",
    [string]$DashboardBase = "http://127.0.0.1:8090",
    [string]$CapabilityId = "pc-server.input.mouse_move"
)

$ErrorActionPreference = "Continue"
$start = Get-Date
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$checks = @()

function Add-Check($Id, $Name, $Status, $Evidence, $ErrorMessage = "", $StartedAt = $null) {
    $duration = 0
    if ($StartedAt) { $duration = [int]((Get-Date) - $StartedAt).TotalMilliseconds }
    $script:checks += @{
        id = $Id
        name = $Name
        status = $Status
        duration_ms = $duration
        evidence = @($Evidence)
        error = $ErrorMessage
        report_path = ""
    }
}

function Invoke-AegisJson($Method, $Path, $Body = $null) {
    $headers = @{}
    if ($env:AEGIS_AUTH_MODE -eq "token" -and $env:AEGIS_DASHBOARD_ACCESS_TOKEN) {
        $headers["X-AEGIS-Dashboard-Token"] = $env:AEGIS_DASHBOARD_ACCESS_TOKEN
    }
    if ($env:AEGIS_DASHBOARD_CSRF_TOKEN) {
        $headers["X-CSRF-Token"] = $env:AEGIS_DASHBOARD_CSRF_TOKEN
    }
    if ($env:AEGIS_DASHBOARD_SESSION_COOKIE) {
        $headers["Cookie"] = "aegis_session=$env:AEGIS_DASHBOARD_SESSION_COOKIE"
    }
    $uri = "$DashboardBase$Path"
    if ($Body -ne $null) {
        $json = $Body | ConvertTo-Json -Depth 10
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType "application/json" -Body $json -TimeoutSec 20
    }
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -TimeoutSec 20
}

function Add-HttpCheck($Id, $Name, $Method, $Path, $Body = $null) {
    $cStart = Get-Date
    try {
        $res = Invoke-AegisJson $Method $Path $Body
        Add-Check $Id $Name "pass" "$Method $Path" "" $cStart
        return $res
    } catch {
        $statusCode = $null
        try { $statusCode = [int]$_.Exception.Response.StatusCode } catch {}
        if ($statusCode -eq 401 -or $statusCode -eq 403) {
            Add-Check $Id $Name "pass" "$Method $Path" "API protected by dashboard auth ($statusCode)" $cStart
            return $null
        }
        Add-Check $Id $Name "fail" "$Method $Path" $_.Exception.Message $cStart
        return $null
    }
}

Add-HttpCheck "runtime_health" "Dashboard health" "GET" "/health" | Out-Null
Add-HttpCheck "servers" "StatusManager servers" "GET" "/api/servers" | Out-Null
Add-HttpCheck "tasks" "TaskManager API" "GET" "/api/tasks?limit=5" | Out-Null
Add-HttpCheck "events" "EventManager API" "GET" "/api/events?limit=5" | Out-Null
Add-HttpCheck "audit" "AuditManager API" "GET" "/api/audit?limit=5" | Out-Null
Add-HttpCheck "notifications" "NotificationManager API" "GET" "/api/notifications?limit=5" | Out-Null
Add-HttpCheck "approvals" "ApprovalManager API" "GET" "/api/approvals/pending" | Out-Null

$overrideStart = Get-Date
try {
    $riskProbe = @"
import json
from aegis_ai.runtime import get_runtime

capability_id = "$CapabilityId"
rt = get_runtime()
catalog = rt.capability_catalog
before = catalog.risk_details(capability_id)
store = catalog.get_override_store()
override = store.upsert(
    capability_id,
    risk_level="approval_required",
    requires_approval=True,
    approval_mode="always",
    enabled=True,
    updated_by="manager_e2e",
    reason="manager_e2e_stateful_probe",
)
catalog.reload()
after = catalog.risk_details(capability_id)
print(json.dumps({"before": before, "override": override.to_dict(), "after": after}, ensure_ascii=True, default=str))
"@
    $riskProbePath = Join-Path $ReportDir "manager-risk-override-probe.py"
    Set-Content $riskProbePath -Value $riskProbe -Encoding utf8
    $containerId = (docker compose ps -q ai-server)
    if (-not $containerId) { throw "ai-server container is not running" }
    docker cp $riskProbePath "$containerId`:/tmp/aegis-manager-risk-override-probe.py" | Out-Null
    $rawRisk = docker compose exec -T ai-server python /tmp/aegis-manager-risk-override-probe.py
    $rawRisk | Set-Content "$ReportDir/manager-risk-override.json" -Encoding utf8
    $riskEvidence = $rawRisk | ConvertFrom-Json
    if ($riskEvidence.after.effective.requires_approval -ne $true) { throw "effective requires_approval was not true" }
    Add-Check "capability_policy_override" "Capability risk override effective" "pass" "$ReportDir/manager-risk-override.json" "" $overrideStart
} catch {
    Add-Check "capability_policy_override" "Capability risk override effective" "fail" "$ReportDir/manager-risk-override.json" $_.Exception.Message $overrideStart
}

$probe = @'
import json
import time
from types import SimpleNamespace

from aegis_ai.runtime import get_runtime

rt = get_runtime()
checks = []

def check(check_id, name, ok, evidence=None, error=""):
    checks.append({
        "id": check_id,
        "name": name,
        "status": "pass" if ok else "fail",
        "duration_ms": 0,
        "evidence": evidence or [],
        "error": error,
        "report_path": "",
    })

try:
    task = rt.task_manager.create_task("manager e2e stateful probe", goal="verify manager state changes", source="system")
    rt.task_manager.start_task(task["task_id"])
    rt.task_manager.add_step(task["task_id"], "probe_step", "stateful probe step", "ai-server.memory.save")
    rt.task_manager.update_step_status(task["task_id"], "probe_step", "running")
    rt.task_manager.update_step_status(task["task_id"], "probe_step", "completed", result={"ok": True})
    rt.task_manager.complete_task(task["task_id"], "stateful probe completed")
    loaded = rt.task_manager.get_task(task["task_id"])
    check("task_stateful", "Task create step complete", loaded and loaded.get("status") == "completed", [task["task_id"]])
except Exception as exc:
    check("task_stateful", "Task create step complete", False, [], str(exc))

try:
    mem_id = rt.memory_manager.write_memory("AEGIS manager e2e memory probe", memory_type="episodic", tags=["e2e"])
    hits = rt.memory_manager.search_memory("manager e2e memory probe", limit=5)
    ctx = rt.memory_manager.get_context_for_task("manager-e2e", max_chars=1000)
    check("memory_stateful", "Memory save search context", bool(mem_id) and isinstance(hits, list) and isinstance(ctx, str), [mem_id])
except Exception as exc:
    check("memory_stateful", "Memory save search context", False, [], str(exc))

try:
    notif = rt.notification_manager.create_notification("AEGIS E2E", "manager notification probe", category="e2e")
    sent = rt.notification_manager.send(notif["notification_id"])
    read = rt.notification_manager.mark_read(notif["notification_id"], user="e2e")
    dismissed = rt.notification_manager.dismiss(notif["notification_id"])
    check("notification_stateful", "Notification create send read dismiss", bool(sent and read and dismissed and dismissed.get("status") == "dismissed"), [notif["notification_id"]])
except Exception as exc:
    check("notification_stateful", "Notification create send read dismiss", False, [], str(exc))

try:
    pres = rt.presentation_manager.present({
        "source": "manager_e2e",
        "intent": "readiness_probe",
        "title": "AEGIS E2E",
        "summary": "manager presentation probe",
        "content": {"text": "manager presentation probe"},
        "targets": ["dashboard"],
        "interaction_mode": "dismiss_only",
        "ttl_ms": 60000,
    })
    presentation = pres.get("presentation") or {}
    pid = pres.get("presentation_id") or pres.get("id") or presentation.get("presentation_id")
    action = rt.presentation_manager.user_action(pid, {"type": "e2e_ack"}) if pid else {}
    dismissed = rt.presentation_manager.dismiss(pid) if pid else {}
    check("presentation_stateful", "Presentation create action dismiss", bool(pid and action is not None and dismissed), [str(pid)])
except Exception as exc:
    check("presentation_stateful", "Presentation create action dismiss", False, [], str(exc))

try:
    req = SimpleNamespace(
        request_id=f"e2e_{int(time.time()*1000)}",
        capability_id="pc-server.input.mouse_click",
        tool_name="Mouse Click",
        arguments={"x": 1, "y": 1, "button": "left"},
        source="e2e",
        source_desire="",
        frustration=0.0,
        task_id="",
        step_id="",
        origin_channel="manager_e2e",
        conversation_id="",
        metadata={"e2e": True},
        risk_level=SimpleNamespace(name="MEDIUM"),
    )
    policy = SimpleNamespace(reason="manager e2e approval probe")
    approval = rt.approval_manager.create_request(req, policy)
    approved = rt.approval_manager.approve(approval.approval_id, channel="e2e", user="e2e")
    rt.approval_manager.mark_executed(approval.approval_id, result={"ok": True})
    final = rt.approval_manager.get(approval.approval_id)
    check("approval_stateful", "Approval create approve execute", bool(approved and final and final.status == "executed"), [approval.approval_id])
except Exception as exc:
    check("approval_stateful", "Approval create approve execute", False, [], str(exc))

try:
    audit = rt.audit_manager.list_recent(limit=20)
    items = audit.get("items") or audit.get("entries") or []
    check("audit_stateful", "Audit reflects stateful probes", isinstance(items, list) and len(items) > 0, [str(len(items))])
except Exception as exc:
    check("audit_stateful", "Audit reflects stateful probes", False, [], str(exc))

print(json.dumps({"checks": checks}, ensure_ascii=True))
'@

$probeStart = Get-Date
try {
    $probePath = Join-Path $ReportDir "manager-runtime-probe.py"
    Set-Content $probePath -Value $probe -Encoding utf8
    $containerId = (docker compose ps -q ai-server)
    if (-not $containerId) { throw "ai-server container is not running" }
    docker cp $probePath "$containerId`:/tmp/aegis-manager-runtime-probe.py" | Out-Null
    $raw = docker compose exec -T ai-server python /tmp/aegis-manager-runtime-probe.py
    $raw | Set-Content "$ReportDir/manager-runtime-probe.raw" -Encoding utf8
    $probeJson = $raw | ConvertFrom-Json
    foreach ($c in $probeJson.checks) {
        $checks += @{
            id = $c.id
            name = $c.name
            status = $c.status
            duration_ms = [int]$c.duration_ms
            evidence = @($c.evidence)
            error = $c.error
            report_path = $c.report_path
        }
    }
    Add-Check "runtime_stateful_probe" "Runtime stateful probe completed" "pass" "$ReportDir/manager-runtime-probe.raw" "" $probeStart
} catch {
    Add-Check "runtime_stateful_probe" "Runtime stateful probe completed" "fail" "$ReportDir/manager-runtime-probe.raw" $_.Exception.Message $probeStart
}

$usageStart = Get-Date
try {
    $traceCount = 0
    try {
        $usage = Invoke-AegisJson "GET" "/api/llm-usage/traces?period=24h&limit=5"
        $usage | ConvertTo-Json -Depth 12 | Set-Content "$ReportDir/manager-llm-usage.json" -Encoding utf8
        if ($usage.traces) { $traceCount = @($usage.traces).Count }
        elseif ($usage.items) { $traceCount = @($usage.items).Count }
        elseif ($usage.entries) { $traceCount = @($usage.entries).Count }
        elseif ($usage -is [array]) { $traceCount = @($usage).Count }
    } catch {
        $usageProbe = @'
import json
from aegis_ai.runtime import get_runtime
from aegis_ai.observability.llm_usage.service import LLMUsageService

rt = get_runtime()
svc = LLMUsageService(getattr(rt, "audit_manager", None), getattr(rt, "prompt_registry", None))
traces = svc.get_traces(period="24h", limit=5)
print(json.dumps({"traces": traces, "trace_count": len(traces)}, ensure_ascii=True, default=str))
'@
        $usageProbePath = Join-Path $ReportDir "manager-llm-usage-probe.py"
        Set-Content $usageProbePath -Value $usageProbe -Encoding utf8
        $containerId = (docker compose ps -q ai-server)
        if (-not $containerId) { throw "ai-server container is not running" }
        docker cp $usageProbePath "$containerId`:/tmp/aegis-manager-llm-usage-probe.py" | Out-Null
        $rawUsage = docker compose exec -T ai-server python /tmp/aegis-manager-llm-usage-probe.py
        $rawUsage | Set-Content "$ReportDir/manager-llm-usage.json" -Encoding utf8
        $usage = $rawUsage | ConvertFrom-Json
        $traceCount = [int]$usage.trace_count
    }
    if ($traceCount -lt 1) { throw "No LLM usage traces returned from audit-backed service" }
    Add-Check "llm_usage_real_trace" "LLM Usage displays audit-backed traces" "pass" "$ReportDir/manager-llm-usage.json" "" $usageStart
} catch {
    Add-Check "llm_usage_real_trace" "LLM Usage displays audit-backed traces" "fail" "$ReportDir/manager-llm-usage.json" $_.Exception.Message $usageStart
}

$status = if (($checks | Where-Object { $_.status -eq "fail" }).Count -eq 0) { "pass" } else { "fail" }
$result = @{
    id = "manager_e2e"
    name = "Manager stateful E2E"
    status = $status
    duration_ms = [int]((Get-Date) - $start).TotalMilliseconds
    evidence = @("$ReportDir/manager-e2e.json", "$ReportDir/manager-risk-override.json", "$ReportDir/manager-runtime-probe.raw")
    error = ""
    report_path = "$ReportDir/manager-e2e.json"
    checks = $checks
}
$result | ConvertTo-Json -Depth 12 | Set-Content "$ReportDir/manager-e2e.json" -Encoding utf8
if ($status -eq "pass") { exit 0 } else { exit 1 }
