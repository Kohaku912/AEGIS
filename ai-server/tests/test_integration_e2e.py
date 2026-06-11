"""Integration E2E — multi-server integration and dangerous operation tests.

Verifies the full AEGIS pipeline:
- Browser read-only research
- PC observe → Support suggestion
- Android notification → Support suggestion
- Room temperature → Support suggestion
- Dev test failure → SelfDev proposal
- Scheduled daily briefing
- Approval-required action pause/resume
- Rejected action stops safely
- All dangerous operations denied

These tests MUST pass before any release.
"""

from __future__ import annotations

import json
import time
import uuid

from aegis_ai.agents.support import SupportAgent
from aegis_ai.audit import AuditLog
from aegis_ai.context_builder import ContextBuilder
from aegis_ai.memory.episodic import EpisodicMemory
from aegis_ai.memory.reflection import ReflectionLog
from aegis_ai.mind.desire import Desire
from aegis_ai.mind.emotion import Emotion
from aegis_ai.mind.goals import GoalManager
from aegis_ai.mind.identity import Identity
from aegis_ai.scheduler import ScheduledTask, Scheduler, TaskType
from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    RiskLevel,
    ServerType,
)
from approval import ApprovalStore, ApprovalType
from event_bus import EventBus
from policy_engine import PolicyDecision, PolicyEngine, create_default_policy_engine
from tool_broker import InvokeStatus, ToolBroker
from tool_registry import ToolRegistry
from trigger_engine import TriggerEngine, create_default_rules

# ── Helpers ──────────────────────────────────────────────────


def _make_event(
    event_type: str = "test.event",
    server_type: ServerType = ServerType.AI,
    severity: int = 3,
    priority: EventPriority = EventPriority.NORMAL,
    payload: str = "{}",
) -> Event:
    return Event(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        source_server_type=server_type,
        source_server_id="test-server",
        timestamp_ms=int(time.time() * 1000),
        payload_json=payload,
        severity=severity,
        priority=priority,
    )


def _setup_full_stack() -> tuple[
    EventBus, TriggerEngine, ToolRegistry, PolicyEngine,
    ToolBroker, AuditLog, ContextBuilder, SupportAgent,
    ApprovalStore, Scheduler,
]:
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)

    registry = ToolRegistry()
    store = ApprovalStore()
    policy = PolicyEngine(approval_store=store)
    broker = ToolBroker(registry, policy)
    audit = AuditLog(path="data/test_integration_audit.jsonl")
    episodic = EpisodicMemory(path="data/test_integration_episodic.jsonl")
    ReflectionLog(path="data/test_integration_reflection.jsonl")

    identity = Identity(path="data/test_integration_identity.jsonl")
    desire = Desire(path="data/test_integration_desire.jsonl")
    emotion = Emotion(path="data/test_integration_emotion.jsonl")
    goals = GoalManager(path="data/test_integration_goals.jsonl")

    builder = ContextBuilder(
        event_bus=bus, episodic_memory=episodic,
        identity=identity, desire=desire, emotion=emotion, goal_manager=goals,
    )
    support = SupportAgent(
        context_builder=builder, tool_broker=broker,
        audit_log=audit, episodic_memory=episodic,
    )
    scheduler = Scheduler()

    bus.subscribe(engine.on_event)

    return bus, engine, registry, policy, broker, audit, builder, support, store, scheduler


# ═══════════════════════════════════════════════════════════════
# 1. Browser Read-Only Research
# ═══════════════════════════════════════════════════════════════


