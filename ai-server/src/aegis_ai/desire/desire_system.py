"""Desire System — D2A-inspired intrinsic motivation for AEGIS.

Based on the D2A (Desire-driven Autonomous Agent) framework.
Implements desire dimensions with frustration tracking and persistence.

All desire values are on a 0.0–10.0 scale where higher = more satisfied.
Frustration = max(0, expected_value − value).

Usage:
    desire_system = DesireSystem(data_dir="data/desires")
    desire_system.apply_decay(now_ms)
    desire_system.update_value("curiosity", 8.0)
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
    """A single desire dimension with frustration tracking.

    All numeric values are on a 0.0–10.0 scale (higher = more satisfied).
    ``frustration`` is derived: ``max(0, expected_value − value)``.
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


# ── Default desire dimensions ────────────────────────────────────────────

DEFAULT_DESIRE_DIMENSIONS: dict[str, dict[str, Any]] = {
    "user_helpfulness": {
        "description": "The drive to effectively assist the user with their tasks.",
        "expected_value": 8.0,
        "decay_rate_per_hour": 0.15,
        "recovery_rate": 0.3,
        "safety_category": "general",
    },
    "learning_progress": {
        "description": "The need for personal growth, learning, and self-improvement.",
        "expected_value": 7.0,
        "decay_rate_per_hour": 0.1,
        "recovery_rate": 0.2,
        "safety_category": "general",
    },
    "curiosity": {
        "description": "The need for exploration, learning, and discovering new things.",
        "expected_value": 7.0,
        "decay_rate_per_hour": 0.08,
        "recovery_rate": 0.2,
        "safety_category": "general",
    },
    "system_safety": {
        "description": "The need for security, stability, and protection from harm.",
        "expected_value": 9.0,
        "decay_rate_per_hour": 0.05,
        "recovery_rate": 0.15,
        "safety_category": "security",
    },
    "reliability": {
        "description": "The need to be dependable, consistent, and error-free.",
        "expected_value": 8.0,
        "decay_rate_per_hour": 0.1,
        "recovery_rate": 0.2,
        "safety_category": "general",
    },
    "autonomy": {
        "description": "The need for independence, control, and self-determination.",
        "expected_value": 6.0,
        "decay_rate_per_hour": 0.12,
        "recovery_rate": 0.25,
        "safety_category": "general",
    },
    "social_connection": {
        "description": "The need for social interaction and connection with others.",
        "expected_value": 6.0,
        "decay_rate_per_hour": 0.15,
        "recovery_rate": 0.3,
        "safety_category": "social",
    },
    "creativity": {
        "description": "The need for self-expression, innovation, and creative output.",
        "expected_value": 6.0,
        "decay_rate_per_hour": 0.1,
        "recovery_rate": 0.2,
        "safety_category": "general",
    },
    "purpose": {
        "description": "The need for meaning, direction, and a sense of purpose.",
        "expected_value": 7.0,
        "decay_rate_per_hour": 0.08,
        "recovery_rate": 0.2,
        "safety_category": "general",
    },
    "maintenance": {
        "description": "The need for system health, resource management, and upkeep.",
        "expected_value": 7.0,
        "decay_rate_per_hour": 0.1,
        "recovery_rate": 0.2,
        "safety_category": "general",
    },
}


def _clamp(value: float, lo: float = 0.0, hi: float = 10.0) -> float:
    """Clamp *value* into [lo, hi]."""
    return max(lo, min(hi, value))


