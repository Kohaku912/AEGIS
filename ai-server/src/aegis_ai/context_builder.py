"""Context Builder — assembles structured context for the LLM / decision engine.

Before any decision, the Context Builder gathers:
- Current events (from Event Bus)
- Relevant memories (from Memory System)
- Current Mind state (identity, goals, emotional state)
- Available capabilities (from Tool Broker)
- User preferences and recent interactions

STATUS: Skeleton — not yet integrated with Memory/Mind/LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aegis_schema.models import Event


@dataclass
class Context:
    """Structured context for the Autonomous Loop / LLM."""

    # Current events
    recent_events: list[Event] = field(default_factory=list)

    # Memory references (将来: 実際のMemory Systemから取得)
    relevant_memories: list[str] = field(default_factory=list)

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


class ContextBuilder:
    """Assembles Context from available data sources.

    Currently a skeleton — in the future, this will query:
    - EventBus.list_recent_events()
    - Memory System (episodic + semantic)
    - Mind Layer (identity, goals, emotion)
    - ToolBroker (list safe capabilities)
    """

    def __init__(self) -> None:
        self._last_context: Context | None = None

    def build(self, triggering_events: list[Event] | None = None) -> Context:
        """Build a context object for decision-making.

        Args:
            triggering_events: Events that triggered this context build.

        Returns:
            A Context object ready for the Autonomous Loop.
        """
        import time

        ctx = Context(
            recent_events=triggering_events or [],
            built_at_ms=int(time.time() * 1000),
            context_id=f"ctx_{int(time.time() * 1000)}",
        )
        self._last_context = ctx
        return ctx

    @property
    def last_context(self) -> Context | None:
        """The most recently built context."""
        return self._last_context
