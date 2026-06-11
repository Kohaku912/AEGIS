"""Desire — priorities and motivations.

STATUS: Skeleton.
"""


class Desire:
    """AEGIS's desire model — priorities that bias decision-making."""

    priorities: list[tuple[str, float]] = [
        ("help_user", 1.0),
        ("learn", 0.8),
        ("stay_safe", 0.95),
        ("be_curious", 0.6),
    ]

    def top_priority(self) -> str:
        return max(self.priorities, key=lambda x: x[1])[0]
