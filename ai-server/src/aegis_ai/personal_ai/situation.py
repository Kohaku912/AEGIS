"""Situation model built from multi-device observations."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from aegis_schema.models import Event

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


class SituationModel:
    """Tracks current user/system situation with evidence."""

    def __init__(self, data_dir: str = "data/personal_ai", event_manager: Any = None, user_state_manager: Any = None) -> None:
        self._state_file = JsonStateFile(Path(data_dir) / "situation.json", {})
        self._event_manager = event_manager
        self._user_state_manager = user_state_manager
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
        if self._user_state_manager is not None:
            try:
                user_state = self._user_state_manager.get_current_user_state()
                return self._state_from_user_state(user_state)
            except Exception:
                pass
        return dict(self._state)

    def update_from_observation(self, source: str, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = _normalize_observation_source(source)
        if self._user_state_manager is not None and normalized in {
            "android",
            "pc",
            "browser",
            "room",
            "webhook",
        }:
            self._user_state_manager.ingest_event(normalized, payload)
        if "user_state" in payload and isinstance(payload.get("user_state"), dict):
            return self.update_from_user_state(payload["user_state"])
        if any(k in payload for k in ("device_type", "activity", "foreground_app", "screen_state", "presence", "focus_mode", "mode")):
            return self.update_from_structured_observation(normalized or source, payload)
        evidence = list(self._state.get("evidence", []))[-19:]
        evidence.append({"source": normalized or source, "payload": payload, "timestamp": now_ms()})
        self._state = {
            "state": "unknown",
            "interruptibility": "unknown",
            "confidence": 0.0,
            "evidence": evidence,
            "updated_at": now_ms(),
        }
        self._save()
        return self.get_state()

    def update_from_user_state(self, user_state: dict[str, Any]) -> dict[str, Any]:
        self._state = self._state_from_user_state(user_state)
        self._save()
        return self.get_state()

    def _state_from_user_state(self, user_state: dict[str, Any]) -> dict[str, Any]:
        activity = user_state.get("activity", {}) if isinstance(user_state.get("activity"), dict) else {}
        where = user_state.get("where", {}) if isinstance(user_state.get("where"), dict) else {}
        attention = user_state.get("attention", {}) if isinstance(user_state.get("attention"), dict) else {}
        label = str(activity.get("label") or "unknown")
        confidence = float(activity.get("confidence") or attention.get("confidence") or where.get("confidence") or 0.0)
        interruptibility = "interruptible"
        if label in {"sleeping"}:
            interruptibility = "suppress"
        elif label in {"gaming", "watching_video", "focused"}:
            interruptibility = "important_only"
        elif label in {"away"} or str(where.get("label")) == "away":
            interruptibility = "batch_later"
        evidence = []
        evidence.extend(where.get("evidence") or [])
        evidence.extend(attention.get("evidence") or [])
        evidence.extend(activity.get("evidence") or [])
        return {
            "state": label,
            "interruptibility": interruptibility,
            "confidence": round(confidence, 3),
            "where": where,
            "attention": attention,
            "activity": activity,
            "evidence": evidence[-10:],
            "user_state": user_state,
            "updated_at": user_state.get("updated_at_ms") or now_ms(),
        }

    def update_from_structured_observation(self, source: str, observation: dict[str, Any]) -> dict[str, Any]:
        """Update situation from normalized observation fields."""
        activity = str(observation.get("activity") or "").lower()
        mode = str(observation.get("mode") or "").lower()
        app = str(observation.get("foreground_app") or observation.get("app") or "").lower()
        screen = str(observation.get("screen_state") or "").lower()
        presence = str(observation.get("presence") or "").lower()
        focus = bool(observation.get("focus_mode", False)) or mode == "focus"
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
        s = self.get_state()
        where = s.get("where", {}) if isinstance(s.get("where"), dict) else {}
        attention = s.get("attention", {}) if isinstance(s.get("attention"), dict) else {}
        activity = s.get("activity", {}) if isinstance(s.get("activity"), dict) else {}
        app = activity.get("app_name") or activity.get("process_name") or ""
        screen = activity.get("screen_title_summary") or activity.get("active_window_title_summary") or ""
        detail = ""
        if app or screen:
            detail = f" / app={app or 'unknown'} / screen={screen or 'unknown'}"
        return (
            f"Current situation: {s.get('state')} / interruptibility={s.get('interruptibility')} / "
            f"where={where.get('label', 'unknown')} / attention={attention.get('device', 'unknown')} / "
            f"activity={activity.get('label', s.get('state'))} / confidence={s.get('confidence')}"
            f"{detail}"
        )

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


def _normalize_observation_source(source: str) -> str:
    """Map server ids like android-server / pc-server to situation source keys."""
    raw = str(source or "").strip().lower()
    aliases = {
        "android-server": "android",
        "pc-server": "pc",
        "browser-server": "browser",
        "room-server": "room",
        "ai-server": "webhook",
    }
    if raw in aliases:
        return aliases[raw]
    if raw.endswith("-server"):
        return raw[: -len("-server")]
    return raw
