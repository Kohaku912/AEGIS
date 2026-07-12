from __future__ import annotations

from types import SimpleNamespace

from flask import Flask

from aegis_ai.web.routes.ui import init_ui_routes
from aegis_ai.web.ui_overview import build_ui_overview, normalize_ui_event


class _StatusManager:
    def get_snapshot(self):
        return {
            "ai-server": {"status": "online", "updated_at": 1000},
            "pc-server": {"status": "offline", "error": "not reachable", "updated_at": 1000},
        }


class _ApprovalManager:
    def list_pending(self):
        return [
            SimpleNamespace(
                to_dict=lambda: {
                    "approval_id": "approval-1",
                    "capability_id": "pc-server.keyboard.type_text",
                    "risk_level": "high",
                    "user_facing_summary": "Type into safe field",
                    "created_at": 1000,
                    "expires_at": 2000,
                    "status": "pending",
                }
            )
        ]


class _TaskManager:
    def list_running(self):
        return [{"task_id": "task-1", "title": "Test task", "status": "running", "updated_at": 1000, "steps": []}]

    def list_waiting_approval(self):
        return []


class _NotificationManager:
    def list_unread(self, limit=50):
        return []

    def list_recent(self, limit=50):
        return []


class _MemoryManager:
    def get_stats(self):
        return {"episodic": 1, "semantic": 2, "procedural": 3}


class _EventManager:
    def subscribe(self, handler, event_filter=None):
        return "sub-1"

    def unsubscribe(self, subscriber_id):
        return True


def _runtime():
    return SimpleNamespace(
        status_manager=_StatusManager(),
        approval_manager=_ApprovalManager(),
        task_manager=_TaskManager(),
        notification_manager=_NotificationManager(),
        memory_manager=_MemoryManager(),
        event_manager=_EventManager(),
    )


def test_ui_overview_sections_have_freshness_envelope():
    overview = build_ui_overview(_runtime())

    for section in [
        "core",
        "attention",
        "current_task",
        "servers",
        "user_state",
        "mind_summary",
        "notifications",
        "approvals",
        "commitments",
        "usage",
        "freshness",
    ]:
        value = overview[section]
        assert {"generated_at", "source_updated_at", "status", "stale", "error", "data"} <= set(value)

    assert overview["approvals"]["data"]["pending"][0]["approval_id"] == "approval-1"
    assert overview["attention"]["data"]["items"]


def test_ui_overview_route_returns_normalized_contract():
    app = Flask(__name__)
    owner = SimpleNamespace(app=app, _runtime=_runtime())
    init_ui_routes(owner)

    response = app.test_client().get("/api/ui/overview")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["schema_version"] == "ui-overview.v2"
    assert payload["servers"]["data"]["items"]


def test_ui_overview_compacts_large_step_results():
    huge_result = {"html": "x" * 5_000_000, "status": "ok", "items": list(range(200))}

    class LargeTaskManager:
        def list_running(self):
            return [
                {
                    "task_id": "task-large",
                    "title": "Large result task",
                    "status": "running",
                    "updated_at": 1000,
                    "steps": [
                        {
                            "step_id": "step-large",
                            "capability_id": "browser-server.page.browse",
                            "status": "completed",
                            "result": huge_result,
                        }
                    ],
                }
            ]

        def list_waiting_approval(self):
            return []

    runtime = SimpleNamespace(
        status_manager=_StatusManager(),
        approval_manager=_ApprovalManager(),
        task_manager=LargeTaskManager(),
        notification_manager=_NotificationManager(),
        memory_manager=_MemoryManager(),
        event_manager=_EventManager(),
    )

    overview = build_ui_overview(runtime)
    step = overview["current_task"]["data"]["steps"][0]

    assert len(str(overview)) < 20_000
    assert step["result"]["available"] is True
    assert step["result"]["truncated"] is True
    assert step["result"]["size_chars"] > 5_000_000
    assert "html" in step["result"]["keys"]


def test_normalize_ui_event_exposes_visual_fields():
    event = SimpleNamespace(
        event_type="tool.execution.failed",
        timestamp=1234,
        payload={
            "capability_id": "android-server.screen.get_ui_tree",
            "task_id": "task-1",
            "status": "failed",
            "error": "permission missing",
        },
    )

    normalized = normalize_ui_event(event)

    assert normalized["type"] == "tool.execution.failed"
    assert normalized["server_id"] == "android-server"
    assert normalized["capability_id"] == "android-server.screen.get_ui_tree"
    assert normalized["task_id"] == "task-1"
    assert normalized["severity"] == "critical"
    assert normalized["message"] == "permission missing"
