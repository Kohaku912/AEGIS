from __future__ import annotations

from types import SimpleNamespace

from flask import Flask

from aegis_ai.web.routes.ui import init_ui_routes
from aegis_ai.web.routes.ui_v2 import init_ui_v2_routes
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


class _UserStateManager:
    def get_current_user_state(self):
        return {
            "where": {"label": "home", "confidence": 0.9},
            "attention": {"device": "pc", "label": "focused", "confidence": 0.8},
            "activity": {"label": "coding", "confidence": 0.7},
            "updated_at_ms": 1234,
        }


def _runtime():
    return SimpleNamespace(
        status_manager=_StatusManager(),
        approval_manager=_ApprovalManager(),
        task_manager=_TaskManager(),
        notification_manager=_NotificationManager(),
        memory_manager=_MemoryManager(),
        event_manager=_EventManager(),
        presentation_manager=_PresentationManager(),
        user_state_manager=_UserStateManager(),
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
        "agent_state",
        "goals",
        "initiative",
        "continuations",
        "repairs",
        "social",
        "behavioral_reports",
        "open_loops",
        "decision_context",
        "generated_capabilities",
        "executions",
        "situation",
    ]:
        value = overview[section]
        assert {"generated_at", "source_updated_at", "status", "stale", "error", "data"} <= set(value)

    assert overview["schema_version"] == "ui-overview.v4"
    assert overview["user_state"] is overview["user_situation"] or overview["user_state"]["data"] == overview["user_situation"]["data"]
    assert overview["mind"] is overview["mind_summary"] or overview["mind"]["data"] == overview["mind_summary"]["data"]
    assert "items" in overview["open_loops"]["data"]
    assert "operations" in overview["activity"]["data"] or "groups" in overview["activity"]["data"]
    ops = overview["activity"]["data"].get("operations") or []
    if ops:
        assert "causal_chain" in ops[0]
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
    assert overview["user_state"]["data"]["activity"]["label"] == "coding"


def test_ui_overview_route_returns_normalized_contract():
    app = Flask(__name__)
    owner = SimpleNamespace(app=app, _runtime=_runtime())
    init_ui_routes(owner)

    response = app.test_client().get("/api/ui/overview")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["schema_version"] == "ui-overview.v4"
    assert payload["servers"]["data"]["items"]
    assert payload["tasks"]["data"]["primary"]["task_id"] == "task-1"
    assert "open_loops" in payload
    assert "social" in payload
    assert "decision_context" in payload
    assert payload["errors"]["data"].get("source") in {None, "repair_manager", "audit"} or "items" in payload["errors"]["data"]


