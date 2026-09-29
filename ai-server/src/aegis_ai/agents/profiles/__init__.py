"""Agent profiles — declarative agent descriptions loaded from YAML.

Public API (instruction.md §8):
- `AgentProfile` — declarative profile dataclass
- `AgentRiskCeiling` / `WorkspaceKind` — enums for risk & isolation
- `AgentProfileRegistry` — YAML loader / in-memory store
- `RoutingDecision` — router return value
"""
from aegis_ai.agents.profiles.models import (
    AgentProfile,
    AgentRiskCeiling,
    RoutingDecision,
    WorkspaceKind,
)
from aegis_ai.agents.profiles.registry import AgentProfileRegistry

__all__ = [
    "AgentProfile",
    "AgentProfileRegistry",
    "AgentRiskCeiling",
    "RoutingDecision",
    "WorkspaceKind",
]
