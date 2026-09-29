from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    """Boot the real runtime, but never leave it running.

    ``get_runtime()`` starts a ``status-check`` daemon thread. That thread is not an
    idle poller: it re-resolves pc-server/room-server with ``allow_lan_scan=True``, so
    it probes the real LAN and records the result in the endpoint resolver's
    process-global cache. Tests in this module boot the runtime and several of them
    never reset it, so the thread used to outlive them and corrupt
    ``tests/test_endpoint_resolver.py``, which asserts on that same cache.

    ``AegisRuntime.stop()`` now stops the thread; this fixture makes sure ``stop()``
    is actually reached at the end of every test in the module. The conftest leak
    guard would otherwise name each offending test individually.
    """
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()


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
    store = first.memory_manager.get_backend("store")
    assert store is not None
    assert store is first.context_builder._memory_store
    assert getattr(first.sleep_manager, "_retention", None) is not None

    reset_runtime_for_tests()
    third = get_runtime()
    assert third is not first
    reset_runtime_for_tests()


def test_entry_points_share_runtime_instances(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")

    from aegis_ai.grpc_server import AegisAIServicer
    from aegis_ai.interaction.channels.cli import CLIChannel
    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests
    from aegis_ai.web.dashboard_routes import DashboardApp

    reset_runtime_for_tests()
    runtime = get_runtime()

    dashboard = DashboardApp(runtime=runtime)
    cli = CLIChannel(router=runtime.interaction_router, session_manager=runtime.session_manager)
    servicer = AegisAIServicer(runtime)

    assert dashboard._runtime is runtime
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
    # Read a wide window: pushing one event may trigger a variable number of
    # downstream pipeline events (l1.observation -> l1.decision -> ... -> l2.*),
    # so asserting membership within the top 5 is not a stable invariant.
    # The invariant that matters is that the pushed event reached the runtime bus.
    recent_events = runtime.event_bus.list_recent_events(50)
    recent_ids = [item.event_id for item in recent_events]
    recent_types = [item.event_type for item in recent_events]
    assert "evt_runtime_test" in recent_ids
    assert "l1.observation" in recent_types
    assert "l1.decision" in recent_types

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


def test_invoke_tool_denies_remote_without_token(monkeypatch) -> None:
    monkeypatch.delenv("AEGIS_GRPC_INVOKE_TOKEN", raising=False)
    from generated.aegis import common_pb2
    from aegis_ai.grpc_server import AegisAIServicer

    runtime = SimpleNamespace(config=None, android_manager=None, tool_broker=SimpleNamespace())
    servicer = AegisAIServicer(runtime)
    request = common_pb2.ToolInvocationRequest(
        capability_id="ai-server.test.echo",
        invocation_id="inv_denied",
        caller="remote",
        params_json="{}",
    )

    class RemoteContext:
        def peer(self) -> str:
            return "ipv4:10.0.0.8:55555"

        def invocation_metadata(self):
            return ()

    response = servicer.InvokeTool(request, RemoteContext())
    assert response.status.code == 16
    assert "loopback" in response.error.lower() or "token" in response.error.lower()


def test_invoke_tool_allows_remote_with_token(monkeypatch) -> None:
    monkeypatch.setenv("AEGIS_GRPC_INVOKE_TOKEN", "invoke-secret")
    from generated.aegis import common_pb2
    from aegis_ai.grpc_server import AegisAIServicer

    calls: list[str] = []

    def fake_execute(request):
        calls.append(request.capability_id)
        return SimpleNamespace(
            success=True,
            output={"ok": True},
            error="",
            duration_ms=1,
            request_id=request.request_id or "inv_ok",
        )

    runtime = SimpleNamespace(
        config=None,
        android_manager=None,
        tool_broker=SimpleNamespace(execute=fake_execute),
    )
    servicer = AegisAIServicer(runtime)
    request = common_pb2.ToolInvocationRequest(
        capability_id="ai-server.test.echo",
        invocation_id="inv_ok",
        caller="remote",
        params_json="{}",
    )

    class RemoteContext:
        def peer(self) -> str:
            return "ipv4:10.0.0.8:55555"

        def invocation_metadata(self):
            return (("x-aegis-invoke-token", "invoke-secret"),)

    response = servicer.InvokeTool(request, RemoteContext())
    assert response.status.code == 0
    assert calls == ["ai-server.test.echo"]


def test_peer_is_loopback_parses_grpc_peer_formats() -> None:
    from aegis_ai.grpc_server import _peer_is_loopback

    class LoopbackContext:
        def __init__(self, peer_value: str) -> None:
            self._peer_value = peer_value

        def peer(self) -> str:
            return self._peer_value

    assert _peer_is_loopback(LoopbackContext("ipv4:127.0.0.1:50051")) is True
    assert _peer_is_loopback(LoopbackContext("ipv6:[::1]:50051")) is True
    assert _peer_is_loopback(LoopbackContext("dns:localhost:50051")) is True
    assert _peer_is_loopback(LoopbackContext("unix:/tmp/aegis.sock")) is True
    assert _peer_is_loopback(LoopbackContext("dns:localhost.attacker:50051")) is False
    assert _peer_is_loopback(LoopbackContext("ipv4:10.0.0.8:50051")) is False


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
    # The forced approval gate is gone, and as of 2026-09-28 so are its wire
    # fields: `ChatResponse` no longer declares `approval_needed` / `approval_id`
    # at all, rather than keeping them permanently empty.
    assert not hasattr(response, "approval_needed")
    assert not hasattr(response, "approval_id")
    assert json.loads(response.tool_results_json)[0]["success"] is True
    assert fake_android.messages
    assert "画面にはホーム画面" in (tmp_path / "data" / "chat_history.jsonl").read_text(encoding="utf-8")


def test_android_direct_chat_requires_pairing_auth_when_configured(monkeypatch, tmp_path) -> None:
    from generated.aegis import ai_server_pb2, android_server_pb2
    from aegis_ai.grpc_server import AegisAIServicer
    from aegis_ai.web import chat_service

    class FakeAndroidManager:
        def validate_direct_rpc_auth(self, auth, *, fallback_device_id: str = ""):
            if getattr(auth, "pairing_token", "") == "good_token":
                return True, getattr(auth, "device_id", "") or fallback_device_id, "ok"
            return False, getattr(auth, "device_id", "") or fallback_device_id, "ANDROID_AUTH_REQUIRED"

        def broadcast_chat_update(self, messages):
            return 1

    runtime = SimpleNamespace(config=SimpleNamespace(), android_manager=FakeAndroidManager())
    servicer = AegisAIServicer(runtime)

    unauthenticated = servicer.SendChat(
        ai_server_pb2.ChatRequest(text="hello", device_id="device_1"),
        None,
    )

    assert unauthenticated.status.code == 16
    assert unauthenticated.status.message == "ANDROID_AUTH_REQUIRED"

    def fake_execute_chat_message(runtime, text, *, origin_channel, conversation_id, device_id, context, task_source):
        return {"conversation_id": conversation_id, "response": "ok"}

    monkeypatch.setattr(chat_service, "execute_chat_message", fake_execute_chat_message)
    monkeypatch.chdir(tmp_path)
    authenticated = servicer.SendChat(
        ai_server_pb2.ChatRequest(
            text="hello",
            device_id="device_1",
            auth=android_server_pb2.AndroidAuth(
                device_id="device_1",
                pairing_token="good_token",
                connection_id="conn_1",
            ),
        ),
        None,
    )

    assert authenticated.status.code == 0
    assert authenticated.response == "ok"


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
    from event_bus import EventBus
    from tool_registry import ToolRegistry

    from aegis_ai.audit import AuditEntry, AuditLog
    from aegis_schema.models import Capability, Event, EventPriority, RiskLevel, ServerType

    registry = ToolRegistry()
    bus = EventBus()
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
        audit.append(AuditEntry(action="thread_smoke", capability_id=cap_id, decision="ALLOW"))

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(worker, range(20)))

    assert len(registry) == 20
    assert bus.pending_count() == 20
    assert len(audit.read_all()) == 20
    assert Path(tmp_path / "audit.db").exists()


