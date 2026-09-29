"""Typed snapshot model for durable user understanding."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class UnderstandingItem:
    """Evidence-backed item used across horizons, deficits, and opportunities."""

    title: str
    summary: str = ""
    confidence: float = 0.0
    timestamp_ms: int = 0
    sources: list[str] = field(default_factory=list)
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class UserUnderstandingSnapshot:
    """Unified durable user understanding exposed to runtime, LLM, and UI."""

    generated_at_ms: int
    summary: str = ""
    identity_profile: dict[str, Any] = field(default_factory=dict)
    preferences: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    commitments: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    resources: list[dict[str, Any]] = field(default_factory=list)
    short_horizon: list[UnderstandingItem] = field(default_factory=list)
    medium_horizon: list[UnderstandingItem] = field(default_factory=list)
    long_horizon: list[UnderstandingItem] = field(default_factory=list)
    life_horizon: list[UnderstandingItem] = field(default_factory=list)
    likely_next_actions: list[UnderstandingItem] = field(default_factory=list)
    predicted_deficits: list[UnderstandingItem] = field(default_factory=list)
    burden_reduction_opportunities: list[UnderstandingItem] = field(default_factory=list)
    self_improvement_queue: list[UnderstandingItem] = field(default_factory=list)
    delegated_authority_state: dict[str, Any] = field(default_factory=dict)
    evidence_log: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at_ms": self.generated_at_ms,
            "summary": self.summary,
            "identity_profile": dict(self.identity_profile),
            "preferences": dict(self.preferences),
            "constraints": dict(self.constraints),
            "commitments": list(self.commitments),
            "relationships": list(self.relationships),
            "resources": list(self.resources),
            "short_horizon": [item.to_dict() for item in self.short_horizon],
            "medium_horizon": [item.to_dict() for item in self.medium_horizon],
            "long_horizon": [item.to_dict() for item in self.long_horizon],
            "life_horizon": [item.to_dict() for item in self.life_horizon],
            "likely_next_actions": [item.to_dict() for item in self.likely_next_actions],
            "predicted_deficits": [item.to_dict() for item in self.predicted_deficits],
            "burden_reduction_opportunities": [
                item.to_dict() for item in self.burden_reduction_opportunities
            ],
            "self_improvement_queue": [item.to_dict() for item in self.self_improvement_queue],
            "delegated_authority_state": dict(self.delegated_authority_state),
            "evidence_log": list(self.evidence_log),
        }

    def to_context_string(self) -> str:
        lines = []
        if self.summary:
            lines.append(f"User understanding: {self.summary}")
        if self.short_horizon:
            lines.append("Short horizon needs:")
            lines.extend(f"- {item.title}: {item.summary}" for item in self.short_horizon[:3])
        if self.likely_next_actions:
            lines.append("Likely next actions:")
            lines.extend(
                f"- {item.title}: {item.summary}" for item in self.likely_next_actions[:3]
            )
        if self.predicted_deficits:
            lines.append("Predicted deficits:")
            lines.extend(
                f"- {item.title}: {item.summary}" for item in self.predicted_deficits[:3]
            )
        authority = self.delegated_authority_state.get("summary")
        if authority:
            lines.append(f"Delegated authority: {authority}")
        return "\n".join(lines)
