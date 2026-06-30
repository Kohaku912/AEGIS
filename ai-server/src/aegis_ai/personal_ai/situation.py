"""Situation model built from multi-device observations."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from aegis_schema.models import Event

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


class SituationModel:
    """Tracks current user/system situation with evidence."""

    def __init__(self, data_dir: str = "data/personal_ai", event_manager: Any = None) -> None:
        self._state_file = JsonStateFile(Path(data_dir) / "situation.json", {})
        self._event_manager = event_manager
        self._state = {
            "state": "unknown",
            "interruptibility": "unknown",
            "confidence": 0.0,
            "evidence": [],
            "updated_at": 0,
        }
        self._load()
        if self._event_manager is not None:
            try:
                self._event_manager.subscribe(self.on_event)
            except Exception:
                pass

    def get_state(self) -> dict[str, Any]:
        return dict(self._state)

    def update_from_observation(self, source: str, payload: dict[str, Any]) -> dict[str, Any]:
        if any(k in payload for k in ("device_type", "activity", "foreground_app", "screen_state", "presence", "focus_mode")):
            return self.update_from_structured_observation(source, payload)
        state = "working"
        interruptibility = "interruptible"
        confidence = 0.45
        text = " ".join(str(v).lower() for v in payload.values())
        if any(term in text for term in ("game", "steam", "fullscreen")):
            state, interruptibility, confidence = "game", "important_only", 0.65
        if any(term in text for term in ("sleep", "doze", "screen_off", "locked")):
            state, interruptibility, confidence = "sleeping", "suppress", 0.7
        if any(term in text for term in ("error", "exception", "failed", "degraded")):
            state, interruptibility, confidence = "error_handling", "interruptible", 0.6
        if any(term in text for term in ("focus", "presentation", "meeting")):
            state, interruptibility, confidence = "focused", "important_only", 0.7
        evidence = list(self._state.get("evidence", []))[-19:]
        evidence.append({"source": source, "payload": payload, "timestamp": now_ms()})
        self._state = {
            "state": state,
            "interruptibility": interruptibility,
            "confidence": confidence,
            "evidence": evidence,
            "updated_at": now_ms(),
        }
        self._save()
        return self.get_state()

    def update_from_structured_observation(self, source: str, observation: dict[str, Any]) -> dict[str, Any]:
        """Update situation from normalized observation fields."""
        activity = str(observation.get("activity") or "").lower()
        app = str(observation.get("foreground_app") or observation.get("app") or "").lower()
        screen = str(observation.get("screen_state") or "").lower()
        presence = str(observation.get("presence") or "").lower()
        focus = bool(observation.get("focus_mode", False))
        error_state = bool(observation.get("error") or observation.get("degraded"))

        state = "working"
        interruptibility = "interruptible"
        confidence = 0.55
        if error_state or activity == "error_handling":
            state, interruptibility, confidence = "error_handling", "interruptible", 0.75
        elif activity in {"sleeping", "sleep"} or screen in {"off", "locked", "screen_off"}:
            state, interruptibility, confidence = "sleeping", "suppress", 0.8
        elif activity in {"away", "out"} or presence in {"away", "out"}:
            state, interruptibility, confidence = "away", "batch_later", 0.75
        elif focus or activity in {"focused", "meeting", "presentation"}:
            state, interruptibility, confidence = "focused", "important_only", 0.8
        elif activity == "gaming" or any(term in app for term in ("steam", "game", "discord")):
            state, interruptibility, confidence = "game", "important_only", 0.7
        elif activity:
            state, confidence = activity, 0.65

        evidence = list(self._state.get("evidence", []))[-19:]
        evidence.append({"source": source, "observation": observation, "timestamp": now_ms()})
        self._state = {
            "state": state,
            "interruptibility": interruptibility,
            "confidence": confidence,
            "evidence": evidence,
            "structured_observation": observation,
            "updated_at": now_ms(),
        }
        self._save()
        return self.get_state()

    def on_event(self, event: Event) -> None:
        event_type = getattr(event, "event_type", "")
        if not self._is_observation_event(event_type):
            return
        payload = getattr(event, "payload", {}) or {}
        if not payload and getattr(event, "payload_json", ""):
            try:
                payload = json.loads(event.payload_json)
            except Exception:
                payload = {}
        if not isinstance(payload, dict):
            payload = {"value": str(payload)}
        self.update_from_observation(getattr(event, "source", event_type), {"event_type": event_type, **payload})

    def to_context_string(self) -> str:
        s = self._state
        return f"Current situation: {s.get('state')} / interruptibility={s.get('interruptibility')} / confidence={s.get('confidence')}"

    @staticmethod
    def _is_observation_event(event_type: str) -> bool:
        prefixes = ("android.", "pc.", "browser.", "room.", "webhook.", "status.")
        return event_type.startswith(prefixes)

    def _load(self) -> None:
        data = self._state_file.load()
        if data:
            self._state.update(data)

    def _save(self) -> None:
        self._state_file.save(self._state)
