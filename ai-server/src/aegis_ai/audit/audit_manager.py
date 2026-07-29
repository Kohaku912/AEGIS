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
import sqlite3
import threading
import time
import uuid
from contextlib import closing
from datetime import datetime, timezone, timedelta
from pathlib import Path

_JST = timezone(timedelta(hours=9))
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
            action = str(e.get("action") or "")
            if isinstance(detail, dict):
                e["detail_summary"] = self._detail_summary(detail, action)
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

    def list_groups(
        self,
        page: int = 1,
        per_page: int = 20,
        group_type: str | None = None,
        errors_only: bool = False,
        max_entries: int = 400,
    ) -> dict[str, Any]:
        """List logical audit groups, newest first."""
        entries = self._read_recent_entries(max(50, min(int(max_entries or 400), 1000)))
        groups = self._build_groups(entries)
        if group_type:
            groups = [g for g in groups if g.get("group_type") == group_type]
        if errors_only:
            groups = [g for g in groups if g.get("error_count", 0) > 0]

        groups.sort(key=lambda g: g.get("end_ms", 0), reverse=True)
        total = len(groups)
        page = max(1, int(page or 1))
        per_page = max(1, int(per_page or 20))
        total_pages = max(1, (total + per_page - 1) // per_page)
        start = (page - 1) * per_page
        return {
            "groups": groups[start:start + per_page],
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        }

    def get_group(self, group_id: str) -> dict[str, Any] | None:
        """Return one logical audit group with its raw entries."""
        if not group_id:
            return None
        for group in self._build_groups(self._read_recent_entries(1000)):
            if group.get("group_id") == group_id:
                return group
        return None

    def get_detail(self, entry_id: str) -> dict[str, Any] | None:
        """Get full detail for a single audit entry."""
        with closing(sqlite3.connect(str(self._log._db_path))) as conn:
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
        # Still bound single-entry responses for UI safety.
        from aegis_ai.audit.audit_log import sanitize_audit_detail

        d['detail'] = sanitize_audit_detail(d.get('detail'))
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
        for e in self._read_recent_entries(1000):
            text = json.dumps(e, ensure_ascii=False).lower()
            if query_lower in text:
                results.append(self._to_summary(e))
                if len(results) >= limit:
                    break
        return results

    def summarize(self, period_hours: int = 24) -> dict[str, Any]:
        """Summarize audit activity for a period."""
        cutoff_ms = int(time.time() * 1000) - (period_hours * 3_600_000)
        recent = [e for e in self._read_recent_entries(1000) if e.get("timestamp_ms", 0) >= cutoff_ms]

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
        return self._read_recent_entries(max_entries)

    def read_recent_for_dashboard(self, max_entries: int = 400) -> list[dict[str, Any]]:
        """Read recent entries for dashboard summaries (hot window only)."""
        return self._read_recent_entries(max_entries)

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
            logger.debug("Tail reader failed", exc_info=True)
            return []

    def _read_recent_entries(self, max_entries: int) -> list[dict[str, Any]]:
        """Read recent audit entries without sharing SQLite connections."""
        max_entries = max(1, int(max_entries or 1))
        try:
            page = self._log.read_page(page=1, per_page=max_entries)
            return page.get("entries", [])
        except Exception:
            logger.debug("SQLite audit page read failed, trying JSONL tail", exc_info=True)
            return self._read_tail(max_entries)

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

    def _build_groups(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        buckets: dict[str, list[dict[str, Any]]] = {}
        for entry in entries:
            gid = self._entry_group_id(entry)
            buckets.setdefault(gid, []).append(self._decorate_for_group(entry))

        groups: list[dict[str, Any]] = []
        for group_id, group_entries in buckets.items():
            group_entries.sort(key=lambda e: e.get("timestamp_ms", 0))
            first = group_entries[0]
            start_ms = group_entries[0].get("timestamp_ms", 0)
            end_ms = group_entries[-1].get("timestamp_ms", 0)
            error_count = sum(1 for e in group_entries if self._is_error(e))
            approval_count = sum(1 for e in group_entries if str(e.get("action", "")).startswith("approval_"))
            tool_count = sum(1 for e in group_entries if self._is_tool_event(e))
            status = self._group_status(group_entries, error_count)
            groups.append({
                "group_id": group_id,
                "group_type": self._entry_group_type(first),
                "title": self._entry_group_title(first, group_id),
                "start_ms": start_ms,
                "end_ms": end_ms,
                "start_time_str": self._format_ts(start_ms),
                "end_time_str": self._format_ts(end_ms),
                "status": status,
                "entry_count": len(group_entries),
                "tool_count": tool_count,
                "approval_count": approval_count,
                "error_count": error_count,
                "summary": self._group_summary(group_entries),
                "entries": group_entries,
            })
        return groups

    def _decorate_for_group(self, entry: dict[str, Any]) -> dict[str, Any]:
        item = dict(entry)
        detail = item.get("detail", {}) if isinstance(item.get("detail"), dict) else {}
        action = str(item.get("action") or "")
        item["time_str"] = self._format_ts(item.get("timestamp_ms", 0))
        item["detail_summary"] = self._detail_summary(detail, action)
        # Never materialize full pretty JSON for group lists — that OOM'd the dashboard path.
        item["detail_pretty"] = ""
        item["audit_group_id"] = self._entry_group_id(item)
        item["audit_group_type"] = self._entry_group_type(item)
        item["audit_group_title"] = self._entry_group_title(item, item["audit_group_id"])
        # Drop bulky nested detail after summary is computed.
        # Keep narrative fields so Activity can show what AEGIS said/did in natural language.
        if isinstance(detail, dict) and detail:
            item["detail"] = {
                key: detail.get(key)
                for key in (
                    "error",
                    "status",
                    "execution_status",
                    "capability_id",
                    "model",
                    "tokens",
                    "response_preview",
                    "result_preview",
                    "result_summary",
                    "what_was_done",
                    "llm_reason",
                    "title",
                )
                if key in detail
            }
        return item

    def _entry_group_id(self, entry: dict[str, Any]) -> str:
        detail = entry.get("detail", {}) if isinstance(entry.get("detail"), dict) else {}
        return str(
            entry.get("audit_group_id")
            or entry.get("task_id")
            or detail.get("task_id")
            or entry.get("request_id")
            or detail.get("request_id")
            or entry.get("approval_id")
            or detail.get("approval_id")
            or entry.get("entry_id")
            or f"audit_{entry.get('timestamp_ms', 0)}"
        )

    def _entry_group_type(self, entry: dict[str, Any]) -> str:
        explicit = str(entry.get("audit_group_type") or "")
        if explicit:
            return explicit
        action = str(entry.get("action") or "")
        actor = str(entry.get("actor") or "")
        detail = entry.get("detail", {}) if isinstance(entry.get("detail"), dict) else {}
        if detail.get("origin_channel") or actor == "chat_tools":
            return "chat"
        if actor == "autonomous" or action.startswith("autonomous_"):
            return "autonomous"
        if action.startswith("approval_") or entry.get("approval_id") or detail.get("approval_id"):
            return "approval"
        if entry.get("task_id") or detail.get("task_id") or action.startswith("task_"):
            return "task"
        return "system"

    def _entry_group_title(self, entry: dict[str, Any], group_id: str) -> str:
        explicit = str(entry.get("audit_group_title") or "")
        if explicit:
            return explicit
        detail = entry.get("detail", {}) if isinstance(entry.get("detail"), dict) else {}
        for key in ("title", "original_message", "goal", "reason"):
            value = str(detail.get(key) or "")
            if value:
                return value[:120]
        action = str(entry.get("action") or "Audit group")
        return f"{action}: {group_id}"[:140]

    def _detail_summary(self, detail: Any, action: str = "") -> str:
        """Human-readable one-liner for Activity / audit groups.

        Prefer natural-language LLM responses and tool results over key=value dumps.
        """
        if not isinstance(detail, dict):
            return str(detail)[:100]

        if detail.get("error"):
            return f"Error: {str(detail['error'])[:180]}"

        if action in ("llm_call", "llm_tool_call", "llm_vision_call"):
            response = str(detail.get("response_preview") or "").strip()
            if response:
                return response[:220]
            tool_calls = detail.get("tool_calls")
            if tool_calls:
                names = [
                    str(tc.get("function") or tc.get("name") or "")
                    for tc in tool_calls
                    if isinstance(tc, dict)
                ]
                names = [name for name in names if name]
                if names:
                    return f"Chose tools: {', '.join(names[:5])}"
            model = str(detail.get("model") or "").strip()
            return f"LLM call ({model})" if model else "LLM call completed"

        if action in ("tool_execution", "tool_invoked") or action.startswith("tool."):
            for key in ("result_summary", "result_preview", "what_was_done", "output_summary"):
                value = str(detail.get(key) or "").strip()
                if value:
                    return value[:180]
            status = str(detail.get("execution_status") or detail.get("status") or "").strip()
            cap_id = str(detail.get("capability_id") or "").strip()
            if status and status.lower() not in {"success", "ok", "completed"}:
                return f"Tool {status}" + (f" ({cap_id})" if cap_id else "")
            if cap_id:
                short = cap_id.rsplit(".", 1)[-1].replace("_", " ")
                return f"Ran {short}"
            return "Tool completed"

        if action.startswith("task_"):
            title = str(detail.get("title") or "").strip()
            status = str(detail.get("status") or "").strip()
            if title and status:
                return f"{title} ({status})"[:180]
            if title:
                return title[:180]
            return status or "Task update"

        if action.startswith("approval_"):
            summary = str(detail.get("user_facing_summary") or detail.get("summary") or "").strip()
            if summary:
                return summary[:180]
            risk = str(detail.get("risk_level") or "").strip()
            return f"Approval ({risk})" if risk else "Approval update"

        if action.startswith("autonomous_"):
            for key in ("llm_reason", "what_was_done", "result_summary", "decision"):
                value = str(detail.get(key) or "").strip()
                if value:
                    return value[:180]
            source = str(detail.get("source") or "").strip()
            return f"Autonomous tick ({source})" if source else "Autonomous update"

        for key in (
            "response_preview",
            "result_summary",
            "what_was_done",
            "llm_reason",
            "summary",
            "message",
            "title",
        ):
            value = str(detail.get(key) or "").strip()
            if value:
                return value[:180]
        for key, value in list(detail.items())[:3]:
            if key != "error" and value not in (None, ""):
                return f"{key}: {str(value)[:80]}"
        return ""

    def _group_summary(self, entries: list[dict[str, Any]]) -> str:
        """Prefer the last natural-language LLM / action narrative for the group."""
        llm_actions = {"llm_call", "llm_tool_call", "llm_vision_call"}
        for entry in reversed(entries):
            action = str(entry.get("action") or "")
            detail = entry.get("detail") if isinstance(entry.get("detail"), dict) else {}
            if action in llm_actions:
                response = str(detail.get("response_preview") or "").strip()
                if response:
                    return response[:280]
                summary = str(entry.get("detail_summary") or "").strip()
                if summary:
                    return summary[:280]
        for entry in reversed(entries):
            detail = entry.get("detail") if isinstance(entry.get("detail"), dict) else {}
            for key in ("what_was_done", "result_summary", "result_preview", "llm_reason"):
                value = str(detail.get(key) or "").strip()
                if value:
                    return value[:280]
            reason = str(entry.get("reason") or "").strip()
            if reason:
                return reason[:220]
            summary = str(entry.get("detail_summary") or "").strip()
            if summary:
                return summary[:220]
        return f"{len(entries)} audit event(s)"

    def _group_status(self, entries: list[dict[str, Any]], error_count: int) -> str:
        actions = {str(e.get("action") or "") for e in entries}
        if error_count and len(entries) > error_count:
            return "mixed"
        if error_count:
            return "failed"
        if {"approval_created", "approval_enqueued"} & actions and not ({"approval_approved", "approval_rejected", "approval_executed", "approval_failed"} & actions):
            return "waiting_approval"
        return "success"

    def _is_tool_event(self, entry: dict[str, Any]) -> bool:
        action = str(entry.get("action") or "")
        return action in {"tool_execution", "tool_invoked"} or action.startswith("tool.")

    def _is_error(self, entry: dict[str, Any]) -> bool:
        action = str(entry.get("action") or "")
        decision = str(entry.get("decision") or "").lower()
        detail = entry.get("detail", {}) if isinstance(entry.get("detail"), dict) else {}
        execution_status = str(detail.get("execution_status") or detail.get("status") or "").lower()
        return bool(
            action.endswith("_failed")
            or decision in {"error", "failed", "deny", "denied"}
            or detail.get("error")
            or (execution_status and execution_status not in {"success", "completed", "started"})
        )

    def _format_ts(self, timestamp_ms: int) -> str:
        if not timestamp_ms:
            return "-"
        try:
            dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=_JST)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "-"
