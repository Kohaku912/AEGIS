"""SessionStore — Phase 8 (Agent Server 分離).

会話再開用 JSONL ストア。Agent task 1 件ごとに 1 ファイルで events を
追記していく。MCP tools/call 側で `tools/call(session_id=...)` 形式で
再開できるよう、`session_id = task_id` をキーに events を append-only
で永続化する。

設計 (instruction.md §36 Phase 8 + §11):
- ファイル形式: 1 line = 1 event dict (JSONL)
- ファイル名: `<root>/<task_id>.jsonl` (task_id は UUID hex を想定)
- ロック: スレッドローカル RLock + ファイル append (`'a'` open) を使用
- 古い event の compaction はしない (AEGIS 側 memory system に任せる)
- 容量管理: 呼び出し側で `gc_older_than(days=N)` を提供

このモジュールは OpenHands SDK に依存しない (Phase 2 DoD と同方針)。
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

logger = logging.getLogger("aegis_ai.agents.runtime.session_store")


@dataclass
class SessionSummary:
    """Stored session の metadata (load せずに一覧できる)."""

    session_id: str
    path: str
    event_count: int
    first_event_ms: int
    last_event_ms: int
    size_bytes: int
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionStore:
    """Task 単位の JSONL event store.

    Args:
        root: 保存先ディレクトリ。存在しなければ作成する。
        retention_days: 0 以下なら無期限。>0 なら `gc_older_than()` で使用。
    """

    def __init__(self, root: str | os.PathLike[str], *, retention_days: int = 0) -> None:
        self._root = Path(root)
        self._retention_days = int(retention_days)
        self._lock = threading.RLock()
        self._open_handles: dict[str, Any] = {}
        self._root.mkdir(parents=True, exist_ok=True)

    # ---- I/O ----------------------------------------------------------

    def _path_for(self, session_id: str) -> Path:
        if not session_id or "/" in session_id or "\\" in session_id or ".." in session_id:
            raise ValueError(f"invalid session_id: {session_id!r}")
        return self._root / f"{session_id}.jsonl"

    def append(self, session_id: str, event: dict[str, Any]) -> None:
        """1 event を JSONL ファイルに追記する."""
        if "ts_ms" not in event:
            event = dict(event)
            event["ts_ms"] = int(time.time() * 1000)
        line = json.dumps(event, ensure_ascii=False, default=str)
        path = self._path_for(session_id)
        with self._lock:
            handle = self._open_handles.get(session_id)
            if handle is None:
                handle = path.open("a", encoding="utf-8")
                self._open_handles[session_id] = handle
            handle.write(line + "\n")
            handle.flush()

    def extend(self, session_id: str, events: Iterable[dict[str, Any]]) -> int:
        """複数 events を一括追記。書き込んだ件数を返す."""
        n = 0
        for ev in events:
            self.append(session_id, ev)
            n += 1
        return n

    def load(self, session_id: str) -> list[dict[str, Any]]:
        """全 events を読み込んで list で返す (新しい順ではなく保存順)."""
        path = self._path_for(session_id)
        if not path.exists():
            return []
        out: list[dict[str, Any]] = []
        with self._lock:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        logger.warning("session %s: invalid json line: %s", session_id, exc)
        return out

    def iter_events(self, session_id: str) -> Iterator[dict[str, Any]]:
        """遅延イテレータ版。"""
        for ev in self.load(session_id):
            yield ev

    def close(self, session_id: str | None = None) -> None:
        """指定 session (or all) の open handle を flush & close."""
        with self._lock:
            if session_id is None:
                sessions = list(self._open_handles.keys())
            else:
                sessions = [session_id] if session_id in self._open_handles else []
            for sid in sessions:
                handle = self._open_handles.pop(sid, None)
                if handle is not None:
                    try:
                        handle.flush()
                        handle.close()
                    except Exception:  # noqa: BLE001
                        logger.debug("close handle for %s failed", sid, exc_info=True)

    # ---- listing / GC -------------------------------------------------

    def list_sessions(self) -> list[SessionSummary]:
        """保存済み session の metadata 一覧."""
        summaries: list[SessionSummary] = []
        for path in self._root.glob("*.jsonl"):
            try:
                summaries.append(self._summary_for(path))
            except Exception:  # noqa: BLE001
                logger.debug("list_sessions: %s summary failed", path, exc_info=True)
        summaries.sort(key=lambda s: s.last_event_ms, reverse=True)
        return summaries

    def _summary_for(self, path: Path) -> SessionSummary:
        size = path.stat().st_size
        first_ms = 0
        last_ms = 0
        event_count = 0
        metadata: dict[str, Any] = {}
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    # The summary is derived from whatever parsed, so one corrupt line
                    # silently under-reports both the event count and the time span.
                    logger.debug("Skipped a session event that would not parse", exc_info=True)
                    continue
                event_count += 1
                ts = int(ev.get("ts_ms", 0) or 0)
                if first_ms == 0 or (ts and ts < first_ms):
                    first_ms = ts
                if ts and ts > last_ms:
                    last_ms = ts
                if ev.get("kind") == "metadata":
                    metadata = dict(ev.get("data", {}))
        return SessionSummary(
            session_id=path.stem,
            path=str(path),
            event_count=event_count,
            first_event_ms=first_ms,
            last_event_ms=last_ms,
            size_bytes=size,
            metadata=metadata,
        )

    def delete(self, session_id: str) -> bool:
        """指定 session を削除。存在しなければ False."""
        path = self._path_for(session_id)
        self.close(session_id)
        with self._lock:
            if not path.exists():
                return False
            path.unlink()
            return True

    def gc_older_than(self, *, days: int | None = None) -> int:
        """指定日数より古い session を削除。削除件数を返す。"""
        threshold_days = days if days is not None else self._retention_days
        if threshold_days <= 0:
            return 0
        cutoff_ms = int(time.time() * 1000) - threshold_days * 86_400_000
        deleted = 0
        for summary in self.list_sessions():
            if summary.last_event_ms and summary.last_event_ms < cutoff_ms:
                if self.delete(summary.session_id):
                    deleted += 1
        return deleted


__all__ = ["SessionStore", "SessionSummary"]