def test_run_l1_pipeline_publishes_observation_decision_and_escalation() -> None:
    from aegis_ai.runtime import _get_recent_l1_summaries, _run_l1_pipeline_for_event

    published: list[tuple[str, str, dict[str, object]]] = []

    class FakeEventManager:
        def publish_event(self, event_type: str, *, source: str, payload: dict[str, object]) -> bool:
            published.append((event_type, source, dict(payload)))
            return True

    obs = SimpleNamespace(
        event_id="evt-l1-1",
        meaning="New inbox item needs attention",
        value=0.8,
        priority=0.7,
        required_intelligence=SimpleNamespace(value="high"),
        confidence=0.9,
        raw={"meaning": "New inbox item needs attention"},
    )
    decision = SimpleNamespace(
        event_id="evt-l1-1",
        action=SimpleNamespace(
            type=SimpleNamespace(value="escalate"),
            capability_id="",
            args={},
            reason="needs deeper reasoning",
        ),
        reasoning="L1 escalates to L2",
        observation=obs,
    )

    class FakeL1Router:
        def observe(self, event, *, event_id="", context_capsule=None):
            assert event["type"] == "social.inbox.received"
            assert event_id == "evt-l1-1"
            assert isinstance(context_capsule, dict)
            return obs

        def decide(self, observation):
            assert observation is obs
            return decision

        def escalate(self, observation, *, reason=""):
            assert observation is obs
            return SimpleNamespace(
                to_payload=lambda: {
                    "event_id": "evt-l1-1",
                    "reason": reason,
                    "problem": obs.meaning,
                }
            )

    runtime = SimpleNamespace(
        l1_router=FakeL1Router(),
        l1_executor=None,
        event_manager=FakeEventManager(),
    )
    event = SimpleNamespace(
        event_id="evt-l1-1",
        event_type="social.inbox.received",
        payload_json='{"message":"hello"}',
        timestamp_ms=1234,
        source_server_id="android-server",
        source_server_type=SimpleNamespace(name="ANDROID"),
    )

    returned = _run_l1_pipeline_for_event(runtime, event)

    assert returned is decision
    assert [kind for kind, _, _ in published] == ["l1.observation", "l1.decision", "l1.escalation"]
    summaries = _get_recent_l1_summaries(runtime, limit=5)
    assert summaries[-1]["event_type"] == "social.inbox.received"
    assert summaries[-1]["meaning"] == "New inbox item needs attention"
    assert summaries[-1]["action_type"] == "escalate"


