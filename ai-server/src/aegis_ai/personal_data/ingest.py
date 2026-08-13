"""Normalize device / bus payloads into PDC observations and events."""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any

from aegis_ai.personal_data.models import (
    Entity,
    Location,
    Observation,
    Provenance,
    Relationship,
    TimelineEvent,
)

_PASSWORD_MARKERS = ("password", "passwd", "otp", "pin")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def now_ms() -> int:
    return int(time.time() * 1000)


def entity_id(kind: str, name: str) -> str:
    digest = hashlib.sha256(f"{kind}:{name.lower()}".encode("utf-8")).hexdigest()[:16]
    return f"ent_{kind}_{digest}"


def _is_secret_control(payload: dict[str, Any]) -> bool:
    if payload.get("is_password") or payload.get("isPassword"):
        return True
    kind = str(payload.get("control_type") or payload.get("control_kind") or "").lower()
    name = str(payload.get("control_name") or payload.get("name") or "").lower()
    return any(marker in kind or marker in name for marker in _PASSWORD_MARKERS)


def is_replacement_text(value: Any) -> bool:
    """True when a collector replaced unreadable glyphs with '?' / U+FFFD."""
    text = str(value or "")
    if len(text) < 3:
        return False
    marks = sum(1 for char in text if char in "?\ufffd")
    return marks >= 3 and marks / len(text) >= 0.4


def readable_text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if not text or is_replacement_text(text) else text


