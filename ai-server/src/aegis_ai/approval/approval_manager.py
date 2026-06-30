"""Approval Manager — unified approval state owner.

Centralizes all approval lifecycle management. Wraps ApprovalQueue
for persistence and provides a clean external API.

Architecture:
- ApprovalManager is the SINGLE entry point for approval state transitions
- PolicyEngine returns ASK_APPROVAL decisions; ToolBroker calls ApprovalManager
- Fanout channels deliver notifications; state changes trigger callbacks
- Double-execution prevented via _executed set (delegated to ApprovalQueue)
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import Any

from aegis_ai.approval.approval_queue import ApprovalQueue
from aegis_ai.approval.approval_types import ApprovalRequest

logger = logging.getLogger("aegis_ai.approval.approval_manager")

# Valid state transitions — any other transition is a no-op
_VALID_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"approved", "modified", "rejected", "expired", "cancelled"},
    "approved": {"executing", "executed", "failed", "cancelled", "expired"},
    "modified": {"executing", "executed", "failed", "cancelled", "expired"},
    "rejected": set(),
    "expired": set(),
    "cancelled": set(),
    "executing": {"executed", "failed"},
    "executed": set(),
    "failed": set(),
}


class ApprovalManager:
    """Unified approval lifecycle manager.

    Wraps ApprovalQueue for persistence. External code uses
    ApprovalManager only — never touches ApprovalQueue directly.

    Parameters
    ----------
    approval_queue:
        The persistent queue backend.
    audit_log:
        Optional audit log for recording state transitions.
    """

    def __init__(
        self,
        approval_queue: ApprovalQueue,
        audit_log: Any = None,
        task_manager: Any = None,
    ) -> None:
        self._queue = approval_queue
        self._audit = audit_log
        self._task_manager = task_manager
        self._callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._lock = threading.RLock()

        # Register TaskManager callback if provided
        if task_manager:
            self.on_state_change(self._task_manager_callback)

    # ── Public API ────────────────────────────────────────────

    def create_request(
        self,
        tool_request: Any,
        policy_result: Any,
    ) -> ApprovalRequest:
        """Create an approval request from a tool execution request.

        Delegates to ApprovalQueue.enqueue() for persistence.
        Notifies registered callbacks with 'created' event.
        """
        req = self._queue.enqueue(tool_request, policy_result)
        self._notify_state_change(req, "created")
        return req

    def list_pending(self) -> list[ApprovalRequest]:
        """Return non-expired pending requests."""
        return self._queue.list_pending()

    def get(self, approval_id: str) -> ApprovalRequest | None:
        """Get an approval request by ID."""
        return self._queue.get(approval_id)

    def approve(
        self,
        approval_id: str,
        channel: str = "unknown",
        user: str = "user",
    ) -> ApprovalRequest | None:
        """Approve a pending request.

        Returns the request if successfully approved, None if not found
        or already in a terminal state (idempotent).
        """
        with self._lock:
            current = self._queue.get(approval_id)
            if current is not None and current.status in ("approved", "modified", "executing", "executed", "failed"):
                self._record_ignored_late_rejection(current, channel, user, "late approval after terminal progress")
                return None
        req = self._queue.approve(approval_id, user_note=f"via {channel}")
        if req is None:
            return None
        req.approved_by_channel = channel  # type: ignore[attr-defined]
        req.approved_by_user = user  # type: ignore[attr-defined]
        req.approved_by_surface = channel
        req.surface_decisions[channel] = {
            "decision": "approved",
            "user": user,
            "reason": "",
            "timestamp": int(time.time() * 1000),
        }
        if hasattr(self._queue, "_save"):
            self._queue._save()
        self._notify_state_change(req, "approved")
        return req

    def reject(
        self,
        approval_id: str,
        channel: str = "unknown",
        user: str = "user",
        reason: str = "",
    ) -> ApprovalRequest | None:
        """Record a surface-level rejection while keeping central state pending."""
        with self._lock:
            req = self._queue.get(approval_id)
            if req is None:
                return None
            if req.status != "pending":
                self._record_ignored_late_rejection(req, channel, user, reason)
                return None
            req.surface_decisions[channel] = {
                "decision": "rejected",
                "user": user,
                "reason": reason,
                "timestamp": int(time.time() * 1000),
            }
            if hasattr(self._queue, "_save"):
                self._queue._save()
        req.rejected_by_channel = channel  # type: ignore[attr-defined]
        req.rejected_by_user = user  # type: ignore[attr-defined]
        self._notify_state_change(req, "surface_rejected")
        return req

    def global_reject(
        self,
        approval_id: str,
        channel: str = "unknown",
        user: str = "user",
        reason: str = "",
    ) -> ApprovalRequest | None:
        """Reject the approval globally, closing all surfaces."""
        req = self._queue.reject(approval_id, reason=reason)
        if req is None:
            current = self._queue.get(approval_id)
            if current is not None:
                self._record_ignored_late_rejection(current, channel, user, reason)
            return None
        req.rejected_by_channel = channel  # type: ignore[attr-defined]
        req.rejected_by_user = user  # type: ignore[attr-defined]
        req.surface_decisions[channel] = {
            "decision": "global_rejected",
            "user": user,
            "reason": reason,
            "timestamp": int(time.time() * 1000),
        }
        if hasattr(self._queue, "_save"):
            self._queue._save()
        self._notify_state_change(req, "rejected")
        return req

    def record_surface_delivery(self, approval_id: str, results: dict[str, bool]) -> None:
        """Record which approval surfaces received a request/update."""
        with self._lock:
            req = self._queue.get(approval_id)
            if req is None:
                return
            req.surface_delivery.update(results)
            if hasattr(self._queue, "_save"):
                self._queue._save()

    def modify_and_approve(
        self,
        approval_id: str,
        modified_arguments: dict[str, Any],
        channel: str = "unknown",
        user: str = "user",
    ) -> ApprovalRequest | None:
        """Modify arguments and approve a pending request."""
        req = self._queue.modify_and_approve(
            approval_id,
            modified_arguments=modified_arguments,
            user_note=f"via {channel}",
        )
        if req is None:
            return None
        req.approved_by_channel = channel  # type: ignore[attr-defined]
        req.approved_by_user = user  # type: ignore[attr-defined]
        self._notify_state_change(req, "modified")
        return req

    def cancel(
        self,
        approval_id: str,
        reason: str = "",
    ) -> ApprovalRequest | None:
        """Cancel a pending/approved/modified request."""
        req = self._queue.cancel(approval_id, reason=reason)
        if req is None:
            return None
        self._notify_state_change(req, "cancelled")
        return req

    def expire_old(self) -> int:
        """Expire old pending requests. Returns count expired."""
        count = self._queue.expire_old_requests()
        return count

    def mark_executed(
        self,
        approval_id: str,
        result: Any = None,
    ) -> None:
        """Mark an approval as executed."""
        self._queue.mark_executed(approval_id, result=result)
        req = self._queue.get(approval_id)
        if req is not None:
            self._notify_state_change(req, "executed")

    def mark_failed(
        self,
        approval_id: str,
        error: str = "",
    ) -> None:
        """Mark an approval as failed."""
        self._queue.mark_failed(approval_id, error=error)
        req = self._queue.get(approval_id)
        if req is not None:
            self._notify_state_change(req, "failed")

    def mark_executing(self, approval_id: str) -> None:
        """Mark an approval as currently executing."""
        with self._lock:
            req = self._queue.get(approval_id)
            if req is None:
                return
            if req.status not in ("approved", "modified"):
                return
            req.status = "executing"
            # Persist via queue's save mechanism
            if hasattr(self._queue, "_save"):
                self._queue._save()
        self._notify_state_change(req, "executing")

    def is_executed(self, approval_id: str) -> bool:
        """Check if an approval has already been executed (or terminally failed)."""
        req = self._queue.get(approval_id)
        if req is None:
            return False
        return req.status in ("executed", "failed")

    def is_approved(self, approval_id: str) -> bool:
        """Check if an approval is in an approved/modified state."""
        req = self._queue.get(approval_id)
        if req is None:
            return False
        return req.status in ("approved", "modified")

    # ── Callback registration ─────────────────────────────────

    def on_state_change(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback for state changes.

        Callback receives a dict with:
        - approval_id: str
        - event_type: str (created/approved/rejected/modified/expired/cancelled/executing/executed/failed)
        - request: ApprovalRequest
        - state: str (new status)
        - timestamp: int (epoch ms)
        - channel: str (which channel triggered, if applicable)
        - user: str (who triggered, if applicable)
        """
        with self._lock:
            self._callbacks.append(callback)

    def remove_state_change_callback(self, callback: Callable) -> None:
        """Remove a registered callback."""
        with self._lock:
            try:
                self._callbacks.remove(callback)
            except ValueError:
                pass

    # ── Internal ──────────────────────────────────────────────

    def _notify_state_change(
        self,
        request: ApprovalRequest,
        event_type: str,
    ) -> None:
        """Notify all registered callbacks of a state change."""
        event = {
            "approval_id": request.approval_id,
            "event_type": event_type,
            "request": request,
            "state": request.status,
            "timestamp": int(time.time() * 1000),
            "channel": getattr(request, "approved_by_channel", "")
                       or getattr(request, "rejected_by_channel", ""),
            "user": getattr(request, "approved_by_user", "")
                    or getattr(request, "rejected_by_user", ""),
        }

        self._record_audit(request, event_type, event.get("channel", ""), event.get("user", ""))

        with self._lock:
            callbacks = list(self._callbacks)
        for cb in callbacks:
            try:
                cb(event)
            except Exception:
                logger.exception("Approval callback failed for %s", event_type)

    def _record_audit(
        self,
        request: ApprovalRequest,
        event_type: str,
        channel: str = "",
        user: str = "",
    ) -> None:
        """Record approval event to audit log."""
        if self._audit is None:
            return
        action_map = {
            "created": "approval_created",
            "approved": "approval_approved",
            "surface_rejected": "approval_surface_rejected",
            "rejected": "approval_rejected",
            "modified": "approval_modified",
            "expired": "approval_expired",
            "cancelled": "approval_cancelled",
            "executing": "approval_executing",
            "executed": "approval_executed",
            "failed": "approval_failed",
        }
        action = action_map.get(event_type, f"approval_{event_type}")
        try:
            metadata = getattr(request, "metadata", {}) or {}
            self._audit.log_approval(
                action=action,
                approval_id=request.approval_id,
                capability_id=request.capability_id,
                channel=channel,
                user=user,
                request_id=request.request_id,
                task_id=request.task_id,
                source_desire=request.source_desire,
                risk_level=request.risk_level,
                audit_group_id=str(metadata.get("audit_group_id") or ""),
                audit_group_type=str(metadata.get("audit_group_type") or ""),
                audit_group_title=str(metadata.get("audit_group_title") or ""),
            )
        except Exception:
            logger.debug("Failed to record approval audit", exc_info=True)

    def _record_ignored_late_rejection(
        self,
        request: ApprovalRequest,
        channel: str,
        user: str,
        reason: str,
    ) -> None:
        """Audit a late rejection without rolling back central approval state."""
        if self._audit is None:
            return
        try:
            from aegis_ai.audit import AuditEntry

            self._audit.append(
                AuditEntry(
                    action="ignored_late_rejection",
                    actor=user,
                    capability_id=request.capability_id,
                    decision=request.status,
                    reason=reason,
                    detail={
                        "approval_id": request.approval_id,
                        "channel": channel,
                        "user": user,
                        "status": request.status,
                    },
                )
            )
        except Exception:
            logger.debug("Failed to record ignored late rejection", exc_info=True)

    def _task_manager_callback(self, event: dict[str, Any]) -> None:
        """Callback to update TaskManager and ExecutionEngine when approval state changes."""
        request = event.get("request")
        if request is None:
            return
        if getattr(request, "origin_channel", "") == "dashboard_chat":
            return

        task_id = getattr(request, "task_id", "")
        step_id = getattr(request, "step_id", "")
        approval_id = getattr(request, "approval_id", "")
        event_type = event.get("event_type")

        if event_type == "approved":
            if self._task_manager and task_id:
                self._task_manager.resume_after_approval(task_id, step_id)
            if hasattr(self, "_execution_engine") and self._execution_engine and approval_id:
                try:
                    self._execution_engine.resume_after_approval(approval_id)
                except Exception:
                    logger.exception("ExecutionEngine resume failed for %s", approval_id)
        elif event_type == "rejected":
            if self._task_manager and task_id:
                self._task_manager.fail_task(task_id, error="Approval rejected")
