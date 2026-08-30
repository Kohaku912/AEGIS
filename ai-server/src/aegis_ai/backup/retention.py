"""Retention — manages data lifecycle and cleanup.

Handles:
- Episodic memory retention
- Notification retention
- Screenshot retention
- Audit retention
- Expired approval cleanup
"""

from __future__ import annotations

import time
from typing import Any


class RetentionManager:
    """Manages data retention policies and cleanup.

    Usage:
        manager = RetentionManager(
            episodic_memory=episodic,
            audit_log=audit,
            approval_store=approval_store,
        )
        cleaned = manager.cleanup_expired()
    """

    def __init__(
        self,
        episodic_memory: Any = None,
        audit_log: Any = None,
        approval_store: Any = None,
        settings_store: Any = None,
        memory_store: Any = None,
    ) -> None:
        self._episodic = episodic_memory
        self._audit = audit_log
        self._approval = approval_store
        self._settings = settings_store
        self._store = memory_store

    def cleanup_expired(self) -> dict[str, int]:
        """Clean up expired data based on retention policies.

        Returns dict with counts of cleaned items.
        """
        cleaned: dict[str, int] = {}

        # Clean expired approvals
        if self._approval:
            count = self._approval.expire_old_requests()
            cleaned["expired_approvals"] = count

        # Clean old episodic memories
        if self._episodic and self._settings:
            settings = self._settings.get()
            retention_days = settings.memory.episodic_retention_days
            max_age_ms = retention_days * 86400 * 1000
            prune = getattr(self._episodic, "prune_expired", None)
            if callable(prune):
                try:
                    cleaned["old_episodes"] = int(prune(max_age_ms=max_age_ms) or 0)
                except TypeError:
                    cleaned["old_episodes"] = int(prune() or 0)
            else:
                cutoff_ms = int(time.time() * 1000) - max_age_ms
                episodes = self._episodic.list_recent(100000)
                cleaned["old_episodes"] = sum(1 for e in episodes if e.timestamp_ms < cutoff_ms)

        # Clean expired unified-store records (desire/failure lessons, preferences)
        if self._store is not None and hasattr(self._store, "prune_expired"):
            cleaned["expired_store"] = int(self._store.prune_expired() or 0)

        pdc = getattr(self, "_personal_data_core", None)
        if pdc is not None:
            cleaned.update({f"pdc_{k}": v for k, v in pdc.apply_retention().items()})

        return cleaned

    def get_retention_status(self) -> dict[str, Any]:
        """Get current retention status for dashboard."""
        status: dict[str, Any] = {}

        if self._settings:
            settings = self._settings.get()
            status["episodic_retention_days"] = settings.memory.episodic_retention_days
            status["notification_retention_hours"] = settings.privacy.notification_text_retention_hours
            status["screenshot_retention_hours"] = settings.privacy.screenshot_retention_hours

        if self._episodic:
            episodes = self._episodic.list_recent(100000)
            status["total_episodes"] = len(episodes)

        if self._approval:
            pending = self._approval.get_pending()
            status["pending_approvals"] = len(pending)

        return status

    def delete_memory_entry(self, memory_type: str, entry_id: str) -> bool:
        """Delete a specific memory entry (user-requested)."""
        backend = self._episodic
        if backend is None:
            return False
        if memory_type in {"entity", "entities"} and hasattr(backend, "delete_entity"):
            return bool(backend.delete_entity(entry_id))
        if memory_type in {"fact", "facts"} and hasattr(backend, "delete_fact"):
            return bool(backend.delete_fact(entry_id))
        deleter = getattr(backend, "delete", None)
        if callable(deleter):
            return bool(deleter(entry_id))
        return False
