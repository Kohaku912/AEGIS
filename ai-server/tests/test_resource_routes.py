from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from flask import Flask

from aegis_ai.web.resource_routes import init_resource_routes


@dataclass
class _Approval:
    approval_id: str
    capability_id: str
    status: str = "pending"

    def to_dict(self):
        return {
            "approval_id": self.approval_id,
            "capability_id": self.capability_id,
            "status": self.status,
            "created_at": 1_700_000_000_000,
        }


@dataclass
class _Capability:
    capability_id: str
    title: str
    server_id: str
    risk_level: str = "READ_ONLY"
    enabled: bool = True


class _TaskManager:
    def list_tasks(self, **_kwargs):
        return [
            {"task_id": "task-1", "title": "Inspect Android", "status": "running", "updated_at": 1_700_000_000_000},
            {"task_id": "task-2", "title": "Archive report", "status": "completed", "updated_at": 1_600_000_000_000},
        ]

    def get_task(self, task_id):
        return next((item for item in self.list_tasks() if item["task_id"] == task_id), None)

    def pause_task(self, task_id):
        task = self.get_task(task_id)
        return {**task, "status": "paused"} if task else None


class _StatusManager:
    def get_snapshot(self):
        return {
            "ai-server": {"status": "online", "latency_ms": 4},
            "android-server": {"status": "offline", "latency_ms": 0},
        }

    def check_now(self):
        return self.get_snapshot()


class _Queue:
    def get_all(self):
        return [_Approval("approval-1", "pc-server.input.click")]


class _MemoryManager:
    def search_memory(self, query, types=None, limit=20):
        return [{"type": (types or ["semantic"])[0], "content": f"memory about {query or 'AEGIS'}", "source": "test"}]


class _HookManager:
    def __init__(self):
        self.items = {"hook-1": {"hook_id": "hook-1", "name": "Daily briefing", "status": "enabled"}}

    def list_hooks(self):
        return list(self.items.values())

    def get_hook(self, hook_id):
        return self.items.get(hook_id)

    def upsert_hook(self, patch):
        self.items[patch["hook_id"]] = {**self.items.get(patch["hook_id"], {}), **patch}
        return self.items[patch["hook_id"]]


class _DelegationManager:
    def __init__(self):
        self.items = {
            "rule-1": {
                "rule_id": "rule-1",
                "description": "Approval for external actions",
                "decision": "approval_required",
            }
        }

    def list_rules(self):
        return list(self.items.values())

    def upsert_rule(self, patch):
        self.items[patch["rule_id"]] = {**self.items.get(patch["rule_id"], {}), **patch}
        return self.items[patch["rule_id"]]


class _EventManager:
    def list_recent(self, **_kwargs):
        return {"events": [{"event_id": "event-1", "type": "task.updated", "message": "Task updated", "status": "ok"}]}


class _AuditManager:
    def list_recent(self, **_kwargs):
        return {"entries": [{"audit_id": "audit-1", "action": "tool.execute", "status": "success"}]}


def _runtime():
    capabilities = [_Capability("android-server.screen.get_ui_tree", "Read UI tree", "android-server")]
    manifest = SimpleNamespace(
        capability_id=capabilities[0].capability_id,
        risk_level="READ_ONLY",
        requires_approval=False,
    )
    policy_result = SimpleNamespace(
        capability_id=capabilities[0].capability_id,
        decision=SimpleNamespace(name="ALLOW"),
        reason="Risk level READ_ONLY - allowed.",
        risk_level=SimpleNamespace(name="READ_ONLY"),
        required_approval_type=None,
        expires_at_ms=0,
        audit_required=False,
    )
    return SimpleNamespace(
        task_manager=_TaskManager(),
        status_manager=_StatusManager(),
        approval_manager=SimpleNamespace(_queue=_Queue(), list_pending=lambda: []),
        capability_catalog=SimpleNamespace(
            list_all=lambda: capabilities,
            describe=lambda capability_id: (
                {"id": capability_id, "title": "Read UI tree", "status": "enabled", "server_id": "android-server"}
                if capability_id == capabilities[0].capability_id
                else None
            ),
            resolve=lambda capability_id: manifest if capability_id == capabilities[0].capability_id else None,
        ),
        tool_registry=SimpleNamespace(
            get_capability=lambda capability_id: (
                SimpleNamespace(id=capability_id) if capability_id == capabilities[0].capability_id else None
            )
        ),
        policy_engine=SimpleNamespace(
            evaluate_tool_invocation=lambda capability, params: policy_result,
            evaluate_event_trigger=lambda capability, params: policy_result,
            evaluate_autonomous_task=lambda capability, params: policy_result,
        ),
        memory_manager=_MemoryManager(),
        event_manager=_EventManager(),
        audit_manager=_AuditManager(),
        commitment_manager=SimpleNamespace(
            list_commitments=lambda status=None: [
                {"commitment_id": "commitment-1", "title": "Finish AEGIS", "status": "active"}
            ]
        ),
        autonomous_loop=SimpleNamespace(stop=lambda: None),
        interruption_controller=SimpleNamespace(set_emergency_stop=lambda active: {"active": active}),
        audit_log=SimpleNamespace(log_decision=lambda *args, **kwargs: None),
        hook_engine=_HookManager(),
        delegation_policy=_DelegationManager(),
        sleep_manager=SimpleNamespace(get_status=lambda: {"status": "idle", "last_run_at": 1_700_000_000_000}),
        user_model_store=SimpleNamespace(get=lambda: {"preferred_language": "ja", "status": "effective"}),
        situation_model=SimpleNamespace(get_state=lambda: {"status": "available", "activity": "testing"}),
        prompt_registry=SimpleNamespace(
            list_prompts=lambda: [{"id": "chat.system", "title": "Chat system", "status": "used"}]
        ),
        android_manager=SimpleNamespace(get_status=lambda: {"status": "online", "device_model": "21121210G"}),
        session_manager=SimpleNamespace(
            list_sessions=lambda: [{"session_id": "session-1", "channel": "dashboard", "status": "active"}]
        ),
        presentation_manager=SimpleNamespace(
            list_summaries=lambda limit=200: [
                {"presentation_id": "presentation-1", "title": "Status", "status": "active"}
            ]
        ),
    )