def test_run_l1_pipeline_executes_low_risk_capability_action() -> None:
    from aegis_ai.runtime import _run_l1_pipeline_for_event

    published: list[str] = []

    class FakeEventManager:
        def publish_event(self, event_type: str, *, source: str, payload: dict[str, object]) -> bool:
            published.append(event_type)
            return True

    obs = SimpleNamespace(
        event_id="evt-l1-cap-1",
        meaning="Capture a safe snapshot",
        value=0.6,
        priority=0.4,
        required_intelligence=SimpleNamespace(value="low"),
        confidence=0.8,
        raw={},
    )
    decision = SimpleNamespace(
        event_id="evt-l1-cap-1",
        action=SimpleNamespace(
            type=SimpleNamespace(value="capability"),
            capability_id="pc-server.screenshot.get_screenshot",
            args={"display": 0},
            reason="simple low-risk observation",
        ),
        reasoning="L1 can handle this directly",
        observation=obs,
    )

    class FakeL1Router:
        def observe(self, event, *, event_id="", context_capsule=None):
            assert context_capsule["user_state"]["current_activity"] == "coding"
            assert context_capsule["task_state"]["active_task_count"] == 1
            return obs

        def decide(self, observation):
            return decision

    class FakeL1Executor:
        def execute(self, capability_id, args, *, event_id=""):
            assert capability_id == "pc-server.screenshot.get_screenshot"
            assert args == {"display": 0}
            assert event_id == "evt-l1-cap-1"
            return SimpleNamespace(
                to_payload=lambda: {
                    "capability_id": capability_id,
                    "event_id": event_id,
                    "success": True,
                }
            )

    runtime = SimpleNamespace(
        l1_router=FakeL1Router(),
        l1_executor=FakeL1Executor(),
        event_manager=FakeEventManager(),
        user_state_manager=SimpleNamespace(
            get_current_user_state=lambda: {
                "attention": {"device": "pc", "app": "vscode"},
                "activity": {"label": "coding", "confidence": 0.8},
            }
        ),
        task_manager=SimpleNamespace(
            list_tasks=lambda limit=20: [
                {"task_id": "t1", "status": "running", "title": "Investigate L1"}
            ]
        ),
    )
    event = SimpleNamespace(
        event_id="evt-l1-cap-1",
        event_type="android.permission.changed",
        payload_json="{}",
        timestamp_ms=99,
        source_server_id="android-server",
        source_server_type=SimpleNamespace(name="ANDROID"),
    )

    _run_l1_pipeline_for_event(runtime, event)

    assert published == [
        "l1.observation",
        "l1.decision",
        "l1.capability.invoked",
        "l1.capability.completed",
    ]


def test_l1_routing_helpers_cover_user_activity_and_exclude_internal_noise() -> None:
    from aegis_ai.runtime import (
        _should_route_to_l1_background,
        _should_route_to_l1_immediate,
    )

    assert _should_route_to_l1_immediate("android.user_activity.changed") is True
    assert _should_route_to_l1_immediate("android.foreground_app.changed") is True
    assert _should_route_to_l1_immediate("android.current_app_changed") is True
    assert _should_route_to_l1_immediate("pc.user_activity.snapshot") is True
    assert _should_route_to_l1_immediate("browser.user_activity.changed") is True
    assert _should_route_to_l1_immediate("hook.matched") is True
    assert _should_route_to_l1_immediate("self_call") is True

    assert _should_route_to_l1_background("memory.written") is True
    assert _should_route_to_l1_background("notification.sent") is True
    assert _should_route_to_l1_background("presentation.created") is False
    assert _should_route_to_l1_background("l1.observation") is False
    assert _should_route_to_l1_background("android.user_activity.changed") is False


