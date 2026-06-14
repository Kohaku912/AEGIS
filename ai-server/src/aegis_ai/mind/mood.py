"""Mood — Medium-term affective state (PAD model).

Mood is the middle layer of the layered affect model:
- More stable than emotions, less stable than personality
- Influenced by accumulated recent emotions
- Influences emotion generation (good mood → easier positive emotions)
- Decays toward personality-derived baseline over time

Uses the PAD (Pleasure-Arousal-Dominance) model:
- Pleasure: -1.0 (negative) to 1.0 (positive)
- Arousal: 0.0 (calm) to 1.0 (excited)
- Dominance: 0.0 (submissive/in-control) to 1.0 (dominant/in-control)

Persistence: JSONL (latest record is current state)
"""

from __future__ import annotations

import json
import math
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MoodState:
    """PAD mood dimensions."""
    pleasure: float = 0.0      # -1.0 (negative) to 1.0 (positive)
    arousal: float = 0.3       # 0.0 (calm) to 1.0 (excited)
    dominance: float = 0.5     # 0.0 (low control) to 1.0 (high control)
    last_updated_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "pleasure": round(self.pleasure, 4),
            "arousal": round(self.arousal, 4),
            "dominance": round(self.dominance, 4),
            "last_updated_ms": self.last_updated_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MoodState:
        return cls(
            pleasure=float(data.get("pleasure", 0.0)),
            arousal=float(data.get("arousal", 0.3)),
            dominance=float(data.get("dominance", 0.5)),
            last_updated_ms=int(data.get("last_updated_ms", 0)),
        )


# Mood labels derived from PAD values
_MOOD_LABELS: list[tuple[str, tuple[float, float, float]]] = [
    ("serene",      ( 0.5, 0.2, 0.5)),
    ("relaxed",     ( 0.6, 0.3, 0.6)),
    ("content",     ( 0.5, 0.3, 0.5)),
    ("cheerful",    ( 0.7, 0.5, 0.6)),
    ("excited",     ( 0.6, 0.8, 0.6)),
    ("alert",       ( 0.2, 0.8, 0.6)),
    ("tense",       (-0.3, 0.7, 0.3)),
    ("nervous",     (-0.4, 0.7, 0.2)),
    ("stressed",    (-0.5, 0.6, 0.3)),
    ("sad",         (-0.6, 0.2, 0.3)),
    ("bored",       (-0.3, 0.1, 0.4)),
    ("melancholy",  (-0.4, 0.2, 0.4)),
    ("neutral",     ( 0.0, 0.3, 0.5)),
]


def _clamp(v: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def _pad_distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class Mood:
    """AEGIS's medium-term mood with PAD model and JSONL persistence.

    Mood sits between emotion (short-term) and personality (long-term):
    - Updated by accumulated emotions
    - Decays toward personality baseline over time
    - Influences emotion generation

    Usage:
        mood = Mood()
        mood.update_from_emotion(pleasure=0.8, arousal=0.6, dominance=0.5)
        label = mood.label  # "cheerful"
    """

    def __init__(
        self,
        path: str = "data/mind_mood.jsonl",
        decay_half_life_hours: float = 6.0,
    ) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._state = MoodState()
        self._decay_half_life_ms = decay_half_life_hours * 3_600_000
        self._lock = threading.RLock()
        self._load()

    @property
    def pleasure(self) -> float:
        return self._state.pleasure

    @property
    def arousal(self) -> float:
        return self._state.arousal

    @property
    def dominance(self) -> float:
        return self._state.dominance

    @property
    def label(self) -> str:
        """Get the closest mood label."""
        current = (self._state.pleasure, self._state.arousal, self._state.dominance)
        best_label = "neutral"
        best_dist = float("inf")
        for name, pad in _MOOD_LABELS:
            d = _pad_distance(current, pad)
            if d < best_dist:
                best_dist = d
                best_label = name
        return best_label

    @property
    def valence(self) -> float:
        """Convenience: pleasure as valence (-1 to 1)."""
        return self._state.pleasure

    def update_from_emotion(
        self,
        pleasure: float,
        arousal: float,
        dominance: float,
        weight: float = 0.1,
    ) -> None:
        """Update mood based on an emotional event.

        Uses weighted moving average:
        new_mood = (1 - weight) * old_mood + weight * emotion_pad

        Args:
            pleasure: Emotion's pleasure component (-1 to 1)
            arousal: Emotion's arousal component (0 to 1)
            dominance: Emotion's dominance component (0 to 1)
            weight: How much this emotion affects mood (0–1)
        """
        with self._lock:
            w = max(0.0, min(1.0, weight))
            self._state.pleasure = _clamp(
                (1 - w) * self._state.pleasure + w * pleasure
            )
            self._state.arousal = max(0.0, min(1.0,
                (1 - w) * self._state.arousal + w * arousal
            ))
            self._state.dominance = max(0.0, min(1.0,
                (1 - w) * self._state.dominance + w * dominance
            ))
            self._state.last_updated_ms = int(time.time() * 1000)
            self._persist()

    def decay_toward_baseline(self, baseline: dict[str, float]) -> None:
        """Decay mood toward personality-derived baseline.

        Uses exponential decay based on time elapsed since last update.

        Args:
            baseline: PAD values from Personality.get_mood_baseline()
        """
        now_ms = int(time.time() * 1000)
        if self._state.last_updated_ms == 0:
            self._state.last_updated_ms = now_ms
            return

        elapsed_ms = now_ms - self._state.last_updated_ms
        if elapsed_ms <= 0:
            return

        # Exponential decay factor
        decay = 1 - math.exp(-0.693 * elapsed_ms / self._decay_half_life_ms)
        decay = max(0.0, min(1.0, decay))

        with self._lock:
            self._state.pleasure = _clamp(
                self._state.pleasure + decay * (baseline.get("pleasure", 0.0) - self._state.pleasure)
            )
            self._state.arousal = max(0.0, min(1.0,
                self._state.arousal + decay * (baseline.get("arousal", 0.3) - self._state.arousal)
            ))
            self._state.dominance = max(0.0, min(1.0,
                self._state.dominance + decay * (baseline.get("dominance", 0.5) - self._state.dominance)
            ))
            self._state.last_updated_ms = now_ms
            self._persist()

    def get_emotion_modulation(self) -> dict[str, float]:
        """Get modulation factors for emotion generation based on current mood.

        Returns multipliers (0.5–1.5) that influence how emotions are generated:
        - positive_emotion_boost: easier to feel positive emotions in good mood
        - negative_emotion_boost: easier to feel negative emotions in bad mood
        - arousal_modulation: mood arousal affects emotion arousal
        """
        p = self._state.pleasure
        a = self._state.arousal

        return {
            # Good mood (high pleasure) → easier positive emotions
            "positive_emotion_boost": 1.0 + (p * 0.3),
            # Bad mood (low pleasure) → easier negative emotions
            "negative_emotion_boost": 1.0 - (p * 0.3),
            # High arousal mood → emotions are more intense
            "arousal_modulation": 0.8 + (a * 0.4),
        }

    def to_context_string(self) -> str:
        """Return mood as a context string for LLM prompts."""
        s = self._state
        return (
            f"Mood: {self.label} "
            f"(pleasure={s.pleasure:.2f}, arousal={s.arousal:.2f}, dominance={s.dominance:.2f})"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._state.to_dict(),
            "label": self.label,
        }

    def _persist(self) -> None:
        record = {
            **self._state.to_dict(),
            "label": self.label,
        }
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                last = json.loads(lines[-1])
                self._state = MoodState.from_dict(last)
        except (json.JSONDecodeError, OSError):
            pass
