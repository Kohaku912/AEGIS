"""Personal Data Core manager — facts/observations/evidence, not MemoryManager."""

from __future__ import annotations

import json
import logging
import os
import secrets
import threading
import time
from pathlib import Path
from typing import Any

from aegis_ai.personal_data.event_store import EventStore
from aegis_ai.personal_data.evidence_store import EvidenceStore
from aegis_ai.personal_data.ingest import (
    apply_notification_policy,
    bus_to_records,
    location_from_payload,
    new_id,
    now_ms,
    sanitize_value_payload,
    title_from_payload,
)
from aegis_ai.personal_data.models import (
    CollectionPolicy,
    Fact,
    Inference,
    MemoryDerivation,
    Observation,
    Provenance,
    TimelineEvent,
)
from aegis_ai.personal_data.policy import policy_from_settings
from aegis_ai.personal_data.room_media import MotionGate, encode_h265, encode_opus, pcm_rms
from aegis_ai.personal_data.search import VectorIndex, merge_search
from aegis_ai.personal_data.state_projector import project_state

logger = logging.getLogger("aegis_ai.personal_data.core")

_BUS_TYPES = {
    "pc.user_activity.snapshot",
    "pc.window.focused",
    "pc.window.opened",
    "pc.window.closed",
    "pc.ui.invoked",
    "pc.ui.value_changed",
    "pc.ui.focus_changed",
    "pc.input.typed",
    "pc.input.clicked",
    "pc.personal_data.event",
    "android.user_activity.changed",
    "android.foreground_app.changed",
    "android.notification.posted",
    "android.ui.tapped",
    "android.ui.text_changed",
    "android.ui.focus_changed",
    "android.ui.scrolled",
    "android.screen.transition",
    "browser.user_activity.changed",
    "room.presence.changed",
    "room.motion",
    "room.still",
    "task.created",
    "task.completed",
    "task.failed",
    "tool.executed",
    "approval.created",
    "llm.request.completed",
}


