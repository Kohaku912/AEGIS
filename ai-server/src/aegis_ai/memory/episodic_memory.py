"""Episodic Memory — Experience-centric memory with temporal awareness.

Records experiences as episodes with:
- What happened (action + observation)
- When it happened (timestamp)
- How it felt (emotion tag)
- What was learned (lesson)
- Who was involved (person references)
- Why it matters (importance)

Supports consolidation: summarization, tagging, dedup, linking.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.episodic_memory")


@dataclass
class Episode:
    """A single episode in AEGIS's life."""
    episode_id: str = ""
    timestamp_ms: int = 0

    # Content
    action: str = ""
    observation: str = ""
    summary: str = ""
    category: str = "general"  # conversation, action, autonomous, learning, error

    # Emotional context
    emotion_tag: str = ""      # satisfied, frustrated, curious, etc.
    valence: float = 0.0       # -1.0 to 1.0

    # Learning
    lesson: str = ""
    importance: float = 0.5    # 0.0 (trivial) to 1.0 (critical)

    # References
    persons: list[str] = field(default_factory=list)
    related_desire: str = ""
    tags: list[str] = field(default_factory=list)
    related_episodes: list[str] = field(default_factory=list)

    # Consolidation
    consolidated: bool = False
    consolidated_at_ms: int = 0
    summary_generated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "timestamp_ms": self.timestamp_ms,
            "action": self.action,
            "observation": self.observation,
            "summary": self.summary,
            "category": self.category,
            "emotion_tag": self.emotion_tag,
            "valence": self.valence,
            "lesson": self.lesson,
            "importance": self.importance,
            "persons": self.persons,
            "related_desire": self.related_desire,
            "tags": self.tags,
            "related_episodes": self.related_episodes,
            "consolidated": self.consolidated,
            "consolidated_at_ms": self.consolidated_at_ms,
            "summary_generated": self.summary_generated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Episode:
        return cls(
            episode_id=data.get("episode_id", ""),
            timestamp_ms=int(data.get("timestamp_ms", 0)),
            action=data.get("action", ""),
            observation=data.get("observation", ""),
            summary=data.get("summary", ""),
            category=data.get("category", "general"),
            emotion_tag=data.get("emotion_tag", ""),
            valence=float(data.get("valence", 0.0)),
            lesson=data.get("lesson", ""),
            importance=float(data.get("importance", 0.5)),
            persons=data.get("persons", []),
            related_desire=data.get("related_desire", ""),
            tags=data.get("tags", []),
            related_episodes=data.get("related_episodes", []),
            consolidated=bool(data.get("consolidated", False)),
            consolidated_at_ms=int(data.get("consolidated_at_ms", 0)),
            summary_generated=bool(data.get("summary_generated", False)),
        )


