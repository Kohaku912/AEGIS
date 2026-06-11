"""Episodic Memory — conversation, event, and action history.

Persists to JSONL file for durability. In-memory cache for fast queries.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Episode:
    """A single episode: conversation turn, event, or action result."""
    episode_id: str = ""
    summary: str = ""
    category: str = "general"           # "conversation", "event", "action_result"
    events: list[str] = field(default_factory=list)   # Referenced event IDs
    detail: dict[str, Any] = field(default_factory=dict)
    timestamp_ms: int = 0


class EpisodicMemory:
    """Stores conversation and event history with JSONL persistence."""

    def __init__(self, path: str = "data/episodic.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._episodes: list[Episode] = []
        self._lock = threading.Lock()

    def add(self, episode: Episode) -> None:
        if not episode.episode_id:
            episode.episode_id = f"ep_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
        if not episode.timestamp_ms:
            episode.timestamp_ms = int(time.time() * 1000)

        record = {
            "episode_id": episode.episode_id, "summary": episode.summary,
            "category": episode.category, "events": episode.events,
            "detail": episode.detail, "timestamp_ms": episode.timestamp_ms,
        }
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._episodes.append(episode)

    def list_recent(self, n: int = 50, category: str | None = None) -> list[Episode]:
        with self._lock:
            eps = list(self._episodes)
        if category:
            eps = [e for e in eps if e.category == category]
        return eps[-n:] if n < len(eps) else eps

    def search(self, query: str, n: int = 20) -> list[Episode]:
        query_lower = query.lower()
        with self._lock:
            eps = list(self._episodes)
        results = [e for e in eps if query_lower in e.summary.lower() or query_lower in str(e.detail).lower()]
        return results[-n:] if n < len(results) else results

    def clear(self) -> None:
        with self._lock:
            self._episodes.clear()