class DesireSystem:
    """D2A-inspired desire system with frustration tracking and persistence.

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
            }

        payload = {
            "desires": serialised,
            "saved_at_ms": int(time.time() * 1000),
        }
        with open(self._state_path(), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

    _OLD_KEY_MAP: dict[str, str] = {
        "social_connectivity": "social_connection",
        "personal_fulfillment": "learning_progress",
        "safety": "system_safety",
        "recognition": "reliability",
    }

    def _load(self) -> None:
        """Restore desire state from JSON, merging into initialised dims."""
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as fh:
                payload = json.load(fh)

            for name, saved in payload.get("desires", {}).items():
                dim = self._desires.get(name)
                if dim is None:
                    mapped = self._OLD_KEY_MAP.get(name)
                    if mapped:
                        dim = self._desires.get(mapped)
                    if dim is None:
                        continue
                if isinstance(saved, (int, float)):
                    dim.value = _clamp(float(saved))
                elif isinstance(saved, dict):
                    dim.value = _clamp(float(saved.get("value", dim.value)))
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

            logger.info("Loaded desire state from %s", path)
        except Exception as exc:
            logger.warning("Failed to load desire state: %s", exc)

    # ── Decay ────────────────────────────────────────────────────────────

    def apply_decay(self, now_ms: int | None = None) -> None:
        """Apply time-based decay to all visible, non-hidden desire values.

        Desires only decrease over time. They change upward ONLY via
        update_after_action() when LLM evaluates an action.

        Parameters
        ----------
        now_ms:
            Current time in epoch-milliseconds.  Defaults to wall-clock.
        """
        if now_ms is None:
            now_ms = int(time.time() * 1000)

        for dim in self._desires.values():
            if dim.hidden:
                continue
            elapsed_hours = (now_ms - dim.last_updated_at) / 3_600_000
            if elapsed_hours <= 0:
                continue
            decay = dim.decay_rate_per_hour * elapsed_hours
            dim.value = _clamp(dim.value - decay)
            dim.last_updated_at = now_ms

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
                f"- {name}: {dim.value:.1f}/10 (expected {dim.expected_value:.1f}, frustration {dim.frustration:.1f})"
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
            "You are AEGIS's desire evaluation system. Objectively analyze how this action affects desires.\n\n"
            f"Action performed: {action}\n"
            f"Result: {observation}\n"
            f"{history_context}\n\n"
            "Current desire states:\n"
            + "\n".join(desire_context) + "\n\n"
            "Evaluate objectively:\n"
            "- How much did this action fulfill each desire? (0-10 scale)\n"
            "- Consider the action's actual impact, not just intent\n"
            "- Failed actions should decrease reliability/safety desires\n"
            "- Successful actions should increase relevant desires\n"
            "- Consider past actions for cumulative effects\n\n"
            "SOCIAL DESIRE SPECIAL RULES:\n"
            "- Posting on AGORA (create_post) fulfills social_connection MORE than just reading\n"
            "- Receiving reactions/mentions after posting fulfills social_connection EVEN MORE\n"
            "- Reading posts without engaging has LOW impact on social_connection\n"
            "- Active participation (posting, replying) has HIGH impact on social_connection\n\n"
            "Respond with ONLY a JSON object:\n"
            '{"desire_updates": {"desire_name": {"new_value": 7.0, "reason": "..."}, ...}}\n\n'
            "Only include desires that actually changed."
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
                    new_val = _clamp(float(update.get("new_value", self._desires[name].value)))
                    reason = update.get("reason", "")
                    self.update_value(name, new_val, reason=reason)
                    applied[name] = {"new_value": new_val, "reason": reason}

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
                f"frustration {dim.frustration:.1f})"
            )
        return "\n".join(parts)

    def to_context_string(self) -> str:
        """Compact desire context for LLM prompts (ContextBuilder compatible).

        Includes: visible desires, top 3 unsatisfied, latest update reason.
        Excludes: hidden desires, full history.
        """
        lines = ["Desire state:"]
        for name, dim in self._desires.items():
            if dim.hidden or not dim.visible:
                continue
            lines.append(
                f"  {name}: {dim.value:.1f}/10 "
                f"(exp {dim.expected_value:.1f}, frust {dim.frustration:.1f})"
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
        """Get desire statistics."""
        visible = [d for d in self._desires.values() if not d.hidden]
        values = [d.value for d in visible]
        frustrations = [d.frustration for d in visible]
        return {
            "desires": {n: d.value for n, d in self._desires.items()},
            "frustrations": {n: d.frustration for n, d in self._desires.items()},
            "average_value": sum(values) / len(values) if values else 0,
            "average_frustration": sum(frustrations) / len(frustrations) if frustrations else 0,
            "max_frustration": max(frustrations) if frustrations else 0,
            "min_value": min(values) if values else 0,
            "max_value": max(values) if values else 0,
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