def _client():
    app = Flask(__name__)
    init_resource_routes(app, _runtime())
    return app.test_client()


def test_entity_api_normalizes_manager_records():
    response = _client().get("/api/ui/entities?resource=tasks")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total"] == 2
    assert payload["items"][0]["type"] == "task"
    assert payload["items"][0]["id"] in {"task-1", "task-2"}
    assert "detail" in payload["items"][0]


def test_entity_api_filters_and_pages():
    response = _client().get("/api/ui/entities?resource=tasks&q=Android&limit=1&page=1")
    payload = response.get_json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == "task-1"
    assert payload["has_more"] is False


def test_global_search_reads_across_managers():
    response = _client().get("/api/ui/search?q=android")
    payload = response.get_json()
    kinds = {item["type"] for item in payload["items"]}
    assert "task" in kinds
    assert "server" in kinds
    assert "capability" in kinds


def test_full_approval_lifecycle_and_memory_alias():
    approvals = _client().get("/api/approvals").get_json()
    memories = _client().get("/api/memories?q=project&type=semantic").get_json()
    assert approvals["items"][0]["id"] == "approval-1"
    assert memories["items"][0]["type"] == "memory"
    assert "project" in memories["items"][0]["detail"]["content"]


def test_unsupported_resource_is_explicit():
    response = _client().get("/api/ui/entities?resource=unknown")
    assert response.status_code == 400
    assert response.get_json()["error"] == "unsupported_resource"


def test_exact_resource_contract_details_and_stable_memory_ids():
    client = _client()
    capability = client.get("/api/capabilities/android-server.screen.get_ui_tree")
    first = client.get("/api/memories?q=stable").get_json()["items"][0]
    second = client.get("/api/memories?q=stable").get_json()["items"][0]
    server = client.get("/api/servers/android-server")
    assert capability.status_code == 200
    assert capability.get_json()["id"] == "android-server.screen.get_ui_tree"
    assert first["id"] == second["id"]
    assert server.get_json()["status"] == "offline"


def test_task_action_previews_controlled_work_and_executes_safe_pause():
    client = _client()
    retry = client.post("/api/tasks/task-1/actions", json={"action": "retry", "confirmed": True})
    pause = client.post("/api/tasks/task-1/actions", json={"action": "pause", "confirmed": True})
    assert retry.status_code == 202
    assert retry.get_json()["preview"]["requires_fresh_auth"] is True
    assert pause.status_code == 200
    assert pause.get_json()["result"]["status"] == "paused"


def test_master_control_requires_preview_and_verifies_refresh():
    client = _client()
    preview = client.post("/api/ui/control-actions", json={"action": "refresh-all-servers"})
    executed = client.post("/api/ui/control-actions", json={"action": "refresh-all-servers", "confirmed": True})
    assert preview.status_code == 202
    assert preview.get_json()["preview"]["verification"]
    assert executed.status_code == 200
    assert executed.get_json()["verified"] is True


def test_policy_simulation_uses_effective_registry_without_execution():
    response = _client().post(
        "/api/policy/simulate",
        json={
            "capability_id": "android-server.screen.get_ui_tree",
            "context": "tool_invocation",
            "arguments": {"depth": 3},
        },
    )
    assert response.status_code == 200
    simulation = response.get_json()["simulation"]
    assert simulation["decision"] == "ALLOW"
    assert simulation["executed"] is False
    assert simulation["arguments"] == {"depth": 3}


def test_manager_specific_resources_do_not_fall_back_to_tasks():
    client = _client()
    hooks = client.get("/api/ui/entities?resource=hooks").get_json()["items"]
    delegations = client.get("/api/ui/entities?resource=delegations").get_json()["items"]
    devices = client.get("/api/ui/entities?resource=devices").get_json()["items"]
    presentations = client.get("/api/ui/entities?resource=presentations").get_json()["items"]
    assert hooks[0]["type"] == "hook"
    assert delegations[0]["type"] == "delegation"
    assert devices[0]["detail"]["device_model"] == "21121210G"
    assert presentations[0]["id"] == "presentation-1"


def test_hook_and_delegation_mutations_require_preview_before_manager_write():
    client = _client()
    hook_preview = client.patch("/api/hooks/hook-1", json={"patch": {"cooldown_seconds": 60}})
    hook_save = client.patch(
        "/api/hooks/hook-1",
        json={"patch": {"cooldown_seconds": 60}, "confirmed": True},
    )
    delegation_preview = client.patch(
        "/api/delegations/rule-1",
        json={"patch": {"decision": "forbidden"}},
    )
    assert hook_preview.status_code == 202
    assert hook_save.get_json()["verified"] is True
    assert hook_save.get_json()["result"]["detail"]["cooldown_seconds"] == 60
    assert delegation_preview.status_code == 202
    assert delegation_preview.get_json()["preview"]["risk"] == "controlled"
