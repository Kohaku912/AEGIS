"""Persistent presentation preference learning."""

from __future__ import annotations

import json
import logging
import os
import threading
from typing import Any

logger = logging.getLogger("aegis_ai.presentation.preferences")


class PresentationPreferences:
    """Track simple preference scores for presentation modality and placement."""

    def __init__(self, data_dir: str = "data") -> None:
        self._dir = os.path.join(data_dir, "presentations")
        self._path = os.path.join(self._dir, "preferences.json")
        self._lock = threading.RLock()
        self._data: dict[str, Any] = {
            "modality_scores": {},
            "placement_scores": {},
            "interaction_count": 0,
        }
        self.load()

    def load(self) -> None:
        """Load preference data from disk if present."""
        with self._lock:
            if not os.path.exists(self._path):
                return
            try:
                with open(self._path, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                if isinstance(loaded, dict):
                    self._data["modality_scores"] = dict(loaded.get("modality_scores") or {})
                    self._data["placement_scores"] = dict(loaded.get("placement_scores") or {})
                    self._data["interaction_count"] = int(loaded.get("interaction_count", 0))
            except FileNotFoundError:
                return
            except Exception:
                logger.debug("Failed to load presentation preferences", exc_info=True)

    def save(self) -> None:
        """Persist preference data to disk."""
        with self._lock:
            os.makedirs(self._dir, exist_ok=True)
            tmp_path = self._path + ".tmp"
            try:
                with open(tmp_path, "w", encoding="utf-8") as fh:
                    json.dump(self._data, fh, ensure_ascii=False, indent=2)
                os.replace(tmp_path, self._path)
            except Exception:
                logger.debug("Failed to save presentation preferences", exc_info=True)

    def record_interaction(self, modality: str, placement: str, action_type: str) -> None:
        """Update scores based on a user interaction."""
        with self._lock:
            modality_scores: dict[str, float] = self._data["modality_scores"]
            placement_scores: dict[str, float] = self._data["placement_scores"]

            modality_scores.setdefault(modality, 0.0)
            placement_scores.setdefault(placement, 0.0)

            action = str(action_type or "").lower()
            delta = 0.0
            if action == "dismiss":
                delta = -0.1
            elif action in {"click", "expand"}:
                delta = 0.2

            if delta != 0.0:
                modality_scores[modality] = self._clamp(modality_scores[modality] + delta)
                placement_scores[placement] = self._clamp(placement_scores[placement] + delta)

            self._data["interaction_count"] = int(self._data["interaction_count"]) + 1
            self.save()

    def get_preferred_modality(self) -> str:
        """Return the highest-scoring modality, defaulting to text cards."""
        with self._lock:
            return self._preferred(self._data["modality_scores"], "text_card")

    def get_preferred_placement(self) -> str:
        """Return the highest-scoring placement, defaulting to main."""
        with self._lock:
            return self._preferred(self._data["placement_scores"], "main")

    def get_scores(self) -> dict[str, Any]:
        """Return a copy of the tracked preference scores."""
        with self._lock:
            return {
                "modality_scores": dict(self._data["modality_scores"]),
                "placement_scores": dict(self._data["placement_scores"]),
                "interaction_count": int(self._data["interaction_count"]),
            }

    @staticmethod
    def _clamp(value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)

    @staticmethod
    def _preferred(scores: dict[str, Any], default: str) -> str:
        best_key = default
        best_score = -1.0
        for key, raw_score in scores.items():
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                continue
            if score > best_score:
                best_key = key
                best_score = score
        return best_key
