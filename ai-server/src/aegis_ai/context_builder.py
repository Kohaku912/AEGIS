"""Context Builder — assembles structured context for the LLM / decision engine.

Before any decision, gathers from:
- EventBus: recent events
- Memory System: episodic, semantic, procedural, reflection
- Mind Layer: identity, goals, emotional state
- ToolBroker: available capabilities
- Scheduler: pending tasks

STATUS: Full implementation with token budget awareness.
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
MAX_TOTAL_CHARS = 8000   # Rough token budget (~2000 tokens for context)


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

    # Available tools
    available_capability_ids: list[str] = field(default_factory=list)

    # User context
    user_preferences: dict[str, Any] = field(default_factory=dict)
    recent_user_messages: list[str] = field(default_factory=list)

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
        identity: str = "AEGIS — autonomous multi-device AI assistant",
    ) -> None:
        self._event_bus = event_bus
        self._episodic = episodic_memory
        self._semantic = semantic_memory
        self._procedural = procedural_memory
        self._reflection = reflection_log
        self._tool_broker = tool_broker
        self._identity = identity
        self._goals: list[str] = []
        self._last_context: Context | None = None

    # ── Goal management ─────────────────────────────────────

    def set_goals(self, goals: list[str]) -> None:
        self._goals = goals

    # ── Build ───────────────────────────────────────────────

    def build(
        self,
        triggering_events: list[Event] | None = None,
        triggering_query: str = "",
    ) -> Context:
        """Build a Context object from all available data sources."""
        ctx = Context(
            built_at_ms=int(time.time() * 1000),
            context_id=f"ctx_{int(time.time() * 1000)}",
            identity=self._identity,
            current_goals=self._goals[:MAX_GOALS],
        )

        # 1. Recent events from EventBus or direct triggering events
        if self._event_bus:
            events: list[Event] = self._event_bus.list_recent_events(MAX_RECENT_EVENTS)
            ctx.recent_events = events
        if triggering_events:
            ctx.recent_events = list(triggering_events) + ctx.recent_events

        # 2. Episodic memory
        if self._episodic:
            episodes = self._episodic.list_recent(MAX_MEMORIES)
            ctx.recent_episodes = [
                f"[{e.category}] {e.summary}" for e in episodes
            ]

        # 3. Semantic memory — search relevant facts
        if self._semantic and triggering_query:
            facts = self._semantic.search(triggering_query, category=None)
            ctx.relevant_facts = [
                _truncate(f"[{f.category}] {f.content}", 200)
                for f in facts[:MAX_FACTS]
            ]

        # 4. Procedural memory — search for relevant procedures
        if self._procedural and triggering_query:
            procs = self._procedural.find_for_goal(triggering_query)
            ctx.relevant_procedures = [
                f"[conf={p.confidence:.0%}] {p.goal}: {' → '.join(p.steps[:5])}"
                for p in procs[:MAX_PROCEDURES] if p.confidence > 0.3
            ]

        # 5. Reflection — recent improvement ideas
        if self._reflection:
            refs = self._reflection.list_recent(MAX_REFLECTIONS)
            ctx.recent_reflections = [
                f"Reflection: {r.summary}" for r in refs
            ]

        # 6. Available capabilities
        if self._tool_broker:
            try:
                safe_caps = self._tool_broker.list_safe_capabilities()
                ctx.available_capability_ids = [
                    c.id for c in safe_caps[:MAX_CAPABILITIES]
                ]
            except Exception:
                ctx.available_capability_ids = []

        # 7. Truncate if needed
        self._apply_budget(ctx)
        self._last_context = ctx
        return ctx

    def _apply_budget(self, ctx: Context) -> None:
        """Truncate context if it exceeds the character budget."""
        # Estimate total chars
        total = (
            len(ctx.identity) +
            len(" ".join(ctx.current_goals)) +
            sum(len(str(e)) for e in ctx.recent_events) +
            sum(len(s) for s in ctx.recent_episodes) +
            sum(len(s) for s in ctx.relevant_facts) +
            sum(len(s) for s in ctx.relevant_procedures) +
            sum(len(s) for s in ctx.recent_reflections) +
            sum(len(s) for s in ctx.available_capability_ids) +
            sum(len(s) for s in ctx.recent_user_messages)
        )
        ctx.total_chars = total

        if total > MAX_TOTAL_CHARS:
            ctx.truncated = True
            # Truncate events first (lowest priority detail)
            while total > MAX_TOTAL_CHARS and len(ctx.recent_events) > 3:
                ctx.recent_events = ctx.recent_events[1:]
                total = (
                    len(ctx.identity) +
                    sum(len(str(e)) for e in ctx.recent_events) +
                    len(" ".join(ctx.recent_episodes)) +
                    len(" ".join(ctx.relevant_facts))
                )
            # If still too large, drop facts
            while total > MAX_TOTAL_CHARS and len(ctx.relevant_facts) > 1:
                ctx.relevant_facts.pop()
                total = (
                    len(ctx.identity) +
                    sum(len(str(e)) for e in ctx.recent_events) +
                    len(" ".join(ctx.relevant_facts))
                )

    @property
    def last_context(self) -> Context | None:
        return self._last_context
