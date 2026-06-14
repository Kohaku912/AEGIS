"""Layered Emotion — Short-term affective states (OCC-inspired).

Emotions are the most reactive layer of the layered affect model:
- Triggered by appraisals of events against goals/standards/preferences
- High intensity, short duration
- Decay rapidly (minutes)
- Influenced by mood and personality

Based on FAtiMA's OCC (Ortony, Clore, Collins) model:
- Joy/Distress: reactions to desirable/undesirable events
- Hope/Fear: reactions to prospects of desirable/undesirable events
- Satisfaction/Disappointment: confirmation of hopes/fears
- Pride/Shame: reactions to self-attributed success/failure
- Admiration/Reproach: reactions to other-attributed success/failure
- Gratitude/Anger: reactions to other-attributed helpful/harmful actions
- Love/Hate: reactions to appealing/unappealing entities

Persistence: JSONL (recent emotion history for mood computation)
"""

from __future__ import annotations

import json
import math
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class EmotionType(Enum):
    """OCC-based emotion types."""
    # Reactions to events (self-attributed)
    JOY = "joy"
    DISTRESS = "distress"

    # Prospective emotions (about future events)
    HOPE = "hope"
    FEAR = "fear"

    # Confirmation emotions
    SATISFACTION = "satisfaction"
    DISAPPOINTMENT = "disappointment"

    # Self-attributed reactions
    PRIDE = "pride"
    SHAME = "shame"

    # Other-attributed reactions (about others' actions)
    ADMIRATION = "admiration"
    REPROACH = "reproach"

    # Other-attributed (about others' fortunes)
    GRATITUDE = "gratitude"
    ANGER = "anger"

    # Attraction-based
    LOVE = "love"
    HATE = "hate"

    # Compound / derived
    SURPRISE = "surprise"
    CURIOSITY = "curiosity"
    BOREDOM = "boredom"
    FRUSTRATION = "frustration"


# Valence and arousal for each emotion type
_EMOTION_PROPERTIES: dict[EmotionType, tuple[float, float]] = {
    #                      (valence, arousal)
    EmotionType.JOY:           ( 0.8, 0.6),
    EmotionType.DISTRESS:      (-0.8, 0.7),
    EmotionType.HOPE:          ( 0.5, 0.6),
    EmotionType.FEAR:          (-0.6, 0.8),
    EmotionType.SATISFACTION:  ( 0.7, 0.3),
    EmotionType.DISAPPOINTMENT:(-0.6, 0.4),
    EmotionType.PRIDE:         ( 0.7, 0.5),
    EmotionType.SHAME:         (-0.7, 0.6),
    EmotionType.ADMIRATION:    ( 0.5, 0.4),
    EmotionType.REPROACH:      (-0.5, 0.5),
    EmotionType.GRATITUDE:     ( 0.6, 0.4),
    EmotionType.ANGER:         (-0.7, 0.8),
    EmotionType.LOVE:          ( 0.9, 0.5),
    EmotionType.HATE:          (-0.8, 0.7),
    EmotionType.SURPRISE:      ( 0.1, 0.9),
    EmotionType.CURIOSITY:     ( 0.4, 0.6),
    EmotionType.BOREDOM:       (-0.3, 0.1),
    EmotionType.FRUSTRATION:   (-0.5, 0.7),
}