def test_display_power_state_route_is_compact_and_runtime_backed():
    app = Flask(__name__)
    owner = SimpleNamespace(app=app, _runtime=_runtime())
    init_ui_v2_routes(owner)

    response = app.test_client().get(
        "/display/power-state",
        headers={"Host": "127.0.0.1:8090"},
        environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["schema_version"] == "display-power-state.v1"
    assert payload["current_task"]["task_id"] == "task-1"
    assert payload["approvals"] == {"pending_count": 1, "ids": ["approval-1"]}
    assert payload["keep_awake"] is True
    assert {server["server_id"] for server in payload["servers"]} == {
        "ai-server",
        "pc-server",
    }


def test_display_power_state_ignores_autonomous_planning_without_operation():
    runtime = _runtime()
    runtime.approval_manager = SimpleNamespace(list_pending=lambda: [])
    runtime.task_manager = SimpleNamespace(
        list_running=lambda: [
            {
                "task_id": "task-background",
                "source": "autonomous",
                "status": "running",
                "title": "Plan next maintenance cycle",
                "steps": [],
            }
        ],
        list_waiting_approval=lambda: [],
    )
    app = Flask(__name__)
    owner = SimpleNamespace(app=app, _runtime=runtime)
    init_ui_v2_routes(owner)

    response = app.test_client().get(
        "/display/power-state",
        headers={"Host": "127.0.0.1:8090"},
        environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["keep_awake"] is False
    assert not any(payload["current_task"].values())


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
    # Pure status/heartbeat noise is excluded from AEGIS operation activity.
    assert overview["activity"]["data"]["count"] == 1
    assert overview["activity"]["data"]["recent"][0]["event_id"] == "evt-approval"


def test_android_telemetry_is_activity_noise():
    from aegis_ai.web.ui_overview import _is_activity_noise_event, normalize_ui_event

    for event_type in (
        "android.heartbeat",
        "android.user_activity.changed",
        "android.foreground_app.changed",
        "android.connected",
    ):
        event = normalize_ui_event(
            {
                "event_id": f"evt-{event_type}",
                "event_type": event_type,
                "timestamp": 1000,
                "payload": {},
            }
        )
        assert _is_activity_noise_event(event), event_type

    title_only = {
        "event_type": "activity.updated",
        "safe_title": "android-server android.heartbeat",
        "message": "android.heartbeat",
    }
    assert _is_activity_noise_event(title_only)

    approval = normalize_ui_event(
        {
            "event_id": "evt-appr",
            "event_type": "android.approval.decided",
            "timestamp": 1000,
            "payload": {"approval_id": "appr_1"},
        }
    )
    assert not _is_activity_noise_event(approval)


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


def test_android_connection_metrics_are_in_server_dependencies(monkeypatch):
    from aegis_ai.web import dashboard_legacy, ui_overview

    runtime = _runtime()
    runtime.android_manager = SimpleNamespace(
        get_status=lambda: {
            "online": True,
            "connection_mode": "reverse_stream",
            "device_model": "21121210G",
            "reconnect_count": 3,
            "heartbeat_failure_count": 1,
        }
    )
    monkeypatch.setattr(
        dashboard_legacy,
        "_runtime_server_status",
        lambda runtime: {"servers": [{"server_id": "android-server", "status": "OFFLINE"}]},
    )

    servers = ui_overview._server_list(runtime)
    android = next(item for item in servers if item["server_id"] == "android-server")

    assert android["dependencies"]["reconnect_count"] == 3
    assert android["dependencies"]["heartbeat_failure_count"] == 1


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


def test_normalize_ui_event_humanizes_json_payload_messages():
    event = SimpleNamespace(
        event_type="pc.user_activity.snapshot",
        timestamp=1234,
        payload={
            "message": '{"timestamp_ms": 1, "active_window_title": "Overwatch", "app_name": "Overwatch"}',
            "capability_id": "pc-server.user_activity.snapshot",
        },
    )

    normalized = normalize_ui_event(event)

    assert normalized["message"] == "Overwatch"
    assert "{" not in normalized["message"]


def test_activity_operations_prefer_aegis_audit_groups():
    class AuditManager:
        def list_groups(self, page=1, per_page=20, group_type=None, errors_only=False, max_entries=400):
            return {
                "groups": [
                    {
                        "group_id": "req-chat-1",
                        "group_type": "chat",
                        "title": "Check AGORA posts",
                        "start_ms": 1000,
                        "end_ms": 2000,
                        "status": "success",
                        "entry_count": 2,
                        "tool_count": 1,
                        "approval_count": 0,
                        "error_count": 0,
                        "summary": "Retrieved 3 posts",
                        "entries": [
                            {
                                "action": "tool_execution",
                                "capability_id": "ai-server.agora.get_posts",
                                "detail_summary": "Retrieved 3 posts",
                                "decision": "allow",
                                "timestamp_ms": 1500,
                            },
                            {
                                "action": "llm_call",
                                "capability_id": "",
                                "detail_summary": "I checked AGORA and found 3 new posts about the weekend plan.",
                                "detail": {
                                    "response_preview": "I checked AGORA and found 3 new posts about the weekend plan.",
                                    "model": "deepseek-chat",
                                },
                                "decision": "success",
                                "timestamp_ms": 1800,
                            },
                            {
                                "action": "status_changed",
                                "capability_id": "",
                                "detail_summary": "android online",
                                "timestamp_ms": 1600,
                            },
                        ],
                    },
                    {
                        "group_id": "sys-noise",
                        "group_type": "system",
                        "title": "android heartbeat",
                        "start_ms": 3000,
                        "end_ms": 3000,
                        "status": "success",
                        "entry_count": 1,
                        "tool_count": 0,
                        "approval_count": 0,
                        "error_count": 0,
                        "summary": "heartbeat",
                        "entries": [{"action": "server_heartbeat", "timestamp_ms": 3000}],
                    },
                ]
            }

    runtime = _runtime()
    runtime.audit_manager = AuditManager()
    overview = build_ui_overview(runtime)
    operations = overview["activity"]["data"]["operations"]

    assert len(operations) == 1
    op = operations[0]
    assert op["kind"] == "chat"
    assert op["kind_label"] == "ユーザー指示"
    assert op["title"] == "Check AGORA posts"
    assert "I checked AGORA and found 3 new posts" in op["what_happened"]
    assert "ai-server.agora.get_posts" not in op["what_happened"]
    assert all(step.get("action") != "status_changed" for step in op["steps"])


def test_activity_what_happened_unwraps_legacy_response_kv():
    from aegis_ai.web.ui_overview import _humanize_activity_text, _what_happened_from_steps

    assert "Found three posts" in _humanize_activity_text(
        "response=Found three posts, model=deepseek, tokens=12"
    )
    text = _what_happened_from_steps(
        [
            {
                "action": "llm_call",
                "summary": "response=I already replied to the user., model=x",
                "narrative": "response=I already replied to the user., model=x",
            }
        ],
        fallback="",
    )
    assert text == "I already replied to the user."


def test_autonomous_activity_prefers_fulfillment_result_over_internal_llm_calls():
    from aegis_ai.web.ui_overview import _operation_from_audit_group

    operation = _operation_from_audit_group(
        {
            "group_id": "autonomous-result",
            "group_type": "autonomous",
            "title": "Advance the social obligation",
            "start_ms": 1000,
            "end_ms": 2000,
            "status": "success",
            "entry_count": 3,
            "tool_count": 1,
            "approval_count": 0,
            "error_count": 0,
            "summary": "LLM call completed",
            "entries": [
                *[
                    {
                        "action": "llm_call",
                        "detail_summary": '{"decision":"read_posts"}',
                        "timestamp_ms": 1000 + index,
                    }
                    for index in range(15)
                ],
                {
                    "action": "tool_execution",
                    "capability_id": "ai-server.agora.read_posts",
                    "detail_summary": "Ran read posts",
                    "timestamp_ms": 1500,
                },
                {
                    "action": "autonomous_fulfillment_evaluated",
                    "detail": {"reason": "Retrieved 7 social posts and queued them for review."},
                    "timestamp_ms": 2000,
                },
            ],
        }
    )

    assert operation is not None
    assert operation["what_happened"] == "Retrieved 7 social posts and queued them for review."
    assert operation["target"] == "ai-server.agora.read_posts"
    assert '{"decision"' not in operation["what_happened"]


def test_autonomous_activity_without_execution_does_not_list_internal_llm_calls():
    from aegis_ai.web.ui_overview import _operation_from_audit_group

    operation = _operation_from_audit_group(
        {
            "group_id": "autonomous-evaluation",
            "group_type": "autonomous",
            "title": "Autonomous execution cycle",
            "start_ms": 1000,
            "end_ms": 2000,
            "status": "success",
            "entry_count": 2,
            "tool_count": 0,
            "approval_count": 0,
            "error_count": 0,
            "summary": "LLM call completed",
            "entries": [
                {
                    "action": "llm_call",
                    "detail_summary": "LLM call (deepseek-v4-flash)",
                    "timestamp_ms": 1000,
                },
                {
                    "action": "autonomous_tick",
                    "detail_summary": "Autonomous tick (task_generation)",
                    "timestamp_ms": 2000,
                },
            ],
        }
    )

    assert operation is not None
    assert operation["what_happened"] == (
        "AEGIS evaluated the current situation but did not execute a capability."
    )
    assert "LLM call" not in operation["what_happened"]


def test_usage_projection_uses_audit_totals_instead_of_not_reported():
    from aegis_ai.web.ui_overview import _usage_projection

    projected = _usage_projection({"total_calls": 12, "total_tokens": 3400, "estimated_cost": 0.02})
    assert projected["budget_state"] == "ready"
    assert projected["total_calls"] == 12
    assert projected["total_tokens"] == 3400
    assert "3400" in projected["summary"]


def test_initiative_record_has_title_for_ui_lists():
    from aegis_ai.web.ui_overview import _initiative_record

    record = _initiative_record({"decision": "observe_more", "reason": "pressure below threshold"})
    assert record["title"] == "observe_more"
    assert record["summary"] == "pressure below threshold"
