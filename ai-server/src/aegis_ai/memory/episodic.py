"""Episodic Memory — conversation and event history.

STATUS: Skeleton — in-memory only, no persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Episode:
    """A single episode (conversation turn, event, action)."""
    episode_id: str = ""
    summary: str = ""
    events: list[str] = field(default_factory=list)
    timestamp_ms: int = 0


class EpisodicMemory:
    """Stores conversation and event history."""

    def __init__(self) -> None:
        self._episodes: list[Episode] = []

    def add(self, episode: Episode) -> None:
        self._episodes.append(episode)

    def list_recent(self, n: int = 50) -> list[Episode]:
        return self._episodes[-n:] if n < len(self._episodes) else list(self._episodes)
