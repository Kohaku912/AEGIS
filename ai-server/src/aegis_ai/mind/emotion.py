"""Emotion — urgency, confidence, fatigue proxy, and other state indicators.

Not real emotions — state proxies that bias ContextBuilder.
Does NOT override PolicyEngine safety decisions.
Persists to JSONL for cross-session continuity.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EmotionState:
    """AEGIS's emotion-like state indicators."""
    urgency: int = 0            # 0 = calm, 10 = critical
    confidence: float = 0.5     # 0.0 = uncertain, 1.0 = very confident
    uncertainty: float = 0.5    # 0.0 = certain, 1.0 = very uncertain
    fatigue_proxy: float = 0.0  # Tracks cognitive load proxy
    risk_sensitivity: float = 0.5  # 0.0 = risk-tolerant, 1.0 = risk-averse
    novelty_interest: float = 0.5  # 0.0 = ignore novelty, 1.0 = very interested


class Emotion:
    """AEGIS's emotion-like state with JSONL persistence."""

    def __init__(self, path: str = "data/mind_emotion.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._state = EmotionState()
        self._lock = threading.Lock()
        self._load()

    @property
    def urgency(self) -> int:
        return self._state.urgency

    @property
    def confidence(self) -> float:
        return self._state.confidence

    @property
    def fatigue_proxy(self) -> float:
        return self._state.fatigue_proxy

    @property
    def risk_sensitivity(self) -> float:
        return self._state.risk_sensitivity

    def update(
        self,
        urgency: int | None = None,
        confidence: float | None = None,
        uncertainty: float | None = None,
        fatigue_proxy: float | None = None,
        risk_sensitivity: float | None = None,
        novelty_interest: float | None = None,
    ) -> None:
        """Update emotion state (persisted)."""
        with self._lock:
            if urgency is not None:
                self._state.urgency = max(0, min(10, urgency))
            if confidence is not None:
                self._state.confidence = max(0.0, min(1.0, confidence))
            if uncertainty is not None:
                self._state.uncertainty = max(0.0, min(1.0, uncertainty))
            if fatigue_proxy is not None:
                self._state.fatigue_proxy = max(0.0, min(1.0, fatigue_proxy))
            if risk_sensitivity is not None:
                self._state.risk_sensitivity = max(0.0, min(1.0, risk_sensitivity))
            if novelty_interest is not None:
                self._state.novelty_interest = max(0.0, min(1.0, novelty_interest))
            self._persist()

    def is_urgent(self) -> bool:
        return self._state.urgency >= 7

    def is_confident(self) -> bool:
        return self._state.confidence >= 0.7

    def is_fatigued(self) -> bool:
        return self._state.fatigue_proxy >= 0.8

    def to_context_string(self) -> str:
        """Return emotion state as a string for ContextBuilder."""
        s = self._state
        return (
            f"Emotional state: urgency={s.urgency}/10, "
            f"confidence={s.confidence:.1f}, "
            f"uncertainty={s.uncertainty:.1f}, "
            f"fatigue={s.fatigue_proxy:.1f}, "
            f"risk_sensitivity={s.risk_sensitivity:.1f}, "
            f"novelty_interest={s.novelty_interest:.1f}"
        )

    def appraise_from_experience(
        self,
        action: str,
        observation: str,
        success: bool,
        desire_name: str = "",
    ) -> None:
        """Update emotion state based on action outcome."""
        with self._lock:
            if success:
                self._state.confidence = min(1.0, self._state.confidence + 0.02)
                self._state.fatigue_proxy = max(0.0, self._state.fatigue_proxy - 0.01)
                self._state.uncertainty = max(0.0, self._state.uncertainty - 0.01)
            else:
                self._state.confidence = max(0.0, self._state.confidence - 0.03)
                self._state.uncertainty = min(1.0, self._state.uncertainty + 0.02)
            self._persist()

    def _persist(self) -> None:
        record = {
            "urgency": self._state.urgency,
            "confidence": self._state.confidence,
            "uncertainty": self._state.uncertainty,
            "fatigue_proxy": self._state.fatigue_proxy,
            "risk_sensitivity": self._state.risk_sensitivity,
            "novelty_interest": self._state.novelty_interest,
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
                self._state.urgency = last.get("urgency", 0)
                self._state.confidence = last.get("confidence", 0.5)
                self._state.uncertainty = last.get("uncertainty", 0.5)
                self._state.fatigue_proxy = last.get("fatigue_proxy", 0.0)
                self._state.risk_sensitivity = last.get("risk_sensitivity", 0.5)
                self._state.novelty_interest = last.get("novelty_interest", 0.5)
        except (json.JSONDecodeError, OSError):
            pass
