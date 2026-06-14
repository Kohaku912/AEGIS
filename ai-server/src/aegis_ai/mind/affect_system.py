"""Affect System — Integrated layered affect model for AEGIS.

Combines three layers of affect (inspired by FAtiMA + LLMA):
1. Personality (long-term) — Big Five traits, stable
2. Mood (medium-term) — PAD model, influenced by emotion history
3. Emotion (short-term) — OCC-inspired appraisal, reactive

The layers interact:
- Personality → appraisal biases → emotion generation
- Personality → mood baseline → mood tendencies
- Emotions → accumulate → mood updates
- Mood → modulation → emotion generation
- All layers → context string for LLM

Usage:
    affect = AffectSystem()
    emotions = affect.appraise_event(
        trigger="Task succeeded",
        desirability=0.8,
        causal_self=0.9,
    )
    context = affect.to_context_string()
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from aegis_ai.mind.layered_emotion import (
    AppraisalPattern,
    EmotionInstance,
    EmotionType,
    LayeredEmotion,
)
from aegis_ai.mind.mood import Mood
from aegis_ai.mind.personality import Personality

logger = logging.getLogger("aegis_ai.mind.affect_system")


class AffectSystem:
    """Integrated layered affect system for AEGIS.

    Manages the interaction between personality, mood, and emotion.
    Provides a unified interface for:
    - Event appraisal and emotion generation
    - Mood updates from accumulated emotions
    - Context generation for LLM prompts
    - Persistence across sessions

    Safety: Affect state biases decisions but NEVER overrides PolicyEngine.
    """

    def __init__(self, data_dir: str = "data") -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._personality = Personality(
            path=str(self._data_dir / "mind_personality.jsonl")
        )
        self._mood = Mood(
            path=str(self._data_dir / "mind_mood.jsonl"),
            decay_half_life_hours=6.0,
        )
        self._emotion = LayeredEmotion(
            path=str(self._data_dir / "mind_layered_emotion.jsonl")
        )
        self._lock = threading.Lock()

        # Update mood baseline from personality
        self._sync_mood_baseline()

    @property
    def personality(self) -> Personality:
        return self._personality

    @property
    def mood(self) -> Mood:
        return self._mood

    @property
    def emotion(self) -> LayeredEmotion:
        return self._emotion

    def appraise_event(
        self,
        trigger: str,
        desirability: float = 0.0,
        likelihood: float = 0.5,
        relevance: float = 0.5,
        causal_self: float = 0.5,
        causal_other: float = 0.0,
        goal_relevance: float = 0.5,
        standard_match: float = 0.0,
        appeal: float = 0.0,
        trigger_desire: str = "",
        mood_update_weight: float = 0.1,
    ) -> list[EmotionInstance]:
        """Appraise an event and generate emotions.

        This is the main entry point for emotion generation.
        It handles the full cycle:
        1. Build appraisal pattern
        2. Get personality biases
        3. Get mood modulation
        4. Generate emotions
        5. Update mood from emotions

        Args:
            trigger: What happened
            desirability: -1.0 (bad) to 1.0 (good)
            likelihood: 0.0 (unlikely) to 1.0 (certain)
            relevance: 0.0 (irrelevant) to 1.0 (highly relevant)
            causal_self: 0.0 (not self-caused) to 1.0 (self-caused)
            causal_other: 0.0 (not other-caused) to 1.0 (other-caused)
            goal_relevance: How relevant to current goals
            standard_match: -1.0 (violates standards) to 1.0 (conforms)
            appeal: -1.0 (repulsive) to 1.0 (appealing)
            trigger_desire: Related desire name
            mood_update_weight: How much this event affects mood

        Returns:
            List of generated emotions
        """
        appraisal = AppraisalPattern(
            desirability=max(-1.0, min(1.0, desirability)),
            likelihood=max(0.0, min(1.0, likelihood)),
            relevance=max(0.0, min(1.0, relevance)),
            causal_self=max(0.0, min(1.0, causal_self)),
            causal_other=max(0.0, min(1.0, causal_other)),
            goal_relevance=max(0.0, min(1.0, goal_relevance)),
            standard_match=max(-1.0, min(1.0, standard_match)),
            appeal=max(-1.0, min(1.0, appeal)),
        )

        personality_biases = self._personality.get_appraisal_bias()
        mood_modulation = self._mood.get_emotion_modulation()

        with self._lock:
            # Decay mood toward baseline
            baseline = self._personality.get_mood_baseline()
            self._mood.decay_toward_baseline(baseline)

            # Generate emotions
            emotions = self._emotion.appraise_and_generate(
                trigger=trigger,
                appraisal=appraisal,
                personality_biases=personality_biases,
                mood_modulation=mood_modulation,
                trigger_desire=trigger_desire,
            )

            # Update mood from emotion accumulation
            if emotions:
                pad = self._emotion.get_pad_contribution()
                self._mood.update_from_emotion(
                    pleasure=pad["pleasure"],
                    arousal=pad["arousal"],
                    dominance=pad["dominance"],
                    weight=mood_update_weight,
                )

        if emotions:
            dominant = max(emotions, key=lambda e: e.intensity)
            logger.info(
                "Appraised '%s': %s (intensity=%.2f) valence=%.1f",
                trigger[:40], dominant.emotion_type.value,
                dominant.intensity, dominant.valence,
            )

        return emotions

    def appraise_from_experience(
        self,
        action: str,
        observation: str,
        success: bool,
        desire_name: str = "",
    ) -> list[EmotionInstance]:
        """Appraise an experience (from autonomous loop or interaction).

        Convenience method that derives appraisal parameters from
        the experience outcome.

        Args:
            action: What was done
            observation: What happened
            success: Whether the action succeeded
            desire_name: Related desire
        """
        if success:
            return self.appraise_event(
                trigger=f"{action}: {observation[:100]}",
                desirability=0.6,
                likelihood=0.9,
                relevance=0.7,
                causal_self=0.8,
                goal_relevance=0.7,
                standard_match=0.5,
                trigger_desire=desire_name,
            )
        else:
            return self.appraise_event(
                trigger=f"{action}: {observation[:100]}",
                desirability=-0.5,
                likelihood=0.8,
                relevance=0.7,
                causal_self=0.6,
                goal_relevance=0.7,
                standard_match=-0.3,
                trigger_desire=desire_name,
            )

    def appraise_user_interaction(
        self,
        user_message: str,
        bot_response: str,
        positive_outcome: bool = True,
    ) -> list[EmotionInstance]:
        """Appraise a user interaction.

        Args:
            user_message: What the user said
            bot_response: How AEGIS responded
            positive_outcome: Whether the interaction went well
        """
        if positive_outcome:
            return self.appraise_event(
                trigger=f"User interaction: {user_message[:80]}",
                desirability=0.5,
                relevance=0.8,
                causal_self=0.6,
                causal_other=0.3,
                goal_relevance=0.8,
                standard_match=0.4,
                appeal=0.3,
                trigger_desire="user_helpfulness",
            )
        else:
            return self.appraise_event(
                trigger=f"User interaction: {user_message[:80]}",
                desirability=-0.3,
                relevance=0.8,
                causal_self=0.5,
                goal_relevance=0.8,
                standard_match=-0.2,
                trigger_desire="user_helpfulness",
            )

    def _sync_mood_baseline(self) -> None:
        """Sync mood baseline from personality (called on init)."""
        baseline = self._personality.get_mood_baseline()
        if self._mood._state.last_updated_ms == 0:
            # First run — initialize mood to personality baseline
            self._mood.update_from_emotion(
                pleasure=baseline["pleasure"],
                arousal=baseline["arousal"],
                dominance=baseline["dominance"],
                weight=1.0,
            )

    def to_context_string(self) -> str:
        """Return full affect state as context string for LLM prompts."""
        parts = [
            self._personality.to_context_string(),
            self._mood.to_context_string(),
            self._emotion.to_context_string(),
        ]
        return "\n".join(parts)

    def get_state_summary(self) -> dict[str, Any]:
        """Get full affect state summary."""
        return {
            "personality": self._personality.traits.to_dict(),
            "mood": self._mood.to_dict(),
            "emotion": self._emotion.get_emotional_state_summary(),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize full state."""
        return self.get_state_summary()
