"""Memory Store — persistent store for unified memory records."""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from aegis_ai.memory.memory_types import (
    FailureType,
    MemoryRecord,
    MemorySource,
    MemoryType,
    Sensitivity,
    Visibility,
    _mask_sensitive,
    _score_for_context,
)

logger = logging.getLogger("aegis_ai.memory.memory_store")


class MemoryStore:
    """Unified memory store with JSON persistence.

    Supports 9 memory types, confidence/importance/recency scoring,
    supersession, expiration, and context summarization.
    """

    def __init__(self, data_dir: str = "data/memory_store") -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, MemoryRecord] = {}
        self._lock = threading.Lock()
        self._load()

    def add_memory(self, record: MemoryRecord) -> MemoryRecord:
        if not record.memory_id:
            record.memory_id = f"mem_{uuid.uuid4().hex[:10]}"
        if not record.created_at:
            record.created_at = int(time.time() * 1000)
        record.updated_at = record.created_at
        record.sensitivity = _mask_sensitive(record.sensitivity, "sensitivity") if record.sensitivity == "secret" else record.sensitivity
        record.content = _mask_sensitive(record.content, record.title)
        with self._lock:
            self._records[record.memory_id] = record
        self._save()
        logger.info("Memory added: %s [%s]", record.memory_id, record.memory_type)
        return record

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        return self._records.get(memory_id)

    def search_memories(
        self,
        query: str = "",
        memory_type: str | None = None,
        source: str | None = None,
        related_desire: str | None = None,
        min_confidence: float = 0.0,
        min_importance: float = 0.0,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        with self._lock:
            records = list(self._records.values())
        if memory_type:
            records = [r for r in records if r.memory_type == memory_type]
        if source:
            records = [r for r in records if r.source == source]
        if related_desire:
            records = [r for r in records if r.related_desire == related_desire]
        if min_confidence > 0:
            records = [r for r in records if r.confidence >= min_confidence]
        if min_importance > 0:
            records = [r for r in records if r.importance >= min_importance]
        if query:
            q = query.lower()
            records = [r for r in records if q in r.title.lower() or q in r.content.lower() or q in " ".join(r.tags).lower()]
        records = [r for r in records if not r.is_expired() and not r.superseded_by]
        records.sort(key=_score_for_context, reverse=True)
        return records[:limit]

    def list_recent(self, memory_type: str | None = None, limit: int = 20) -> list[MemoryRecord]:
        with self._lock:
            records = list(self._records.values())
        if memory_type:
            records = [r for r in records if r.memory_type == memory_type]
        records = [r for r in records if not r.is_expired() and not r.superseded_by]
        records.sort(key=lambda r: r.created_at, reverse=True)
        return records[:limit]

    def list_by_task(self, task_id: str) -> list[MemoryRecord]:
        return [r for r in self._records.values() if r.related_task_id == task_id and not r.superseded_by]

    def list_by_desire(self, desire_name: str) -> list[MemoryRecord]:
        return [r for r in self._records.values() if r.related_desire == desire_name and not r.superseded_by]

    def update_memory(self, memory_id: str, patch: dict[str, Any]) -> MemoryRecord | None:
        record = self._records.get(memory_id)
        if record is None:
            return None
        for k, v in patch.items():
            if hasattr(record, k):
                setattr(record, k, v)
        record.updated_at = int(time.time() * 1000)
        self._save()
        return record

    def mark_superseded(self, old_memory_id: str, new_memory_id: str) -> bool:
        old = self._records.get(old_memory_id)
        new = self._records.get(new_memory_id)
        if old is None or new is None:
            return False
        old.superseded_by = new_memory_id
        new.supersedes = old_memory_id
        self._save()
        return True

    def forget_memory(self, memory_id: str) -> bool:
        if memory_id in self._records:
            del self._records[memory_id]
            self._save()
            return True
        return False

    def prune_expired(self, now_ms: int | None = None) -> int:
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        to_remove = [mid for mid, r in self._records.items() if r.is_expired(now)]
        for mid in to_remove:
            del self._records[mid]
        if to_remove:
            self._save()
        return len(to_remove)

    def summarize_for_context(
        self,
        memory_type: str | None = None,
        max_chars: int = 2000,
        max_items: int = 10,
    ) -> str:
        with self._lock:
            records = list(self._records.values())
        records = [r for r in records if r.visibility != Visibility.HIDDEN.value and r.sensitivity != Sensitivity.SECRET.value]
        if memory_type:
            records = [r for r in records if r.memory_type == memory_type]
        records = [r for r in records if not r.is_expired() and not r.superseded_by]
        records.sort(key=_score_for_context, reverse=True)
        records = records[:max_items]
        lines: list[str] = []
        total = 0
        for r in records:
            line = r.to_context_string(200)
            if total + len(line) > max_chars:
                break
            lines.append(line)
            total += len(line)
        return "\n".join(lines) if lines else ""

    def summarize_old_episodes(self, max_age_hours: float = 168.0) -> list[MemoryRecord]:
        now_ms = int(time.time() * 1000)
        threshold = now_ms - int(max_age_hours * 3_600_000)
        old = [r for r in self._records.values() if r.memory_type == MemoryType.EPISODIC.value and r.created_at < threshold and not r.superseded_by]
        return old

    def merge_similar_lessons(self, memory_type: str) -> list[tuple[str, str]]:
        records = [r for r in self._records.values() if r.memory_type == memory_type and not r.superseded_by]
        merged: list[tuple[str, str]] = []
        seen: dict[str, str] = {}
        for r in records:
            key = r.title.lower().strip()
            if key in seen:
                self.mark_superseded(r.memory_id, seen[key])
                merged.append((r.memory_id, seen[key]))
            else:
                seen[key] = r.memory_id
        return merged

    def build_project_summary(self, max_chars: int = 1000) -> str:
        return self.summarize_for_context(memory_type=MemoryType.PROJECT_CONTEXT.value, max_chars=max_chars)

    def get_all(self) -> list[MemoryRecord]:
        return list(self._records.values())

    def count(self) -> int:
        return len(self._records)

    def _state_path(self) -> Path:
        return self._data_dir / "memory_store.json"

    def _save(self) -> None:
        data = {mid: r.to_dict() for mid, r in self._records.items()}
        try:
            with open(self._state_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Failed to save memory store: %s", exc)

    def _load(self) -> None:
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for mid, d in data.items():
                self._records[mid] = MemoryRecord(**d)
            logger.info("Loaded %d memory records", len(self._records))
        except Exception as exc:
            logger.warning("Failed to load memory store: %s", exc)
