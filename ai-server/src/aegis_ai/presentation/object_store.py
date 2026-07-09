"""Presentation Object Store — JSONL-backed persistence.

Persists to ``data/presentations/presentations.jsonl``.
Thread-safe; rewrites the full file on every mutation (same pattern as TaskManager).
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from typing import Any

from aegis_ai.presentation.models import PresentationSpec, PresentationStatus

logger = logging.getLogger("aegis_ai.presentation.object_store")


class PresentationObjectStore:
    """Append/load/store for PresentationSpec objects on disk."""

    def __init__(self, data_dir: str = "data") -> None:
        self._dir = os.path.join(data_dir, "presentations")
        os.makedirs(self._dir, exist_ok=True)
        self._path = os.path.join(self._dir, "presentations.jsonl")
        self._lock = threading.Lock()
        self._store: dict[str, PresentationSpec] = {}
        self._load()

    # ── Persistence helpers ──────────────────────────────────────

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        spec = PresentationSpec.from_dict(data)
                        self._store[spec.presentation_id] = spec
                    except Exception:
                        logger.debug("Skipping malformed presentation line", exc_info=True)
        except FileNotFoundError:
            pass

    def _save(self) -> None:
        tmp = self._path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                for spec in self._store.values():
                    fh.write(json.dumps(spec.to_dict(), ensure_ascii=False) + "\n")
            os.replace(tmp, self._path)
        except Exception:
            logger.exception("Failed to persist presentations")

    # ── Public API ───────────────────────────────────────────────

    def put(self, spec: PresentationSpec) -> None:
        with self._lock:
            self._store[spec.presentation_id] = spec
            self._save()

    def get(self, presentation_id: str) -> PresentationSpec | None:
        with self._lock:
            return self._store.get(presentation_id)

    def list_active(self, limit: int = 100) -> list[PresentationSpec]:
        with self._lock:
            active = [
                s for s in self._store.values()
                if s.status in (PresentationStatus.PENDING, PresentationStatus.ACTIVE, PresentationStatus.DELIVERED)
            ]
        active.sort(key=lambda s: s.created_at_ms, reverse=True)
        return active[:limit]

    def list_all(self, limit: int = 200) -> list[PresentationSpec]:
        with self._lock:
            items = list(self._store.values())
        items.sort(key=lambda s: s.created_at_ms, reverse=True)
        return items[:limit]

    def list_expired(self) -> list[PresentationSpec]:
        now_ms = int(time.time() * 1000)
        with self._lock:
            expired = [
                s for s in self._store.values()
                if s.lifecycle.expires_at_ms > 0
                and s.lifecycle.expires_at_ms < now_ms
                and s.status in (PresentationStatus.PENDING, PresentationStatus.ACTIVE, PresentationStatus.DELIVERED)
            ]
        expired.sort(key=lambda s: s.created_at_ms, reverse=True)
        return expired

    def delete(self, presentation_id: str) -> bool:
        with self._lock:
            if presentation_id in self._store:
                del self._store[presentation_id]
                self._save()
                return True
            return False

    def count(self) -> int:
        with self._lock:
            return len(self._store)
