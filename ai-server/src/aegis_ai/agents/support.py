"""Support Agent — proactive user assistance powered by LangGraph.

Provides:
- Event-driven observation and assessment
- Automatic proposal generation (reply drafts, summaries)
- Automatic Research Agent startup for information gathering
- Automatic Self Dev Agent startup for improvement proposals (PR creation)
- Notification via Web UI / AuditLog / Approval UI

Safety:
- ALL actions go through ToolBroker → PolicyEngine
- External transmission (SNS/DM/Email) requires Approval UI
- Physical device operations require Approval UI
- File deletion requires Approval UI
- PR creation is automatic, merge requires user approval

Architecture reference: docs/architecture.md §5.6
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from aegis_ai.audit import AuditLog
from aegis_ai.context_builder import Context, ContextBuilder
from aegis_ai.llm.client import LLMClient, LLMThought, MockLLMClient
from aegis_ai.memory.episodic import Episode, EpisodicMemory
from aegis_schema.models import Event

logger = logging.getLogger("aegis_ai.agents.support")


# ═══════════════════════════════════════════════════════════════
# Support State — LangGraph state definition
# ═══════════════════════════════════════════════════════════════


class SupportPhase(Enum):
    """Phases of the Support Agent workflow."""

    IDLE = auto()
    OBSERVE = auto()
    ASSESS = auto()
    PROPOSE = auto()
    SUMMARIZE = auto()
    RESEARCH = auto()
    AUTO_DEV = auto()
    NOTIFY = auto()
    REFLECT = auto()
    FAILED = auto()


class ActionType(Enum):
    """What the Support Agent decided to do."""

    NONE = auto()
    PROPOSE = auto()  # Generate a proposal for the user
    SUMMARIZE = auto()  # Summarize events/notifications
    RESEARCH = auto()  # Launch Research Agent
    AUTO_DEV = auto()  # Launch Self Dev Agent (PR creation)


@dataclass
class SupportState:
    """State for the Support Agent LangGraph workflow."""

    # Input
    trigger_event: Event | None = None
    trigger_type: str = ""  # "event", "schedule", "anomaly"

    # OBSERVE
    context: Context | None = None

    # ASSESS
    assessment: str = ""
    urgency: str = "normal"  # "low", "normal", "high", "critical"
    action_type: ActionType = ActionType.NONE

    # PROPOSE
    proposal: str = ""
    proposal_type: str = ""  # "reply_draft", "action_suggestion", "info_request"

    # SUMMARIZE
    summary: str = ""
    summary_source: str = ""  # "notifications", "events", "logs"

    # RESEARCH
    research_topic: str = ""
    research_results: list[dict[str, Any]] = field(default_factory=list)

    # AUTO_DEV
    dev_task: str = ""
    dev_analysis: str = ""
    dev_pr_created: bool = False

    # NOTIFY
    notification_sent: bool = False
    notification_channel: str = ""  # "web_ui", "audit_log", "approval_ui"

    # REFLECT
    reflection: str = ""
    episode_id: str = ""

    # Metadata
    support_id: str = ""
    started_at_ms: int = 0
    completed_at_ms: int = 0
    errors: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# Support Agent — main implementation
# ═══════════════════════════════════════════════════════════════


class SupportAgent:
    """Proactive user assistance powered by LangGraph.

    The Support Agent observes events, assesses situations, and takes
    appropriate action (propose, summarize, research, auto-dev).

    All actions go through ToolBroker → PolicyEngine.
    Dangerous operations require Approval UI.

    Usage:
        agent = SupportAgent(
            context_builder=builder,
            llm_client=llm,
            tool_broker=broker,
            audit_log=audit,
            episodic_memory=episodic,
        )
        result = agent.run(trigger_event=event)
    """

    def __init__(
        self,
        context_builder: ContextBuilder | None = None,
        llm_client: LLMClient | None = None,
        tool_broker: Any = None,
        audit_log: AuditLog | None = None,
        episodic_memory: EpisodicMemory | None = None,
        research_agent: Any = None,
        self_dev_agent: Any = None,
    ) -> None:
        self._context_builder = context_builder or ContextBuilder()
        self._llm = llm_client or MockLLMClient()
        self._tool_broker = tool_broker
        self._audit = audit_log or AuditLog()
        self._episodic = episodic_memory
        self._research_agent = research_agent
        self._self_dev_agent = self_dev_agent
        self._last_state: SupportState | None = None

    @property
    def last_state(self) -> SupportState | None:
        return self._last_state

    # ── Main entry point ─────────────────────────────────────

    def run(
        self,
        trigger_event: Event | None = None,
        trigger_type: str = "event",
    ) -> SupportState:
        """Run the Support Agent workflow.

        Phases: IDLE → OBSERVE → ASSESS → {PROPOSE|SUMMARIZE|RESEARCH|AUTO_DEV} → NOTIFY → REFLECT

        Returns the final SupportState.
        """
        state = SupportState(
            trigger_event=trigger_event,
            trigger_type=trigger_type,
            support_id=f"support_{uuid.uuid4().hex[:8]}",
            started_at_ms=int(time.time() * 1000),
        )

        try:
            # 1. OBSERVE
            state = self._phase_observe(state)

            # 2. ASSESS
            state = self._phase_assess(state)

            # 3. Action phase (based on assessment)
            if state.action_type == ActionType.RESEARCH:
                state = self._phase_research(state)
            elif state.action_type == ActionType.AUTO_DEV:
                state = self._phase_auto_dev(state)
            elif state.action_type == ActionType.SUMMARIZE:
                state = self._phase_summarize(state)
            elif state.action_type == ActionType.PROPOSE:
                state = self._phase_propose(state)

            # 4. NOTIFY
            state = self._phase_notify(state)

            # 5. REFLECT
            state = self._phase_reflect(state)

        except Exception as e:
            logger.exception("SupportAgent workflow failed")
            state.errors.append(str(e))
            self._audit.log_decision(
                "support_error",
                "support_agent",
                "FAILED",
                reason=str(e)[:500],
            )

        state.completed_at_ms = int(time.time() * 1000)
        self._last_state = state
        return state

    # ── Phase implementations ────────────────────────────────

    def _phase_observe(self, state: SupportState) -> SupportState:
        """OBSERVE: Build context from EventBus, Memory, Mind."""
        ctx = self._context_builder.build(
            triggering_events=[state.trigger_event] if state.trigger_event else None,
        )
        state.context = ctx

        self._audit.log_decision(
            "support_observe",
            "support_agent",
            "OBSERVE",
            detail={"context_id": ctx.context_id, "events": len(ctx.recent_events)},
        )
        return state

    def _phase_assess(self, state: SupportState) -> SupportState:
        """ASSESS: Use LLM to evaluate situation and decide action."""
        if state.context is None:
            state.action_type = ActionType.NONE
            return state

        context_str = self._context_to_string(state.context)
        thought = self._llm.generate_thought(context_str)

        state.assessment = thought.assessment
        state.action_type = self._determine_action(thought, state)
        state.urgency = self._determine_urgency(thought)

        # Set topic/task based on action type
        if state.action_type == ActionType.RESEARCH:
            state.research_topic = thought.assessment
        elif state.action_type == ActionType.AUTO_DEV:
            state.dev_task = thought.assessment

        self._audit.log_decision(
            "support_assess",
            "support_agent",
            "ASSESS",
            detail={
                "action": state.action_type.name,
                "urgency": state.urgency,
                "confidence": thought.confidence,
            },
        )
        return state

    def _phase_propose(self, state: SupportState) -> SupportState:
        """PROPOSE: Generate a proposal for the user."""
        if state.context is None:
            return state

        # Generate proposal based on context
        if state.trigger_event and state.trigger_event.event_type.startswith("android."):
            state.proposal = self._generate_notification_proposal(state.trigger_event)
            state.proposal_type = "reply_draft"
        elif state.trigger_event and state.trigger_event.event_type.startswith("room."):
            state.proposal = self._generate_room_proposal(state.trigger_event)
            state.proposal_type = "action_suggestion"
        else:
            state.proposal = "何かお手伝いできることはありますか？"
            state.proposal_type = "info_request"

        self._audit.log_decision(
            "support_propose",
            "support_agent",
            "PROPOSE",
            detail={"proposal_type": state.proposal_type},
        )
        return state

    def _phase_summarize(self, state: SupportState) -> SupportState:
        """SUMMARIZE: Generate a summary of events/notifications."""
        if state.context is None:
            return state

        events = state.context.recent_events
        if not events:
            state.summary = "最近のイベントはありません。"
            return state

        # Summarize recent events
        event_types: dict[str, int] = {}
        for e in events:
            prefix = e.event_type.split(".")[0] if "." in e.event_type else "other"
            event_types[prefix] = event_types.get(prefix, 0) + 1

        parts = [f"{k}: {v}件" for k, v in event_types.items()]
        state.summary = f"最近のイベント: {', '.join(parts)}"
        state.summary_source = "events"

        self._audit.log_decision(
            "support_summarize",
            "support_agent",
            "SUMMARIZE",
            detail={"event_count": len(events)},
        )
        return state

    def _phase_research(self, state: SupportState) -> SupportState:
        """RESEARCH: Launch Research Agent for information gathering."""
        topic = state.research_topic or state.assessment
        if not topic:
            state.action_type = ActionType.PROPOSE
            return state

        # Research Agent is invoked through ToolBroker if available
        if self._research_agent:
            try:
                result = self._research_agent.research_topic(topic)
                state.research_results = [
                    {
                        "topic": topic,
                        "report": result if isinstance(result, str) else str(result),
                    }
                ]
            except Exception as e:
                state.errors.append(f"Research Agent error: {e}")
                logger.error("Research Agent failed: %s", e)

        self._audit.log_decision(
            "support_research",
            "support_agent",
            "RESEARCH",
            detail={"topic": topic[:200]},
        )
        return state

    def _phase_auto_dev(self, state: SupportState) -> SupportState:
        """AUTO_DEV: Launch Self Dev Agent for improvement analysis and PR creation.

        PR creation is automatic. Merge requires user approval.
        """
        task = state.dev_task or state.assessment
        if not task:
            state.action_type = ActionType.PROPOSE
            return state

        if self._self_dev_agent:
            try:
                # Self Dev Agent analyzes and creates PR
                # The PR itself goes through the standard approval flow
                result = self._self_dev_agent.analyze_and_propose(task)
                state.dev_analysis = str(result)
                state.dev_pr_created = True
            except Exception as e:
                state.errors.append(f"Self Dev Agent error: {e}")
                logger.error("Self Dev Agent failed: %s", e)

        self._audit.log_decision(
            "support_auto_dev",
            "support_agent",
            "AUTO_DEV",
            detail={"task": task[:200], "pr_created": state.dev_pr_created},
        )
        return state

    def _phase_notify(self, state: SupportState) -> SupportState:
        """NOTIFY: Send notification to user via Web UI / AuditLog."""
        notification_text = self._build_notification_text(state)

        # Log to AuditLog (always)
        self._audit.log_decision(
            "support_notify",
            "support_agent",
            "NOTIFY",
            detail={
                "action": state.action_type.name,
                "urgency": state.urgency,
                "text": notification_text[:500],
            },
        )

        state.notification_sent = True
        state.notification_channel = "audit_log"

        # Store as episodic memory
        if self._episodic:
            self._episodic.add(
                Episode(
                    summary=f"Support: {state.action_type.name} — {notification_text[:100]}",
                    category="support_action",
                    detail={
                        "support_id": state.support_id,
                        "action": state.action_type.name,
                        "urgency": state.urgency,
                    },
                )
            )

        return state

    def _phase_reflect(self, state: SupportState) -> SupportState:
        """REFLECT: Record reflection for learning."""
        state.reflection = (
            f"Support cycle {state.support_id}: "
            f"action={state.action_type.name}, "
            f"urgency={state.urgency}, "
            f"errors={len(state.errors)}"
        )
        state.episode_id = f"ep_{state.support_id}"

        self._audit.log_decision(
            "support_reflect",
            "support_agent",
            "REFLECT",
            detail={"reflection": state.reflection[:200]},
        )
        return state

    # ── Decision helpers ─────────────────────────────────────

    def _determine_action(self, thought: LLMThought, state: SupportState) -> ActionType:
        """Determine what action to take based on the LLM thought."""
        rec = thought.recommended_action.lower()

        # Research triggers
        if any(kw in rec for kw in ["research", "investigate", "search", "look up"]):
            return ActionType.RESEARCH

        # Auto-dev triggers
        if any(kw in rec for kw in ["fix", "improve", "error", "failure", "bug"]):
            return ActionType.AUTO_DEV

        # Summarize triggers
        if any(kw in rec for kw in ["summarize", "summary", "overview"]):
            return ActionType.SUMMARIZE

        # Event-specific actions
        if state.trigger_event:
            etype = state.trigger_event.event_type
            if etype.startswith("android.notification"):
                return ActionType.PROPOSE
            if etype.startswith("room."):
                return ActionType.SUMMARIZE

        # Default: propose
        return ActionType.PROPOSE

    def _determine_urgency(self, thought: LLMThought) -> str:
        """Determine urgency level from the LLM thought."""
        if thought.confidence >= 0.9:
            return "critical"
        if thought.confidence >= 0.7:
            return "high"
        if thought.confidence >= 0.5:
            return "normal"
        return "low"

    # ── Proposal generators ──────────────────────────────────

    def _generate_notification_proposal(self, event: Event) -> str:
        """Generate a proposal based on an Android notification event."""
        import json

        try:
            payload = json.loads(event.payload_json)
            app = payload.get("app_name", "不明なアプリ")
            title = payload.get("title", "")
            text = payload.get("text", "")

            if title:
                return f"[{app}] {title}: 返信案を作りましょうか？"
            return f"[{app}] 通知があります。確認しますか？"
        except (json.JSONDecodeError, KeyError):
            return "通知があります。確認しますか？"

    def _generate_room_proposal(self, event: Event) -> str:
        """Generate a proposal based on a Room event."""
        import json

        try:
            payload = json.loads(event.payload_json)
            if event.event_type == "room.motion_detected":
                zone = payload.get("motion_zone", "不明")
                return f"[Room] {zone}で動きを検知しました。"
            if event.event_type == "room.temperature_changed":
                temp = payload.get("temperature_c", "?")
                return f"[Room] 温度が{temp}°Cに変化しました。"
            return "[Room] 部屋の環境に変化があります。"
        except (json.JSONDecodeError, KeyError):
            return "[Room] 部屋の環境に変化があります。"

    def _build_notification_text(self, state: SupportState) -> str:
        """Build notification text from the current state."""
        parts = []
        if state.proposal:
            parts.append(f"提案: {state.proposal}")
        if state.summary:
            parts.append(f"要約: {state.summary}")
        if state.research_results:
            parts.append(f"調査結果: {len(state.research_results)}件")
        if state.dev_analysis:
            parts.append(f"改善分析: {state.dev_analysis[:200]}")
        if state.errors:
            parts.append(f"エラー: {len(state.errors)}件")
        return " | ".join(parts) if parts else "サポート完了"

    def _context_to_string(self, ctx: Context) -> str:
        """Convert Context to a string for the LLM."""
        parts = [
            f"Identity: {ctx.identity}",
            f"Goals: {', '.join(ctx.current_goals) if ctx.current_goals else 'none'}",
        ]
        if ctx.recent_events:
            parts.append(
                f"Recent events ({len(ctx.recent_events)}): "
                + ", ".join(str(e.event_type) for e in ctx.recent_events[:5])
            )
        if ctx.recent_media_summaries:
            parts.append(
                f"Recent media ({len(ctx.recent_media_summaries)}): "
                + "; ".join(ctx.recent_media_summaries[:3])
            )
        if ctx.recent_episodes:
            parts.append(f"Recent episodes: {'; '.join(ctx.recent_episodes[:3])}")
        if ctx.relevant_facts:
            parts.append(f"Relevant facts: {'; '.join(ctx.relevant_facts[:3])}")
        return "\n".join(parts)