def sanitize_value_payload(payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    if _is_secret_control(out):
        out["classification_hint"] = "secret"
        out["control_kind"] = "password"
    for key in ("value", "text", "input_text", "control_name", "title", "window_title", "active_window_title"):
        if is_replacement_text(out.get(key)):
            out[key] = ""
    return out


def apply_notification_policy(payload: dict[str, Any], *, allow_raw: bool) -> dict[str, Any]:
    """Keep notification hashes always; drop raw title/text unless policy allows."""
    out = dict(payload)
    if allow_raw:
        return out
    if "title" in out:
        out.pop("title", None)
    if "text" in out:
        out.pop("text", None)
    out["metadata_only"] = True
    return out


def device_from_event_type(event_type: str, source: str = "") -> str:
    if event_type.startswith("pc.") or source.startswith("pc"):
        return "pc"
    if event_type.startswith("android.") or source.startswith("android"):
        return "android"
    if event_type.startswith("browser.") or source.startswith("browser"):
        return "browser-aegis"
    if event_type.startswith("room.") or source.startswith("room"):
        return "room"
    if event_type.startswith(("task.", "tool.", "approval.", "llm.", "chat.", "autonomous.")):
        return "aegis"
    return "aegis"


def sensor_from_event_type(event_type: str) -> str:
    if event_type.startswith("pc.input."):
        return "os"
    if "uia" in event_type or event_type.startswith("pc.window") or event_type.startswith("pc.ui"):
        return "uia"
    if event_type.startswith("android."):
        return "accessibility"
    if "camera" in event_type:
        return "camera"
    if "mic" in event_type or "audio" in event_type or "sound" in event_type:
        return "mic"
    if event_type.startswith("pc.user_activity"):
        return "os"
    return "capability"


def _keys_summary(payload: dict[str, Any]) -> str:
    keys = payload.get("keys")
    if isinstance(keys, list) and keys:
        return "+".join(str(item) for item in keys if item)
    return ""


def _click_summary(payload: dict[str, Any]) -> str:
    buttons = payload.get("mouse_buttons")
    button = ""
    if isinstance(buttons, list) and buttons:
        button = "/".join(str(item) for item in buttons if item)
    x = payload.get("click_x")
    y = payload.get("click_y")
    if x is None and y is None:
        return button
    if button:
        return f"{button} ({x},{y})"
    if x is not None and y is not None:
        return f"({x},{y})"
    return ""


def _input_summary(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    keys = _keys_summary(payload)
    click = _click_summary(payload)
    if keys:
        parts.append(keys)
    if click:
        parts.append(click)
    counts = payload.get("key_category_counts")
    if isinstance(counts, dict) and not keys:
        for key in ("printable", "editing", "navigation", "function", "modifier", "system", "mouse"):
            count = int(counts.get(key) or 0)
            if count:
                parts.append(f"{key}×{count}")
    if not parts:
        keyboard = int(payload.get("keyboard_count") or 0)
        mouse = int(payload.get("mouse_count") or 0)
        if keyboard:
            parts.append(f"keys×{keyboard}")
        if mouse:
            parts.append(f"clicks×{mouse}")
    return " ".join(parts)


def title_from_payload(event_type: str, payload: dict[str, Any]) -> str:
    if event_type.startswith("pc.input.") or event_type in {"pc.ui.invoked", "pc.ui.value_changed"}:
        app = readable_text(
            payload.get("app_name") or payload.get("process_name") or payload.get("window_title")
        )
        summary = _input_summary(payload)
        bits = [bit for bit in (app, summary or event_type.split(".")[-1]) if bit]
        value = readable_text(payload.get("value"))
        if value:
            bits.append(value[:80])
        return " · ".join(bits)[:240]
    for key in ("title", "window_title", "active_window_title", "control_name", "app_name", "package_name", "url"):
        value = readable_text(payload.get(key))
        if value:
            return value[:240]
    return event_type


def bus_to_records(
    *,
    event_type: str,
    payload: dict[str, Any],
    source: str = "",
    bus_event_id: str = "",
    timestamp_ms: int = 0,
) -> tuple[Observation, TimelineEvent, list[Entity], list[Relationship]]:
    ts = timestamp_ms or int(payload.get("timestamp_ms") or now_ms())
    device = device_from_event_type(event_type, source)
    sensor = sensor_from_event_type(event_type)
    clean = sanitize_value_payload(payload)
    provenance = Provenance(
        collector="event_bus",
        bus_event_id=bus_event_id,
        bus_event_type=event_type,
    )
    obs = Observation(
        id=new_id("obs"),
        timestamp_ms=ts,
        source_device=device,
        source_sensor=sensor,
        event_type=event_type,
        epistemics="observed",
        payload=clean,
        title=title_from_payload(event_type, clean),
        provenance=provenance,
        classification="secret" if clean.get("control_kind") == "password" else "personal",
    )
    mapped_type = _map_event_type(event_type, clean)
    event = TimelineEvent(
        id=new_id("pdc"),
        timestamp_ms=ts,
        source_device=device,
        source_sensor=sensor,
        event_type=mapped_type,
        epistemics="observed",
        payload=clean,
        title=title_from_payload(mapped_type, clean),
        observation_ids=[obs.id],
        provenance=provenance,
        classification=obs.classification,
    )
    entities, rels = entities_from_payload(device, clean, ts, event.id)
    event.entity_ids = [ent.id for ent in entities]
    obs.entity_ids = event.entity_ids
    return obs, event, entities, rels


def entities_from_payload(
    device: str,
    payload: dict[str, Any],
    timestamp_ms: int,
    event_id: str,
) -> tuple[list[Entity], list[Relationship]]:
    entities: list[Entity] = []
    rels: list[Relationship] = []
    user = Entity(id="ent_user_self", kind="user", name="user", first_seen_ms=timestamp_ms, last_seen_ms=timestamp_ms)
    entities.append(user)
    app = str(payload.get("app_name") or payload.get("process_name") or payload.get("package_name") or "")
    if app:
        ent = Entity(
            id=entity_id("app", app),
            kind="app",
            name=app,
            first_seen_ms=timestamp_ms,
            last_seen_ms=timestamp_ms,
        )
        entities.append(ent)
        rels.append(Relationship(
            id=new_id("rel"),
            from_id=user.id,
            rel_type="used",
            to_id=ent.id,
            valid_from_ms=timestamp_ms,
            event_ids=[event_id],
        ))
    url = str(payload.get("url") or payload.get("browser_url") or "")
    if url:
        ent = Entity(
            id=entity_id("url", url),
            kind="url",
            name=url[:240],
            first_seen_ms=timestamp_ms,
            last_seen_ms=timestamp_ms,
        )
        entities.append(ent)
        rels.append(Relationship(
            id=new_id("rel"),
            from_id=user.id,
            rel_type="visited",
            to_id=ent.id,
            valid_from_ms=timestamp_ms,
            event_ids=[event_id],
        ))
    room = str(payload.get("room") or "")
    if room:
        ent = Entity(
            id=entity_id("room", room),
            kind="room",
            name=room,
            attributes={"zone": payload.get("zone") or ""},
            first_seen_ms=timestamp_ms,
            last_seen_ms=timestamp_ms,
        )
        entities.append(ent)
    _ = device
    return entities, rels


def location_from_payload(payload: dict[str, Any]) -> Location:
    loc = payload.get("location") if isinstance(payload.get("location"), dict) else {}
    return Location(
        country=str(loc.get("country") or payload.get("country") or ""),
        building=str(loc.get("building") or payload.get("building") or ""),
        floor=str(loc.get("floor") or payload.get("floor") or ""),
        room=str(loc.get("room") or payload.get("room") or ""),
        zone=str(loc.get("zone") or payload.get("zone") or ""),
        position=loc.get("position") if isinstance(loc.get("position"), dict) else {},
        confidence=float(loc.get("confidence") or payload.get("location_confidence") or 0.0),
    )


def _map_event_type(event_type: str, payload: dict[str, Any]) -> str:
    if event_type == "pc.user_activity.snapshot":
        keyboard = int(payload.get("keyboard_count") or 0)
        mouse = int(payload.get("mouse_count") or 0)
        if keyboard > 0:
            return "pc.input.typed"
        if mouse > 0:
            return "pc.input.clicked"
        return "pc.window.focused"
    if event_type == "android.foreground_app.changed":
        return "android.app.foreground"
    if event_type == "android.user_activity.changed":
        if payload.get("a11y_event") == "click":
            return "android.ui.tapped"
        if payload.get("a11y_event") == "text":
            return "android.ui.text_changed"
        if payload.get("a11y_event") == "window":
            return "android.screen.transition"
        return "android.activity"
    if event_type.startswith("pc.ui."):
        return event_type
    return event_type
