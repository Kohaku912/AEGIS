"""Context Builder — assembles structured context for the LLM / decision engine.

Gathers from:
- EventBus: recent events
- Memory System: episodic, semantic, procedural, reflection
- Mind Layer: identity, desires, emotion, goals, priorities
- ToolBroker: available capabilities
- Scheduler: pending tasks

Architecture reference: docs/architecture.md §5.2
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from aegis_schema.models import Event

# ── Context maximums ────────────────────────────────────────

MAX_RECENT_EVENTS = 20
MAX_MEMORIES = 10
MAX_CAPABILITIES = 30
MAX_FACTS = 10
MAX_PROCEDURES = 5
MAX_REFLECTIONS = 5
MAX_GOALS = 5
MAX_TOTAL_CHARS = 8000


def _truncate(text: str, max_chars: int) -> str:
    return text[:max_chars] + "..." if len(text) > max_chars else text


@dataclass
class Context:
    """Structured context for the Autonomous Loop / LLM."""

    # Current events
    recent_events: list[Event] = field(default_factory=list)

    # Memory references
    recent_episodes: list[str] = field(default_factory=list)
    relevant_facts: list[str] = field(default_factory=list)
    relevant_procedures: list[str] = field(default_factory=list)
    recent_reflections: list[str] = field(default_factory=list)

    # Mind state
    identity: str = "AEGIS — autonomous multi-device AI assistant"
    current_goals: list[str] = field(default_factory=list)
    emotional_state: str = "neutral"
    priorities: str = ""
    desires: str = ""

    # Available tools
    available_capability_ids: list[str] = field(default_factory=list)

    # User context
    user_preferences: dict[str, Any] = field(default_factory=dict)
    recent_user_messages: list[str] = field(default_factory=list)

    # Scheduled tasks
    pending_tasks: list[str] = field(default_factory=list)

    # Metadata
    built_at_ms: int = 0
    context_id: str = ""
    total_chars: int = 0
    truncated: bool = False


class ContextBuilder:
    """Assembles Context from EventBus, Memory, Mind, ToolBroker, and Scheduler."""

    def __init__(
        self,
        event_bus: Any = None,
        episodic_memory: Any = None,
        semantic_memory: Any = None,
        procedural_memory: Any = None,
        reflection_log: Any = None,
        tool_broker: Any = None,
        identity: Any = None,
        desire: Any = None,
        emotion: Any = None,
        goal_manager: Any = None,
        scheduler: Any = None,
    ) -> None:
        self._event_bus = event_bus
        self._episodic = episodic_memory
        self._semantic = semantic_memory
        self._procedural = procedural_memory
        self._reflection = reflection_log
        self._tool_broker = tool_broker
        self._identity = identity
        self._desire = desire
        self._emotion = emotion
        self._goals = goal_manager
        self._scheduler = scheduler
        self._goals_list: list[str] = []  # Legacy support for set_goals()
        self._last_context: Context | None = None

    def set_goals(self, goals: list[str]) -> None:
        """Set goals directly (legacy support). Prefer goal_manager."""
        self._goals_list = goals

    def build(
        self,
        triggering_events: list[Event] | None = None,
        triggering_query: str = "",
    ) -> Context:
        """Build a Context object from all available data sources."""
        ctx = Context(
            built_at_ms=int(time.time() * 1000),
            context_id=f"ctx_{int(time.time() * 1000)}",
        )

        # 1. Identity
        if self._identity:
            if hasattr(self._identity, "to_context_string"):
                ctx.identity = self._identity.to_context_string()
            else:
                ctx.identity = str(self._identity)

        # 2. Desires
        if self._desire:
            if hasattr(self._desire, "to_context_string"):
                ctx.desires = self._desire.to_context_string()

        # 3. Emotion
        if self._emotion:
            if hasattr(self._emotion, "to_context_string"):
                ctx.emotional_state = self._emotion.to_context_string()

        # 4. Goals
        if self._goals:
            ctx.current_goals = [g.description for g in self._goals.list_active()[:MAX_GOALS]]
        elif self._goals_list:
            ctx.current_goals = self._goals_list[:MAX_GOALS]

        # 5. Recent events
        if self._event_bus:
            events: list[Event] = self._event_bus.list_recent_events(MAX_RECENT_EVENTS)
            ctx.recent_events = events
        if triggering_events:
            ctx.recent_events = list(triggering_events) + ctx.recent_events

        # 6. Episodic memory
        if self._episodic:
            episodes = self._episodic.list_recent(MAX_MEMORIES)
            ctx.recent_episodes = [
                f"[{e.category}] {e.summary}" for e in episodes
            ]

        # 7. Semantic memory
        if self._semantic and triggering_query:
            facts = self._semantic.search(triggering_query, category=None)
            ctx.relevant_facts = [
                _truncate(f"[{f.category}] {f.content}", 200)
                for f in facts[:MAX_FACTS]
            ]

        # 8. Procedural memory
        if self._procedural and triggering_query:
            procs = self._procedural.find_for_goal(triggering_query)
            ctx.relevant_procedures = [
                f"[conf={p.confidence:.0%}] {p.goal}: {' → '.join(p.steps[:5])}"
                for p in procs[:MAX_PROCEDURES] if p.confidence > 0.3
            ]

        # 9. Reflection
        if self._reflection:
            refs = self._reflection.list_recent(MAX_REFLECTIONS)
            ctx.recent_reflections = [
                f"Reflection: {r.summary}" for r in refs
            ]

        # 10. Available capabilities
        if self._tool_broker:
            try:
                safe_caps = self._tool_broker.list_safe_capabilities()
                ctx.available_capability_ids = [
                    c.id for c in safe_caps[:MAX_CAPABILITIES]
                ]
            except Exception:
                ctx.available_capability_ids = []

        # 11. Scheduled tasks
        if self._scheduler:
            due_tasks = self._scheduler.get_due_tasks()
            ctx.pending_tasks = [
                f"{t.name}: {t.description}" for t in due_tasks[:5]
            ]

        # 12. Truncate if needed
        self._apply_budget(ctx)
        self._last_context = ctx
        return ctx

    def _apply_budget(self, ctx: Context) -> None:
        """Truncate context if it exceeds the character budget."""
        total = (
            len(ctx.identity) +
            len(ctx.desires) +
            len(ctx.emotional_state) +
            len(" ".join(ctx.current_goals)) +
            sum(len(str(e)) for e in ctx.recent_events) +
            sum(len(s) for s in ctx.recent_episodes) +
            sum(len(s) for s in ctx.relevant_facts) +
            sum(len(s) for s in ctx.relevant_procedures) +
            sum(len(s) for s in ctx.recent_reflections) +
            sum(len(s) for s in ctx.available_capability_ids) +
            sum(len(s) for s in ctx.recent_user_messages) +
            sum(len(s) for s in ctx.pending_tasks)
        )
        ctx.total_chars = total

        if total > MAX_TOTAL_CHARS:
            ctx.truncated = True
            while total > MAX_TOTAL_CHARS and len(ctx.recent_events) > 3:
                ctx.recent_events = ctx.recent_events[1:]
                total = self._recalc_chars(ctx)
            while total > MAX_TOTAL_CHARS and len(ctx.relevant_facts) > 1:
                ctx.relevant_facts.pop()
                total = self._recalc_chars(ctx)

    def _recalc_chars(self, ctx: Context) -> int:
        return (
            len(ctx.identity) + len(ctx.desires) + len(ctx.emotional_state) +
            sum(len(str(e)) for e in ctx.recent_events) +
            len(" ".join(ctx.recent_episodes)) +
            len(" ".join(ctx.relevant_facts))
        )

    @property
    def last_context(self) -> Context | None:
        return self._last_context
