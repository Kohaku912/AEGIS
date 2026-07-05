"""User state inference from low-volume device activity events."""

from __future__ import annotations

import base64
import gzip
import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from aegis_schema.models import Event

_JST = timezone(timedelta(hours=9))

FORBIDDEN_KEYS = {
    "text",
    "raw_text",
    "clipboard",
    "clipboard_text",
    "password",
    "otp",
    "token",
    "authorization",
    "message_body",
    "dm_body",
    "input_text",
    "key",
    "keys",
    "key_text",
    "raw_key",
    "raw_keys",
    "vk_code",
    "vk_codes",
    "layout_tree",
    "ui_tree",
    "raw_layout",
    "body",
}

_CODE_RE = re.compile(r"\b\d{6,}\b")
_SECRETISH_RE = re.compile(r"(?i)(password|passcode|otp|認証コード|verification code|token|secret)")


def now_ms() -> int:
    return int(time.time() * 1000)


def _day_from_ms(timestamp_ms: int) -> str:
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=_JST)
    return dt.strftime("%Y-%m-%d")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class TimelineStore:
    """Append-only daily JSONL storage for normalized user-state events."""

    def __init__(self, data_dir: str | Path) -> None:
        self._dir = Path(data_dir) / "timeline"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        timestamp_ms = _safe_int(event.get("timestamp_ms"), now_ms())
        event["timestamp_ms"] = timestamp_ms
        event.setdefault("day", _day_from_ms(timestamp_ms))
        path = self._path_for_day(event["day"])
        with self._lock:
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return event

    def query_recent(self, *, limit: int = 100, source: str | None = None, since_ms: int | None = None) -> list[dict[str, Any]]:
        limit = max(1, min(5000, int(limit or 100)))
        events: list[dict[str, Any]] = []
        for path in sorted(self._dir.glob("*.jsonl"), reverse=True):
            for line in reversed(path.read_text(encoding="utf-8").splitlines()):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except Exception:
                    continue
                if source and event.get("source") != source:
                    continue
                if since_ms is not None and _safe_int(event.get("timestamp_ms")) < since_ms:
                    continue
                events.append(event)
                if len(events) >= limit:
                    return sorted(events, key=lambda item: item.get("timestamp_ms", 0))
        return sorted(events, key=lambda item: item.get("timestamp_ms", 0))

    def list_days(self) -> list[dict[str, Any]]:
        days = []
        for path in sorted(self._dir.glob("*.jsonl"), reverse=True):
            count = 0
            first = 0
            last = 0
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                count += 1
                try:
                    timestamp = _safe_int(json.loads(line).get("timestamp_ms"))
                except Exception:
                    timestamp = 0
                first = timestamp if first == 0 else min(first, timestamp)
                last = max(last, timestamp)
            days.append({"day": path.stem, "count": count, "first_timestamp_ms": first, "last_timestamp_ms": last, "archived": False})
        return days

    def _path_for_day(self, day: str) -> Path:
        return self._dir / f"{day}.jsonl"


