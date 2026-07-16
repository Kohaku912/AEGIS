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

    def list_recent(self, limit=50, cursor=None):
        return {
            "events": [
                {
                    "event_id": "evt-offline",
                    "event_type": "status.changed",
                    "timestamp": 1000,
                    "payload": {"server_id": "pc-server", "status": "offline", "message": "PC offline"},
                },
                {
                    "event_id": "evt-approval",
                    "event_type": "approval.created",
                    "timestamp": 1100,
                    "payload": {
                        "approval_id": "approval-queue",
                        "capability_id": "pc-server.keyboard.type_text",
                        "message": "Approval still pending",
                    },
                },
            ],
        }


class _ReplayEventManager(_EventManager):
    def __init__(self):
        self.unsubscribe_called = False

    def list_recent(self, limit=50, cursor=None):
        assert cursor == "evt-1"
        return {
            "events": [
                {
                    "event_id": "evt-2",
                    "event_type": "approval.created",
                    "timestamp": 2222,
                    "severity": "warning",
                    "payload": {"approval_id": "approval-2", "capability_id": "pc-server.mouse.click"},
                }
            ],
            "next_cursor": None,
        }

    def unsubscribe(self, subscriber_id):
        self.unsubscribe_called = True
        return True


class _PresentationManager:
    def list_active(self, limit=30):
        return [
            {
                "presentation_id": "presentation-1",
                "title": "Display item",
                "summary": "Visible on dedicated display",
                "status": "active",
                "priority": "high",
                "ttl_seconds": "0",
                "created_at": 1000,
            }
        ]


def _runtime():
    return SimpleNamespace(
        status_manager=_StatusManager(),
        approval_manager=_ApprovalManager(),
        task_manager=_TaskManager(),
        notification_manager=_NotificationManager(),
        memory_manager=_MemoryManager(),
        event_manager=_EventManager(),
        presentation_manager=_PresentationManager(),
    )


def test_ui_overview_sections_have_freshness_envelope():
    overview = build_ui_overview(_runtime())

    for section in [
        "core",
        "connection",
        "display_scene",
        "presentations",
        "presentation_events",
        "surface_roles",
        "display_queue",
        "tasks",
        "activity",
        "attention",
        "current_task",
        "servers",
        "capabilities",
        "user_situation",
        "user_state",
        "mind",
        "mind_summary",
        "memory",
        "notifications",
        "approvals",
        "commitments",
        "usage",
        "errors",
        "freshness",
    ]:
        value = overview[section]
        assert {"generated_at", "source_updated_at", "status", "stale", "error", "data"} <= set(value)

    assert overview["approvals"]["data"]["pending"][0]["approval_id"] == "approval-1"
    assert overview["presentations"]["status"] == "ok"
    assert overview["presentations"]["data"]["count"] == 1
    assert overview["surface_roles"]["data"]["items"]
    assert any(item["surface_id"] == "dedicated_display" and item["interactive"] is False for item in overview["surface_roles"]["data"]["items"])
    assert overview["presentation_events"]["data"]["items"]
    assert "recommended_surfaces" in overview["presentation_events"]["data"]["items"][0]
    assert overview["activity"]["data"]["groups"]
    assert overview["display_queue"]["data"]["persisted"] is True
    assert overview["display_queue"]["data"]["items"]
    assert overview["attention"]["data"]["items"]


def test_ui_overview_route_returns_normalized_contract():
    app = Flask(__name__)
    owner = SimpleNamespace(app=app, _runtime=_runtime())
    init_ui_routes(owner)

    response = app.test_client().get("/api/ui/overview")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["schema_version"] == "ui-overview.v3"
    assert payload["servers"]["data"]["items"]
    assert payload["tasks"]["data"]["primary"]["task_id"] == "task-1"


def test_ui_stream_replays_events_after_last_event_id():
    app = Flask(__name__)
    runtime = _runtime()
    runtime.event_manager = _ReplayEventManager()
    owner = SimpleNamespace(app=app, _runtime=runtime)
    init_ui_routes(owner)

    response = app.test_client().get("/api/ui/stream?last_event_id=evt-1", buffered=False)
    chunks = []
    iterator = iter(response.response)
    for _ in range(3):
        chunks.append(next(iterator).decode("utf-8"))
    response.close()
    body = "".join(chunks)

    assert "retry: 3000" in body
    assert "id: evt-2" in body
    assert "event: approval.created" in body
    assert '"event_id": "evt-2"' in body
    assert "event: ui.snapshot" in body


