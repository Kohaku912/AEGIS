"""Approval types — data structures for the approval queue."""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    EXECUTED = "executed"
    FAILED = "failed"


class DecisionType(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY_AND_APPROVE = "modify_and_approve"
    CANCEL = "cancel"


_SENSITIVE_KEYS = {"key", "token", "password", "secret", "cookie", "auth", "credential"}
_SENSITIVE_PATTERNS = [
    (re.compile(r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+", re.IGNORECASE), r"\1=***"),
    (re.compile(r"Bearer\s+\S+", re.IGNORECASE), "Bearer ***"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "sk-***"),
]


def _mask_value(key: str, value: Any) -> Any:
    if any(s in key.lower() for s in _SENSITIVE_KEYS):
        return "***MASKED***"
    if isinstance(value, str):
        for pat, repl in _SENSITIVE_PATTERNS:
            value = pat.sub(repl, value)
    return value


def _mask_arguments(args: dict[str, Any]) -> dict[str, Any]:
    return {k: _mask_value(k, v) for k, v in args.items()}


def _summarize_arguments(args: dict[str, Any], max_len: int = 300) -> str:
    masked = _mask_arguments(args)
    s = str(masked)
    return s[:max_len] + "..." if len(s) > max_len else s


def _generate_user_facing_summary(
    capability_id: str,
    tool_name: str,
    arguments: dict[str, Any],
    approval_reason: str,
    source_desire: str = "",
    frustration: float = 0.0,
) -> str:
    parts = [f"操作: {tool_name or capability_id}"]
    if approval_reason:
        parts.append(f"理由: {approval_reason}")
    arg_summary = _summarize_arguments(arguments, 150)
    if arg_summary and arg_summary != "{}":
        parts.append(f"引数: {arg_summary}")
    if source_desire:
        parts.append(f"欲求: {source_desire} (frustration={frustration:.1f})")
    return "\n".join(parts)


# Expiry by risk level (ms)
_EXPIRY_BY_RISK: dict[str, int] = {
    "low": 3_600_000,       # 1 hour
    "medium": 1_800_000,    # 30 min
    "high": 600_000,        # 10 min
    "critical": 300_000,    # 5 min
}


def compute_args_hash(arguments: dict[str, Any]) -> str:
    """Compute SHA-256 hash of tool arguments for tamper detection."""
    canonical = json.dumps(arguments, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class ApprovalRequest:
    approval_id: str = ""
    request_id: str = ""
    task_id: str = ""
    step_id: str = ""
    source: str = ""
    source_desire: str = ""
    frustration: float = 0.0
    capability_id: str = ""
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    arguments_summary: str = ""
    tool_args_hash: str = ""
    resume_token: str = ""
    created_from: str = ""
    risk_level: str = ""
    policy_decision: str = ""
    approval_reason: str = ""
    user_facing_summary: str = ""
    expected_outcome: str = ""
    possible_side_effects: str = ""
    created_at: int = 0
    expires_at: int = 0
    status: str = "pending"
    surface_delivery: dict[str, bool] = field(default_factory=dict)
    surface_decisions: dict[str, dict[str, Any]] = field(default_factory=dict)
    approved_by_surface: str = ""

    def is_expired(self, now_ms: int | None = None) -> bool:
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        return self.expires_at > 0 and now > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "request_id": self.request_id,
            "task_id": self.task_id,
            "step_id": self.step_id,
            "source": self.source,
            "source_desire": self.source_desire,
            "frustration": self.frustration,
            "capability_id": self.capability_id,
            "tool_name": self.tool_name,
            "arguments_summary": self.arguments_summary,
            "tool_args_hash": self.tool_args_hash,
            "resume_token": self.resume_token,
            "created_from": self.created_from,
            "risk_level": self.risk_level,
            "policy_decision": self.policy_decision,
            "approval_reason": self.approval_reason,
            "user_facing_summary": self.user_facing_summary,
            "expected_outcome": self.expected_outcome,
            "possible_side_effects": self.possible_side_effects,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "status": self.status,
            "surface_delivery": self.surface_delivery,
            "surface_decisions": self.surface_decisions,
            "approved_by_surface": self.approved_by_surface,
        }


@dataclass
class ApprovalDecision:
    approval_id: str = ""
    decision: DecisionType = DecisionType.APPROVE
    modified_arguments: dict[str, Any] | None = None
    user_note: str = ""
    decided_at: int = 0
    decided_by: str = "user"
    reason: str = ""