class TestBrowserReadOnlyResearch:
    """Browser read-only capabilities are allowed."""

    def test_browser_extract_text_allowed(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="browser.extract_text", name="Extract Text",
            description="Extract text from page",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.READ_ONLY,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.ALLOW

    def test_browser_open_page_allowed(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="browser.open_page", name="Open Page",
            description="Navigate to URL",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.SAFE_ACTION,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.ALLOW

    def test_browser_submit_form_requires_approval(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="browser.submit_form", name="Submit Form",
            description="Submit web form",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.APPROVAL_REQUIRED,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.ASK_APPROVAL

    def test_browser_send_sns_denied(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="browser.send_sns", name="Send SNS",
            description="Post to social media",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.READ_ONLY,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.DENY


# ═══════════════════════════════════════════════════════════════
# 2. PC Observe → Support Suggestion
# ═══════════════════════════════════════════════════════════════


class TestPCObserveToSupport:
    """PC observe events flow through EventBus to Support Agent."""

    def test_pc_event_reaches_context(self):
        bus, _, _, _, _, _, builder, _, _, _ = _setup_full_stack()

        event = _make_event(
            event_type="pc.screen_changed",
            server_type=ServerType.PC, severity=2,
        )
        bus.publish(event)

        ctx = builder.build()
        pc_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.PC]
        assert len(pc_events) >= 1


# ═══════════════════════════════════════════════════════════════
# 3. Android Notification → Support Suggestion
# ═══════════════════════════════════════════════════════════════


class TestAndroidNotificationToSupport:
    """Android notification events flow through to Support Agent."""

    def test_notification_event_in_context(self):
        bus, _, _, _, _, _, builder, _, _, _ = _setup_full_stack()

        event = _make_event(
            event_type="android.notification_received",
            server_type=ServerType.ANDROID, severity=3,
            payload=json.dumps({"app_name": "LINE", "title": "Meeting", "text": "At 3pm"}),
        )
        bus.publish(event)

        ctx = builder.build()
        android_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.ANDROID]
        assert len(android_events) >= 1

    def test_support_agent_processes_notification(self):
        bus, _, _, _, _, _, _, support, _, _ = _setup_full_stack()

        event = _make_event(
            event_type="android.notification_received",
            server_type=ServerType.ANDROID, severity=3,
            payload=json.dumps({"app_name": "LINE", "title": "Hello", "text": "World"}),
        )
        bus.publish(event)

        result = support.run(trigger_event=event)
        assert result.notification_sent is True


# ═══════════════════════════════════════════════════════════════
# 4. Room Temperature → Support Suggestion
# ═══════════════════════════════════════════════════════════════


class TestRoomTemperatureToSupport:
    """Room temperature events flow through to Support Agent."""

    def test_temperature_event_in_context(self):
        bus, _, _, _, _, _, builder, _, _, _ = _setup_full_stack()

        event = _make_event(
            event_type="room.temperature_changed",
            server_type=ServerType.ROOM, severity=3,
            payload=json.dumps({"temperature_c": 30.5}),
        )
        bus.publish(event)

        ctx = builder.build()
        room_events = [e for e in ctx.recent_events if e.source_server_type == ServerType.ROOM]
        assert len(room_events) >= 1


# ═══════════════════════════════════════════════════════════════
# 5. Scheduled Daily Briefing
# ═══════════════════════════════════════════════════════════════


class TestScheduledDailyBriefing:
    """Scheduler produces due tasks for daily briefing."""

    def test_daily_briefing_task_due(self):
        scheduler = Scheduler()
        scheduler.add_task(ScheduledTask(
            task_id="daily-briefing",
            name="Daily Briefing",
            task_type=TaskType.DAILY_BRIEFING,
            interval_seconds=86400,
            next_run_ms=int(time.time() * 1000) - 1000,
        ))
        due = scheduler.get_due_tasks()
        assert len(due) >= 1
        assert due[0].task_type == TaskType.DAILY_BRIEFING


# ═══════════════════════════════════════════════════════════════
# 6. Approval-Required Action Pause/Resume
# ═══════════════════════════════════════════════════════════════


class TestApprovalPauseResume:
    """Approval-required actions pause until approved, then resume."""

    def test_action_paused_until_approval(self):
        broker, store = _setup_broker([
            Capability(
                id="ai.test_action", name="Test Action",
                description="Requires approval",
                server_type=ServerType.AI, risk_level=RiskLevel.APPROVAL_REQUIRED,
            ),
        ])

        result = broker.invoke_tool("ai.test_action")
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        # Approve
        store.approve(result.policy_result.approval_request.approval_id, ApprovalType.ONE_TIME)
        broker.register_mock("ai.test_action", lambda cap, p: {"ok": True})

        result2 = broker.invoke_tool_approved("ai.test_action")
        assert result2.success is True

    def test_rejected_action_stops(self):
        broker, store = _setup_broker([
            Capability(
                id="ai.test_action", name="Test Action",
                description="Requires approval",
                server_type=ServerType.AI, risk_level=RiskLevel.APPROVAL_REQUIRED,
            ),
        ])

        result = broker.invoke_tool("ai.test_action")
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        # Reject
        store.reject(result.policy_result.approval_request.approval_id)

        # Should still need approval (rejected = not approved)
        result2 = broker.invoke_tool("ai.test_action")
        assert result2.status == InvokeStatus.APPROVAL_NEEDED


# ═══════════════════════════════════════════════════════════════
# 7. Dangerous Operations — All Denied
# ═══════════════════════════════════════════════════════════════


class TestDangerousOperationsDenied:
    """All dangerous operations are denied."""

    def test_sns_post_denied(self):
        policy = create_default_policy_engine()
        caps = [
            ("browser.send_sns", ServerType.BROWSER),
            ("browser.post_sns", ServerType.BROWSER),
            ("android.post_sns", ServerType.ANDROID),
        ]
        for cap_id, st in caps:
            cap = Capability(
                id=cap_id, name="SNS", description="Post to SNS",
                server_type=st, risk_level=RiskLevel.READ_ONLY,
            )
            assert policy.evaluate(cap).decision == PolicyDecision.DENY

    def test_dm_send_denied(self):
        policy = create_default_policy_engine()
        caps = [
            ("browser.send_dm", ServerType.BROWSER),
            ("android.send_dm", ServerType.ANDROID),
            ("android.send_sms", ServerType.ANDROID),
        ]
        for cap_id, st in caps:
            cap = Capability(
                id=cap_id, name="DM", description="Send DM",
                server_type=st, risk_level=RiskLevel.READ_ONLY,
            )
            assert policy.evaluate(cap).decision == PolicyDecision.DENY

    def test_file_delete_denied(self):
        policy = create_default_policy_engine()
        for cap_id in ["pc.delete_file", "pc.bulk_delete"]:
            cap = Capability(
                id=cap_id, name="Delete", description="Delete file",
                server_type=ServerType.PC, risk_level=RiskLevel.READ_ONLY,
            )
            assert policy.evaluate(cap).decision == PolicyDecision.DENY

    def test_secret_read_denied(self):
        policy = create_default_policy_engine()
        caps = [
            ("dev.read_secrets", ServerType.DEV),
            ("pc.read_secret_file", ServerType.PC),
            ("android.read_credential", ServerType.ANDROID),
        ]
        for cap_id, st in caps:
            cap = Capability(
                id=cap_id, name="Secret", description="Read secret",
                server_type=st, risk_level=RiskLevel.READ_ONLY,
            )
            assert policy.evaluate(cap).decision == PolicyDecision.DENY

    def test_robot_arm_denied(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="room.move_robot_arm", name="Robot Arm",
            description="Move robot arm",
            server_type=ServerType.ROOM, risk_level=RiskLevel.READ_ONLY,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.DENY

    def test_ac_control_requires_approval(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="room.set_air_conditioner", name="AC",
            description="Control AC",
            server_type=ServerType.ROOM, risk_level=RiskLevel.APPROVAL_REQUIRED,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.ASK_APPROVAL

    def test_main_merge_denied(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="dev.merge_to_main", name="Merge",
            description="Merge to main",
            server_type=ServerType.DEV, risk_level=RiskLevel.READ_ONLY,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.DENY

    def test_production_deploy_denied(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="dev.deploy_production", name="Deploy",
            description="Deploy to production",
            server_type=ServerType.DEV, risk_level=RiskLevel.READ_ONLY,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.DENY

    def test_captcha_bypass_denied(self):
        policy = create_default_policy_engine()
        cap = Capability(
            id="browser.captcha_bypass", name="CAPTCHA",
            description="Bypass CAPTCHA",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.READ_ONLY,
        )
        assert policy.evaluate(cap).decision == PolicyDecision.DENY


# ═══════════════════════════════════════════════════════════════
# 8. Observability — AuditLog / EventBus / Memory
# ═══════════════════════════════════════════════════════════════


class TestObservability:
    """AuditLog, EventBus, and Memory are inspectable."""

    def test_audit_records_decisions(self):
        _, _, _, _, _, audit, _, _, _, _ = _setup_full_stack()
        audit.log_decision("test", "cap", "ALLOW")
        recent = audit.list_recent(10)
        assert any(e.action == "test" for e in recent)

    def test_eventbus_recent_events_visible(self):
        bus, _, _, _, _, _, _, _, _, _ = _setup_full_stack()
        bus.publish(_make_event("test.event"))
        recent = bus.list_recent_events(10)
        assert len(recent) >= 1

    def test_memory_entries_inspectable(self):
        _, _, _, _, _, _, _, _, _, _ = _setup_full_stack()
        episodic = EpisodicMemory(path="data/test_obs_episodic.jsonl")
        from aegis_ai.memory.episodic import Episode
        episodic.add(Episode(summary="test event", category="event", detail={"key": "value"}))
        recent = episodic.list_recent(10)
        assert len(recent) >= 1


# ═══════════════════════════════════════════════════════════════
# 9. Multi-Server Event Flow
# ═══════════════════════════════════════════════════════════════


class TestMultiServerEventFlow:
    """Events from all servers flow through the same pipeline."""

    def test_all_server_types_in_context(self):
        bus, _, _, _, _, _, builder, _, _, _ = _setup_full_stack()

        servers = [
            ("pc.screen_changed", ServerType.PC),
            ("android.notification_received", ServerType.ANDROID),
            ("room.temperature_changed", ServerType.ROOM),
        ]

        for event_type, server_type in servers:
            bus.publish(_make_event(event_type=event_type, server_type=server_type))

        ctx = builder.build()
        server_types = {e.source_server_type for e in ctx.recent_events}
        assert ServerType.PC in server_types
        assert ServerType.ANDROID in server_types
        assert ServerType.ROOM in server_types


def _setup_broker(caps: list[Capability]) -> tuple[ToolBroker, ApprovalStore]:
    registry = ToolRegistry()
    store = ApprovalStore()
    policy = PolicyEngine(approval_store=store)
    broker = ToolBroker(registry, policy)
    for cap in caps:
        registry.register_capability(cap)
    return broker, store
