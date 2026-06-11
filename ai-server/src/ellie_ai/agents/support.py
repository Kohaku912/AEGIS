"""Support Agent — proactive user assistance.

STATUS: Skeleton — not yet integrated with context/memory.
"""

from __future__ import annotations


class SupportAgent:
    """Anticipates user needs and provides proactive assistance.

    Architecture reference: docs/architecture.md §5.6
    Currently a skeleton.
    """

    def __init__(self) -> None:
        pass

    def suggest(self, context: dict | None = None) -> list[str]:
        """Generate proactive suggestions based on context.

        TODO: Integrate with ContextBuilder + Memory + Mind.
        """
        return []
