from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace


def test_get_runtime_returns_shared_singleton(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))

    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    first = get_runtime()
    second = get_runtime()

    assert first is second
    assert first.tool_registry is second.tool_registry
    assert first.tool_broker is second.tool_broker
    assert first.policy_engine is second.policy_engine
    assert first.event_bus is second.event_bus
    assert first.audit_log is second.audit_log
    assert first.llm_router is second.llm_router

    reset_runtime_for_tests()
    third = get_runtime()
    assert third is not first
    reset_runtime_for_tests()


def test_entry_points_share_runtime_instances(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")

    from aegis_ai.grpc_server import AegisAIServicer
    from aegis_ai.interaction.channels.cli import CLIChannel
    from aegis_ai.interaction.channels.web import WebChatApp
    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests
    from aegis_ai.web.dashboard_routes import DashboardApp

    reset_runtime_for_tests()
    runtime = get_runtime()

    dashboard = DashboardApp(runtime=runtime)
    web_chat = WebChatApp(router=runtime.interaction_router, session_manager=runtime.session_manager)
    cli = CLIChannel(router=runtime.interaction_router, session_manager=runtime.session_manager)
    servicer = AegisAIServicer(runtime)

    assert dashboard._runtime is runtime
    assert web_chat._router is runtime.interaction_router
    assert web_chat._sessions is runtime.session_manager
    assert cli._router is runtime.interaction_router
    assert cli._sessions is runtime.session_manager
    assert servicer._runtime is runtime

    reset_runtime_for_tests()


def test_grpc_servicer_uses_runtime_state(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")

    from generated.aegis import ai_server_pb2, common_pb2
    from aegis_ai.grpc_server import AegisAIServicer
    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    runtime = get_runtime()
    servicer = AegisAIServicer(runtime)

    cap = common_pb2.Capability(
        id="ai-server.test.echo",
        name="Echo",
        description="Echo test capability",
        server_type=common_pb2.SERVER_TYPE_AI,
        safety_level=common_pb2.LEVEL_0_READ,
    )
    register_response = servicer.RegisterCapability(
        ai_server_pb2.RegisterCapabilityRequest(capability=cap),
        None,
    )
    assert register_response.status.code == 0
    assert runtime.tool_registry.get_capability("ai-server.test.echo") is not None

    listed = servicer.ListCapabilities(ai_server_pb2.ListCapabilitiesRequest(), None)
    assert any(item.id == "ai-server.test.echo" for item in listed.capabilities)

    event = common_pb2.Event(
        event_id="evt_runtime_test",
        event_type="test.runtime",
        source_server_type=common_pb2.SERVER_TYPE_AI,
        source_server_id="ai-server",
        payload_json="{}",
        priority=common_pb2.EVENT_PRIORITY_NORMAL,
    )
    push_response = servicer.PushEvent(ai_server_pb2.PushEventRequest(event=event), None)
    assert push_response.status.code == 0
    assert runtime.event_bus.list_recent_events(1)[-1].event_id == "evt_runtime_test"

    calls: list[tuple[str, dict[str, str]]] = []

    def fake_execute(request):
        calls.append((request.capability_id, request.arguments))
        return SimpleNamespace(
            success=True,
            output={"ok": True},
            error="",
            duration_ms=3,
            request_id=request.request_id or "inv_test",
        )

    runtime.tool_broker.execute = fake_execute
    invoke_response = servicer.InvokeTool(
        common_pb2.ToolInvocationRequest(
            capability_id="ai-server.test.echo",
            invocation_id="inv_test",
            caller="pytest",
            params_json=json.dumps({"value": "hello"}),
        ),
        None,
    )

    assert invoke_response.status.code == 0
    assert json.loads(invoke_response.output_json) == {"ok": True}
    assert calls == [("ai-server.test.echo", {"value": "hello"})]
    reset_runtime_for_tests()


def test_grpc_send_chat_preserves_response_shape(monkeypatch, tmp_path) -> None:
    from generated.aegis import ai_server_pb2, common_pb2
    from aegis_ai.grpc_server import AegisAIServicer
    from aegis_ai.web import chat_service

    class FakeAndroidManager:
        def __init__(self) -> None:
            self.messages = []

        def broadcast_chat_update(self, messages):
            self.messages.append(messages)
            return 1

    fake_android = FakeAndroidManager()
    runtime = SimpleNamespace(config=SimpleNamespace(), android_manager=fake_android)
    servicer = AegisAIServicer(runtime)

    health = servicer.HealthCheck(common_pb2.HealthCheckRequest(), None)
    assert "sendchat" in health.version.lower()

    def fake_execute_chat_message(runtime, text, *, origin_channel, conversation_id, device_id, context, task_source):
        assert text == "スマホの画面を確認して"
        assert origin_channel == "android_app"
        assert device_id == "device_1"
        assert context == {"surface": "android_app"}
        assert task_source == "android_chat"
        return {
            "conversation_id": conversation_id,
            "response": "画面にはホーム画面が表示されています。",
            "approval_needed": True,
            "approval_id": "appr_1",
            "tool_results": [{"function": "android-server__screen__get_screenshot", "success": True}],
        }

    monkeypatch.setattr(chat_service, "execute_chat_message", fake_execute_chat_message)
    monkeypatch.chdir(tmp_path)

    response = servicer.SendChat(
        ai_server_pb2.ChatRequest(
            conversation_id="conv_1",
            text="スマホの画面を確認して",
            device_id="device_1",
            context={"surface": "android_app"},
        ),
        None,
    )

    assert response.status.code == 0
    assert response.conversation_id == "conv_1"
    assert response.response == "画面にはホーム画面が表示されています。"
    assert response.approval_needed is True
    assert response.approval_id == "appr_1"
    assert json.loads(response.tool_results_json)[0]["success"] is True
    assert fake_android.messages
    assert "画面にはホーム画面" in (tmp_path / "data" / "chat_history.jsonl").read_text(encoding="utf-8")


def test_grpc_mobile_dashboard_state_reads_shared_history(monkeypatch, tmp_path) -> None:
    from generated.aegis import ai_server_pb2
    from aegis_ai.grpc_server import AegisAIServicer
    from aegis_ai.web.chat_history import ChatHistoryStore

    monkeypatch.chdir(tmp_path)
    ChatHistoryStore().append("hello", "hi", source="dashboard", conversation_id="conv_1")

    runtime = SimpleNamespace(
        config=SimpleNamespace(),
        status_manager=SimpleNamespace(
            get_snapshot=lambda: {
                "ai-server": {"status": "online"},
                "pc-server": {"status": "offline", "error": "down"},
                "browser-server": {"status": "online"},
                "android-server": {"status": "online"},
                "room-server": {"status": "unknown"},
                "dashboard": {"status": "online"},
            }
        ),
        android_manager=SimpleNamespace(
            get_status=lambda: {
                "online": True,
                "connection_mode": "reverse_stream",
                "capability_availability": {},
                "permission_status": {"screenshot": False},
                "active_approvals": [],
                "pairing_configured": True,
            }
        ),
    )
    servicer = AegisAIServicer(runtime)

    response = servicer.GetMobileDashboardState(
        ai_server_pb2.MobileDashboardStateRequest(device_id="device_1", history_limit=10),
        None,
    )

    assert response.status.code == 0
    assert {item.server_id for item in response.server_statuses} >= {"ai-server", "pc-server", "android-server"}
    assert [item.text for item in response.chat_history] == ["hello", "hi"]
    assert any("screenshot" in warning for warning in response.warnings)


def test_shared_components_thread_safety_smoke(tmp_path) -> None:
    from approval import ApprovalStore
    from event_bus import EventBus
    from tool_registry import ToolRegistry

    from aegis_ai.audit import AuditEntry, AuditLog
    from aegis_schema.models import Capability, Event, EventPriority, RiskLevel, ServerType

    registry = ToolRegistry()
    bus = EventBus()
    approvals = ApprovalStore()
    audit = AuditLog(path=str(tmp_path / "audit.jsonl"))

    def worker(index: int) -> None:
        cap_id = f"ai-server.thread.cap_{index}"
        registry.register_capability(
            Capability(
                id=cap_id,
                name=f"Cap {index}",
                description="Thread smoke capability",
                server_type=ServerType.AI,
                risk_level=RiskLevel.READ_ONLY,
            )
        )
        bus.publish(
            Event(
                event_id=f"event_{index}",
                event_type="thread.smoke",
                source_server_type=ServerType.AI,
                source_server_id="pytest",
                priority=EventPriority.NORMAL,
            )
        )
        req = approvals.create_request(capability_id=cap_id)
        approvals.approve_once(req.approval_id)
        audit.append(AuditEntry(action="thread_smoke", capability_id=cap_id, decision="ALLOW"))

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(worker, range(20)))

    assert len(registry) == 20
    assert bus.pending_count() == 20
    assert len(approvals.get_approved_capabilities()) == 20
    assert len(audit.read_all()) == 20
    assert Path(tmp_path / "audit.db").exists()
