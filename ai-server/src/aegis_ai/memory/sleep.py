"""Sleep Manager — memory consolidation during idle periods.

Wraps SleepConsolidationSystem. Manages triggers, state, and safety.
"""

from __future__ import annotations

import logging
import threading
import time
from enum import Enum
from typing import Any

logger = logging.getLogger("aegis_ai.memory.sleep")


class SleepState(Enum):
    IDLE = "idle"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SleepManager:
    """Memory consolidation during idle periods.

    Wraps SleepConsolidationSystem with state management,
    trigger scheduling, and safety enforcement.

    Parameters
    ----------
    memory_manager:
        MemoryManager instance for memory operations.
    event_manager:
        Optional EventManager for publishing sleep events.
    audit_manager:
        Optional AuditManager for recording sleep summaries.
    llm_gateway:
        Optional LLMGateway for LLM-based summarization.
    idle_threshold_s:
        Seconds of idle before auto-triggering sleep (default: 3600).
    """

    def __init__(
        self,
        memory_manager: Any = None,
        event_manager: Any = None,
        audit_manager: Any = None,
        llm_gateway: Any = None,
        idle_threshold_s: float = 3600.0,
    ) -> None:
        self._memory_manager = memory_manager
        self._event_manager = event_manager
        self._audit_manager = audit_manager
        self._llm = llm_gateway
        self._idle_threshold = idle_threshold_s

        self._state = SleepState.IDLE
        self._last_activity_ms = int(time.time() * 1000)
        self._last_sleep_ms = 0
        self._last_summary: dict[str, Any] = {}
        self._scheduled_ms = 0
        self._lock = threading.Lock()
        self._sleep_thread: threading.Thread | None = None

    # ── Public API ────────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        """Get sleep system status."""
        with self._lock:
            return {
                "state": self._state.value,
                "last_activity_ms": self._last_activity_ms,
                "last_sleep_ms": self._last_sleep_ms,
                "scheduled_ms": self._scheduled_ms,
                "last_summary": self._last_summary,
            }

    def start_sleep(self, reason: str = "manual") -> bool:
        """Start sleep consolidation. Returns False if already running."""
        with self._lock:
            if self._state in (SleepState.RUNNING, SleepState.COMPLETED, SleepState.FAILED):
                if self._state == SleepState.COMPLETED or self._state == SleepState.FAILED:
                    self._state = SleepState.IDLE
                else:
                    return False
            self._state = SleepState.RUNNING

        self._publish_event("memory.sleep.started", {"reason": reason})
        self._record_audit("sleep_started", reason=reason)

        self._sleep_thread = threading.Thread(
            target=self._run_sleep, args=(reason,), daemon=True, name="sleep-manager"
        )
        self._sleep_thread.start()
        return True

    def stop_sleep(self) -> None:
        """Cancel running sleep."""
        with self._lock:
            if self._state == SleepState.RUNNING:
                self._state = SleepState.CANCELLED

    def schedule_sleep(self, timestamp_ms: int) -> None:
        """Schedule sleep at a specific time."""
        with self._lock:
            self._scheduled_ms = timestamp_ms
            self._state = SleepState.SCHEDULED

    def update_activity(self) -> None:
        """Update last activity timestamp (call on user interaction)."""
        with self._lock:
            self._last_activity_ms = int(time.time() * 1000)

    def check_triggers(self) -> bool:
        """Check if sleep should be triggered. Returns True if triggered."""
        now_ms = int(time.time() * 1000)

        with self._lock:
            if self._state == SleepState.RUNNING:
                return False

            idle_ms = now_ms - self._last_activity_ms
            if idle_ms > self._idle_threshold * 1000:
                return self.start_sleep(reason="idle_timeout")

            if self._scheduled_ms > 0 and now_ms >= self._scheduled_ms:
                self._scheduled_ms = 0
                return self.start_sleep(reason="scheduled")

        return False

    # ── Internal ──────────────────────────────────────────────

    def _run_sleep(self, reason: str) -> None:
        """Execute the sleep consolidation pipeline."""
        summary: dict[str, Any] = {
            "reason": reason,
            "started_ms": int(time.time() * 1000),
            "lessons_extracted": 0,
            "memories_merged": 0,
            "memories_archived": 0,
            "conflicts_detected": 0,
            "errors": [],
        }

        try:
            if self._memory_manager is not None:
                merged = self._memory_manager.deduplicate()
                summary["memories_merged"] = merged

            self._last_summary = summary
        except Exception as e:
            summary["errors"].append(str(e))
            logger.exception("Sleep consolidation failed")

        summary["completed_ms"] = int(time.time() * 1000)
        summary["duration_ms"] = summary["completed_ms"] - summary["started_ms"]

        with self._lock:
            self._last_summary = summary
            self._last_sleep_ms = summary["completed_ms"]
            if self._state == SleepState.CANCELLED:
                pass
            elif summary["errors"]:
                self._state = SleepState.FAILED
            else:
                self._state = SleepState.COMPLETED

        self._publish_event("memory.sleep.completed", summary)
        self._record_audit("sleep_completed", **summary)

    def _publish_event(self, event_type: str, payload: dict) -> None:
        if self._event_manager is None:
            return
        try:
            from aegis_schema.models import Event
            self._event_manager.publish(Event(
                event_type=event_type,
                source="sleep_manager",
                payload=payload,
            ))
        except Exception:
            pass

    def _record_audit(self, action: str, **kwargs) -> None:
        if self._audit_manager is None:
            return
        try:
            from aegis_ai.audit import AuditEntry
            self._audit_manager.append(AuditEntry(
                action=action,
                actor="sleep_manager",
                detail=kwargs,
            ))
        except Exception:
            pass