class PersonalDataCore:
    def __init__(
        self,
        data_dir: str | Path,
        *,
        event_manager: Any = None,
        settings_store: Any = None,
        audit_manager: Any = None,
        memory_manager: Any = None,
        server_executor: Any = None,
    ) -> None:
        self._root = Path(data_dir) / "personal_data"
        self._root.mkdir(parents=True, exist_ok=True)
        self._event_manager = event_manager
        self._settings_store = settings_store
        self._audit = audit_manager
        self._memory = memory_manager
        self._server_executor = server_executor
        self._store = EventStore(self._root / "core.db")
        self._evidence = EvidenceStore(self._root / "evidence", key=self._load_key())
        self._vectors = VectorIndex(self._root)
        self._lock = threading.RLock()
        self._last_state: dict[str, dict[str, Any]] = {}
        self._motion = MotionGate()
        self._stop = threading.Event()
        self._pc_thread: threading.Thread | None = None
        self._retention_thread: threading.Thread | None = None
        self._room_thread: threading.Thread | None = None
        self._last_pc_scene = ""
        self._last_room_still_ms = 0

    def policy(self) -> CollectionPolicy:
        settings = self._settings_store.get() if self._settings_store is not None else None
        return policy_from_settings(settings)

    def ingest_bus_event(self, event: Any) -> dict[str, Any] | None:
        policy = self.policy()
        if not policy.enabled:
            return None
        event_type = str(getattr(event, "event_type", "") or "")
        if event_type not in _BUS_TYPES and not event_type.startswith(("pc.", "android.", "room.", "task.", "tool.")):
            return None
        if event_type.startswith("pc.") and not policy.pc_uia_enabled and event_type != "pc.user_activity.snapshot":
            return None
        if event_type.startswith("android.") and not policy.android_a11y_enabled:
            return None
        payload = _event_payload(event)
        if event_type == "android.notification.posted":
            payload = apply_notification_policy(payload, allow_raw=policy.notification_raw_text)
        if not policy.value_capture_enabled:
            payload.pop("value", None)
            payload.pop("text", None)
        obs, timeline, entities, rels = bus_to_records(
            event_type=event_type,
            payload=payload,
            source=str(getattr(event, "source_server_id", "") or ""),
            bus_event_id=str(getattr(event, "event_id", "") or ""),
            timestamp_ms=int(getattr(event, "timestamp_ms", 0) or now_ms()),
        )
        loc = location_from_payload(payload)
        obs.location = loc
        timeline.location = loc
        self._attach_screenshot_evidence(
            obs,
            timeline,
            payload,
            source_device=timeline.source_device,
            enabled=policy.screenshot_on_change,
        )
        return self._commit(obs, timeline, entities, rels)

    def ingest_pc_stream(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        policy = self.policy()
        if not policy.enabled or not policy.pc_uia_enabled:
            return []
        written = []
        for item in items:
            payload = sanitize_value_payload(dict(item))
            if not policy.value_capture_enabled:
                payload.pop("value", None)
            event_type = str(payload.get("event_type") or "pc.ui.focus_changed")
            obs, timeline, entities, rels = bus_to_records(
                event_type=event_type,
                payload=payload,
                source="pc-server",
                timestamp_ms=int(payload.get("timestamp_ms") or now_ms()),
            )
            self._attach_screenshot_evidence(
                obs,
                timeline,
                payload,
                source_device="pc",
                enabled=policy.screenshot_on_change,
            )
            written.append(self._commit(obs, timeline, entities, rels))
        return written

    def ingest_android_a11y(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        policy = self.policy()
        if not policy.enabled or not policy.android_a11y_enabled:
            return None
        event_type = str(payload.get("event_type") or "android.user_activity.changed")
        class Fake:
            pass
        fake = Fake()
        fake.event_type = event_type
        fake.payload_json = json.dumps(payload, ensure_ascii=False)
        fake.source_server_id = "android-server"
        fake.event_id = str(payload.get("event_id") or "")
        fake.timestamp_ms = int(payload.get("timestamp_ms") or now_ms())
        return self.ingest_bus_event(fake)

    def ingest_room_frame(self, jpeg: bytes, *, timestamp_ms: int = 0, location: dict[str, Any] | None = None) -> dict[str, Any]:
        policy = self.policy()
        ts = timestamp_ms or now_ms()
        loc = location or {}
        if not policy.enabled or not policy.camera_enabled:
            return {"ok": False, "error": "camera collection disabled"}
        result = self._motion.push(jpeg, ts)
        if result.get("kind") == "still":
            event = TimelineEvent(
                id=new_id("pdc"),
                timestamp_ms=ts,
                source_device="room",
                source_sensor="camera",
                event_type="room.still",
                epistemics="observed",
                payload={
                    "room": loc.get("room") or "bedroom",
                    "zone": loc.get("zone") or "desk",
                    "motion": "low",
                    "video": False,
                    "still_since_ms": result.get("still_since_ms"),
                },
                title="Room still — no raw recording",
                location=location_from_payload(loc),
                retention_class="forever_metadata",
            )
            self._store.insert_event(event)
            return {"ok": True, "event": event.model_dump(), "video": False}
        if result.get("kind") == "clip_ready":
            frames = list(result.get("frames") or [])
            blob, codec = encode_h265(frames)
            meta = self._evidence.put(
                blob,
                codec=codec,
                source_device="room",
                timestamp_ms=ts,
                duration_ms=max(0, len(frames) * 200),
                retention_class="short_media",
                mime="video/hevc" if codec == "h265" else "image/jpeg",
            )
            self._store.insert_evidence_meta(meta)
            event = TimelineEvent(
                id=new_id("pdc"),
                timestamp_ms=ts,
                duration_ms=meta["duration_ms"],
                source_device="room",
                source_sensor="camera",
                event_type="room.motion",
                epistemics="observed",
                payload={"room": loc.get("room") or "", "zone": loc.get("zone") or "", "video": True, "frames": len(frames)},
                title="Room motion clip",
                evidence_ids=[meta["id"]],
                location=location_from_payload(loc),
                retention_class="short_media",
            )
            self._store.insert_event(event)
            return {"ok": True, "event": event.model_dump(), "evidence_id": meta["id"]}
        return {"ok": True, "status": result.get("kind")}

    def ingest_room_audio(self, pcm: bytes, *, timestamp_ms: int = 0, sample_rate: int = 16000) -> dict[str, Any]:
        policy = self.policy()
        if not policy.enabled or not policy.mic_enabled:
            return {"ok": False, "error": "mic collection disabled"}
        ts = timestamp_ms or now_ms()
        rms = pcm_rms(pcm)
        if rms < 500:
            return {"ok": True, "stored": False, "reason": "silence"}
        blob, codec = encode_opus(pcm, sample_rate=sample_rate)
        duration_ms = int(len(pcm) / 2 / sample_rate * 1000)
        meta = self._evidence.put(
            blob,
            codec=codec,
            source_device="room",
            timestamp_ms=ts,
            duration_ms=duration_ms,
            retention_class="short_media",
            mime="audio/opus" if codec == "opus" else "audio/pcm",
        )
        self._store.insert_evidence_meta(meta)
        event = TimelineEvent(
            id=new_id("pdc"),
            timestamp_ms=ts,
            duration_ms=duration_ms,
            source_device="room",
            source_sensor="mic",
            event_type="room.audio.segment",
            epistemics="observed",
            payload={"rms": rms, "codec": codec},
            title="Room audio segment",
            evidence_ids=[meta["id"]],
            retention_class="short_media",
        )
        inf = Inference(
            id=new_id("inf"),
            statement="speaker unknown",
            confidence=0.2,
            timestamp_ms=ts,
            based_on_event_ids=[event.id],
            method="vad",
        )
        self._store.insert_event(event)
        self._store.insert_inference(inf)
        return {"ok": True, "event_id": event.id, "evidence_id": meta["id"], "inference_id": inf.id}

    def timeline(self, **kwargs: Any) -> dict[str, Any]:
        event_type = str(kwargs.pop("event_type", "") or "")
        device = str(kwargs.get("device") or "")
        items, total = self._store.timeline(event_type=event_type, **kwargs)
        facets = self._store.event_type_counts(
            from_ms=int(kwargs.get("from_ms") or 0),
            to_ms=int(kwargs.get("to_ms") or 0),
            device=device,
        )
        return {
            "items": items,
            "total": total,
            "event_types": facets,
            "source": "personal_data",
        }

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        return self._store.get_event(event_id)

    def search(self, query: str, *, from_ms: int = 0, to_ms: int = 0, limit: int = 50) -> dict[str, Any]:
        fts = self._store.search_fts(query, from_ms=from_ms, to_ms=to_ms, limit=limit)
        vector_ids = self._vectors.query(query, limit=min(limit, 200))
        items = merge_search(fts_hits=fts, vector_ids=vector_ids, lookup=self._store.get_event, limit=limit)
        return {"items": items, "total": len(items), "query": query, "source": "personal_data"}

    def recent_facts(self, *, limit: int = 20) -> list[dict[str, Any]]:
        return self._store.list_facts(from_ms=now_ms() - 86400_000, limit=limit)

    def get_evidence_bytes(self, evidence_id: str) -> tuple[bytes, dict[str, Any]] | None:
        meta = self._store.get_evidence_meta(evidence_id)
        if meta is None:
            return None
        data = self._evidence.get(str(meta["path"]), str(meta["sha256"]))
        self._audit_action("personal_data.evidence.read", {"evidence_id": evidence_id, "codec": meta.get("codec")})
        return data, meta

    def record_fact(
        self,
        statement: str,
        *,
        event_ids: list[str],
        evidence_ids: list[str] | None = None,
        confidence: float = 0.9,
        timestamp_ms: int = 0,
    ) -> Fact:
        fact = Fact(
            id=new_id("fact"),
            statement=statement,
            confidence=confidence,
            timestamp_ms=timestamp_ms or now_ms(),
            source_event_ids=event_ids,
            source_evidence_ids=evidence_ids or [],
            epistemics="observed",
        )
        self._store.insert_fact(fact)
        return fact

    def record_inference(
        self,
        statement: str,
        *,
        event_ids: list[str] | None = None,
        fact_ids: list[str] | None = None,
        confidence: float = 0.5,
        method: str = "rule",
    ) -> Inference:
        inf = Inference(
            id=new_id("inf"),
            statement=statement,
            confidence=confidence,
            timestamp_ms=now_ms(),
            based_on_event_ids=event_ids or [],
            based_on_fact_ids=fact_ids or [],
            method=method,
        )
        self._store.insert_inference(inf)
        return inf

    def derive_memory(self, *, fact_ids: list[str], event_ids: list[str], statement: str) -> dict[str, Any]:
        memory_id = ""
        if self._memory is not None and hasattr(self._memory, "write_memory"):
            memory_id = self._memory.write_memory(
                statement,
                memory_type="episodic",
                source_event_id=event_ids[0] if event_ids else "",
                tags=["personal_data"],
            )
        elif self._memory is not None and hasattr(self._memory, "add_memory"):
            memory_id = str(self._memory.add_memory(statement) or "")
        row = MemoryDerivation(
            id=new_id("memd"),
            memory_id=str(memory_id or ""),
            fact_ids=fact_ids,
            event_ids=event_ids,
            created_at_ms=now_ms(),
        )
        self._store.insert_memory_derivation(row)
        return row.model_dump()

    def export_range(self, from_ms: int, to_ms: int) -> dict[str, Any]:
        self._audit_action("personal_data.export", {"from_ms": from_ms, "to_ms": to_ms})
        return self._store.export_range(from_ms, to_ms)

    def delete_events(self, event_ids: list[str]) -> dict[str, Any]:
        count = self._store.delete_ids(event_ids)
        self._audit_action("personal_data.delete", {"count": count, "ids": event_ids[:20]})
        return {"deleted": count}

    def apply_retention(self) -> dict[str, int]:
        policy = self.policy()
        now = now_ms()
        cleaned: dict[str, int] = {}
        event_cut = now - policy.event_retention_days * 86400 * 1000
        shot_cut = now - policy.screenshot_retention_hours * 3600 * 1000
        media_cut = now - policy.media_retention_hours * 3600 * 1000
        for retention_class, cutoff in (
            ("long_event", event_cut),
            ("ephemeral_screen", shot_cut),
            ("short_media", media_cut),
        ):
            deleted, evidence_rows = self._store.delete_before(cutoff, retention_class=retention_class)
            for row in evidence_rows:
                self._evidence.delete(str(row.get("path") or ""))
            cleaned[retention_class] = deleted + len(evidence_rows)
        return cleaned

    def start_background(self, server_executor: Any = None) -> None:
        if server_executor is not None:
            self._server_executor = server_executor
        if self._pc_thread is None or not self._pc_thread.is_alive():
            self._pc_thread = threading.Thread(target=self._pc_drain_loop, name="aegis-pdc-pc", daemon=True)
            self._pc_thread.start()
        if self._retention_thread is None or not self._retention_thread.is_alive():
            self._retention_thread = threading.Thread(target=self._retention_loop, name="aegis-pdc-retention", daemon=True)
            self._retention_thread.start()
        if self._room_thread is None or not self._room_thread.is_alive():
            self._room_thread = threading.Thread(target=self._room_loop, name="aegis-pdc-room", daemon=True)
            self._room_thread.start()

    def stop(self) -> None:
        self._stop.set()
        for thread in (self._pc_thread, self._retention_thread, self._room_thread):
            if thread is not None and thread.is_alive():
                thread.join(timeout=2)
        self._store.close()

    def _commit(self, obs: Observation, event: TimelineEvent, entities, rels) -> dict[str, Any]:
        self._store.insert_observation(obs)
        self._store.insert_event(event)
        for ent in entities:
            self._store.upsert_entity(ent)
        for rel in rels:
            self._store.insert_relationship(rel)
        prev = self._last_state.get(event.source_device)
        state = project_state(event.model_dump(), previous=prev)
        self._store.insert_state(state)
        self._last_state[event.source_device] = state.model_dump()
        self._vectors.upsert(event.id, f"{event.title} {event.event_type} {_payload_text(event.payload)}")
        if event.epistemics == "observed" and event.event_type in {
            "pc.ui.invoked",
            "pc.ui.value_changed",
            "pc.window.opened",
            "android.app.foreground",
            "android.ui.tapped",
            "android.ui.text_changed",
            "android.screen.transition",
            "room.motion",
            "tool.executed",
        }:
            self.record_fact(
                f"{event.source_device}: {event.title}",
                event_ids=[event.id],
                evidence_ids=event.evidence_ids,
                timestamp_ms=event.timestamp_ms,
                confidence=event.confidence,
            )
        return event.model_dump()

    def _attach_screenshot_evidence(
        self,
        obs: Observation,
        timeline: TimelineEvent,
        payload: dict[str, Any],
        *,
        source_device: str,
        enabled: bool,
    ) -> None:
        if not enabled:
            payload.pop("screenshot_jpeg_base64", None)
            payload.pop("image_base64", None)
            return
        screenshot_b64 = payload.pop("screenshot_jpeg_base64", None) or payload.pop("image_base64", None)
        if not screenshot_b64:
            return
        import base64

        try:
            raw = base64.b64decode(screenshot_b64)
        except Exception:
            return
        if not raw:
            return
        meta = self._evidence.put(
            raw,
            codec="jpeg",
            source_device=source_device,
            timestamp_ms=timeline.timestamp_ms,
            retention_class="ephemeral_screen",
            mime="image/jpeg",
        )
        self._store.insert_evidence_meta(meta)
        timeline.evidence_ids.append(meta["id"])
        obs.evidence_ids.append(meta["id"])
        # Keep payload free of giant base64 after evidence store.
        timeline.payload = {k: v for k, v in timeline.payload.items() if k not in {"screenshot_jpeg_base64", "image_base64"}}
        obs.payload = {k: v for k, v in obs.payload.items() if k not in {"screenshot_jpeg_base64", "image_base64"}}

    def _on_bus_event(self, event: Any) -> None:
        try:
            self.ingest_bus_event(event)
        except Exception:
            logger.debug("PDC ingest failed", exc_info=True)

    def _pc_drain_loop(self) -> None:
        while not self._stop.wait(5):
            executor = self._server_executor
            if executor is None or not self.policy().pc_uia_enabled:
                continue
            try:
                result = executor.execute_capability("pc-server.personal_data.drain", {})
            except Exception:
                continue
            if not isinstance(result, dict):
                continue
            items = result.get("events") or result.get("items") or []
            if isinstance(items, list) and items:
                try:
                    self.ingest_pc_stream(items)
                except Exception:
                    logger.debug("PC stream ingest failed", exc_info=True)

    def _room_loop(self) -> None:
        while not self._stop.wait(8):
            executor = self._server_executor
            policy = self.policy()
            if executor is None or not policy.enabled:
                continue
            if policy.mic_enabled:
                try:
                    sample = executor.execute_capability("room-server.sound.get_level", {"duration_ms": 250})
                except Exception:
                    sample = None
                if isinstance(sample, dict):
                    rms = float(sample.get("rms") or sample.get("level") or 0)
                    if rms >= 500:
                        event = TimelineEvent(
                            id=new_id("pdc"),
                            timestamp_ms=now_ms(),
                            source_device="room",
                            source_sensor="mic",
                            event_type="room.audio.segment",
                            epistemics="observed",
                            payload={"rms": rms, "raw_pcm": False, "note": "level-only; pcm not retained"},
                            title="Room sound above VAD",
                            retention_class="forever_metadata",
                        )
                        self._store.insert_event(event)
                    elif now_ms() - self._last_room_still_ms > 60_000:
                        self._last_room_still_ms = now_ms()
                        event = TimelineEvent(
                            id=new_id("pdc"),
                            timestamp_ms=now_ms(),
                            source_device="room",
                            source_sensor="mic",
                            event_type="room.still",
                            epistemics="observed",
                            payload={"rms": rms, "audio": False},
                            title="Room quiet — no audio stored",
                            retention_class="forever_metadata",
                        )
                        self._store.insert_event(event)
            if policy.camera_enabled:
                try:
                    snap = executor.execute_capability("room-server.camera.get_snapshot", {})
                except Exception:
                    snap = None
                if isinstance(snap, dict) and snap.get("image_base64"):
                    import base64
                    try:
                        jpeg = base64.b64decode(snap.get("image_base64") or "")
                    except Exception:
                        jpeg = b""
                    if jpeg:
                        loc = snap.get("location") if isinstance(snap.get("location"), dict) else {"room": "bedroom", "zone": "desk"}
                        self.ingest_room_frame(jpeg, location=loc)

    def _retention_loop(self) -> None:
        while not self._stop.wait(3600):
            try:
                self.apply_retention()
            except Exception:
                logger.debug("PDC retention failed", exc_info=True)

    def _load_key(self) -> bytes:
        env = os.getenv("AEGIS_PERSONAL_DATA_KEY_B64", "").strip()
        if env:
            import base64

            return base64.b64decode(env)
        path = self._root / "evidence.key"
        if path.exists():
            return path.read_bytes()
        key = secrets.token_bytes(32)
        path.write_bytes(key)
        logger.warning("Personal Data evidence key stored locally at %s", path)
        return key

    def _audit_action(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit is None:
            return
        try:
            from aegis_ai.audit import AuditEntry

            self._audit.append(AuditEntry(
                action=action,
                actor="personal_data_core",
                decision="ALLOW",
                detail=detail,
            ))
        except Exception:
            logger.debug("PDC audit write failed", exc_info=True)


def _event_payload(event: Any) -> dict[str, Any]:
    raw = getattr(event, "payload_json", None)
    if isinstance(raw, str) and raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {"raw": raw}
    payload = getattr(event, "payload", None)
    return dict(payload) if isinstance(payload, dict) else {}


def _payload_text(payload: dict[str, Any]) -> str:
    return " ".join(str(payload.get(k) or "") for k in ("app_name", "url", "control_name", "package_name", "window_title"))
