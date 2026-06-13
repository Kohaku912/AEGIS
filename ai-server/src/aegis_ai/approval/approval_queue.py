"""Approval Queue — persistent queue for user approval of dangerous operations."""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from aegis_ai.approval.approval_types import (
    _EXPIRY_BY_RISK,
    ApprovalRequest,
    _generate_user_facing_summary,
    _summarize_arguments,
)

logger = logging.getLogger("aegis_ai.approval.approval_queue")


class ApprovalQueue:
    """Persistent approval queue with JSON file storage.

    Parameters
    ----------
    data_dir:
        Directory for persistence files.
    audit_log:
        Optional audit log for recording decisions.
    memory_store:
        Optional MemoryStore for recording approval lessons.
    """

    def __init__(
        self,
        data_dir: str = "data/approvals",
        audit_log: Any = None,
        memory_store: Any = None,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._audit = audit_log
        self._memory_store = memory_store
        self._requests: dict[str, ApprovalRequest] = {}
        self._executed: set[str] = set()
        self._load()

    # ── Public API ────────────────────────────────────────────

    def enqueue(
        self,
        tool_request: Any,
        policy_result: Any,
    ) -> ApprovalRequest:
        """Enqueue a tool execution request for approval."""
        request_id = getattr(tool_request, "request_id", "")
        cap_id = getattr(tool_request, "capability_id", "")
        tool_name = getattr(tool_request, "tool_name", "")
        arguments = getattr(tool_request, "arguments", {})
        source = getattr(tool_request, "source", "system")
        source_val = source.value if hasattr(source, "value") else str(source)
        source_desire = getattr(tool_request, "source_desire", "")
        frustration = getattr(tool_request, "frustration", 0.0)
        task_id = getattr(tool_request, "task_id", "")
        risk_level = getattr(tool_request, "risk_level", None)
        risk_name = risk_level.name.lower() if hasattr(risk_level, "name") else "medium"
        policy_reason = getattr(policy_result, "reason", "") if policy_result else ""

        now_ms = int(time.time() * 1000)
        expiry_ms = _EXPIRY_BY_RISK.get(risk_name, 1_800_000)

        req = ApprovalRequest(
            approval_id=f"appr_{uuid.uuid4().hex[:10]}",
            request_id=request_id,
            task_id=task_id,
            source=source_val,
            source_desire=source_desire,
            frustration=frustration,
            capability_id=cap_id,
            tool_name=tool_name,
            arguments=dict(arguments),
            arguments_summary=_summarize_arguments(arguments),
            risk_level=risk_name,
            policy_decision="ASK_APPROVAL",
            approval_reason=policy_reason,
            user_facing_summary=_generate_user_facing_summary(
                cap_id, tool_name, arguments, policy_reason, source_desire, frustration,
            ),
            created_at=now_ms,
            expires_at=now_ms + expiry_ms,
            status="pending",
        )

        self._requests[req.approval_id] = req
        self._save()

        if self._audit is not None:
            self._record_audit("approval_enqueued", req)

        logger.info("Approval enqueued: %s for %s", req.approval_id, cap_id)
        return req

    def list_pending(self) -> list[ApprovalRequest]:
        """Return non-expired pending requests."""
        self._expire_old()
        return [r for r in self._requests.values() if r.status == "pending"]

    def get(self, approval_id: str) -> ApprovalRequest | None:
        return self._requests.get(approval_id)

    def approve(self, approval_id: str, user_note: str = "") -> ApprovalRequest | None:
        req = self._requests.get(approval_id)
        if req is None or req.status != "pending":
            return None
        if req.is_expired():
            req.status = "expired"
            self._save()
            return None
        req.status = "approved"
        self._save()
        if self._audit is not None:
            self._record_audit("approval_granted", req, user_note=user_note)
        self._record_approval_memory(req, "approved", user_note)
        return req

    def reject(self, approval_id: str, reason: str = "") -> ApprovalRequest | None:
        req = self._requests.get(approval_id)
        if req is None or req.status != "pending":
            return None
        req.status = "rejected"
        self._save()
        if self._audit is not None:
            self._record_audit("approval_rejected", req, reason=reason)
        self._record_approval_memory(req, "rejected", reason)
        return req

    def modify_and_approve(
        self,
        approval_id: str,
        modified_arguments: dict[str, Any],
        user_note: str = "",
    ) -> ApprovalRequest | None:
        req = self._requests.get(approval_id)
        if req is None or req.status != "pending":
            return None
        if req.is_expired():
            req.status = "expired"
            self._save()
            return None
        req.arguments = dict(modified_arguments)
        req.arguments_summary = _summarize_arguments(modified_arguments)
        req.status = "modified"
        self._save()
        if self._audit is not None:
            self._record_audit("approval_modified", req, user_note=user_note)
        return req

    def cancel(self, approval_id: str, reason: str = "") -> ApprovalRequest | None:
        req = self._requests.get(approval_id)
        if req is None or req.status not in ("pending", "approved", "modified"):
            return None
        req.status = "cancelled"
        self._save()
        if self._audit is not None:
            self._record_audit("approval_cancelled", req, reason=reason)
        return req

    def expire_old_requests(self, now_ms: int | None = None) -> int:
        return self._expire_old(now_ms)

    def mark_executed(self, approval_id: str, result: Any = None) -> None:
        req = self._requests.get(approval_id)
        if req is None:
            return
        req.status = "executed"
        self._executed.add(approval_id)
        self._save()
        if self._audit is not None:
            self._record_audit("approval_executed", req)

    def mark_failed(self, approval_id: str, error: str = "") -> None:
        req = self._requests.get(approval_id)
        if req is None:
            return
        req.status = "failed"
        self._save()
        if self._audit is not None:
            self._record_audit("approval_failed", req, reason=error)

    def is_executed(self, approval_id: str) -> bool:
        return approval_id in self._executed

    def get_all(self) -> list[ApprovalRequest]:
        return list(self._requests.values())

    def format_pending_summary(self) -> str:
        pending = self.list_pending()
        if not pending:
            return "No pending approvals."
        lines = ["Pending approvals:"]
        for r in pending:
            lines.append(f"  [{r.approval_id}] {r.tool_name or r.capability_id}")
            lines.append(f"    risk={r.risk_level} source={r.source}")
            lines.append(f"    reason: {r.approval_reason[:100]}")
            if r.source_desire:
                lines.append(f"    desire: {r.source_desire} (frust={r.frustration:.1f})")
        return "\n".join(lines)

    # ── Persistence ───────────────────────────────────────────

    def _state_path(self) -> Path:
        return self._data_dir / "approval_queue.json"

    def _save(self) -> None:
        data = {
            "requests": {aid: r.to_dict() for aid, r in self._requests.items()},
            "executed": list(self._executed),
            "saved_at": int(time.time() * 1000),
        }
        try:
            with open(self._state_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Failed to save approval queue: %s", exc)

    def _load(self) -> None:
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for aid, d in data.get("requests", {}).items():
                self._requests[aid] = ApprovalRequest(**d)
            self._executed = set(data.get("executed", []))
            logger.info("Loaded %d approval requests", len(self._requests))
        except Exception as exc:
            logger.warning("Failed to load approval queue: %s", exc)

    # ── Internal ──────────────────────────────────────────────

    def _expire_old(self, now_ms: int | None = None) -> int:
        count = 0
        for req in self._requests.values():
            if req.status == "pending" and req.is_expired(now_ms):
                req.status = "expired"
                count += 1
        if count > 0:
            self._save()
        return count

    def _record_audit(
        self,
        action: str,
        req: ApprovalRequest,
        reason: str = "",
        user_note: str = "",
    ) -> None:
        try:
            from aegis_ai.audit import AuditEntry
            entry = AuditEntry(
                action=action,
                actor=req.source,
                capability_id=req.capability_id,
                decision=req.status,
                reason=reason or req.approval_reason,
                detail={
                    "approval_id": req.approval_id,
                    "request_id": req.request_id,
                    "task_id": req.task_id,
                    "source": req.source,
                    "source_desire": req.source_desire,
                    "frustration": req.frustration,
                    "risk_level": req.risk_level,
                    "user_note": user_note,
                },
            )
            self._audit.append(entry)
        except Exception as exc:
            logger.warning("Failed to record audit: %s", exc)

    def _record_approval_memory(
        self,
        req: ApprovalRequest,
        decision: str,
        note: str = "",
    ) -> None:
        """Store approval decision as a memory record."""
        if self._memory_store is None:
            return
        try:
            from aegis_ai.memory.memory_types import (
                MemoryRecord,
                MemorySource,
                MemoryType,
                Sensitivity,
                Visibility,
            )
            title = f"Approval {decision}: {req.tool_name or req.capability_id}"
            content_parts = [
                f"Decision: {decision}",
                f"Capability: {req.capability_id}",
                f"Risk: {req.risk_level}",
                f"Reason: {req.approval_reason}",
            ]
            if note:
                content_parts.append(f"Note: {note}")
            if req.source_desire:
                content_parts.append(f"Source desire: {req.source_desire} (frust={req.frustration:.1f})")

            importance = 0.8 if decision == "rejected" else 0.6
            self._memory_store.add_memory(MemoryRecord(
                memory_type=MemoryType.APPROVAL_LESSON.value,
                title=title,
                content="\n".join(content_parts),
                source=MemorySource.APPROVAL_DECISION.value,
                related_approval_id=req.approval_id,
                related_task_id=req.task_id,
                related_desire=req.source_desire,
                structured_data={
                    "decision": decision,
                    "capability_id": req.capability_id,
                    "risk_level": req.risk_level,
                    "source": req.source,
                },
                confidence=0.9,
                importance=importance,
                visibility=Visibility.LLM_VISIBLE.value,
                sensitivity=Sensitivity.NORMAL.value,
            ))
        except Exception as exc:
            logger.warning("Failed to record approval memory: %s", exc)