def test_immediate_user_activity_events_are_not_debounced(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")

    from generated.aegis import ai_server_pb2, common_pb2
    from aegis_ai.grpc_server import AegisAIServicer
    from aegis_ai.intake.l1_models import (
        L1Action,
        L1ActionType,
        L1Decision,
        L1Observation,
        RequiredIntelligence,
    )
    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    runtime = get_runtime()
    servicer = AegisAIServicer(runtime)

    observe_calls: list[str] = []

    def fake_observe(event, *, event_id="", context_capsule=None):
        observe_calls.append(event_id)
        return L1Observation(
            event_id=event_id,
            meaning="pc activity",
            value=0.9,
            priority=0.9,
            required_intelligence=RequiredIntelligence.LOW,
            confidence=0.9,
            raw={"summary_bucket": "user_state", "observed_action": "editing code", "possible_intent": "continue coding"},
        )

    def fake_decide(observation):
        return L1Decision(
            action=L1Action(type=L1ActionType.OBSERVE, reason="observe"),
            reasoning="user activity should still be observed",
            observation=observation,
        )

    runtime.l1_router.observe = fake_observe
    runtime.l1_router.decide = fake_decide

    for idx in range(3):
        event = common_pb2.Event(
            event_id=f"evt_user_activity_{idx}",
            event_type="pc.user_activity.snapshot",
            source_server_type=common_pb2.SERVER_TYPE_PC,
            source_server_id="pc-server",
            payload_json=json.dumps({"activity": "coding", "window_title": f"file{idx}.py"}),
            priority=common_pb2.EVENT_PRIORITY_NORMAL,
        )
        push_response = servicer.PushEvent(ai_server_pb2.PushEventRequest(event=event), None)
        assert push_response.status.code == 0

    assert observe_calls == [
        "evt_user_activity_0",
        "evt_user_activity_1",
        "evt_user_activity_2",
    ]
    reset_runtime_for_tests()


def test_build_l1_context_capsule_compacts_runtime_state() -> None:
    from aegis_ai.runtime import _build_l1_context_capsule

    runtime = SimpleNamespace(
        _recent_l1_summaries=[
            {
                "event_type": "social.inbox.received",
                "summary_bucket": "task_candidate",
                "meaning": "Need to reply to user",
                "action_type": "escalate",
                "priority": 0.9,
            }
        ],
        user_state_manager=SimpleNamespace(
            get_current_user_state=lambda: {
                "attention": {"device": "pc", "app": "vscode"},
                "activity": {"label": "coding", "confidence": 0.8},
            }
        ),
        user_understanding_service=SimpleNamespace(
            get_latest_snapshot=lambda: {
                "summary": "attention=pc, activity=coding, open_commitments=2",
                "identity_profile": {
                    "attention_device": "pc",
                    "current_activity": "coding",
                },
                "constraints": {"focus_mode": True},
                "likely_next_actions": [{"title": "Finish current patch"}],
                "predicted_deficits": [{"title": "Need regression verification"}],
            }
        ),
        status_manager=SimpleNamespace(
            get_snapshot=lambda: {
                "browser-server": {"status": "degraded"},
                "pc-server": {"status": "online"},
            }
        ),
        situation_model=SimpleNamespace(
            get_state=lambda: {"state": "focused", "interruptibility": "low"}
        ),
        task_manager=SimpleNamespace(
            list_tasks=lambda limit=20: [
                {"task_id": "t1", "status": "running", "title": "Investigate L1"},
                {"task_id": "t2", "status": "completed", "title": "Done"},
            ]
        ),
        commitment_manager=SimpleNamespace(
            list_commitments=lambda status="open": [
                {"kind": "reply", "summary": "Reply to user", "due_at_ms": 123}
            ]
        ),
        personal_data_core=SimpleNamespace(
            recent_facts=lambda limit=3: [
                {"statement": "User is currently coding", "confidence": 0.9}
            ]
        ),
    )

    capsule = _build_l1_context_capsule(runtime, {"type": "pc.user_activity.snapshot", "activity": "coding"})

    assert capsule["user_state"]["current_activity"] == "coding"
    assert capsule["user_understanding"]["focus_mode"] is True
    assert capsule["world_state"]["degraded_server_count"] == 1
    assert capsule["task_state"]["active_task_count"] == 1
    assert capsule["pending_obligations"][0]["summary"] == "Reply to user"
    assert capsule["recent_l1"][0]["summary_bucket"] == "task_candidate"
    assert capsule["recent_facts"][0]["statement"] == "User is currently coding"
