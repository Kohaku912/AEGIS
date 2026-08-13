"""Pressure accumulation engine for AEGIS desires.

This module models desire pressure as an urgency signal that grows from
elapsed time, system events, and unprocessed state, then drops after a
successful action. Pressure is separate from the older frustration-based
model and is designed to better drive periodic autonomous execution.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger("aegis_ai.desire.pressure")

_ALPHA: float = 0.3
_MIN_PRESSURE: float = 0.0
_MAX_PRESSURE: float = 10.0
_TIME_PRESSURE_PER_HOUR: float = float(os.environ.get("AEGIS_PRESSURE_PER_HOUR", "10.0"))

_DEFAULT_PRESSURES: dict[str, float] = {
    "user_support": 0.0,
    "social": 0.0,
    "growth": 0.0,
}

_EVENT_PRESSURE_DELTAS: dict[str, float] = {
    "health_alert": 0.5,
    "system_health_alert": 0.5,
    "observation": 0.3,
    "system_observation": 0.3,
    "unprocessed_mention": 0.2,
    "mention_unprocessed": 0.2,
}


def _clamp(value: float, lo: float = _MIN_PRESSURE, hi: float = _MAX_PRESSURE) -> float:
    return max(lo, min(hi, value))


class PressureEngine:
    """Standalone pressure model with persistence and drift tracking."""

    def __init__(self, data_dir: str = "data/pressure") -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._state_path = self._data_dir / "pressure_state.json"

        self._pressures: dict[str, float] = dict(_DEFAULT_PRESSURES)
        self._drift_rates: dict[str, float] = {name: 0.0 for name in _DEFAULT_PRESSURES}
        self._last_pressure_values: dict[str, float] = dict(self._pressures)
        self._last_updated_ms: int = int(time.time() * 1000)

        self._load()

    def _ensure_desire(self, desire: str) -> None:
        if desire not in self._pressures:
            self._pressures[desire] = 0.0
            self._drift_rates[desire] = 0.0
            self._last_pressure_values[desire] = 0.0

    def _apply_delta(self, desire: str, delta: float) -> None:
        self._ensure_desire(desire)
        old = self._pressures[desire]
        new = _clamp(old + delta)
        self._pressures[desire] = new
        self._last_pressure_values[desire] = old
        self._drift_rates[desire] = self._ema_drift(desire, new - old)
        self._last_updated_ms = int(time.time() * 1000)

    def _ema_drift(self, desire: str, current_change: float) -> float:
        previous = self._drift_rates.get(desire, 0.0)
        drift = _ALPHA * current_change + (1.0 - _ALPHA) * previous
        return round(drift, 6)

    def accumulate_from_time(self, desire: str, elapsed_hours: float) -> None:
        """Accumulate pressure from elapsed time."""
        if elapsed_hours <= 0:
            return
        delta = _TIME_PRESSURE_PER_HOUR * elapsed_hours
        self._apply_delta(desire, delta)

    def accumulate_from_event(self, desire: str, event_type: str, severity: float) -> None:
        """Accumulate pressure from a system event.

        Known event types use a small base * severity. Unknown reasons treat
        ``severity`` as a direct delta so DesireSystem.accumulate_pressure()
        actually moves the needle.
        """
        if severity <= 0:
            return
        base = _EVENT_PRESSURE_DELTAS.get(event_type)
        if base is None:
            self._apply_delta(desire, min(float(severity), 3.0))
            return
        if base <= 0:
            return
        self._apply_delta(desire, base * severity)

    def accumulate_from_state(self, desire: str, unprocessed_count: int) -> None:
        """Accumulate pressure from unprocessed work."""
        if unprocessed_count <= 0:
            return
        delta = min(unprocessed_count * 0.1, 2.0)
        self._apply_delta(desire, delta)

    def reduce_after_action(self, desire: str, effectiveness: float) -> None:
        """Reduce pressure after a successful action."""
        effectiveness = _clamp(effectiveness)
        reduction = min(2.0, 2.0 * effectiveness)
        self._apply_delta(desire, -reduction)

    def get_pressure(self, desire: str) -> float:
        self._ensure_desire(desire)
        return self._pressures[desire]

    def get_all_pressures(self) -> dict[str, float]:
        return dict(self._pressures)

    def get_drift_rate(self, desire: str) -> float:
        self._ensure_desire(desire)
        return self._drift_rates[desire]

    def should_trigger(self, threshold: float = 5.0) -> bool:
        return any(pressure >= threshold for pressure in self._pressures.values())

    def get_highest_pressure(self) -> tuple[str, float]:
        if not self._pressures:
            return "", 0.0
        desire, pressure = max(self._pressures.items(), key=lambda item: item[1])
        return desire, pressure

    def get_pressure_signature(self) -> str:
        payload = {
            "pressures": {k: round(v, 6) for k, v in sorted(self._pressures.items())},
            "drift_rates": {k: round(v, 6) for k, v in sorted(self._drift_rates.items())},
            "last_updated_ms": self._last_updated_ms,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def save(self) -> None:
        payload = {
            "pressures": {k: round(v, 6) for k, v in self._pressures.items()},
            "drift_rates": {k: round(v, 6) for k, v in self._drift_rates.items()},
            "last_updated_ms": self._last_updated_ms,
        }
        with open(self._state_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        if not self._state_path.exists():
            return

        try:
            with open(self._state_path, encoding="utf-8") as fh:
                payload = json.load(fh)

            pressures = payload.get("pressures", {})
            drift_rates = payload.get("drift_rates", {})

            if isinstance(pressures, dict):
                for desire, value in pressures.items():
                    self._pressures[desire] = _clamp(float(value))
                    self._last_pressure_values[desire] = self._pressures[desire]

            if isinstance(drift_rates, dict):
                for desire, value in drift_rates.items():
                    self._drift_rates[desire] = float(value)

            if "last_updated_ms" in payload:
                self._last_updated_ms = int(payload["last_updated_ms"])

            logger.info("Loaded pressure state from %s", self._state_path)
        except Exception as exc:  # pragma: no cover - defensive load guard
            logger.warning("Failed to load pressure state: %s", exc)