@dataclass
class EmotionInstance:
    """A single emotion instance with intensity and decay."""
    emotion_type: EmotionType = EmotionType.JOY
    intensity: float = 0.5         # 0.0 (weak) to 1.0 (strong)
    valence: float = 0.0           # Derived from type
    arousal: float = 0.5           # Derived from type
    trigger: str = ""              # What caused this emotion
    trigger_desire: str = ""       # Related desire name
    created_at_ms: int = 0
    peak_intensity: float = 0.5    # Highest intensity reached
    decay_rate: float = 0.1        # Decay per minute

    @property
    def age_seconds(self) -> float:
        return (time.time() * 1000 - self.created_at_ms) / 1000

    @property
    def current_intensity(self) -> float:
        """Intensity after time-based decay."""
        age_min = self.age_seconds / 60
        decay = math.exp(-self.decay_rate * age_min)
        return max(0.0, self.intensity * decay)

    @property
    def is_active(self) -> bool:
        """Emotion is active if intensity > threshold."""
        return self.current_intensity > 0.05

    def to_dict(self) -> dict[str, Any]:
        return {
            "emotion_type": self.emotion_type.value,
            "intensity": round(self.intensity, 3),
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "trigger": self.trigger[:200],
            "trigger_desire": self.trigger_desire,
            "created_at_ms": self.created_at_ms,
            "peak_intensity": round(self.peak_intensity, 3),
            "decay_rate": self.decay_rate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EmotionInstance:
        return cls(
            emotion_type=EmotionType(data.get("emotion_type", "joy")),
            intensity=float(data.get("intensity", 0.5)),
            valence=float(data.get("valence", 0.0)),
            arousal=float(data.get("arousal", 0.5)),
            trigger=data.get("trigger", ""),
            trigger_desire=data.get("trigger_desire", ""),
            created_at_ms=int(data.get("created_at_ms", 0)),
            peak_intensity=float(data.get("peak_intensity", 0.5)),
            decay_rate=float(data.get("decay_rate", 0.1)),
        )


@dataclass
class AppraisalPattern:
    """Describes how an event is appraised.

    Used to determine what emotion is generated and at what intensity.
    """
    desirability: float = 0.0    # -1.0 (undesirable) to 1.0 (desirable)
    likelihood: float = 0.5      # 0.0 (unlikely) to 1.0 (certain)
    relevance: float = 0.5       # 0.0 (irrelevant) to 1.0 (highly relevant)
    causal_self: float = 0.5     # 0.0 (other-caused) to 1.0 (self-caused)
    causal_other: float = 0.0    # 0.0 (not other-caused) to 1.0 (other-caused)
    goal_relevance: float = 0.5  # How relevant to current goals
    standard_match: float = 0.0  # -1.0 (violates) to 1.0 (conforms to standards)
    appeal: float = 0.0          # -1.0 (repulsive) to 1.0 (appealing)


class LayeredEmotion:
    """AEGIS's short-term emotion system with OCC-inspired appraisal.

    Emotions are generated through appraisal of events:
    1. Event occurs (action result, observation, etc.)
    2. Event is appraised (desirability, likelihood, causality, etc.)
    3. Appraisal + personality + mood → emotion type + intensity
    4. Emotion decays over time
    5. Emotions accumulate and influence mood

    Usage:
        emotion = LayeredEmotion()
        emotion.appraise_and_generate(
            trigger="Task succeeded",
            appraisal=AppraisalPattern(desirability=0.8, causal_self=0.9),
        )
        active = emotion.get_active_emotions()
    """

    MAX_HISTORY = 100

    def __init__(self, path: str = "data/mind_layered_emotion.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._active: list[EmotionInstance] = []
        self._lock = threading.RLock()
        self._load()

    def appraise_and_generate(
        self,
        trigger: str,
        appraisal: AppraisalPattern,
        personality_biases: dict[str, float] | None = None,
        mood_modulation: dict[str, float] | None = None,
        trigger_desire: str = "",
    ) -> list[EmotionInstance]:
        """Appraise an event and generate appropriate emotions.

        This is the core emotion generation mechanism, inspired by FAtiMA.

        Args:
            trigger: Description of what happened
            appraisal: How the event is appraised
            personality_biases: From Personality.get_appraisal_bias()
            mood_modulation: From Mood.get_emotion_modulation()
            trigger_desire: Related desire name

        Returns:
            List of generated emotions
        """
        biases = personality_biases or {}
        mood_mod = mood_modulation or {}

        positive_boost = mood_mod.get("positive_emotion_boost", 1.0)
        negative_boost = mood_mod.get("negative_emotion_boost", 1.0)
        arousal_mod = mood_mod.get("arousal_modulation", 1.0)
        pos_bias = biases.get("positive_valence_bias", 1.0)
        neg_bias = biases.get("negative_valence_bias", 1.0)

        generated: list[EmotionInstance] = []

        # Determine emotions based on appraisal pattern
        emotions = self._compute_emotions_from_appraisal(
            appraisal,
            positive_boost * pos_bias,
            negative_boost * neg_bias,
            arousal_mod,
        )

        for emotion_type, intensity in emotions:
            if intensity < 0.05:
                continue

            props = _EMOTION_PROPERTIES.get(emotion_type, (0.0, 0.5))
            instance = EmotionInstance(
                emotion_type=emotion_type,
                intensity=min(1.0, intensity),
                valence=props[0],
                arousal=max(0.0, min(1.0, props[1] * arousal_mod)),
                trigger=trigger,
                trigger_desire=trigger_desire,
                created_at_ms=int(time.time() * 1000),
                peak_intensity=min(1.0, intensity),
                decay_rate=self._get_decay_rate(emotion_type),
            )
            generated.append(instance)

        with self._lock:
            self._active.extend(generated)
            # Trim old emotions
            self._active = [e for e in self._active if e.is_active]
            if len(self._active) > self.MAX_HISTORY:
                self._active = self._active[-self.MAX_HISTORY:]
            self._persist()

        return generated

    def _compute_emotions_from_appraisal(
        self,
        a: AppraisalPattern,
        pos_boost: float,
        neg_boost: float,
        arousal_mod: float,
    ) -> list[tuple[EmotionType, float]]:
        """Compute emotions from appraisal pattern (OCC-inspired)."""
        results: list[tuple[EmotionType, float]] = []

        # --- Reactions to events ---
        # Joy: desirable event occurred
        if a.desirability > 0.3:
            intensity = a.desirability * a.relevance * pos_boost
            results.append((EmotionType.JOY, intensity))

        # Distress: undesirable event occurred
        if a.desirability < -0.3:
            intensity = abs(a.desirability) * a.relevance * neg_boost
            results.append((EmotionType.DISTRESS, intensity))

        # --- Prospective emotions ---
        # Hope: prospect of desirable event
        if a.desirability > 0.3 and a.likelihood > 0.3:
            intensity = a.desirability * a.likelihood * a.relevance * pos_boost * 0.8
            results.append((EmotionType.HOPE, intensity))

        # Fear: prospect of undesirable event
        if a.desirability < -0.3 and a.likelihood > 0.3:
            intensity = abs(a.desirability) * a.likelihood * a.relevance * neg_boost * 0.8
            results.append((EmotionType.FEAR, intensity))

        # --- Confirmation emotions ---
        # Satisfaction: hope confirmed (desirable + likely → happened)
        if a.desirability > 0.5 and a.likelihood > 0.7:
            intensity = a.desirability * a.likelihood * pos_boost * 0.7
            results.append((EmotionType.SATISFACTION, intensity))

        # Disappointment: fear confirmed or hope disconfirmed
        if a.desirability < -0.5 and a.likelihood > 0.7:
            intensity = abs(a.desirability) * a.likelihood * neg_boost * 0.7
            results.append((EmotionType.DISAPPOINTMENT, intensity))

        # --- Self-attributed ---
        # Pride: self-caused desirable outcome
        if a.desirability > 0.3 and a.causal_self > 0.6:
            intensity = a.desirability * a.causal_self * a.standard_match * pos_boost * 0.8
            if a.standard_match > 0:
                results.append((EmotionType.PRIDE, max(0, intensity)))

        # Shame: self-caused undesirable outcome
        if a.desirability < -0.3 and a.causal_self > 0.6:
            intensity = abs(a.desirability) * a.causal_self * neg_boost * 0.8
            results.append((EmotionType.SHAME, intensity))

        # --- Other-attributed ---
        # Admiration: other caused desirable outcome that conforms to standards
        if a.desirability > 0.3 and a.causal_other > 0.6 and a.standard_match > 0.3:
            intensity = a.desirability * a.causal_other * pos_boost * 0.7
            results.append((EmotionType.ADMIRATION, intensity))

        # Reproach: other caused undesirable outcome that violates standards
        if a.desirability < -0.3 and a.causal_other > 0.6 and a.standard_match < -0.3:
            intensity = abs(a.desirability) * a.causal_other * neg_boost * 0.7
            results.append((EmotionType.REPROACH, intensity))

        # Gratitude: other helped
        if a.desirability > 0.5 and a.causal_other > 0.6 and a.appeal > 0.3:
            intensity = a.desirability * a.causal_other * pos_boost * 0.6
            results.append((EmotionType.GRATITUDE, intensity))

        # Anger: other harmed
        if a.desirability < -0.5 and a.causal_other > 0.6 and a.appeal < -0.3:
            intensity = abs(a.desirability) * a.causal_other * neg_boost * 0.6
            results.append((EmotionType.ANGER, intensity))

        # --- Attraction ---
        if a.appeal > 0.5:
            intensity = a.appeal * a.relevance * pos_boost * 0.5
            results.append((EmotionType.LOVE, intensity))

        if a.appeal < -0.5:
            intensity = abs(a.appeal) * a.relevance * neg_boost * 0.5
            results.append((EmotionType.HATE, intensity))

        # --- Surprise (high unexpectedness) ---
        if abs(a.desirability) > 0.5 and a.likelihood < 0.3:
            intensity = abs(a.desirability) * (1 - a.likelihood) * arousal_mod * 0.6
            results.append((EmotionType.SURPRISE, intensity))

        # --- Curiosity (relevant but uncertain) ---
        if a.relevance > 0.5 and a.goal_relevance > 0.5 and 0.2 < a.likelihood < 0.8:
            intensity = a.relevance * a.goal_relevance * 0.4
            results.append((EmotionType.CURIOSITY, intensity))

        # --- Frustration (undesirable + self-caused + repeated) ---
        if a.desirability < -0.4 and a.causal_self > 0.5:
            intensity = abs(a.desirability) * a.causal_self * neg_boost * 0.5
            results.append((EmotionType.FRUSTRATION, intensity))

        return results

    def _get_decay_rate(self, emotion_type: EmotionType) -> float:
        """Get decay rate for emotion type (per minute)."""
        high_arousal = {
            EmotionType.ANGER, EmotionType.FEAR, EmotionType.SURPRISE,
            EmotionType.DISTRESS,
        }
        low_arousal = {
            EmotionType.SATISFACTION, EmotionType.PRIDE, EmotionType.LOVE,
            EmotionType.ADMIRATION, EmotionType.GRATITUDE,
        }
        if emotion_type in high_arousal:
            return 0.15  # Decay faster
        if emotion_type in low_arousal:
            return 0.05  # Decay slower
        return 0.1

    def get_active_emotions(self) -> list[EmotionInstance]:
        """Get currently active (non-decayed) emotions."""
        with self._lock:
            self._active = [e for e in self._active if e.is_active]
            return list(self._active)

    def get_dominant_emotion(self) -> EmotionInstance | None:
        """Get the currently dominant (highest intensity) emotion."""
        active = self.get_active_emotions()
        if not active:
            return None
        return max(active, key=lambda e: e.current_intensity)

    def get_emotional_state_summary(self) -> dict[str, Any]:
        """Get summary of current emotional state."""
        active = self.get_active_emotions()
        if not active:
            return {
                "active_count": 0,
                "dominant": None,
                "average_valence": 0.0,
                "average_arousal": 0.3,
            }

        dominant = max(active, key=lambda e: e.current_intensity)
        total_intensity = sum(e.current_intensity for e in active)
        avg_valence = sum(e.valence * e.current_intensity for e in active) / total_intensity if total_intensity > 0 else 0
        avg_arousal = sum(e.arousal * e.current_intensity for e in active) / total_intensity if total_intensity > 0 else 0

        return {
            "active_count": len(active),
            "dominant": {
                "type": dominant.emotion_type.value,
                "intensity": round(dominant.current_intensity, 3),
                "trigger": dominant.trigger[:100],
            },
            "average_valence": round(avg_valence, 3),
            "average_arousal": round(avg_arousal, 3),
        }

    def get_pad_contribution(self) -> dict[str, float]:
        """Get PAD (Pleasure-Arousal-Dominance) contribution from active emotions.

        Used to update mood based on accumulated emotions.
        """
        active = self.get_active_emotions()
        if not active:
            return {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}

        total_intensity = sum(e.current_intensity for e in active)
        if total_intensity == 0:
            return {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}

        pleasure = sum(e.valence * e.current_intensity for e in active) / total_intensity
        arousal = sum(e.arousal * e.current_intensity for e in active) / total_intensity

        # Dominance: positive emotions → higher dominance, negative → lower
        positive_intensity = sum(e.current_intensity for e in active if e.valence > 0)
        negative_intensity = sum(e.current_intensity for e in active if e.valence < 0)
        dominance = 0.5 + 0.3 * (positive_intensity - negative_intensity) / total_intensity
        dominance = max(0.0, min(1.0, dominance))

        return {
            "pleasure": max(-1.0, min(1.0, pleasure)),
            "arousal": max(0.0, min(1.0, arousal)),
            "dominance": dominance,
        }

    def to_context_string(self) -> str:
        """Return emotional state as context string."""
        active = self.get_active_emotions()
        if not active:
            return "Emotional state: neutral (no active emotions)"

        lines = ["Emotional state:"]
        for e in sorted(active, key=lambda x: x.current_intensity, reverse=True)[:3]:
            lines.append(f"  {e.emotion_type.value}: {e.current_intensity:.2f} — {e.trigger[:60]}")
        return "\n".join(lines)

    def _persist(self) -> None:
        record = {
            "timestamp_ms": int(time.time() * 1000),
            "active_emotions": [e.to_dict() for e in self._active if e.is_active],
            "summary": self.get_emotional_state_summary(),
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
                for e_data in last.get("active_emotions", []):
                    instance = EmotionInstance.from_dict(e_data)
                    if instance.is_active:
                        self._active.append(instance)
        except (json.JSONDecodeError, OSError):
            pass
