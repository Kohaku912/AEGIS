"""Audit View — provides audit log history for dashboard display."""

from __future__ import annotations

import re
from typing import Any


class AuditView:
    """Read-only view of AuditLog for dashboard display.

    Masks sensitive values in audit entries before display.
    """

    def __init__(self, audit_log: Any = None) -> None:
        self._audit = audit_log

    def get_recent_entries(self, n: int = 50) -> list[dict[str, Any]]:
        """Get recent audit entries with masked sensitive values."""
        if not self._audit:
            return []

        entries = self._audit.list_recent(n)
        result = []
        for e in entries:
            detail = self._mask_detail(e.detail) if e.detail else {}
            result.append({
                "entry_id": e.entry_id,
                "timestamp_ms": e.timestamp_ms,
                "action": e.action,
                "actor": e.actor,
                "capability_id": e.capability_id,
                "decision": e.decision,
                "reason": self._mask_text(e.reason),
                "detail": detail,
            })
        return result

    def get_stats(self) -> dict[str, Any]:
        """Get audit log statistics."""
        if not self._audit:
            return {}
        entries = self._audit.list_recent(1000)
        actions: dict[str, int] = {}
        decisions: dict[str, int] = {}
        for e in entries:
            actions[e.action] = actions.get(e.action, 0) + 1
            decisions[e.decision] = decisions.get(e.decision, 0) + 1
        return {
            "total_entries": len(entries),
            "actions": actions,
            "decisions": decisions,
        }

    @staticmethod
    def _mask_text(text: str) -> str:
        """Mask sensitive values in text."""
        patterns = [
            (r'(password|passwd|secret|token|api_key|apikey)\s*[=:]\s*"[^"]*"', r'\1="[REDACTED]"'),
            (r'(password|passwd|secret|token|api_key|apikey)\s*[=:]\s*[^\s,;]+', r'\1=[REDACTED]'),
        ]
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _mask_detail(detail: dict[str, Any]) -> dict[str, Any]:
        """Mask sensitive values in detail dict."""
        masked = {}
        sensitive_keys = {"password", "secret", "token", "api_key", "apikey", "credential"}
        for k, v in detail.items():
            if k.lower() in sensitive_keys:
                masked[k] = "[REDACTED]"
            elif isinstance(v, str):
                masked[k] = AuditView._mask_text(v)
            else:
                masked[k] = v
        return masked
