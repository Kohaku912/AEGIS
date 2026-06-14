"""Social Intelligence — tracks social context and interaction patterns.

Monitors communication style preferences, interaction frequency,
and user patience to adapt response behavior.
Persists to JSONL for cross-session continuity.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SocialState:
    """Social interaction state."""
    formality: float = 0.5        # 0.0=casual, 1.0=formal
    verbosity: float = 0.5        # 0.0=concise, 1.0=detailed
    user_patience: float = 0.7    # 0.0=impatient, 1.0=patient
    interaction_count: int = 0
    last_interaction_ms: int = 0
    preferred_topics: list[str] = field(default_factory=list)


class SocialIntelligence:
    """Tracks social context and interaction patterns."""

    def __init__(self, path: str = "data/mind_social.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._state = SocialState()
        self._lock = threading.Lock()
        self._load()

    @property
    def formality(self) -> float:
        return self._state.formality

    @property
    def verbosity(self) -> float:
        return self._state.verbosity

    @property
    def user_patience(self) -> float:
        return self._state.user_patience

    @property
    def interaction_count(self) -> int:
        return self._state.interaction_count

    def update_from_interaction(
        self,
        action: str,
        response: str,
        feedback: str = "",
    ) -> None:
        """Update social state from interaction."""
        with self._lock:
            self._state.interaction_count += 1
            self._state.last_interaction_ms = int(time.time() * 1000)
            lower_feedback = feedback.lower()
            if "too long" in lower_feedback or "shorter" in lower_feedback:
                self._state.verbosity = max(0.0, self._state.verbosity - 0.05)
            elif "more detail" in lower_feedback or "explain" in lower_feedback:
                self._state.verbosity = min(1.0, self._state.verbosity + 0.05)
            if "too formal" in lower_feedback:
                self._state.formality = max(0.0, self._state.formality - 0.05)
            elif "too casual" in lower_feedback:
                self._state.formality = min(1.0, self._state.formality + 0.05)
            self._persist()

    def to_context_string(self) -> str:
        """Return social state as a string for ContextBuilder."""
        s = self._state
        return (
            f"Social context: formality={s.formality:.1f}, "
            f"verbosity={s.verbosity:.1f}, "
            f"user_patience={s.user_patience:.1f}, "
            f"interactions={s.interaction_count}"
        )

    def _persist(self) -> None:
        record = {
            "formality": self._state.formality,
            "verbosity": self._state.verbosity,
            "user_patience": self._state.user_patience,
            "interaction_count": self._state.interaction_count,
            "last_interaction_ms": self._state.last_interaction_ms,
            "preferred_topics": self._state.preferred_topics,
            "timestamp_ms": int(time.time() * 1000),
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
                self._state.formality = last.get("formality", 0.5)
                self._state.verbosity = last.get("verbosity", 0.5)
                self._state.user_patience = last.get("user_patience", 0.7)
                self._state.interaction_count = last.get("interaction_count", 0)
                self._state.last_interaction_ms = last.get("last_interaction_ms", 0)
                self._state.preferred_topics = last.get("preferred_topics", [])
        except (json.JSONDecodeError, OSError):
            pass