class EpisodicMemory:
    """Experience-centric episodic memory.

    Records and retrieves episodes — integrated memories of
    actions, observations, emotions, and lessons.

    Usage:
        em = EpisodicMemory()
        em.record(action="Checked AGORA", observation="Found 3 messages",
                  emotion_tag="satisfied", persons=["Kohaku"])
        recent = em.recall_recent(10)
        similar = em.recall_similar("AGORA messages")
    """

    MAX_EPISODES = 2000

    def __init__(self, path: str = "data/memory/episodic.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._episodes: list[Episode] = []
        self._index: dict[str, Episode] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    data = json.loads(line)
                    ep = Episode.from_dict(data)
                    self._episodes.append(ep)
                    self._index[ep.episode_id] = ep
            logger.info("Loaded %d episodes", len(self._episodes))
        except Exception as e:
            logger.warning("Failed to load episodes: %s", e)

    def _persist(self, episode: Episode) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(episode.to_dict(), ensure_ascii=False) + "\n")

    def record(
        self,
        action: str,
        observation: str,
        category: str = "general",
        emotion_tag: str = "",
        valence: float = 0.0,
        lesson: str = "",
        importance: float = 0.5,
        persons: list[str] | None = None,
        related_desire: str = "",
        tags: list[str] | None = None,
    ) -> Episode:
        """Record a new episode."""
        ep = Episode(
            episode_id=f"ep_{os.urandom(6).hex()}",
            timestamp_ms=int(time.time() * 1000),
            action=action,
            observation=observation,
            category=category,
            emotion_tag=emotion_tag,
            valence=valence,
            lesson=lesson,
            importance=importance,
            persons=persons or [],
            related_desire=related_desire,
            tags=tags or [],
        )

        self._episodes.append(ep)
        self._index[ep.episode_id] = ep
        self._persist(ep)

        # Trim old episodes
        if len(self._episodes) > self.MAX_EPISODES:
            self._episodes = self._episodes[-self.MAX_EPISODES:]

        return ep

    def recall_recent(self, count: int = 10, category: str | None = None) -> list[Episode]:
        """Recall most recent episodes."""
        eps = self._episodes
        if category:
            eps = [e for e in eps if e.category == category]
        return eps[-count:]

    def recall_important(self, count: int = 10) -> list[Episode]:
        """Recall most important episodes."""
        return sorted(self._episodes, key=lambda e: e.importance, reverse=True)[:count]

    def recall_similar(self, query: str, count: int = 5) -> list[Episode]:
        """Recall episodes similar to query (keyword matching)."""
        q = query.lower()
        scored: list[tuple[float, Episode]] = []
        for ep in self._episodes:
            text = f"{ep.action} {ep.observation} {ep.summary} {ep.lesson} {' '.join(ep.tags)}".lower()
            score = sum(1 for word in q.split() if word in text)
            if score > 0:
                # Recency bonus
                age_hours = (time.time() * 1000 - ep.timestamp_ms) / 3_600_000
                recency = max(0, 1.0 - age_hours / 168)
                score += recency * 0.5 + ep.importance * 0.3
                scored.append((score, ep))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored[:count]]

    def recall_by_person(self, person_name: str, count: int = 10) -> list[Episode]:
        """Recall episodes involving a specific person."""
        p = person_name.lower()
        matching = [e for e in self._episodes if any(p in per.lower() for per in e.persons)]
        return matching[-count:]

    def recall_by_tag(self, tag: str, count: int = 10) -> list[Episode]:
        """Recall episodes with a specific tag."""
        t = tag.lower()
        matching = [e for e in self._episodes if t in [tg.lower() for tg in e.tags]]
        return matching[-count:]

    def get_unconsolidated(self, max_count: int = 50) -> list[Episode]:
        """Get episodes that haven't been consolidated yet."""
        return [e for e in self._episodes if not e.consolidated][:max_count]

    def mark_consolidated(self, episode_id: str, summary: str = "") -> None:
        """Mark an episode as consolidated."""
        ep = self._index.get(episode_id)
        if ep:
            ep.consolidated = True
            ep.consolidated_at_ms = int(time.time() * 1000)
            if summary:
                ep.summary = summary
                ep.summary_generated = True

    def link_episodes(self, ep_id1: str, ep_id2: str) -> None:
        """Create a bidirectional link between episodes."""
        ep1 = self._index.get(ep_id1)
        ep2 = self._index.get(ep_id2)
        if ep1 and ep2:
            if ep_id2 not in ep1.related_episodes:
                ep1.related_episodes.append(ep_id2)
            if ep_id1 not in ep2.related_episodes:
                ep2.related_episodes.append(ep_id1)

    def update_importance(self, episode_id: str, new_importance: float) -> None:
        """Update importance of an episode."""
        ep = self._index.get(episode_id)
        if ep:
            ep.importance = max(0.0, min(1.0, new_importance))

    def get_stats(self) -> dict[str, Any]:
        total = len(self._episodes)
        consolidated = sum(1 for e in self._episodes if e.consolidated)
        return {
            "total_episodes": total,
            "consolidated": consolidated,
            "unconsolidated": total - consolidated,
            "categories": {cat: sum(1 for e in self._episodes if e.category == cat) for cat in set(e.category for e in self._episodes)},
            "average_importance": sum(e.importance for e in self._episodes) / total if total else 0,
        }
