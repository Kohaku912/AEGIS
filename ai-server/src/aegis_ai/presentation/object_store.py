"""Bounded, append-only persistence for presentation metadata.

The legacy store rewrote and loaded the complete JSONL file. Presentation
content may contain screenshots, so that design made both disk and resident
memory grow without bound. The legacy file remains readable and untouched;
new compact records are appended to a v2 journal.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from typing import Any

from aegis_ai.presentation.models import PresentationSpec, PresentationStatus

logger = logging.getLogger("aegis_ai.presentation.object_store")


class PresentationObjectStore:
    """Maintain a bounded working set backed by a compact append-only journal."""

    def __init__(self, data_dir: str = "data") -> None:
        self._dir = os.path.join(data_dir, "presentations")
        os.makedirs(self._dir, exist_ok=True)
        self._path = os.path.join(self._dir, "presentations.jsonl")
        self._journal_path = os.path.join(self._dir, "presentations-v2.jsonl")
        self._max_loaded_records = max(20, int(os.getenv("AEGIS_PRESENTATION_STORE_MAX_RECORDS", "500")))
        self._max_load_bytes = max(
            1_048_576,
            int(
                os.getenv(
                    "AEGIS_PRESENTATION_STORE_MAX_LOAD_BYTES",
                    str(64 * 1024 * 1024),
                )
            ),
        )
        self._lock = threading.Lock()
        self._store: dict[str, PresentationSpec] = {}
        self._load()

    def _load(self) -> None:
        for path in (self._path, self._journal_path):
            for line in _tail_lines(path, self._max_load_bytes):
                try:
                    data = json.loads(line)
                    if data.get("_event") == "delete":
                        self._store.pop(str(data.get("presentation_id") or ""), None)
                        continue
                    spec = PresentationSpec.from_dict(data)
                    if spec.presentation_id:
                        self._store[spec.presentation_id] = spec
                except Exception:
                    logger.debug("Skipping malformed presentation line", exc_info=True)
        self._trim_store()

    def _append(self, data: dict[str, Any]) -> None:
        try:
            with open(self._journal_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")
                fh.flush()
        except Exception:
            logger.exception("Failed to persist presentation journal")

    def _trim_store(self) -> None:
        excess = len(self._store) - self._max_loaded_records
        if excess <= 0:
            return
        oldest = sorted(
            self._store.values(),
            key=lambda spec: (
                spec.updated_at_ms or spec.created_at_ms,
                spec.presentation_id,
            ),
        )[:excess]
        for spec in oldest:
            self._store.pop(spec.presentation_id, None)

    def put(self, spec: PresentationSpec) -> None:
        """Store a compact copy while leaving the caller's full spec unchanged."""

        compact = PresentationSpec.from_dict(_compact_value(spec.to_dict()))
        with self._lock:
            self._store[spec.presentation_id] = compact
            self._trim_store()
            self._append(compact.to_dict())

    def get(self, presentation_id: str) -> PresentationSpec | None:
        with self._lock:
            return self._store.get(presentation_id)

    def list_active(self, limit: int = 100) -> list[PresentationSpec]:
        with self._lock:
            active = [
                spec
                for spec in self._store.values()
                if spec.status
                in (
                    PresentationStatus.PENDING,
                    PresentationStatus.ACTIVE,
                    PresentationStatus.DELIVERED,
                )
            ]
        active.sort(key=lambda spec: spec.created_at_ms, reverse=True)
        return active[:limit]

    def list_all(self, limit: int = 200) -> list[PresentationSpec]:
        with self._lock:
            items = list(self._store.values())
        items.sort(key=lambda spec: spec.created_at_ms, reverse=True)
        return items[:limit]

    def list_expired(self) -> list[PresentationSpec]:
        now_ms = int(time.time() * 1000)
        with self._lock:
            expired = [
                spec
                for spec in self._store.values()
                if spec.lifecycle.expires_at_ms > 0
                and spec.lifecycle.expires_at_ms < now_ms
                and spec.status
                in (
                    PresentationStatus.PENDING,
                    PresentationStatus.ACTIVE,
                    PresentationStatus.DELIVERED,
                )
            ]
        expired.sort(key=lambda spec: spec.created_at_ms, reverse=True)
        return expired

    def delete(self, presentation_id: str) -> bool:
        with self._lock:
            if presentation_id not in self._store:
                return False
            del self._store[presentation_id]
            self._append(
                {
                    "_event": "delete",
                    "presentation_id": presentation_id,
                    "timestamp_ms": int(time.time() * 1000),
                }
            )
            return True

    def count(self) -> int:
        with self._lock:
            return len(self._store)


def _tail_lines(path: str, max_bytes: int) -> list[str]:
    """Return complete UTF-8 lines from a bounded tail of ``path``."""

    try:
        size = os.path.getsize(path)
        offset = max(0, size - max_bytes)
        with open(path, "rb") as fh:
            fh.seek(offset)
            chunk = fh.read(max_bytes)
        if offset:
            newline = chunk.find(b"\n")
            chunk = chunk[newline + 1 :] if newline >= 0 else b""
        return [line.decode("utf-8", errors="replace").strip() for line in chunk.splitlines() if line.strip()]
    except FileNotFoundError:
        return []
    except OSError:
        logger.warning("Failed to read presentation journal tail: %s", path, exc_info=True)
        return []


def _compact_value(value: Any, *, depth: int = 0) -> Any:
    """Keep useful metadata while replacing binary-sized payloads."""

    if depth >= 10:
        return {"omitted": True, "reason": "max_depth"}
    if isinstance(value, str):
        encoded = value.encode("utf-8", errors="replace")
        if len(encoded) <= 16_384:
            return value
        return {
            "omitted": True,
            "type": "string",
            "length": len(encoded),
            "sha256": hashlib.sha256(encoded).hexdigest(),
        }
    if isinstance(value, bytes):
        return {
            "omitted": True,
            "type": "bytes",
            "length": len(value),
            "sha256": hashlib.sha256(value).hexdigest(),
        }
    if isinstance(value, dict):
        items = list(value.items())
        compact = {str(key): _compact_value(item, depth=depth + 1) for key, item in items[:100]}
        if len(items) > 100:
            compact["_omitted_items"] = len(items) - 100
        return compact
    if isinstance(value, (list, tuple)):
        compact_list = [_compact_value(item, depth=depth + 1) for item in value[:100]]
        if len(value) > 100:
            compact_list.append({"omitted_items": len(value) - 100})
        return compact_list
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _compact_value(str(value), depth=depth + 1)
