"""Approval Queue — user approval flow for dangerous operations."""

from aegis_ai.approval.approval_manager import ApprovalManager
from aegis_ai.approval.approval_queue import ApprovalQueue
from aegis_ai.approval.approval_types import (
    ApprovalDecision,
    DecisionType,
)
from aegis_ai.approval.approval_types import (
    ApprovalRequest as QueueApprovalRequest,
)
from aegis_ai.approval.approval_types import (
    ApprovalStatus as QueueApprovalStatus,
)

# Re-export legacy types from src/approval.py for backward compatibility
from approval import ApprovalRequest, ApprovalStatus, ApprovalStore, ApprovalType  # noqa: F401

__all__ = [
    "ApprovalDecision",
    "ApprovalManager",
    "ApprovalQueue",
    "ApprovalRequest",
    "ApprovalStatus",
    "ApprovalStore",
    "ApprovalType",
    "DecisionType",
    "QueueApprovalRequest",
    "QueueApprovalStatus",
]