class EventIngest:
    """Normalize and redact device events before persistence."""

    def __init__(self, *, hash_key: bytes, home_wifi_bssids: set[str] | None = None) -> None:
        self._hash_key = hash_key
        self._home_wifi_bssids = {_normalize_bssid(item) for item in (home_wifi_bssids or set()) if item}

    def normalize(self, source: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload = payload if isinstance(payload, dict) else {"value": str(payload)}
        timestamp_ms = _safe_int(payload.get("timestamp_ms") or payload.get("timestamp") or payload.get("posted_ms"), now_ms())
        safe_payload = self._sanitize_dict(payload)
        safe_payload.pop("timestamp", None)
        safe_payload.pop("timestamp_ms", None)
        event_type = str(payload.get("event_type") or payload.get("type") or source)
        event = {
            "event_id": str(payload.get("event_id") or f"user_state_{secrets.token_hex(8)}"),
            "source": source,
            "event_type": event_type,
            "timestamp_ms": timestamp_ms,
            "payload": safe_payload,
        }
        return event

    def _sanitize_dict(self, value: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            lower = key.lower()
            if lower in FORBIDDEN_KEYS or _SECRETISH_RE.search(lower):
                out[f"{key}_redacted"] = True
                continue
            if lower in {"url", "browser_url"} and isinstance(raw_value, str):
                out.update(_safe_url(raw_value, self._hash_key))
                continue
            if lower in {"bssid", "wifi_bssid"} and isinstance(raw_value, str):
                normalized = _normalize_bssid(raw_value)
                out["wifi_bssid_hash"] = _hmac_value(self._hash_key, normalized)
                out["home_wifi_match"] = bool(normalized and normalized in self._home_wifi_bssids)
                continue
            if lower in {"ssid", "wifi_ssid"} and isinstance(raw_value, str):
                out["wifi_ssid_hash"] = _hmac_value(self._hash_key, raw_value)
                continue
            if lower in {"title", "window_title", "active_window_title", "notification_title"} and isinstance(raw_value, str):
                out[f"{key}_hash"] = _hmac_value(self._hash_key, raw_value)
                out[f"{key}_summary"] = _redact_text(raw_value)[:80]
                continue
            if isinstance(raw_value, dict):
                out[key] = self._sanitize_dict(raw_value)
            elif isinstance(raw_value, list):
                out[key] = [self._sanitize_value(item) for item in raw_value[:20]]
            else:
                out[key] = self._sanitize_value(raw_value)
        return out

    def _sanitize_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return self._sanitize_dict(value)
        if isinstance(value, str):
            return _redact_text(value)[:200]
        return value


class LocationEstimator:
    def estimate(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        recent = _events_since(events, 10 * 60_000)
        evidence = []
        for event in reversed(recent):
            payload = event.get("payload", {})
            if payload.get("home_wifi_match") is True:
                evidence.append(_evidence(event, "home Wi-Fi BSSID matched"))
                return _state("home", 0.9, evidence)
        pc_events = [e for e in recent if str(e.get("source", "")).startswith("pc")]
        if pc_events:
            latest = pc_events[-1]
            payload = latest.get("payload", {})
            idle = _safe_int(payload.get("idle_ms"), 999999)
            if idle < 120_000:
                evidence.append(_evidence(latest, "recent PC activity"))
                return _state("home_pc_desk", 0.65, evidence)
        android_recent = [e for e in recent if str(e.get("source", "")).startswith("android")]
        for event in reversed(android_recent):
            payload = event.get("payload", {})
            if payload.get("wifi_connected") is False or payload.get("home_wifi_match") is False:
                if payload.get("gps_available") is True or payload.get("latitude_bucket") or payload.get("location_accuracy_m"):
                    evidence.append(_evidence(event, "not on home Wi-Fi with location signal"))
                    return _state("away", 0.6, evidence)
        return _state("unknown", 0.2, evidence)


class AttentionEstimator:
    def estimate(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        recent = _events_since(events, 30_000)
        scores = {"pc": 0.0, "android": 0.0}
        evidence: dict[str, list[dict[str, Any]]] = {"pc": [], "android": []}
        for event in recent:
            payload = event.get("payload", {})
            source = str(event.get("source", ""))
            event_type = str(event.get("event_type", ""))
            age_ms = max(0, now_ms() - _safe_int(event.get("timestamp_ms"), now_ms()))
            decay = max(0.25, 1.0 - (age_ms / 30_000))
            if source.startswith("pc"):
                event_score = 0.05
                keyboard = _safe_int(payload.get("keyboard_count"))
                mouse = _safe_int(payload.get("mouse_count"))
                key_events = _safe_int(payload.get("key_event_count"))
                idle = _safe_int(payload.get("idle_ms"), 999999)
                fullscreen = payload.get("fullscreen") is True
                semantic = " ".join(
                    str(payload.get(key, ""))
                    for key in ("app_name", "process_name", "active_window_title_summary", "input_target_category", "content_kind")
                ).lower()
                if keyboard or mouse or key_events:
                    event_score += 2.0 + min(1.0, (keyboard + mouse + key_events) / 10)
                if idle < 5_000:
                    event_score += 0.75
                elif idle < 30_000:
                    event_score += 0.45
                elif idle < 60_000:
                    event_score += 0.25
                if fullscreen and _classify_activity(semantic) in {"gaming", "watching_video"}:
                    event_score += 1.0
                if payload.get("locked") is True:
                    event_score -= 1.0
                scores["pc"] = max(scores["pc"], event_score * decay)
                evidence["pc"].append(_evidence(event, "PC input/window activity"))
            if source.startswith("android"):
                event_score = 0.05
                if payload.get("locked") is True:
                    event_score -= 0.6
                touch = _safe_int(payload.get("touch_count"))
                if touch:
                    event_score += 2.1 + min(1.0, touch / 8)
                elif event_type == "android.user_activity.changed" and payload.get("screen_on") is True:
                    event_score += 1.25
                elif event_type == "android.foreground_app.changed":
                    event_score += 0.7
                elif event_type == "android.heartbeat" and payload.get("screen_on") is True:
                    event_score += 0.15
                scores["android"] = max(scores["android"], event_score * decay)
                evidence["android"].append(_evidence(event, "Android screen/app/touch activity"))
        device = max(scores, key=scores.get)
        score = scores[device]
        if score <= 0.1:
            return {"device": "none", "label": "away", "confidence": 0.4, "evidence": []}
        return {"device": device, "label": f"{device}_active", "confidence": min(0.95, max(0.2, score)), "evidence": evidence[device][-5:]}


class ActivityEstimator:
    def estimate(self, events: list[dict[str, Any]], attention: dict[str, Any]) -> dict[str, Any]:
        device = attention.get("device")
        relevant = [e for e in _events_since(events, 10 * 60_000) if str(e.get("source", "")).startswith(str(device))]
        if not relevant:
            return _state("away" if device == "none" else "unknown", 0.35, [])
        event = relevant[-1]
        payload = event.get("payload", {})
        semantic = " ".join(
            str(payload.get(key, ""))
            for key in (
                "semantic",
                "semantic_summary",
                "layout_category",
                "app_category",
                "domain",
                "process_name",
                "foreground_app",
                "package_name",
                "app_name",
                "screen_title_summary",
                "active_window_title_summary",
                "content_kind",
                "input_target_category",
            )
        ).lower()
        if payload.get("locked") is True or payload.get("screen_on") is False:
            return _state("sleeping", 0.65, [_evidence(event, "screen locked/off")])
        category = _classify_activity(semantic)
        detail = _activity_detail(payload)
        return _state(category, 0.72 if category != "unknown" else 0.45, [_evidence(event, f"classified from {device} semantic metadata")], detail)


class TemporalSmoother:
    def smooth(self, current: dict[str, Any], previous: dict[str, Any] | None, events: list[dict[str, Any]]) -> dict[str, Any]:
        if not previous:
            return current
        recent_count = len(_events_since(events, 30_000))
        for key in ("where", "activity"):
            old = previous.get(key, {}) if isinstance(previous.get(key), dict) else {}
            new = current.get(key, {})
            if old.get("label") and old.get("label") != new.get("label") and recent_count < 2 and _safe_float(new.get("confidence")) < 0.8:
                current[key] = {**new, "label": old.get("label"), "confidence": min(_safe_float(old.get("confidence"), 0.0), 0.6), "smoothed_from": new.get("label")}
        return current


class ConfidenceEngine:
    def summarize_windows(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "last_30s": self._summary(_events_since(events, 30_000)),
            "last_10m": self._summary(_events_since(events, 10 * 60_000)),
            "last_24h": self._summary(_events_since(events, 24 * 3_600_000)),
        }

    @staticmethod
    def _summary(events: list[dict[str, Any]]) -> dict[str, Any]:
        sources: dict[str, int] = {}
        for event in events:
            sources[event.get("source", "unknown")] = sources.get(event.get("source", "unknown"), 0) + 1
        return {"count": len(events), "sources": sources}


class ArchiveManager:
    def __init__(self, data_dir: str | Path) -> None:
        self._base = Path(data_dir)
        self._timeline = self._base / "timeline"
        self._archive = self._base / "archive"
        self._archive.mkdir(parents=True, exist_ok=True)
        self._index = self._archive / "index.jsonl"
        self._key_path = self._base / "archive.key"
        self._key, self.local_key_warning = self._load_key()

    def archive_due_logs(self, now: int | None = None) -> dict[str, Any]:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        current_day = _day_from_ms(now or now_ms())
        archived = []
        for path in sorted(self._timeline.glob("*.jsonl")):
            if path.stem >= current_day:
                continue
            raw = path.read_bytes()
            if not raw:
                continue
            compressed = gzip.compress(raw)
            nonce = secrets.token_bytes(12)
            encrypted = AESGCM(self._key).encrypt(nonce, compressed, path.stem.encode("utf-8"))
            out_path = self._archive / f"{path.stem}.jsonl.gz.aesgcm"
            out_path.write_bytes(nonce + encrypted)
            entry = {
                "day": path.stem,
                "archive_path": str(out_path),
                "bytes_plain": len(raw),
                "bytes_encrypted": out_path.stat().st_size,
                "archived_at_ms": now_ms(),
                "algorithm": "gzip+AESGCM",
            }
            with self._index.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
            path.unlink()
            archived.append(entry)
        return {"archived": archived, "local_key_warning": self.local_key_warning}

    def list_archives(self) -> list[dict[str, Any]]:
        if not self._index.exists():
            return []
        rows = []
        for line in self._index.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
        return rows

    def _load_key(self) -> tuple[bytes, bool]:
        raw_env = os.environ.get("AEGIS_USER_STATE_ARCHIVE_KEY_B64", "").strip()
        if raw_env:
            key = base64.b64decode(raw_env)
            if len(key) != 32:
                raise ValueError("AEGIS_USER_STATE_ARCHIVE_KEY_B64 must decode to 32 bytes")
            return key, False
        self._key_path.parent.mkdir(parents=True, exist_ok=True)
        if self._key_path.exists():
            return base64.b64decode(self._key_path.read_text(encoding="ascii").strip()), True
        key = secrets.token_bytes(32)
        self._key_path.write_text(base64.b64encode(key).decode("ascii"), encoding="ascii")
        return key, True


class UserStateManager:
    """Single runtime entry point for user state inference."""

    def __init__(self, *, data_dir: str = "data/user_state", event_manager: Any = None, settings_store: Any = None) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._hash_key = self._load_hash_key()
        self._store = TimelineStore(self._data_dir)
        self._archive = ArchiveManager(self._data_dir)
        self._ingest = EventIngest(hash_key=self._hash_key, home_wifi_bssids=self._home_wifi_bssids(settings_store))
        self._location = LocationEstimator()
        self._attention = AttentionEstimator()
        self._activity = ActivityEstimator()
        self._smoother = TemporalSmoother()
        self._confidence = ConfidenceEngine()
        self._event_manager = event_manager
        self._state: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._pc_poller_stop = threading.Event()
        self._pc_poller_thread: threading.Thread | None = None
        self._last_pc_signature: tuple[Any, ...] | None = None
        self._last_pc_saved_ms = 0
        if event_manager is not None:
            try:
                event_manager.subscribe(self.on_event)
            except Exception:
                pass

    def ingest_event(self, source: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = self._ingest.normalize(source, payload)
        with self._lock:
            saved = self._store.append(event)
            self._state = self._compute_state_locked()
        return saved

    def on_event(self, event: Event) -> None:
        event_type = str(getattr(event, "event_type", ""))
        if not self._is_user_state_event(event_type):
            return
        payload = getattr(event, "payload", {}) or {}
        if not payload and getattr(event, "payload_json", ""):
            try:
                payload = json.loads(event.payload_json)
            except Exception:
                payload = {}
        if not isinstance(payload, dict):
            payload = {"value": str(payload)}
        payload.setdefault("event_type", event_type)
        payload.setdefault("event_id", getattr(event, "event_id", ""))
        payload.setdefault("timestamp_ms", getattr(event, "timestamp_ms", 0))
        source = str(getattr(event, "source_server_id", "") or getattr(event, "source", "") or event_type.split(".", 1)[0])
        self.ingest_event(source, payload)

    def get_current_user_state(self) -> dict[str, Any]:
        with self._lock:
            if not self._state:
                self._state = self._compute_state_locked()
            return json.loads(json.dumps(self._state, ensure_ascii=False))

    def get_recent_events(self, limit: int = 20, source: str | None = None) -> list[dict[str, Any]]:
        return self._store.query_recent(limit=limit, source=source)

    def list_days(self) -> dict[str, Any]:
        return {
            "days": self._store.list_days(),
            "archives": self._archive.list_archives(),
            "local_key_warning": self._archive.local_key_warning,
        }

    def archive_due_logs(self, now: int | None = None) -> dict[str, Any]:
        return self._archive.archive_due_logs(now)

    def poll_pc_once(self, server_executor: Any, *, force: bool = True) -> dict[str, Any]:
        if server_executor is None:
            return {"ok": False, "error": "server_executor unavailable"}
        result = server_executor.execute_capability("pc-server.user_activity.snapshot", {})
        if isinstance(result, dict) and result.get("error"):
            return {"ok": False, "error": result.get("error")}
        if not force and not self._should_save_pc_snapshot(result or {}):
            return {"ok": True, "skipped": True, "reason": "unchanged"}
        event = self.ingest_event("pc-server", {"event_type": "pc.user_activity.snapshot", **(result or {})})
        return {"ok": True, "event": event}

    def start_pc_poller(self, server_executor: Any, *, status_manager: Any = None, interval_seconds: int = 2) -> None:
        if self._pc_poller_thread and self._pc_poller_thread.is_alive():
            return
        self._pc_poller_stop.clear()

        def _loop() -> None:
            while not self._pc_poller_stop.wait(max(5, interval_seconds)):
                if not self._pc_poll_allowed(status_manager):
                    continue
                try:
                    self.poll_pc_once(server_executor, force=False)
                except Exception:
                    pass

        self._pc_poller_thread = threading.Thread(target=_loop, name="aegis-user-state-pc-poller", daemon=True)
        self._pc_poller_thread.start()

    def stop(self) -> None:
        self._pc_poller_stop.set()
        if self._pc_poller_thread and self._pc_poller_thread.is_alive():
            self._pc_poller_thread.join(timeout=2)

    def to_context_string(self) -> str:
        state = self.get_current_user_state()
        where = state.get("where", {})
        attention = state.get("attention", {})
        activity = state.get("activity", {})
        app = activity.get("app_name") or attention.get("app_name") or ""
        screen = activity.get("screen_title_summary") or activity.get("active_window_title_summary") or ""
        detail = ""
        if app or screen:
            detail = f"; app={app or 'unknown'}; screen={screen or 'unknown'}"
        return (
            "User state: "
            f"where={where.get('label')}({where.get('confidence')}); "
            f"attention={attention.get('device')}/{attention.get('label')}({attention.get('confidence')}); "
            f"activity={activity.get('label')}({activity.get('confidence')})"
            f"{detail}"
        )

    def _compute_state_locked(self) -> dict[str, Any]:
        events = self._store.query_recent(limit=5000, since_ms=now_ms() - 24 * 3_600_000)
        where = self._location.estimate(events)
        attention = self._attention.estimate(events)
        activity = self._activity.estimate(events, attention)
        state = {
            "where": where,
            "attention": attention,
            "activity": activity,
            "updated_at_ms": now_ms(),
            "window_summary": self._confidence.summarize_windows(events),
            "archive": {"local_key_warning": self._archive.local_key_warning},
        }
        return self._smoother.smooth(state, self._state, events)

    def _should_save_pc_snapshot(self, snapshot: dict[str, Any]) -> bool:
        current_ms = now_ms()
        keyboard = _safe_int(snapshot.get("keyboard_count"))
        mouse = _safe_int(snapshot.get("mouse_count"))
        key_events = _safe_int(snapshot.get("key_event_count"))
        active = _safe_int(snapshot.get("idle_ms"), 999999) < 60_000 or bool(snapshot.get("fullscreen"))
        if keyboard > 0 or mouse > 0 or key_events > 0:
            self._last_pc_signature = self._pc_signature(snapshot)
            self._last_pc_saved_ms = current_ms
            return True
        signature = self._pc_signature(snapshot)
        if signature != self._last_pc_signature:
            self._last_pc_signature = signature
            self._last_pc_saved_ms = current_ms
            return True
        if active and current_ms - self._last_pc_saved_ms >= 10_000:
            self._last_pc_saved_ms = current_ms
            return True
        if current_ms - self._last_pc_saved_ms >= 60_000:
            self._last_pc_saved_ms = current_ms
            return True
        return False

    @staticmethod
    def _pc_signature(snapshot: dict[str, Any]) -> tuple[Any, ...]:
        idle_bucket = _safe_int(snapshot.get("idle_ms"), 999999) // 10_000
        return (
            snapshot.get("process_name"),
            snapshot.get("app_name"),
            snapshot.get("active_window_title_hash") or snapshot.get("active_window_title_summary") or snapshot.get("active_window_title"),
            snapshot.get("browser_domain"),
            snapshot.get("browser_url_hash"),
            bool(snapshot.get("locked")),
            bool(snapshot.get("fullscreen")),
            snapshot.get("input_target_category"),
            idle_bucket,
        )

    def _load_hash_key(self) -> bytes:
        raw_env = os.environ.get("AEGIS_USER_STATE_HASH_KEY", "").strip()
        if raw_env:
            return raw_env.encode("utf-8")
        path = self._data_dir / "hash.key"
        if path.exists():
            return base64.b64decode(path.read_text(encoding="ascii").strip())
        key = secrets.token_bytes(32)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(base64.b64encode(key).decode("ascii"), encoding="ascii")
        return key

    def _home_wifi_bssids(self, settings_store: Any) -> set[str]:
        raw = os.environ.get("AEGIS_HOME_WIFI_BSSIDS", "")
        items = {item.strip() for item in raw.split(",") if item.strip()}
        if settings_store is not None and hasattr(settings_store, "get_all"):
            try:
                settings = settings_store.get_all()
                user_state = settings.get("user_state", {}) if isinstance(settings, dict) else {}
                items.update(str(item) for item in user_state.get("home_wifi_bssids", []) if item)
            except Exception:
                pass
        return items

    @staticmethod
    def _is_user_state_event(event_type: str) -> bool:
        return event_type in {
            "android.user_activity.changed",
            "android.presence.changed",
            "android.semantic_layout.changed",
            "android.foreground_app.changed",
            "android.heartbeat",
            "android.notification.posted",
            "pc.user_activity.snapshot",
            "browser.user_activity.changed",
            "room.presence.changed",
            "webhook.presence.changed",
        }

    @staticmethod
    def _pc_poll_allowed(status_manager: Any) -> bool:
        if status_manager is None:
            return True
        try:
            snapshot = status_manager.get_snapshot()
            servers = snapshot.get("servers", snapshot) if isinstance(snapshot, dict) else {}
            pc = servers.get("pc-server") if isinstance(servers, dict) else None
            status = str((pc or {}).get("status") or (pc or {}).get("state") or "").lower()
            return status in {"online", "degraded", "healthy", "ok", ""}
        except Exception:
            return True


def _events_since(events: list[dict[str, Any]], window_ms: int) -> list[dict[str, Any]]:
    cutoff = now_ms() - window_ms
    return [event for event in events if _safe_int(event.get("timestamp_ms")) >= cutoff]


def _evidence(event: dict[str, Any], reason: str) -> dict[str, Any]:
    payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
    evidence = {
        "reason": reason,
        "source": event.get("source"),
        "event_type": event.get("event_type"),
        "timestamp_ms": event.get("timestamp_ms"),
    }
    for key in ("app_name", "process_name", "screen_title_summary", "active_window_title_summary", "content_kind", "input_target_category"):
        if payload.get(key):
            evidence[key] = payload.get(key)
    return evidence


def _state(label: str, confidence: float, evidence: list[dict[str, Any]], detail: dict[str, Any] | None = None) -> dict[str, Any]:
    state = {"label": label, "confidence": round(max(0.0, min(1.0, confidence)), 3), "evidence": evidence[-5:]}
    if detail:
        state.update({key: value for key, value in detail.items() if value not in ("", None, [], {})})
    return state


def _classify_activity(text: str) -> str:
    if any(term in text for term in ("code", "editor", "vscode", "visual studio", "terminal", "github", "jetbrains")) or re.search(r"\bide\b", text):
        return "coding"
    if any(term in text for term in ("chat", "discord", "line", "slack", "message")):
        return "chatting"
    if any(term in text for term in ("game", "steam", "minecraft", "unity", "unreal", "valorant", "apex", "elden", "genshin")):
        return "gaming"
    if any(term in text for term in ("video", "youtube", "netflix", "fullscreen", "media", "player", "twitch")):
        return "watching_video"
    if any(term in text for term in ("browser", "chrome", "edge", "firefox", "web")):
        return "browsing"
    if any(term in text for term in ("reader", "pdf", "book", "article")):
        return "reading"
    if any(term in text for term in ("home", "launcher", "settings")):
        return "browsing"
    return "unknown"


def _activity_detail(payload: dict[str, Any]) -> dict[str, Any]:
    detail: dict[str, Any] = {}
    for key in (
        "app_name",
        "process_name",
        "screen_title_summary",
        "active_window_title_summary",
        "content_kind",
        "input_target_category",
    ):
        if payload.get(key):
            detail[key] = payload.get(key)
    if isinstance(payload.get("key_category_counts"), dict):
        detail["key_category_counts"] = payload.get("key_category_counts")
    return detail


def _safe_url(value: str, key: bytes) -> dict[str, Any]:
    parsed = urlparse(value)
    domain = parsed.netloc.lower()
    return {"domain": domain, "url_hash": _hmac_value(key, value), "path_hash": _hmac_value(key, parsed.path or "/")}


def _redact_text(value: str) -> str:
    if _SECRETISH_RE.search(value):
        return "<redacted>"
    return _CODE_RE.sub("<code>", value)


def _normalize_bssid(value: str) -> str:
    return re.sub(r"[^0-9a-f]", "", value.lower())


def _hmac_value(key: bytes, value: str) -> str:
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()
