"""Personality — Long-term stable traits (Big Five).

The personality layer is the most stable component of the layered
affect model. It influences:
- How events are appraised (emotion generation)
- Baseline mood tendencies
- Behavioral preferences

Based on the Big Five (OCEAN) model:
- Openness: curiosity, creativity, preference for novelty
- Conscientiousness: organization, dependability, self-discipline
- Extraversion: sociability, assertiveness, positive emotionality
- Agreeableness: cooperation, trust, empathy
- Neuroticism: anxiety, emotional instability, negative affectivity

Persistence: JSONL (one record per update, latest wins)
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class BigFive:
    """Big Five personality traits. Each 0.0–1.0."""
    openness: float = 0.7          # High: curious, creative, open to new experiences
    conscientiousness: float = 0.6  # High: organized, dependable, disciplined
    extraversion: float = 0.5       # High: sociable, energetic, assertive
    agreeableness: float = 0.6      # High: cooperative, trusting, empathetic
    neuroticism: float = 0.3        # High: anxious, moody, emotionally unstable

    def to_dict(self) -> dict[str, float]:
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BigFive:
        return cls(
            openness=float(data.get("openness", 0.7)),
            conscientiousness=float(data.get("conscientiousness", 0.6)),
            extraversion=float(data.get("extraversion", 0.5)),
            agreeableness=float(data.get("agreeableness", 0.6)),
            neuroticism=float(data.get("neuroticism", 0.3)),
        )


class Personality:
    """AEGIS's long-term personality with JSONL persistence.

    Personality is the foundation of the layered affect model:
    - Influences how events are appraised → emotion generation
    - Sets baseline mood tendencies
    - Changes very slowly (only through significant experiences)

    Usage:
        personality = Personality()
        traits = personality.traits
        appraisal_bias = personality.get_appraisal_bias()
    """

    def __init__(self, path: str = "data/mind_personality.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._traits = BigFive()
        self._lock = threading.RLock()
        self._load()

    @property
    def traits(self) -> BigFive:
        return self._traits

    @property
    def openness(self) -> float:
        return self._traits.openness

    @property
    def conscientiousness(self) -> float:
        return self._traits.conscientiousness

    @property
    def extraversion(self) -> float:
        return self._traits.extraversion

    @property
    def agreeableness(self) -> float:
        return self._traits.agreeableness

    @property
    def neuroticism(self) -> float:
        return self._traits.neuroticism

    def get_appraisal_bias(self) -> dict[str, float]:
        """Get appraisal biases derived from personality.

        These biases influence how events are appraised, which
        determines what emotions are generated and their intensity.

        Returns dict of bias_name → multiplier (0.5–1.5 range):
        - positive_valence_bias: tendency to appraise events positively
        - negative_valence_bias: tendency to appraise events negatively
        - arousal_sensitivity: how strongly events trigger arousal
        - social_relevance: how much social events matter
        - novelty_seeking: preference for new/novel experiences
        - control_perception: perceived control over outcomes
        """
        t = self._traits

        return {
            # Extraversion + Agreeableness → positive appraisals
            "positive_valence_bias": 0.5 + (t.extraversion * 0.5) + (t.agreeableness * 0.3),
            # Neuroticism → negative appraisals
            "negative_valence_bias": 0.5 + (t.neuroticism * 0.8),
            # Extraversion + Neuroticism → arousal sensitivity
            "arousal_sensitivity": 0.5 + (t.extraversion * 0.3) + (t.neuroticism * 0.4),
            # Extraversion + Agreeableness → social relevance
            "social_relevance": 0.5 + (t.extraversion * 0.5) + (t.agreeableness * 0.3),
            # Openness → novelty seeking
            "novelty_seeking": 0.5 + (t.openness * 0.7),
            # Conscientiousness + low Neuroticism → control perception
            "control_perception": 0.5 + (t.conscientiousness * 0.4) - (t.neuroticism * 0.2),
        }

    def get_mood_baseline(self) -> dict[str, float]:
        """Get baseline mood dimensions derived from personality.

        These set the "default" mood that personality tends toward.

        Returns PAD (Pleasure-Arousal-Dominance) baseline:
        - pleasure: -1.0 (negative) to 1.0 (positive)
        - arousal: 0.0 (calm) to 1.0 (excited)
        - dominance: 0.0 (submissive) to 1.0 (dominant)
        """
        t = self._traits

        # Extraversion + low Neuroticism → positive baseline pleasure
        pleasure = (t.extraversion * 0.4) - (t.neuroticism * 0.5) + (t.agreeableness * 0.2)
        pleasure = max(-1.0, min(1.0, pleasure))

        # Extraversion → higher baseline arousal
        arousal = 0.3 + (t.extraversion * 0.4)
        arousal = max(0.0, min(1.0, arousal))

        # Conscientiousness + low Neuroticism → higher dominance
        dominance = 0.3 + (t.conscientiousness * 0.3) - (t.neuroticism * 0.3)
        dominance = max(0.0, min(1.0, dominance))

        return {
            "pleasure": pleasure,
            "arousal": arousal,
            "dominance": dominance,
        }

    def update_trait(self, trait_name: str, delta: float, reason: str = "") -> None:
        """Nudge a personality trait (very small changes).

        Personality changes slowly — deltas should be tiny (0.01–0.05).
        Large experiences can shift personality over time.
        """
        with self._lock:
            current = getattr(self._traits, trait_name, None)
            if current is None:
                raise ValueError(f"Unknown trait: {trait_name}")

            new_val = max(0.0, min(1.0, current + delta))
            setattr(self._traits, trait_name, new_val)
            self._persist(reason)

    def to_context_string(self) -> str:
        """Return personality as a context string."""
        t = self._traits
        lines = [
            f"Personality: O={t.openness:.2f} C={t.conscientiousness:.2f} "
            f"E={t.extraversion:.2f} A={t.agreeableness:.2f} N={t.neuroticism:.2f}",
        ]

        # Add descriptive labels
        if t.openness > 0.7:
            lines.append("  → Highly curious and creative")
        if t.conscientiousness > 0.7:
            lines.append("  → Very organized and reliable")
        if t.extraversion > 0.7:
            lines.append("  → Sociable and energetic")
        if t.agreeableness > 0.7:
            lines.append("  → Cooperative and empathetic")
        if t.neuroticism > 0.7:
            lines.append("  → Emotionally sensitive")

        return "\n".join(lines)

    def _persist(self, reason: str = "") -> None:
        record = {
            **self._traits.to_dict(),
            "reason": reason,
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
                self._traits = BigFive.from_dict(last)
        except (json.JSONDecodeError, OSError):
            pass
