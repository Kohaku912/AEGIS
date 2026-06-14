"""Experiential Memory — autobiographical memory for AEGIS.

Stores experiences as integrated records of:
- What happened (action + observation)
- How it felt (emotion evaluation)
- What was learned (learning extraction)

Unlike fact-based memory, this stores holistic experiences
that help AEGIS build a sense of "personal history."

Usage:
    exp_memory = ExperientialMemory(llm_provider=llm)
    exp_memory.record_experience(
        action="Checked AGORA for messages",
        observation="Found 3 new messages from user",
        context="autonomous_social_connection",
    )
    past = exp_memory.recall_similar("messages from user")
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.experiential")


@dataclass
class Experience:
    """A single experience — the basic unit of autobiographical memory."""
    experience_id: str = ""
    timestamp_ms: int = 0

    # What happened
    action: str = ""
    observation: str = ""
    context: str = ""

    # How it felt (filled by LLM evaluation)
    emotion_label: str = ""       # e.g., "satisfied", "frustrated", "curious"
    emotion_valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    emotion_arousal: float = 0.0  # 0.0 (calm) to 1.0 (excited)

    # What was learned (filled by LLM extraction)
    learning: str = ""
    importance: float = 0.5  # 0.0 = trivial, 1.0 = life-changing

    # Connections
    tags: list[str] = field(default_factory=list)
    related_desire: str = ""
    outcome_success: bool = False


class ExperientialMemory:
    """Autobiographical memory system for AEGIS.

    Stores and retrieves experiences — integrated records of
    actions, observations, emotions, and learnings.
    """

    def __init__(
        self,
        data_dir: str = "data/memory",
        llm_provider: Any = None,
        max_entries: int = 1000,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._llm = llm_provider
        self._max_entries = max_entries

        self._experiences: list[Experience] = []
        self._load()

    def _state_path(self) -> Path:
        return self._data_dir / "experiences.jsonl"

    def _load(self) -> None:
        """Load experiences from disk."""
        path = self._state_path()
        if not path.exists():
            return
        try:
            for line in path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    data = json.loads(line)
                    self._experiences.append(Experience(**data))
            logger.info("Loaded %d experiences", len(self._experiences))
        except Exception as exc:
            logger.warning("Failed to load experiences: %s", exc)

    def _save(self) -> None:
        """Persist experiences to disk."""
        path = self._state_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                for exp in self._experiences[-self._max_entries:]:
                    f.write(json.dumps(self._to_dict(exp), ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.warning("Failed to save experiences: %s", exc)

    def _to_dict(self, exp: Experience) -> dict[str, Any]:
        return {
            "experience_id": exp.experience_id,
            "timestamp_ms": exp.timestamp_ms,
            "action": exp.action,
            "observation": exp.observation,
            "context": exp.context,
            "emotion_label": exp.emotion_label,
            "emotion_valence": exp.emotion_valence,
            "emotion_arousal": exp.emotion_arousal,
            "learning": exp.learning,
            "importance": exp.importance,
            "tags": exp.tags,
            "related_desire": exp.related_desire,
            "outcome_success": exp.outcome_success,
        }

    def record_experience(
        self,
        action: str,
        observation: str,
        context: str = "",
        related_desire: str = "",
        outcome_success: bool = False,
    ) -> Experience:
        """Record a new experience and evaluate it with LLM.

        This is the main entry point. It:
        1. Creates the experience record
        2. Uses LLM to evaluate emotion and extract learning
        3. Persists to disk
        """
        exp = Experience(
            experience_id=f"exp_{uuid.uuid4().hex[:10]}",
            timestamp_ms=int(time.time() * 1000),
            action=action,
            observation=observation,
            context=context,
            related_desire=related_desire,
            outcome_success=outcome_success,
        )

        if self._llm:
            self._evaluate_experience(exp)

        self._experiences.append(exp)
        self._save()

        logger.info(
            "Recorded experience: %s [%s] valence=%.1f",
            exp.action[:40], exp.emotion_label, exp.emotion_valence,
        )
        return exp

    def _evaluate_experience(self, exp: Experience) -> None:
        """Use LLM to evaluate the emotional impact and extract learning."""
        prompt = f"""You are AEGIS's experience evaluator. Analyze this experience and provide emotional and learning assessments.

Experience:
- Action: {exp.action}
- Observation: {exp.observation}
- Context: {exp.context}
- Outcome: {"success" if exp.outcome_success else "failure"}

Respond with JSON:
{{
  "emotion_label": "one of: satisfied, frustrated, curious, surprised, bored, anxious, proud, disappointed, neutral",
  "emotion_valence": 0.0,
  "emotion_arousal": 0.0,
  "learning": "What was learned from this experience (one sentence)",
  "importance": 0.5,
  "tags": ["tag1", "tag2"]
}}