def test_display_queue_resolves_persistent_server_items():
    class ResolvingEvents(_EventManager):
        def list_recent(self, limit=50, cursor=None):
            return {
                "events": [
                    {
                        "event_id": "evt-offline",
                        "event_type": "status.changed",
                        "timestamp": 1000,
                        "payload": {"server_id": "pc-server", "status": "offline", "message": "PC offline"},
                    },
                    {
                        "event_id": "evt-online",
                        "event_type": "status.changed",
                        "timestamp": 2000,
                        "payload": {"server_id": "pc-server", "status": "online", "message": "PC recovered"},
                    },
                    {
                        "event_id": "evt-approval",
                        "event_type": "approval.created",
                        "timestamp": 2100,
                        "payload": {
                            "approval_id": "approval-queue",
                            "capability_id": "android-server.input.type_text",
                            "message": "Android approval pending",
                        },
                    },
                ],
            }

    runtime = _runtime()
    runtime.event_manager = ResolvingEvents()
    overview = build_ui_overview(runtime)

    items = overview["display_queue"]["data"]["items"]
    assert all(item["event_id"] != "evt-offline" for item in items)
    assert any(item["event_id"] == "evt-approval" for item in items)
    assert overview["activity"]["data"]["count"] == 3


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

    assert len(str(overview)) < 35_000
    assert step["result"]["available"] is True
    assert step["result"]["truncated"] is True
    assert len(step["result"]["preview"]) < 500
    assert step["result"]["size_chars"] > 5_000_000
    assert "html" in step["result"]["keys"]


def test_core_uses_effective_server_status(monkeypatch):
    from aegis_ai.web import ui_overview

    runtime = _runtime()
    monkeypatch.setattr(
        ui_overview,
        "_server_list",
        lambda _runtime: [
            {"server_id": "ai-server", "status": "ONLINE"},
            {"server_id": "android-server", "status": "ONLINE", "mode": "reverse_stream"},
            {"server_id": "room-server", "status": "UNCONFIGURED"},
        ],
    )

    overview = build_ui_overview(runtime)

    assert "android-server" not in overview["core"]["data"]["offline_servers"]
    assert overview["core"]["data"]["health"] == "ONLINE"


def test_display_queue_resolves_android_disconnected():
    class AndroidEvents(_EventManager):
        def list_recent(self, limit=50, cursor=None):
            return {
                "events": [
                    {
                        "event_id": "evt-android-disconnect",
                        "event_type": "android.disconnected",
                        "timestamp": 1000,
                        "payload": {"device_id": "ed96f3f7", "connection_id": "android_abc", "reason": "stream closed"},
                    },
                    {
                        "event_id": "evt-android-connect",
                        "event_type": "android.connected",
                        "timestamp": 2000,
                        "payload": {"device_id": "ed96f3f7", "connection_id": "android_def", "connection_mode": "reverse_stream"},
                    },
                ],
            }

    runtime = _runtime()
    runtime.event_manager = AndroidEvents()
    overview = build_ui_overview(runtime)

    items = overview["display_queue"]["data"]["items"]
    assert all("android.disconnected" not in item.get("title", "") for item in items), (
        f"android.disconnected should be resolved: {items}"
    )


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
    assert normalized["event_id"]
    assert normalized["priority"] == "P0"
    assert normalized["dedupe_key"]
    assert normalized["visual_hint"]["effect"] == "fracture"
    assert normalized["affected_servers"] == ["android-server"]
    assert normalized["affected_capabilities"] == ["android-server.screen.get_ui_tree"]
    assert normalized["server_id"] == "android-server"
    assert normalized["capability_id"] == "android-server.screen.get_ui_tree"
    assert normalized["task_id"] == "task-1"
    assert normalized["severity"] == "critical"
    assert normalized["message"] == "permission missing"
    assert normalized["scene_type"] == "critical"
    assert normalized["privacy_class"] == "normal"
    assert "presentation_event" in normalized
    assert "dedicated_display" in normalized["presentation_event"]["recommended_surfaces"]
    assert "mobile_app" in normalized["presentation_event"]["recommended_surfaces"]
