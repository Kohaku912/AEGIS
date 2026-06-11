"""Audit Log — append-only, immutable decision record.

Architecture reference: docs/architecture.md §5.9
Security requirement: every policy decision, tool invocation, and approval is recorded.

Implementation: JSONL file (one JSON object per line).
Future: SQLite or tamper-evident log (hash chain).

STATUS: Minimal implementation — append + list_recent.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AuditEntry:
    """A single audit log entry."""
    timestamp_ms: int = 0
    action: str = ""                   # e.g. "tool_invoked", "policy_decision"
    actor: str = ""                    # Agent name, user, system
    capability_id: str = ""
    decision: str = ""                 # "ALLOW", "DENY", "ASK_APPROVAL"
    reason: str = ""
    detail: dict[str, Any] = field(default_factory=dict)
    entry_id: str = ""


class AuditLog:
    """Append-only audit log backed by JSONL.

    Thread-safe for concurrent writes.
    """

    def __init__(self, path: str = "data/audit.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._entries: list[AuditEntry] = []  # In-memory buffer

    # ── Write ───────────────────────────────────────────────

    def append(self, entry: AuditEntry) -> None:
        """Append an entry to the audit log. Thread-safe."""
        if not entry.entry_id:
            entry.entry_id = f"audit_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
        if not entry.timestamp_ms:
            entry.timestamp_ms = int(time.time() * 1000)

        record = {
            "entry_id": entry.entry_id,
            "timestamp_ms": entry.timestamp_ms,
            "action": entry.action,
            "actor": entry.actor,
            "capability_id": entry.capability_id,
            "decision": entry.decision,
            "reason": entry.reason,
            "detail": entry.detail,
        }

        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._entries.append(entry)

    # ── Read ────────────────────────────────────────────────

    def list_recent(self, n: int = 50) -> list[AuditEntry]:
        """Return the most recent N entries from in-memory buffer."""
        with self._lock:
            entries = list(self._entries)
        return entries[-n:] if n < len(entries) else entries

    def read_all(self) -> list[dict[str, Any]]:
        """Read all entries from the JSONL file."""
        if not self._path.exists():
            return []
        records: list[dict[str, Any]] = []
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    # ── Utility ─────────────────────────────────────────────

    def log_decision(
        self,
        action: str,
        capability_id: str,
        decision: str,
        reason: str = "",
        actor: str = "ellie",
        detail: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Convenience method: log a policy/tool decision and return the entry."""
        entry = AuditEntry(
            action=action,
            capability_id=capability_id,
            decision=decision,
            reason=reason,
            actor=actor,
            detail=detail or {},
        )
        self.append(entry)
        return entry

    def clear(self) -> None:
        """Clear in-memory buffer (for testing). Does NOT delete file."""
        with self._lock:
            self._entries.clear()
