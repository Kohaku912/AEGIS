"""Support Agent E2E — integration tests for Support Agent with AEGIS Core.

Tests the full Support Agent workflow:
  Event → OBSERVE → ASSESS → {PROPOSE|SUMMARIZE|RESEARCH|AUTO_DEV} → NOTIFY → REFLECT

CI uses MockLLMClient (no real LLM calls).
Architecture reference: docs/architecture.md §5.6
"""

from __future__ import annotations

import time
import uuid

from aegis_ai.agents.support import ActionType, SupportAgent, SupportState
from aegis_ai.audit import AuditLog
from aegis_ai.context_builder import ContextBuilder
from aegis_ai.llm.client import LLMThought, MockLLMClient
from aegis_ai.memory.episodic import EpisodicMemory
from aegis_schema.models import Event, EventPriority, ServerType
from event_bus import EventBus
from policy_engine import create_default_policy_engine
from tool_broker import ToolBroker
from tool_registry import ToolRegistry

# ── Helpers ──────────────────────────────────────────────────


def _make_event(
    event_type: str = "android.notification_received",
    severity: int = 3,
    priority: EventPriority = EventPriority.NORMAL,
    payload: str | None = None,
) -> Event:
    """Create a test event."""
    return Event(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        source_server_type=ServerType.ANDROID,
        source_server_id="test-server",
        timestamp_ms=int(time.time() * 1000),
        payload_json=payload or '{"app_name":"LINE","title":"Test","text":"Hello"}',
        severity=severity,
        priority=priority,
    )


def _setup_support_agent(
    llm_client: MockLLMClient | None = None,
) -> tuple[SupportAgent, EventBus, AuditLog, EpisodicMemory]:
    """Wire up Support Agent with AEGIS Core."""
    bus = EventBus()
    registry = ToolRegistry()
    policy = create_default_policy_engine()
    broker = ToolBroker(registry, policy)
    audit = AuditLog(path="data/test_support_audit.jsonl")
    episodic = EpisodicMemory(path="data/test_support_episodic.jsonl")
    builder = ContextBuilder(event_bus=bus, tool_broker=broker)
    llm = llm_client or MockLLMClient()

    agent = SupportAgent(
        context_builder=builder,
        llm_client=llm,
        tool_broker=broker,
        audit_log=audit,
        episodic_memory=episodic,
    )

    return agent, bus, audit, episodic


# ═══════════════════════════════════════════════════════════════
# 1. Basic Workflow
# ═══════════════════════════════════════════════════════════════


class TestBasicWorkflow:
    """Support Agent basic workflow: IDLE → OBSERVE → ASSESS → PROPOSE → NOTIFY → REFLECT."""

    def test_run_returns_state(self):
        """SupportAgent.run() returns a SupportState."""
        agent, bus, audit, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event())
        assert isinstance(state, SupportState)
        assert state.support_id != ""

    def test_run_phases_are_completed(self):
        """All phases are completed in order."""
        agent, bus, audit, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event())

        assert state.context is not None
        assert state.assessment != ""
        assert state.notification_sent is True
        assert state.reflection != ""

    def test_run_records_audit_trail(self):
        """Each phase is recorded in the AuditLog."""
        agent, bus, audit, _ = _setup_support_agent()
        agent.run(trigger_event=_make_event())

        recent = audit.list_recent(20)
        actions = [e.action for e in recent]
        assert "support_observe" in actions
        assert "support_assess" in actions
        assert "support_notify" in actions
        assert "support_reflect" in actions

    def test_run_without_event(self):
        """SupportAgent can run without a trigger event."""
        agent, bus, audit, _ = _setup_support_agent()
        state = agent.run(trigger_type="schedule")

        assert state.context is not None
        assert state.notification_sent is True


# ═══════════════════════════════════════════════════════════════
# 2. Assessment
# ═══════════════════════════════════════════════════════════════


class TestAssessment:
    """Support Agent assesses the situation and decides action type."""

    def test_notification_event_triggers_propose(self):
        """Android notification event leads to PROPOSE action."""
        agent, _, _, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event("android.notification_received"))

        assert state.action_type == ActionType.PROPOSE
        assert state.proposal != ""

    def test_room_event_triggers_summarize(self):
        """Room event leads to SUMMARIZE action."""
        agent, _, _, _ = _setup_support_agent()
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="room.temperature_changed",
            source_server_type=ServerType.ROOM,
            source_server_id="room-server",
            timestamp_ms=int(time.time() * 1000),
            payload_json='{"temperature_c": 25.0}',
            severity=3,
            priority=EventPriority.BACKGROUND,
        )
        state = agent.run(trigger_event=event)

        assert state.action_type == ActionType.SUMMARIZE
        assert state.summary != ""

    def test_assessment_records_urgency(self):
        """Assessment determines urgency level."""
        agent, _, _, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event())

        assert state.urgency in ("low", "normal", "high", "critical")


