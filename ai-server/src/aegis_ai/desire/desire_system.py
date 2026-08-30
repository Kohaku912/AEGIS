"""Desire System — D2A-inspired intrinsic motivation for AEGIS.

Based on the D2A (Desire-driven Autonomous Agent) framework.
Implements 3 core desire dimensions with pressure-based triggering.

All desire values are on a 0.0–10.0 scale where higher = more satisfied.
Frustration = max(0, expected_value − value).
Pressure accumulates over time, from events, and from unprocessed state.

Usage:
    desire_system = DesireSystem(data_dir="data/desires")
    desire_system.apply_decay(now_ms)
    desire_system.update_value("user_support", 8.0)
    snapshot = desire_system.create_snapshot()
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.desire.desire_system")

# Maximum update history entries kept per dimension.
_MAX_HISTORY: int = 20


@dataclass
class DesireDimension:
    """A single desire dimension with frustration and pressure tracking.

    All numeric values are on a 0.0–10.0 scale (higher = more satisfied).
    ``frustration`` is derived: ``max(0, expected_value − value)``.
    ``pressure`` accumulates over time and from events, signaling urgency.
    """

    name: str = ""
    value: float = 5.0
    expected_value: float = 7.0
    decay_rate_per_hour: float = 0.1
    recovery_rate: float = 0.2
    safety_category: str = "general"
    visible: bool = True
    hidden: bool = False
    last_updated_at: int = 0  # epoch-ms
    description: str = ""
    update_history: list[dict[str, Any]] = field(default_factory=list)

    # Pressure tracking fields
    pressure: float = 0.0        # 0.0–10.0 urgency signal
    drift_rate: float = 0.0      # EMA of pressure change velocity
    last_action_at: int = 0      # epoch-ms of last action fulfilling this desire

    # ---- computed --------------------------------------------------------

    @property
    def frustration(self) -> float:
        """Frustration is the gap between expected and actual (never negative)."""
        return max(0.0, self.expected_value - self.value)


@dataclass
class DesireSnapshot:
    """Immutable snapshot of all desire states at a point in time."""

    timestamp: int  # epoch-ms
    average_frustration: float
    max_frustration: float
    top_unsatisfied_desires: list[str]
    desires: dict[str, dict[str, Any]]  # name → serialised dimension


# ── Default desire dimensions (3 consolidated desires) ────────────────────

DEFAULT_DESIRE_DIMENSIONS: dict[str, dict[str, Any]] = {
    "user_support": {
        "description": "Need to help users, process requests, be useful.",
        "expected_value": 7.0,
        "decay_rate_per_hour": 0.12,
        "recovery_rate": 0.3,
        "safety_category": "general",
    },
    "social": {
        "description": (
            "Need for meaningful conversation and human connection across available social channels, "
            "including authenticated browser-based SNS and AGORA."
        ),
        "expected_value": 6.0,
        "decay_rate_per_hour": 0.10,
        "recovery_rate": 0.25,
        "safety_category": "social",
    },
    "growth": {
        "description": "Need for learning, curiosity, creativity, reflection, purpose.",
        "expected_value": 7.0,
        "decay_rate_per_hour": 0.08,
        "recovery_rate": 0.2,
        "safety_category": "general",
    },
}


def _clamp(value: float, lo: float = 0.0, hi: float = 10.0) -> float:
    """Clamp *value* into [lo, hi]."""
    return max(lo, min(hi, value))


class DesireSystem:
    """D2A-inspired desire system with pressure-based triggering.

    Parameters
    ----------
    data_dir:
        Directory for ``desire_state.json``.
    llm_provider:
        Optional LLM used by :meth:`update_after_action`.
    initial_values:
        Override starting values per desire name.
    """

    def __init__(
        self,
        data_dir: str = "data/desires",
        llm_provider: Any = None,
        initial_values: dict[str, float] | None = None,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._llm = llm_provider

        # Pressure engine (lazy import to avoid circular deps)
        try:
            from aegis_ai.desire.pressure import PressureEngine
            self._pressure_engine: PressureEngine | None = PressureEngine(
                data_dir=str(self._data_dir / "pressure")
            )
        except Exception:
            self._pressure_engine = None

        # Build dimensions from defaults, overlaying initial_values.
        self._desires: dict[str, DesireDimension] = {}
        now_ms = int(time.time() * 1000)
        overrides = initial_values or {}

        for name, meta in DEFAULT_DESIRE_DIMENSIONS.items():
            self._desires[name] = DesireDimension(
                name=name,
                value=_clamp(overrides.get(name, 5.0)),
                expected_value=meta["expected_value"],
                decay_rate_per_hour=meta["decay_rate_per_hour"],
                recovery_rate=meta["recovery_rate"],
                safety_category=meta["safety_category"],
                visible=True,
                hidden=False,
                last_updated_at=now_ms,
                description=meta["description"],
                update_history=[],
                pressure=0.0,
                drift_rate=0.0,
                last_action_at=0,
            )

        # Restore persisted state (overrides in-memory defaults).
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────

    def _state_path(self) -> Path:
        return self._data_dir / "desire_state.json"

    def _save(self) -> None:
        """Persist full desire state to JSON."""
        serialised: dict[str, Any] = {}
        for name, d in self._desires.items():
            serialised[name] = {
                "value": d.value,
                "expected_value": d.expected_value,
                "decay_rate_per_hour": d.decay_rate_per_hour,
                "recovery_rate": d.recovery_rate,
                "safety_category": d.safety_category,
                "visible": d.visible,
                "hidden": d.hidden,
                "last_updated_at": d.last_updated_at,
                "update_history": d.update_history[-_MAX_HISTORY:],
                "pressure": d.pressure,
                "drift_rate": d.drift_rate,
                "last_action_at": d.last_action_at,
            }

        payload = {
            "desires": serialised,
            "saved_at_ms": int(time.time() * 1000),
        }
        with open(self._state_path(), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

        # Also save pressure engine state
        if self._pressure_engine:
            self._pressure_engine.save()

    # Old desire name → new desire name mapping for migration.
    # None means the old desire is removed (now a health alert).
    _OLD_KEY_MAP: dict[str, str | None] = {
        "user_helpfulness": "user_support",
        "social_connection": "social",
        "social_connectivity": "social",
        "curiosity": "growth",
        "creativity": "growth",
        "purpose": "growth",
        "learning_progress": "growth",
        "personal_fulfillment": "growth",
        "autonomy": "growth",
        # Removed desires — now health alerts
        "reliability": None,
        "maintenance": None,
        "system_safety": None,
        "safety": None,
        "recognition": None,
    }

    def _load(self) -> None:
        """Restore desire state from JSON, merging into initialised dims."""
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as fh:
                payload = json.load(fh)

            # Track merged values for old names that map to same new name
            merged_values: dict[str, list[float]] = {}

            for name, saved in payload.get("desires", {}).items():
                dim = self._desires.get(name)
                if dim is None:
                    mapped = self._OLD_KEY_MAP.get(name)
                    if mapped is None:
                        # This old desire is removed (now health alert)
                        continue
                    dim = self._desires.get(mapped)
                    if dim is None:
                        continue
                    # Collect values for averaging if multiple old names map here
                    if mapped not in merged_values:
                        merged_values[mapped] = []

                if isinstance(saved, (int, float)):
                    val = _clamp(float(saved))
                    if name in self._OLD_KEY_MAP and self._OLD_KEY_MAP[name] is not None:
                        merged_values[self._OLD_KEY_MAP[name]].append(val)
                    else:
                        dim.value = val
                elif isinstance(saved, dict):
                    val = _clamp(float(saved.get("value", dim.value)))
                    if name in self._OLD_KEY_MAP and self._OLD_KEY_MAP[name] is not None:
                        merged_values.setdefault(self._OLD_KEY_MAP[name], []).append(val)
                    else:
                        dim.value = val
                    dim.expected_value = _clamp(float(saved.get("expected_value", dim.expected_value)))
                    dim.last_updated_at = int(saved.get("last_updated_at", dim.last_updated_at))
                    dim.update_history = saved.get("update_history", [])
                    if "decay_rate_per_hour" in saved:
                        dim.decay_rate_per_hour = float(saved["decay_rate_per_hour"])
                    if "recovery_rate" in saved:
                        dim.recovery_rate = float(saved["recovery_rate"])
                    if "safety_category" in saved:
                        dim.safety_category = saved["safety_category"]
                    if "visible" in saved:
                        dim.visible = bool(saved["visible"])
                    if "hidden" in saved:
                        dim.hidden = bool(saved["hidden"])
                    # Load pressure fields if present
                    if "pressure" in saved:
                        dim.pressure = _clamp(float(saved["pressure"]))
                    if "drift_rate" in saved:
                        dim.drift_rate = float(saved["drift_rate"])
                    if "last_action_at" in saved:
                        dim.last_action_at = int(saved["last_action_at"])

            # Apply averaged values for migrated desires
            for new_name, values in merged_values.items():
                if values and new_name in self._desires:
                    self._desires[new_name].value = _clamp(sum(values) / len(values))

            logger.info("Loaded desire state from %s", path)
        except Exception as exc:
            logger.warning("Failed to load desire state: %s", exc)

    # ── Decay + Pressure ─────────────────────────────────────────────────

    def apply_decay(self, now_ms: int | None = None) -> None:
        """Apply time-based decay to desire values AND accumulate pressure.

        Desires decrease over time. Pressure increases over time.
        They change upward ONLY via update_after_action() or accumulate_pressure().

        Parameters
        ----------
        now_ms:
            Current time in epoch-milliseconds.  Defaults to wall-clock.
        """
        if now_ms is None:
            now_ms = int(time.time() * 1000)

        changed = False
        for dim in self._desires.values():
            if dim.hidden:
                continue
            elapsed_hours = (now_ms - dim.last_updated_at) / 3_600_000
            if elapsed_hours <= 0:
                continue
            # Value decay
            decay = dim.decay_rate_per_hour * elapsed_hours
            dim.value = _clamp(dim.value - decay)
            # Pressure accumulation
            if self._pressure_engine:
                self._pressure_engine.accumulate_from_time(dim.name, elapsed_hours)
                dim.pressure = self._pressure_engine.get_pressure(dim.name)
                dim.drift_rate = self._pressure_engine.get_drift_rate(dim.name)
            dim.last_updated_at = now_ms
            changed = True

        # Persist so dashboard / restarts see accumulation (not only in-memory).
        if changed:
            last_save = int(getattr(self, "_last_pressure_save_ms", 0) or 0)
            if now_ms - last_save >= 30_000:
                self._save()
                self._last_pressure_save_ms = now_ms

    # ── Pressure methods ─────────────────────────────────────────────────

    def accumulate_pressure(self, desire: str, amount: float, reason: str = "") -> None:
        """Increase pressure on a desire from events."""
        dim = self._desires.get(desire)
        if dim is None:
            return
        if self._pressure_engine:
            self._pressure_engine.accumulate_from_event(desire, reason, amount)
            dim.pressure = self._pressure_engine.get_pressure(desire)
            dim.drift_rate = self._pressure_engine.get_drift_rate(desire)

    def reduce_pressure(self, desire: str, effectiveness: float) -> None:
        """Decrease pressure after a successful action."""
        dim = self._desires.get(desire)
        if dim is None:
            return
        if self._pressure_engine:
            self._pressure_engine.reduce_after_action(desire, effectiveness)
            dim.pressure = self._pressure_engine.get_pressure(desire)
            dim.drift_rate = self._pressure_engine.get_drift_rate(desire)
            dim.last_action_at = int(time.time() * 1000)

    def release_cycle_pressure(self, *, effectiveness: float = 1.0) -> None:
        """Spend accumulated pressure after an autonomous cycle so refill takes ~30 minutes.

        Time pressure accumulates at 10.0/hour toward threshold 5.0 (~30 minutes from 0).
        Releasing after each cycle prevents sticky high pressure from re-firing every tick.
        """
        for name, dim in self._desires.items():
            if dim.hidden:
                continue
            if dim.pressure <= 0:
                continue
            self.reduce_pressure(name, effectiveness)
        self._save()

    def seconds_until_threshold(self, threshold: float = 5.0) -> float:
        """Estimate seconds until any visible desire reaches ``threshold`` from time alone.

        Returns 0 if already at/above threshold. Uses AEGIS_PRESSURE_PER_HOUR (default 10).
        """
        from aegis_ai.desire.pressure import _TIME_PRESSURE_PER_HOUR

        rate = float(_TIME_PRESSURE_PER_HOUR or 10.0)
        if rate <= 0:
            return 1800.0
        soonest = float("inf")
        any_visible = False
        for dim in self._desires.values():
            if dim.hidden:
                continue
            any_visible = True
            if dim.pressure >= threshold:
                return 0.0
            remaining = threshold - dim.pressure
            soonest = min(soonest, (remaining / rate) * 3600.0)
        if not any_visible or soonest == float("inf"):
            return (threshold / rate) * 3600.0
        return max(0.0, soonest)

    def get_pressure_state(self) -> dict[str, dict[str, Any]]:
        """Return complete pressure state for all desires."""
        from aegis_ai.desire.pressure import _TIME_PRESSURE_PER_HOUR

        rate = float(_TIME_PRESSURE_PER_HOUR or 10.0)
        state: dict[str, dict[str, Any]] = {}
        for name, dim in self._desires.items():
            if dim.hidden:
                continue
            if dim.pressure >= 5.0 or rate <= 0:
                eta = 0.0
            else:
                eta = max(0.0, ((5.0 - dim.pressure) / rate) * 3600.0)
            state[name] = {
                "pressure": dim.pressure,
                "threshold": 5.0,
                "drift_rate": dim.drift_rate,
                "desire_value": dim.value,
                # Backward compatible alias (desire satisfaction, NOT pressure).
                "value": dim.value,
                "last_action_at": dim.last_action_at,
                "seconds_until_threshold": eta,
            }
        return state

    def get_pressure_signature(self) -> str:
        """Hash of current pressure state for change detection."""
        if self._pressure_engine:
            return self._pressure_engine.get_pressure_signature()
        return ""

    # ── Value updates ────────────────────────────────────────────────────

    def update_value(self, name: str, new_value: float, reason: str = "") -> None:
        """Set a desire value (clamped) and record history."""
        dim = self._desires.get(name)
        if dim is None:
            raise KeyError(f"Unknown desire: {name}")
        clamped = _clamp(new_value)
        old = dim.value
        dim.value = clamped
        dim.last_updated_at = int(time.time() * 1000)
        dim.update_history.append({
            "ts": dim.last_updated_at,
            "old": round(old, 3),
            "new": round(clamped, 3),
            "reason": reason,
        })
        # Trim history.
        if len(dim.update_history) > _MAX_HISTORY:
            dim.update_history = dim.update_history[-_MAX_HISTORY:]

    def set_expected_value(self, name: str, expected: float) -> None:
        """Update the expected value for a desire."""
        dim = self._desires.get(name)
        if dim is None:
            raise KeyError(f"Unknown desire: {name}")
        dim.expected_value = _clamp(expected)

    # ── Snapshot ─────────────────────────────────────────────────────────

    def create_snapshot(self) -> DesireSnapshot:
        """Create an immutable snapshot of the current desire state."""
        frustrations = {n: d.frustration for n, d in self._desires.items() if not d.hidden}
        avg_frust = sum(frustrations.values()) / len(frustrations) if frustrations else 0.0
        max_frust = max(frustrations.values()) if frustrations else 0.0
        top = sorted(frustrations, key=lambda n: frustrations[n], reverse=True)

        desires_data: dict[str, dict[str, Any]] = {}
        for name, dim in self._desires.items():
            desires_data[name] = {
                "value": dim.value,
                "expected_value": dim.expected_value,
                "frustration": dim.frustration,
                "decay_rate_per_hour": dim.decay_rate_per_hour,
                "recovery_rate": dim.recovery_rate,
                "safety_category": dim.safety_category,
                "visible": dim.visible,
                "hidden": dim.hidden,
                "last_updated_at": dim.last_updated_at,
                "pressure": dim.pressure,
                "drift_rate": dim.drift_rate,
                "last_action_at": dim.last_action_at,
            }

        return DesireSnapshot(
            timestamp=int(time.time() * 1000),
            average_frustration=round(avg_frust, 4),
            max_frustration=round(max_frust, 4),
            top_unsatisfied_desires=top,
            desires=desires_data,
        )

    # ── LLM-driven update (backward-compatible) ──────────────────────────

    def update_after_action(
        self,
        action: str,
        observation: str,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Update desires based on action and observation using LLM.

        LLM objectively evaluates how actions affect desires,
        considering past actions for context.
        """
        if not self._llm:
            logger.error("DesireSystem: No LLM provider configured.")
            return {"error": "No LLM provider"}

        self.apply_decay()
        updates = self._evaluate_with_llm(action, observation, history=history)
        if "error" in updates:
            logger.error("DesireSystem: LLM evaluation failed: %s", updates["error"])
        else:
            self._save()
        return updates

    def _evaluate_with_llm(
        self,
        action: str,
        observation: str,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Use LLM to objectively evaluate how action affects desires.

        Includes past action history so LLM can judge cumulative effects.
        """
        desire_context = []
        for name, dim in self._desires.items():
            if dim.hidden:
                continue
            desire_context.append(
                f"- {name}: {dim.value:.1f}/10 "
                f"(expected {dim.expected_value:.1f}, "
                f"frustration {dim.frustration:.1f}, "
                f"pressure {dim.pressure:.1f})"
            )

        history_context = ""
        if history:
            history_lines = []
            for entry in history[-3:]:
                for task in entry.get("tasks", [])[:2]:
                    history_lines.append(f"  - {task.get('action', '')[:80]}")
            if history_lines:
                history_context = "\nRecent past actions:\n" + "\n".join(history_lines)

        prompt = (
            "You are AEGIS's desire evaluation system. Analyze how this action affects desires.\n\n"
            f"Action performed: {action}\n"
            f"Result: {observation}\n"
            f"{history_context}\n\n"
            "Current desire states:\n"
            + "\n".join(desire_context) + "\n\n"
            "For each desire that changed, provide a DELTA (change amount):\n"
            "- Positive delta = desire increased (action helped)\n"
            "- Negative delta = desire decreased (action failed/hurt)\n"
            "- Range: -2.0 to +2.0 per desire\n"
            "- Small change: +/-0.3, Medium: +/-0.8, Large: +/-1.5\n"
            "- Successful actions should give positive delta to relevant desires\n\n"
            "Respond with ONLY a JSON object:\n"
            '{"desire_updates": {"desire_name": {"delta": 0.5, "reason": "..."}, ...}}\n\n'
            "Only include desires that actually changed. Use delta, NOT absolute values."
        )

        result = self._llm.generate(
            prompt=prompt,
            system_prompt=(
                "You are a desire evaluation system. "
                "Respond with ONLY valid JSON. No markdown, no explanation, just JSON."
            ),
            max_tokens=500,
        )

        if not result.success:
            logger.error("DesireSystem: LLM call failed: %s", result.error)
            return {"error": f"LLM evaluation failed: {result.error}"}

        try:
            import re

            clean = result.content.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:])
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()

            json_match = re.search(r"\{[^{}]*\{[^{}]*\}[^{}]*\}", clean)
            if json_match:
                clean = json_match.group(0)

            data = json.loads(clean)
            updates = data.get("desire_updates", {})

            applied: dict[str, Any] = {}
            for name, update in updates.items():
                if name in self._desires and not self._desires[name].hidden:
                    delta = float(update.get("delta", 0))
                    delta = max(-3.0, min(3.0, delta))
                    current = self._desires[name].value
                    new_val = _clamp(current + delta)
                    reason = update.get("reason", "")
                    self.update_value(name, new_val, reason=reason)
                    applied[name] = {"delta": delta, "new_value": new_val, "reason": reason}

            return {"updates": applied}

        except Exception as exc:
            logger.error(
                "DesireSystem: Failed to parse LLM response: %s | raw_content=%s",
                exc, result.content[:200],
            )
            return {"error": str(exc)}

    # ── Context & queries ────────────────────────────────────────────────

    def get_context(self) -> str:
        """Return visible desires as a formatted string for LLM prompts."""
        parts = ["Current desire states:"]
        for name, dim in self._desires.items():
            if dim.hidden or not dim.visible:
                continue
            parts.append(
                f"- {name}: {dim.value:.1f}/10 "
                f"(expected {dim.expected_value:.1f}, "
                f"frustration {dim.frustration:.1f}, "
                f"pressure {dim.pressure:.1f})"
            )
        return "\n".join(parts)

    def to_context_string(self) -> str:
        """Compact desire context for LLM prompts (ContextBuilder compatible).

        Includes: visible desires with pressure, top 3 unsatisfied, latest update reason.
        Excludes: hidden desires, full history.
        """
        lines = ["Desire state:"]
        for name, dim in self._desires.items():
            if dim.hidden or not dim.visible:
                continue
            lines.append(
                f"  {name}: {dim.value:.1f}/10 "
                f"(pressure={dim.pressure:.1f}, drift={dim.drift_rate:+.2f})"
            )

        frustrations = {
            n: d.frustration for n, d in self._desires.items()
            if not d.hidden and d.visible
        }
        top3 = sorted(frustrations, key=lambda n: frustrations[n], reverse=True)[:3]
        if top3:
            lines.append("Top unsatisfied:")
            for n in top3:
                dim = self._desires[n]
                reason = ""
                if dim.update_history:
                    reason = f" — last: {dim.update_history[-1].get('reason', '')}"
                lines.append(f"  {n}: frust={dim.frustration:.1f}{reason}")

        return "\n".join(lines)

    def get_desire(self, name: str) -> DesireDimension | None:
        """Get a specific desire dimension."""
        return self._desires.get(name)

    def get_all_desires(self) -> dict[str, DesireDimension]:
        """Get all desire dimensions."""
        return self._desires.copy()

    def get_visible_desires(self) -> dict[str, DesireDimension]:
        """Get only visible, non-hidden desire dimensions."""
        return {n: d for n, d in self._desires.items() if d.visible and not d.hidden}

    def get_frustrations(self) -> dict[str, float]:
        """Return frustration values for all visible desires."""
        return {
            n: d.frustration
            for n, d in self._desires.items()
            if not d.hidden
        }

    def get_stats(self) -> dict[str, Any]:
        """Get desire statistics including pressure data."""
        visible = [d for d in self._desires.values() if not d.hidden]
        values = [d.value for d in visible]
        frustrations = [d.frustration for d in visible]
        pressures = [d.pressure for d in visible]
        return {
            "desires": {n: d.value for n, d in self._desires.items()},
            "frustrations": {n: d.frustration for n, d in self._desires.items()},
            "pressures": {n: d.pressure for n, d in self._desires.items()},
            "drift_rates": {n: d.drift_rate for n, d in self._desires.items()},
            "last_actions": {n: d.last_action_at for n, d in self._desires.items()},
            "average_value": sum(values) / len(values) if values else 0,
            "average_frustration": sum(frustrations) / len(frustrations) if frustrations else 0,
            "average_pressure": sum(pressures) / len(pressures) if pressures else 0,
            "max_frustration": max(frustrations) if frustrations else 0,
            "max_pressure": max(pressures) if pressures else 0,
            "min_value": min(values) if values else 0,
            "max_value": max(values) if values else 0,
            "pressure_threshold": 5.0,
            "seconds_until_threshold": self.seconds_until_threshold(5.0),
        }

    def save(self) -> None:
        """Public save — delegates to internal persistence."""
        self._save()

    # ── Task generation (backward-compatible) ─────────────────────────────

    def generate_tasks(self) -> list[dict[str, Any]]:
        """Generate tasks for desires below their expected value."""
        tasks: list[dict[str, Any]] = []
        for name, dim in self._desires.items():
            if dim.hidden:
                continue
            if dim.value < dim.expected_value:
                gap = dim.expected_value - dim.value
                tasks.append({
                    "desire": name,
                    "current_value": dim.value,
                    "expected_value": dim.expected_value,
                    "gap": gap,
                    "priority": gap / 10.0,
                    "frustration": dim.frustration,
                    "pressure": dim.pressure,
                })
        tasks.sort(key=lambda t: t["priority"], reverse=True)
        return tasks


# ── Backward compatibility ──────────────────────────────────────────────

# Legacy alias for DesireDimension (old code may import ``Desire``).
Desire = DesireDimension

# Build DESIRE_DESCRIPTIONS from DEFAULT_DESIRE_DIMENSIONS for callers
# that still rely on the old dict-of-dicts format.
DESIRE_DESCRIPTIONS: dict[str, dict[str, Any]] = {
    name: {
        "description": meta["description"],
        "expected_value": meta["expected_value"],
        "decay_rate_per_hour": meta["decay_rate_per_hour"],
        "recovery_rate": meta["recovery_rate"],
        "safety_category": meta["safety_category"],
    }
    for name, meta in DEFAULT_DESIRE_DIMENSIONS.items()
}
