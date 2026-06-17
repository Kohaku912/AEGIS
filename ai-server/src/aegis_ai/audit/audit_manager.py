"""Audit Manager — centralized audit log with cursor pagination and search.

Wraps AuditLog as internal implementation. Adds:
- Cursor-based pagination (no read_all)
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

    Wraps AuditLog for write operations. Adds cursor-based
    pagination and filtered search for read operations.

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

    # ── Read with cursor pagination ───────────────────────────

    def list_recent(
        self,
        limit: int = 100,
        cursor: str | None = None,
        action: str | None = None,
        task_id: str | None = None,
        approval_id: str | None = None,
        errors_only: bool = False,
    ) -> dict[str, Any]:
        """List recent audit entries with cursor pagination.

        Returns: {entries: [...], next_cursor: str | None}
        Each entry is a summary (no raw detail_json).
        """
        entries = self._log.read_all()

        if cursor:
            idx = 0
            for i, e in enumerate(entries):
                if e.get("entry_id") == cursor:
                    idx = i + 1
                    break
            entries = entries[idx:]

        if action:
            entries = [e for e in entries if e.get("action") == action]
        if task_id:
            entries = [e for e in entries if e.get("detail", {}).get("task_id") == task_id or e.get("task_id") == task_id]
        if approval_id:
            entries = [e for e in entries if e.get("detail", {}).get("approval_id") == approval_id or e.get("approval_id") == approval_id]
        if errors_only:
            entries = [e for e in entries if e.get("action", "").endswith("_failed") or e.get("detail", {}).get("error")]

        entries = entries[-limit:]
        summaries = [self._to_summary(e) for e in entries]
        next_cursor = summaries[-1].get("entry_id") if len(summaries) == limit and summaries else None
        return {"entries": summaries, "next_cursor": next_cursor}

    def get_detail(self, entry_id: str) -> dict[str, Any] | None:
        """Get full detail for a single audit entry."""
        entries = self._log.read_all()
        for e in entries:
            if e.get("entry_id") == entry_id:
                return e
        return None

    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search audit entries by text query."""
        entries = self._log.read_all()
        query_lower = query.lower()
        results = []
        for e in entries:
            text = json.dumps(e, ensure_ascii=False).lower()
            if query_lower in text:
                results.append(self._to_summary(e))
                if len(results) >= limit:
                    break
        return results

    def summarize(self, period_hours: int = 24) -> dict[str, Any]:
        """Summarize audit activity for a period."""
        cutoff_ms = int(time.time() * 1000) - (period_hours * 3_600_000)
        entries = self._log.read_all()
        recent = [e for e in entries if e.get("timestamp_ms", 0) >= cutoff_ms]

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

    # ── Rotation ──────────────────────────────────────────────

    def rotate(self) -> int:
        """Rotate old entries to archive. Returns count rotated."""
        self._archive_dir.mkdir(parents=True, exist_ok=True)
        entries = self._log.read_all()
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