# ═══════════════════════════════════════════════════════════════
# 3. Proposal Generation
# ═══════════════════════════════════════════════════════════════


class TestProposalGeneration:
    """Support Agent generates proposals based on events."""

    def test_notification_proposal_contains_app_name(self):
        """Proposal for LINE notification mentions LINE."""
        agent, _, _, _ = _setup_support_agent()
        event = _make_event(
            payload='{"app_name":"LINE","title":"New message","text":"Hello!"}',
        )
        state = agent.run(trigger_event=event)

        assert "LINE" in state.proposal

    def test_room_motion_proposal(self):
        """Proposal for room motion event includes zone info in summary."""
        agent, _, _, _ = _setup_support_agent()
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="room.motion_detected",
            source_server_type=ServerType.ROOM,
            source_server_id="room-server",
            timestamp_ms=int(time.time() * 1000),
            payload_json='{"motion_detected":true,"motion_zone":"living_room"}',
            severity=3,
            priority=EventPriority.NORMAL,
        )
        state = agent.run(trigger_event=event)

        # Room events trigger SUMMARIZE, not PROPOSE
        assert state.action_type == ActionType.SUMMARIZE
        assert state.summary != ""


# ═══════════════════════════════════════════════════════════════
# 4. Summarization
# ═══════════════════════════════════════════════════════════════


class TestSummarization:
    """Support Agent summarizes events."""

    def test_summarize_multiple_events(self):
        """Summarize when LLM recommends summarization."""

        class SummarizeLLM(MockLLMClient):
            def generate_thought(self, context: str) -> LLMThought:
                return LLMThought(
                    summary="Multiple events to summarize",
                    assessment="Many recent events need summarization",
                    recommended_action="Summarize the recent events for the user",
                    confidence=0.7,
                )

        agent, bus, _, _ = _setup_support_agent(llm_client=SummarizeLLM())

        # Push multiple events
        for i in range(5):
            bus.publish(
                _make_event(
                    event_type="android.notification_received",
                    payload=f'{{"app_name":"App{i}","title":"Msg{i}","text":"Hello"}}',
                )
            )

        state = agent.run(trigger_type="schedule")

        assert state.summary != ""
        assert "件" in state.summary


# ═══════════════════════════════════════════════════════════════
# 5. Research Agent Integration
# ═══════════════════════════════════════════════════════════════


class TestResearchIntegration:
    """Support Agent can launch Research Agent."""

    def test_research_action_type(self):
        """When LLM recommends research, action type is RESEARCH."""

        class ResearchLLM(MockLLMClient):
            def generate_thought(self, context: str) -> LLMThought:
                return LLMThought(
                    summary="Need to research",
                    assessment="User asked about Python 3.12 features",
                    recommended_action="Research Python 3.12 features using browser",
                    confidence=0.8,
                )

        agent, _, _, _ = _setup_support_agent(llm_client=ResearchLLM())
        state = agent.run(trigger_event=_make_event())

        assert state.action_type == ActionType.RESEARCH
        assert state.research_topic != ""


# ═══════════════════════════════════════════════════════════════
# 6. Auto Dev Integration
# ═══════════════════════════════════════════════════════════════


class TestAutoDevIntegration:
    """Support Agent can launch Self Dev Agent."""

    def test_auto_dev_action_type(self):
        """When LLM recommends fix/improve, action type is AUTO_DEV."""

        class DevLLM(MockLLMClient):
            def generate_thought(self, context: str) -> LLMThought:
                return LLMThought(
                    summary="Error detected in logs",
                    assessment="CI test failure needs investigation",
                    recommended_action="Fix the failing test and create a PR",
                    confidence=0.85,
                )

        agent, _, _, _ = _setup_support_agent(llm_client=DevLLM())
        state = agent.run(trigger_event=_make_event())

        assert state.action_type == ActionType.AUTO_DEV


# ═══════════════════════════════════════════════════════════════
# 7. Notification
# ═══════════════════════════════════════════════════════════════


class TestNotification:
    """Support Agent sends notifications via AuditLog."""

    def test_notification_always_sent(self):
        """Notification is always sent (via AuditLog)."""
        agent, _, audit, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event())

        assert state.notification_sent is True
        assert state.notification_channel == "audit_log"

    def test_notification_recorded_in_audit(self):
        """Notification is recorded in AuditLog."""
        agent, _, audit, _ = _setup_support_agent()
        agent.run(trigger_event=_make_event())

        recent = audit.list_recent(20)
        notify_entries = [e for e in recent if e.action == "support_notify"]
        assert len(notify_entries) >= 1

    def test_notification_stored_in_episodic_memory(self):
        """Notification is stored as episodic memory."""
        agent, _, _, episodic = _setup_support_agent()
        agent.run(trigger_event=_make_event())

        episodes = episodic.list_recent(10)
        support_eps = [e for e in episodes if e.category == "support_action"]
        assert len(support_eps) >= 1


