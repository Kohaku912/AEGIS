"""Approval System — manages user approval for dangerous operations.

This module provides:
- ApprovalRequest: A pending approval that the user must act on
- ApprovalStore: In-memory store for creating, approving, rejecting, and expiring requests
- ApprovalType: Kinds of approval (one_time, session, permanent — permanent is forbidden)

Architecture reference: docs/architecture.md §7.4
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto


# ═══════════════════════════════════════════════════════════════
# Approval Type
# ═══════════════════════════════════════════════════════════════

class ApprovalType(Enum):
    """The scope of an approval grant."""
    ONE_TIME = auto()     # Valid for a single execution only
    SESSION = auto()      # Valid for the duration of a user session
    # PERMANENT is intentionally absent — nothing is permanently auto-approved


class ApprovalStatus(Enum):
    """Current state of an approval request."""
    PENDING = auto()      # Waiting for user decision
    APPROVED = auto()     # User granted approval
    REJECTED = auto()     # User denied approval
    EXPIRED = auto()      # Timed out before user responded


# ═══════════════════════════════════════════════════════════════
# Approval Request
# ═══════════════════════════════════════════════════════════════

@dataclass
class ApprovalRequest:
    """A request for user approval before executing a dangerous capability.

    Created by the PolicyEngine when a capability requires approval.
    Presented to the user via the Approval UI.
    """

    approval_id: str = ""                           # Unique ID
    capability_id: str = ""                         # Which capability needs approval
    tool_name: str = ""                             # Human-readable tool name
    requested_action: str = ""                      # What is being requested
    human_readable_summary: str = ""                # Plain-language explanation
    risk_explanation: str = ""                      # Why this is risky
    payload_preview: str = ""                       # Preview of the parameters (truncated)
    risk_level: int = 0                             # Numeric risk level (1–5)
    created_at_ms: int = 0                          # When the request was created
    expires_at_ms: int = 0                          # When the request auto-expires
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_type: ApprovalType | None = None       # Set when approved

    def is_expired(self) -> bool:
        """Check if this request has expired (pending too long)."""
        if self.status != ApprovalStatus.PENDING:
            return False
        now_ms = int(time.time() * 1000)
        return self.expires_at_ms > 0 and now_ms > self.expires_at_ms

    def is_valid_approval(self) -> bool:
        """Check if this approval is currently valid for execution."""
        if self.status != ApprovalStatus.APPROVED:
            return False
        if self.approved_type == ApprovalType.ONE_TIME:
            return True  # Valid until consumed
        if self.approved_type == ApprovalType.SESSION:
            # SESSION approvals expire after configurable time
            # Checked by ApprovalStore
            return True
        return False


# ═══════════════════════════════════════════════════════════════
# Approval Store
# ═══════════════════════════════════════════════════════════════

class ApprovalStore:
    """In-memory store for approval requests.

    Manages the lifecycle:
    1. PolicyEngine creates an ApprovalRequest → status=PENDING
    2. User approves → status=APPROVED
    3. ToolBroker checks for valid approval before executing
    4. Expired/consumed approvals are cleaned up

    Usage:
        store = ApprovalStore()
        req = store.create_request(capability_id="room.ir_send", ...)
        # ... present to user ...
        store.approve(req.approval_id, ApprovalType.ONE_TIME)
        # ... ToolBroker checks ...
        store.is_approved("room.ir_send")  # True
    """

    # Default expiry times (milliseconds)
    DEFAULT_REQUEST_TIMEOUT_MS = 60_000       # 1 minute for user to respond
    DEFAULT_APPROVAL_VALIDITY_MS = 300_000    # 5 minutes for approved operations
    DEFAULT_SESSION_VALIDITY_MS = 3_600_000   # 1 hour for session approvals

    def __init__(
        self,
        request_timeout_ms: int = DEFAULT_REQUEST_TIMEOUT_MS,
        approval_validity_ms: int = DEFAULT_APPROVAL_VALIDITY_MS,
        session_validity_ms: int = DEFAULT_SESSION_VALIDITY_MS,
    ) -> None:
        self._request_timeout_ms = request_timeout_ms
        self._approval_validity_ms = approval_validity_ms
        self._session_validity_ms = session_validity_ms

        self._requests: dict[str, ApprovalRequest] = {}
        # Track consumed one-time approvals: approval_id → consumption timestamp
        self._consumed: set[str] = set()

    # ── Create ──────────────────────────────────────────────

    def create_request(
        self,
        capability_id: str,
        tool_name: str = "",
        requested_action: str = "",
        human_readable_summary: str = "",
        risk_explanation: str = "",
        payload_preview: str = "",
        risk_level: int = 3,
    ) -> ApprovalRequest:
        """Create a new approval request. Returns the request for UI presentation."""
        now_ms = int(time.time() * 1000)
        req = ApprovalRequest(
            approval_id=f"approval_{uuid.uuid4().hex[:8]}",
            capability_id=capability_id,
            tool_name=tool_name,
            requested_action=requested_action,
            human_readable_summary=human_readable_summary,
            risk_explanation=risk_explanation,
            payload_preview=payload_preview,
            risk_level=risk_level,
            created_at_ms=now_ms,
            expires_at_ms=now_ms + self._request_timeout_ms,
            status=ApprovalStatus.PENDING,
        )
        self._requests[req.approval_id] = req
        return req

    # ── Approve / Reject ────────────────────────────────────

    def approve(self, approval_id: str, approval_type: ApprovalType = ApprovalType.ONE_TIME) -> bool:
        """Approve a pending request. Returns True if successful."""
        req = self._requests.get(approval_id)
        if req is None or req.status != ApprovalStatus.PENDING:
            return False
        if req.is_expired():
            req.status = ApprovalStatus.EXPIRED
            return False

        req.status = ApprovalStatus.APPROVED
        req.approved_type = approval_type
        return True

    def reject(self, approval_id: str) -> bool:
        """Reject a pending request. Returns True if successful."""
        req = self._requests.get(approval_id)
        if req is None or req.status != ApprovalStatus.PENDING:
            return False

        req.status = ApprovalStatus.REJECTED
        return True

    # ── Query ───────────────────────────────────────────────

    def is_approved(self, capability_id: str) -> bool:
        """Check if there is a valid (non-expired, non-consumed) approval for a capability."""
        self._expire_old()

        for req in self._requests.values():
            if req.capability_id != capability_id:
                continue
            if not req.is_valid_approval():
                continue
            if req.approval_id in self._consumed:
                continue

            # Check session expiry
            if req.approved_type == ApprovalType.SESSION:
                now_ms = int(time.time() * 1000)
                if now_ms > req.created_at_ms + self._session_validity_ms:
                    continue

            return True

        return False

    def consume_approval(self, capability_id: str) -> ApprovalRequest | None:
        """Find and consume a valid one-time approval. Returns the request or None."""
        self._expire_old()

        for req in self._requests.values():
            if req.capability_id != capability_id:
                continue
            if not req.is_valid_approval():
                continue
            if req.approval_id in self._consumed:
                continue

            # Session approvals are not consumed
            if req.approved_type == ApprovalType.ONE_TIME:
                self._consumed.add(req.approval_id)
                return req
            elif req.approved_type == ApprovalType.SESSION:
                return req  # Not consumed, can be reused

        return None

    def get_pending_requests(self) -> list[ApprovalRequest]:
        """Get all currently pending (non-expired) approval requests."""
        self._expire_old()
        return [
            req for req in self._requests.values()
            if req.status == ApprovalStatus.PENDING and not req.is_expired()
        ]

    def get_request(self, approval_id: str) -> ApprovalRequest | None:
        """Get a request by ID."""
        return self._requests.get(approval_id)

    def get_approved_capabilities(self) -> set[str]:
        """Get the set of capability IDs that currently have valid approval."""
        self._expire_old()
        approved: set[str] = set()
        for req in self._requests.values():
            if req.is_valid_approval() and req.approval_id not in self._consumed:
                approved.add(req.capability_id)
        return approved

    # ── Expiry ──────────────────────────────────────────────

    def expire_old_requests(self) -> int:
        """Expire pending requests past their timeout. Returns count of expired."""
        return self._expire_old()

    def clear(self) -> None:
        """Clear all requests (for testing)."""
        self._requests.clear()
        self._consumed.clear()

    # ── Internal ────────────────────────────────────────────

    def _expire_old(self) -> int:
        """Mark expired pending requests as EXPIRED. Returns count."""
        count = 0
        for req in self._requests.values():
            if req.status == ApprovalStatus.PENDING and req.is_expired():
                req.status = ApprovalStatus.EXPIRED
                count += 1
        return count
