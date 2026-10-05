"""Append-only full-fidelity event journal."""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from aegis_ai.schema.models import JournalEvent

logger = logging.getLogger("aegis_ai.journal.journal_store")

_TAIL_READ_CHUNK_BYTES = 64 * 1024
_TAIL_READ_MAX_BYTES = 8 * 1024 * 1024


def _read_tail_lines(path: Path, *, max_lines: int, max_bytes: int | None = None) -> list[str]:
    max_bytes = _TAIL_READ_MAX_BYTES if max_bytes is None else max_bytes
    if max_lines <= 0 or max_bytes <= 0 or not path.exists():
        return []
    try:
        size = path.stat().st_size
    except OSError:
        return []
    if size <= 0:
        return []

    offset = size
    collected = b""
    lines: list[bytes] = []
    while offset > 0 and len(lines) <= max_lines and len(collected) < max_bytes:
        read_size = min(_TAIL_READ_CHUNK_BYTES, offset, max_bytes - len(collected))
        offset -= read_size
        with open(path, "rb") as handle:
            handle.seek(offset)
            collected = handle.read(read_size) + collected
        lines = collected.splitlines()

    if offset > 0:
        newline = collected.find(b"\n")
        if newline >= 0:
            collected = collected[newline + 1 :]
            lines = collected.splitlines()

    decoded: list[str] = []
    for raw in lines[-max_lines:]:
        line = raw.decode("utf-8", errors="replace").strip()
        if line:
            decoded.append(line)
    return decoded


class JournalStore:
    """Append-only JSONL journal with monotonic sequence numbers."""

    def __init__(self, data_dir: str = "data") -> None:
        self._dir = Path(data_dir) / "journal"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path = self._dir / "events.jsonl"
        self._offsets_path = self._dir / "offsets.json"
        self._lock = threading.RLock()
        self._sequence = self._load_last_sequence()

    def _load_last_sequence(self) -> int:
        if not self._path.exists():
            return 0
        try:
            for line in reversed(_read_tail_lines(self._path, max_lines=64)):
                try:
                    return int(json.loads(line).get("sequence", 0))
                except Exception:
                    logger.debug(
                        "Skipped a journal line that would not parse while reading the last sequence",
                        exc_info=True,
                    )
                    continue
        except Exception:
            logger.debug("Failed to read journal tail sequence", exc_info=True)
        return 0

    def append(
        self,
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        correlation_id: str = "",
        causation_id: str = "",
    ) -> JournalEvent:
        with self._lock:
            self._sequence += 1
            entry = JournalEvent(
                sequence=self._sequence,
                event_type=event_type,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                timestamp_ms=int(time.time() * 1000),
                payload=payload,
                metadata=metadata or {},
                correlation_id=correlation_id,
                causation_id=causation_id or str(uuid.uuid4().hex[:12]),
            )
            record = entry.model_dump()
            if not record.get("metadata"):
                record["metadata"] = {}
            try:
                from aegis_ai.observability.otel_tracing import current_trace_metadata, start_span

                with start_span(
                    "journal.append",
                    **{"aegis.event_type": event_type, "aegis.aggregate_id": aggregate_id},
                ):
                    for key, value in current_trace_metadata().items():
                        record["metadata"].setdefault(key, value)
                entry = JournalEvent.model_validate(record)
            except Exception:
                pass
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.model_dump(), ensure_ascii=False) + "\n")
            return entry

    def list_recent(self, *, limit: int = 100, after_sequence: int = 0) -> list[dict[str, Any]]:
        """Return the newest journal rows, newest last."""
        if not self._path.exists() or limit <= 0:
            return []
        try:
            size = self._path.stat().st_size
            max_bytes = 2 * 1024 * 1024
            with open(self._path, "rb") as f:
                offset = max(0, size - max_bytes)
                f.seek(offset)
                payload = f.read(max_bytes)
            if offset:
                newline = payload.find(b"\n")
                payload = payload[newline + 1 :] if newline >= 0 else b""
            rows: list[dict[str, Any]] = []
            for raw in payload.splitlines():
                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    logger.debug(
                        "Skipped a journal line that would not parse; it is missing from the result",
                        exc_info=True,
                    )
                    continue
                if int(row.get("sequence") or 0) <= after_sequence:
                    continue
                rows.append(row)
            return rows[-limit:]
        except Exception:
            logger.debug("Failed to read recent journal", exc_info=True)
            return []

    def list_for_aggregate(self, aggregate_id: str, *, limit: int = 500) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        rows: list[dict[str, Any]] = []
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    if str(row.get("aggregate_id") or "") == aggregate_id:
                        rows.append(row)
        except Exception:
            logger.debug("Failed to scan journal", exc_info=True)
        return rows[-limit:]

    def save_offset(self, consumer_id: str, sequence: int) -> None:
        with self._lock:
            offsets: dict[str, int] = {}
            if self._offsets_path.exists():
                try:
                    offsets = json.loads(self._offsets_path.read_text(encoding="utf-8"))
                except Exception:
                    offsets = {}
            offsets[consumer_id] = sequence
            self._offsets_path.write_text(json.dumps(offsets, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_offset(self, consumer_id: str) -> int:
        if not self._offsets_path.exists():
            return 0
        try:
            offsets = json.loads(self._offsets_path.read_text(encoding="utf-8"))
            return int(offsets.get(consumer_id, 0))
        except Exception:
            return 0
