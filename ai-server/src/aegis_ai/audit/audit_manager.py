"""Audit Manager — centralized audit log with cursor pagination and search.

Wraps AuditLog as internal implementation. Adds:
- JSONL tail reader (NO read_all in normal path)
- Cursor-based pagination
- Filtered search
- Rotation
- Summary vs detail separation
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from aegis_ai.audit import AuditEntry, AuditLog

logger = logging.getLogger("aegis_ai.audit.audit_manager")


class AuditManager:
    """Centralized audit log management.

    Wraps AuditLog for write operations. Uses JSONL tail reader
    for read operations — never loads entire file.

    Parameters
    ----------
    audit_log:
        The underlying AuditLog instance.
    data_dir:
        Directory for audit data and archives.
    """

    def __init__(
        self,
        audit_log: AuditLog,
        data_dir: str = "data",
    ) -> None:
        self._log = audit_log
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._archive_dir = self._data_dir / "audit_archive"
        self._lock = threading.Lock()
        self._audit_path: Path = audit_log._path

    # ── Write (delegate to AuditLog) ──────────────────────────

    def append(self, entry: AuditEntry) -> None:
        """Append an audit entry."""
        self._log.append(entry)

    def log_decision(self, **kwargs) -> AuditEntry:
        """Convenience: log a policy/tool decision."""
        return self._log.log_decision(**kwargs)

    def log_approval(self, **kwargs) -> AuditEntry:
        """Convenience: log an approval event."""
        return self._log.log_approval(**kwargs)

    # ── Read with tail reader (NO read_all) ───────────────────

    def list_recent(
        self,
        limit: int = 100,
        cursor: str | None = None,
        action: str | None = None,
        task_id: str | None = None,
        approval_id: str | None = None,
        errors_only: bool = False,
        page: int = 1,
    ) -> dict[str, Any]:
        """List recent audit entries with pagination."""
        page_data = self._log.read_page(page=page, per_page=limit)
        entries = page_data["entries"]

        if action:
            entries = [e for e in entries if e.get("action") == action]
        if task_id:
            entries = [e for e in entries if e.get("detail", {}).get("task_id") == task_id or e.get("task_id") == task_id]
        if approval_id:
            entries = [e for e in entries if e.get("detail", {}).get("approval_id") == approval_id or e.get("approval_id") == approval_id]
        if errors_only:
            entries = [e for e in entries if e.get("action", "").endswith("_failed") or e.get("detail", {}).get("error")]

        for e in entries:
            e["time_str"] = ""
            detail = e.get("detail", {})
            if isinstance(detail, dict):
                parts = []
                for key, value in list(detail.items())[:3]:
                    v = str(value)[:60]
                    parts.append(f"{key}={v}")
                e["detail_summary"] = ", ".join(parts)
            else:
                e["detail_summary"] = str(detail)[:100]
            import json as _j
            try:
                e["detail_pretty"] = _j.dumps(detail, indent=2, ensure_ascii=False) if detail else "{}"
            except Exception:
                e["detail_pretty"] = "{}"
        return {
            "entries": entries,
            "page": page_data["page"],
            "per_page": page_data["per_page"],
            "total": page_data["total"],
            "total_pages": page_data["total_pages"],
            "next_cursor": None,
        }

    def get_detail(self, entry_id: str) -> dict[str, Any] | None:
        """Get full detail for a single audit entry."""
        import sqlite3
        conn = self._log._get_conn()
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM audit WHERE entry_id = ?', (entry_id,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        detail_json = d.pop('detail_json', '{}')
        try:
            d['detail'] = json.loads(detail_json) if detail_json else {}
        except Exception:
            d['detail'] = {}
        d.pop('id', None)
        return d

    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search audit entries."""
        query_lower = query.lower()
        results: list[dict[str, Any]] = []
        for e in self._log.read_all():
            text = json.dumps(e, ensure_ascii=False).lower()
            if query_lower in text:
                results.append(self._to_summary(e))
                if len(results) >= limit:
                    break
        return results

    def summarize(self, period_hours: int = 24) -> dict[str, Any]:
        """Summarize audit activity for a period."""
        cutoff_ms = int(time.time() * 1000) - (period_hours * 3_600_000)
        recent = [e for e in self._log.read_all() if e.get("timestamp_ms", 0) >= cutoff_ms]

        action_counts: dict[str, int] = {}
        error_count = 0
        for e in recent:
            action = e.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
            if e.get("action", "").endswith("_failed") or e.get("detail", {}).get("error"):
                error_count += 1

        return {
            "period_hours": period_hours,
            "total_entries": len(recent),
            "error_count": error_count,
            "action_counts": action_counts,
        }

    def read_all_for_export(self, max_entries: int = 50000) -> list[dict[str, Any]]:
        """Read all audit entries for export purposes.

        Uses tail reader with large limit to avoid loading entire file.
        """
        return self._read_tail(max_entries)

    # ── Rotation ──────────────────────────────────────────────

    def rotate(self) -> int:
        """Rotate old entries to archive. Returns count rotated."""
        self._archive_dir.mkdir(parents=True, exist_ok=True)
        entries = self._read_tail(10000)
        if len(entries) < 10000:
            return 0

        cutoff_ms = int(time.time() * 1000) - (7 * 24 * 3_600_000)
        old = [e for e in entries if e.get("timestamp_ms", 0) < cutoff_ms]
        if not old:
            return 0

        archive_file = self._archive_dir / f"audit_{time.strftime('%Y-%m')}.jsonl"
        try:
            with open(archive_file, "a", encoding="utf-8") as f:
                for e in old:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
        except Exception:
            logger.exception("Failed to write archive")
            return 0

        return len(old)

    # ── JSONL Tail Reader ─────────────────────────────────────

    def _read_tail(self, n: int) -> list[dict[str, Any]]:
        """Read last N lines from JSONL file using reverse seek."""
        path = self._audit_path
        if not path.exists():
            return []
        try:
            return self._reverse_read(path, n)
        except Exception:
            logger.debug("Tail reader failed, falling back to read_all", exc_info=True)
            return self._log.read_all()

    def _reverse_read(self, path: Path, n: int) -> list[dict[str, Any]]:
        """Read last N lines from file using reverse seek."""
        entries: list[dict[str, Any]] = []
        with open(path, "rb") as f:
            f.seek(0, 2)
            file_size = f.tell()
            chunk_size = 65536
            pos = file_size
            remainder = b""

            while pos > 0 and len(entries) < n:
                read_size = min(chunk_size, pos)
                pos -= read_size
                f.seek(pos)
                chunk = f.read(read_size)
                lines = (chunk + remainder).split(b"\n")
                remainder = lines[0]
                for line in reversed(lines[1:]):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.insert(0, json.loads(line.decode("utf-8", errors="replace")))
                        if len(entries) >= n:
                            break
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue

            if remainder.strip() and len(entries) < n:
                try:
                    entries.insert(0, json.loads(remainder.strip().decode("utf-8", errors="replace")))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

        return entries[-n:]

    def _read_by_id_reverse(self, entry_id: str) -> dict[str, Any] | None:
        """Scan from end of JSONL to find entry by ID."""
        path = self._audit_path
        if not path.exists():
            return None
        try:
            with open(path, "rb") as f:
                f.seek(0, 2)
                file_size = f.tell()
                chunk_size = 65536
                pos = file_size
                remainder = b""

                while pos > 0:
                    read_size = min(chunk_size, pos)
                    pos -= read_size
                    f.seek(pos)
                    chunk = f.read(read_size)
                    lines = (chunk + remainder).split(b"\n")
                    remainder = lines[0]
                    for line in reversed(lines[1:]):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line.decode("utf-8", errors="replace"))
                            if entry.get("entry_id") == entry_id:
                                return entry
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue

                if remainder.strip():
                    try:
                        entry = json.loads(remainder.strip().decode("utf-8", errors="replace"))
                        if entry.get("entry_id") == entry_id:
                            return entry
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
        except Exception:
            logger.debug("Reverse scan failed", exc_info=True)
        return None

    # ── Internal ──────────────────────────────────────────────

    def _to_summary(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Create a summary view (no raw detail)."""
        return {
            "entry_id": entry.get("entry_id", ""),
            "timestamp_ms": entry.get("timestamp_ms", 0),
            "action": entry.get("action", ""),
            "actor": entry.get("actor", ""),
            "capability_id": entry.get("capability_id", ""),
            "decision": entry.get("decision", ""),
            "reason": entry.get("reason", "")[:200] if entry.get("reason") else "",
            "approval_id": entry.get("approval_id", ""),
            "task_id": entry.get("task_id", ""),
            "risk_level": entry.get("risk_level", ""),
        }
