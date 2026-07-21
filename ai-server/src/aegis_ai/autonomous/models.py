"""Policy-aware autonomous action models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class CapabilityDisposition(StrEnum):
    """How autonomy may use a capability before execution."""

    EXECUTE_SAFE = "execute_safe"
    PROPOSE_FOR_APPROVAL = "propose_for_approval"
    ASK_USER = "ask_user"
    DEFER = "defer"
    FORBIDDEN = "forbidden"
    UNAVAILABLE = "unavailable"


class ActionLifecycleState(StrEnum):
    """Durable lifecycle of a selected autonomous action."""

    SELECTED = "selected"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    FAILED = "failed"


class InitiativeDecision(StrEnum):
    EXECUTE_NOW = "execute_now"
    PROPOSE_APPROVAL = "propose_approval"
    ASK_USER = "ask_user"
    SAVE_FOR_LATER = "save_for_later"
    OBSERVE_MORE = "observe_more"
    IGNORE_WITH_REASON = "ignore_with_reason"


@dataclass(frozen=True)
class AutonomousCapabilityOption:
    capability_id: str
    disposition: CapabilityDisposition
    policy_decision: str
    policy_reason: str
    risk_level: str
    requires_approval: bool
    enabled: bool = True
    available: bool = True
    server_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["disposition"] = self.disposition.value
        return data


@dataclass
class ActionCandidate:
    """A reasoned candidate considered by the Initiative Engine."""

    candidate_id: str
    goal: str
    why_now: str
    trigger: str
    related_task: str = ""
    related_person: str = ""
    related_conversation: str = ""
    expected_benefit: float = 0.0
    commitment_value: float = 0.0
    social_obligation: float = 0.0
    urgency: float = 0.0
    relevance: float = 0.0
    novelty: float = 0.0
    curiosity_value: float = 0.0
    continuity_value: float = 0.0
    risk: float = 0.0
    uncertainty: float = 0.0
    interruption_cost: float = 0.0
    repetition: float = 0.0
    token_cost: float = 0.0
    candidate_capabilities: list[str] = field(default_factory=list)
    visibility: str = "agent_private"
    requires_approval: bool = False
    success_condition: dict[str, Any] = field(default_factory=dict)
    stop_condition: dict[str, Any] = field(default_factory=dict)
    continuation: dict[str, Any] = field(default_factory=dict)

    @property
    def initiative_score(self) -> float:
        positive = (
            self.expected_benefit
            + self.commitment_value
            + self.social_obligation
            + self.urgency
            + self.relevance
            + self.novelty
            + self.curiosity_value
            + self.continuity_value
        )
        negative = self.risk + self.uncertainty + self.interruption_cost + self.repetition + self.token_cost
        return positive - negative

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