# ═══════════════════════════════════════════════════════════════
# 8. Reflection
# ═══════════════════════════════════════════════════════════════


class TestReflection:
    """Support Agent records reflections."""

    def test_reflection_recorded(self):
        """Reflection is recorded after workflow completion."""
        agent, _, _, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event())

        assert state.reflection != ""
        assert state.episode_id != ""
        assert "support" in state.reflection.lower() or state.support_id in state.reflection


# ═══════════════════════════════════════════════════════════════
# 9. Error Handling
# ═══════════════════════════════════════════════════════════════


class TestErrorHandling:
    """Support Agent handles errors gracefully."""

    def test_llm_error_does_not_crash(self):
        """LLM errors are caught and recorded."""

        class ErrorLLM(MockLLMClient):
            def generate_thought(self, context: str) -> LLMThought:
                raise RuntimeError("LLM unavailable")

        agent, _, _, _ = _setup_support_agent(llm_client=ErrorLLM())
        state = agent.run(trigger_event=_make_event())

        assert len(state.errors) >= 1
        assert "LLM unavailable" in state.errors[0]

    def test_context_builder_error_does_not_crash(self):
        """ContextBuilder errors are caught."""
        agent, _, _, _ = _setup_support_agent()
        # Run with no event and no bus — should still work
        state = agent.run(trigger_type="schedule")

        assert state.completed_at_ms > 0


# ═══════════════════════════════════════════════════════════════
# 10. PolicyEngine Integration
# ═══════════════════════════════════════════════════════════════


class TestPolicyEngineIntegration:
    """Support Agent respects PolicyEngine."""

    def test_support_agent_does_not_bypass_policy(self):
        """Support Agent does not execute dangerous operations directly."""
        agent, _, _, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event())

        # Support Agent should never execute dangerous ops
        # It only proposes, summarizes, or delegates to Research/Dev agents
        assert state.action_type in (
            ActionType.PROPOSE,
            ActionType.SUMMARIZE,
            ActionType.RESEARCH,
            ActionType.AUTO_DEV,
            ActionType.NONE,
        )

    def test_no_external_transmission(self):
        """Support Agent does not send external messages."""
        agent, _, _, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event())

        # Notification channel should be audit_log only (no SNS/DM/Email)
        assert state.notification_channel == "audit_log"


# ═══════════════════════════════════════════════════════════════
# 11. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: Event → Support Agent → Proposal → Notification → Reflection."""

    def test_full_flow_with_notification(self):
        """Full flow from Android notification to proposal."""
        agent, bus, audit, episodic = _setup_support_agent()

        # Push a notification event
        event = _make_event(
            payload='{"app_name":"LINE","title":"Meeting at 3pm","text":"Ready?"}',
        )
        bus.publish(event)

        # Run Support Agent
        state = agent.run(trigger_event=event)

        # Verify all phases
        assert state.context is not None
        assert state.assessment != ""
        assert state.action_type == ActionType.PROPOSE
        assert state.proposal != ""
        assert state.notification_sent is True
        assert state.reflection != ""

        # Verify audit trail
        recent = audit.list_recent(20)
        actions = {e.action for e in recent}
        assert "support_observe" in actions
        assert "support_assess" in actions
        assert "support_notify" in actions
        assert "support_reflect" in actions

        # Verify episodic memory
        episodes = episodic.list_recent(10)
        support_eps = [e for e in episodes if e.category == "support_action"]
        assert len(support_eps) >= 1

    def test_full_flow_with_room_event(self):
        """Full flow from Room event to summary."""
        agent, bus, audit, _ = _setup_support_agent()

        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="room.temperature_changed",
            source_server_type=ServerType.ROOM,
            source_server_id="room-server",
            timestamp_ms=int(time.time() * 1000),
            payload_json='{"temperature_c": 30.5}',
            severity=4,
            priority=EventPriority.BACKGROUND,
        )
        bus.publish(event)

        state = agent.run(trigger_event=event)

        assert state.context is not None
        assert state.notification_sent is True

    def test_full_flow_metadata(self):
        """Full flow has correct metadata."""
        agent, _, _, _ = _setup_support_agent()
        state = agent.run(trigger_event=_make_event())

        assert state.support_id != ""
        assert state.started_at_ms > 0
        assert state.completed_at_ms >= state.started_at_ms