Guidelines:
- emotion_valence: -1.0 (very negative) to 1.0 (very positive)
- emotion_arousal: 0.0 (calm/quiet) to 1.0 (excited/intense)
- importance: 0.0 (trivial routine) to 1.0 (significant life event)
- learning: Be specific and actionable
- tags: 2-4 relevant tags for retrieval"""

        result = self._llm.generate(
            prompt=prompt,
            system_prompt="You are an experience evaluator. Output only valid JSON.",
            max_tokens=300,
        )

        if not result.success:
            return

        try:
            clean = result.content.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:])
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()

            data = json.loads(clean)
            exp.emotion_label = data.get("emotion_label", "neutral")
            exp.emotion_valence = max(-1.0, min(1.0, float(data.get("emotion_valence", 0.0))))
            exp.emotion_arousal = max(0.0, min(1.0, float(data.get("emotion_arousal", 0.0))))
            exp.learning = data.get("learning", "")
            exp.importance = max(0.0, min(1.0, float(data.get("importance", 0.5))))
            exp.tags = data.get("tags", [])
        except Exception as e:
            logger.warning("Failed to parse experience evaluation: %s", e)

    def recall_recent(self, count: int = 5) -> list[Experience]:
        """Recall the most recent experiences."""
        return self._experiences[-count:]

    def recall_important(self, count: int = 5) -> list[Experience]:
        """Recall the most important experiences."""
        sorted_exps = sorted(self._experiences, key=lambda e: e.importance, reverse=True)
        return sorted_exps[:count]

    def recall_similar(self, query: str, count: int = 3) -> list[Experience]:
        """Recall experiences similar to the query using keyword matching.

        For now uses simple keyword matching. Could be enhanced with
        vector embeddings for semantic similarity.
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored: list[tuple[float, Experience]] = []
        for exp in self._experiences:
            score = 0.0
            exp_text = f"{exp.action} {exp.observation} {exp.context} {exp.learning}".lower()
            exp_words = set(exp_text.split())

            # Word overlap
            overlap = query_words & exp_words
            score += len(overlap) * 0.3

            # Substring match
            for word in query_words:
                if word in exp_text:
                    score += 0.2

            # Recency bonus (more recent = higher score)
            age_hours = (time.time() * 1000 - exp.timestamp_ms) / 3_600_000
            recency_bonus = max(0, 1.0 - age_hours / 168)  # Decay over 1 week
            score += recency_bonus * 0.3

            # Importance bonus
            score += exp.importance * 0.2

            if score > 0.1:
                scored.append((score, exp))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored[:count]]

    def recall_by_desire(self, desire_name: str, count: int = 3) -> list[Experience]:
        """Recall experiences related to a specific desire."""
        matching = [e for e in self._experiences if e.related_desire == desire_name]
        return matching[-count:]

    def recall_by_tag(self, tag: str, count: int = 5) -> list[Experience]:
        """Recall experiences with a specific tag."""
        matching = [e for e in self._experiences if tag in e.tags]
        return matching[-count:]

    def get_emotional_summary(self, hours: int = 24) -> dict[str, Any]:
        """Get emotional summary for the recent period."""
        cutoff_ms = int(time.time() * 1000) - (hours * 3_600_000)
        recent = [e for e in self._experiences if e.timestamp_ms > cutoff_ms]

        if not recent:
            return {"period_hours": hours, "count": 0, "mood": "no data"}

        valences = [e.emotion_valence for e in recent]
        avg_valence = sum(valences) / len(valences)

        emotions = {}
        for e in recent:
            emotions[e.emotion_label] = emotions.get(e.emotion_label, 0) + 1
        dominant_emotion = max(emotions, key=emotions.get) if emotions else "neutral"

        success_count = sum(1 for e in recent if e.outcome_success)
        success_rate = success_count / len(recent) if recent else 0

        return {
            "period_hours": hours,
            "count": len(recent),
            "average_valence": round(avg_valence, 2),
            "dominant_emotion": dominant_emotion,
            "success_rate": round(success_rate, 2),
            "emotion_distribution": emotions,
        }

    def get_context_string(self, max_chars: int = 1000) -> str:
        """Get experiential memory as context string for LLM prompts."""
        recent = self.recall_recent(5)
        important = self.recall_important(3)

        if not recent and not important:
            return ""

        parts = ["Recent experiences:"]
        for exp in recent:
            mood = f"[{exp.emotion_label}]" if exp.emotion_label else ""
            parts.append(f"- {exp.action}: {exp.observation[:80]} {mood}")

        if important:
            parts.append("\nImportant past experiences:")
            for exp in important:
                if exp not in recent:
                    parts.append(f"- {exp.action}: {exp.learning[:80]}")

        summary = self.get_emotional_summary(24)
        if summary["count"] > 0:
            parts.append(f"\nRecent mood: {summary['dominant_emotion']} (valence={summary['average_valence']})")

        result = "\n".join(parts)
        return result[:max_chars]

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_experiences": len(self._experiences),
            "recent_24h": len([e for e in self._experiences if e.timestamp_ms > time.time() * 1000 - 86400000]),
            "average_importance": sum(e.importance for e in self._experiences) / len(self._experiences) if self._experiences else 0,
            "unique_emotions": len(set(e.emotion_label for e in self._experiences if e.emotion_label)),
        }
