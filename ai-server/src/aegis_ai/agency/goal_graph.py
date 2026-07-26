"""Outcome-first goal graph shared by planning, execution, and presentation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class VerificationStatus(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class GoalOutcome:
    """The user-visible state a goal is intended to produce."""

    description: str = ""
    success_condition: str = ""
    value_to_user: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoalOutcome:
        return cls(
            description=str(data.get("description") or ""),
            success_condition=str(data.get("success_condition") or ""),
            value_to_user=str(data.get("value_to_user") or ""),
        )


@dataclass
class GoalVerification:
    """One observable criterion for goal completion."""

    verification_id: str
    criterion: str
    linked_step_ids: list[str] = field(default_factory=list)
    status: VerificationStatus = VerificationStatus.PENDING
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_id": self.verification_id,
            "criterion": self.criterion,
            "linked_step_ids": list(self.linked_step_ids),
            "status": self.status.value,
            "evidence": list(self.evidence),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoalVerification:
        try:
            status = VerificationStatus(str(data.get("status") or "pending"))
        except ValueError:
            status = VerificationStatus.PENDING
        return cls(
            verification_id=str(data.get("verification_id") or ""),
            criterion=str(data.get("criterion") or ""),
            linked_step_ids=[str(item) for item in data.get("linked_step_ids", [])],
            status=status,
            evidence=[str(item) for item in data.get("evidence", [])],
        )


@dataclass
class GoalGraph:
    """Connects outcome, obligations, execution, verification, and reporting."""

    goal_id: str = ""
    outcome: GoalOutcome = field(default_factory=GoalOutcome)
    source: str = "user"
    priority: int = 0
    obligation_ids: list[str] = field(default_factory=list)
    verification: list[GoalVerification] = field(default_factory=list)
    presentation: dict[str, Any] = field(default_factory=lambda: {"report_when": "terminal", "audience": "user"})
    stop_conditions: list[str] = field(default_factory=list)

    def is_verified(self) -> bool:
        """Return true only when every criterion has passed."""
        return bool(self.verification) and all(item.status == VerificationStatus.PASSED for item in self.verification)

    def sync_step_evidence(self, steps: list[Any]) -> None:
        """Update linked criteria from terminal step evidence."""
        by_id = {str(getattr(step, "step_id", "")): step for step in steps}
        for check in self.verification:
            if not check.linked_step_ids:
                continue
            linked = [by_id.get(step_id) for step_id in check.linked_step_ids]
            if any(step is None for step in linked):
                continue
            names = {str(getattr(getattr(step, "status", None), "name", "")).lower() for step in linked}
            if "failed" in names or "blocked" in names:
                check.status = VerificationStatus.FAILED
                check.evidence = ["A linked execution step failed."]
            elif names and names.issubset({"completed", "skipped"}):
                check.status = VerificationStatus.PASSED
                check.evidence = [f"step:{getattr(step, 'step_id', '')}" for step in linked if step is not None]

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "outcome": self.outcome.to_dict(),
            "source": self.source,
            "priority": self.priority,
            "obligation_ids": list(self.obligation_ids),
            "verification": [item.to_dict() for item in self.verification],
            "presentation": dict(self.presentation),
            "stop_conditions": list(self.stop_conditions),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoalGraph:
        return cls(
            goal_id=str(data.get("goal_id") or ""),
            outcome=GoalOutcome.from_dict(dict(data.get("outcome") or {})),
            source=str(data.get("source") or "user"),
            priority=int(data.get("priority") or 0),
            obligation_ids=[str(item) for item in data.get("obligation_ids", [])],
            verification=[
                GoalVerification.from_dict(item) for item in data.get("verification", []) if isinstance(item, dict)
            ],
            presentation=dict(data.get("presentation") or {}),
            stop_conditions=[str(item) for item in data.get("stop_conditions", [])],
        )
