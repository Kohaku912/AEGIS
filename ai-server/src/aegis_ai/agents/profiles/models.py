"""Agent profile models — Phase 5 (instruction.md §21, §36).

`AgentProfile` is the declarative description of an agent's capabilities,
risk ceiling, workspace kind, and LLM settings. The `AgentProfileRegistry`
loads these from `config/agent_profiles.yaml`; the `AgentRouter`
(in `aegis_ai/agents/runtime/router.py`) selects one based on
`AgentTask.profile` (or heuristics).

These types MUST NOT import any external SDK (OpenHands etc.) — they are
plain AEGIS-side dataclasses that flow across the agent boundary only via
the `AgentTask` / `AgentResult` payloads defined in
`aegis_ai/agents/runtime/models.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRiskCeiling(str, Enum):
    """Allowed upper bound for capability risk on an AgentProfile.

    Values match `instruction.md §21`:
    - ``READ_ONLY``         — read-only files / search, no writes, no approval
    - ``SAFE_ACTION``       — non-destructive actions, no approval
    - ``APPROVAL_REQUIRED`` — write-class actions, each needs user approval
    - ``HIGH_RISK``         — destructive / external actions, explicit
                              approval + audit
    """

    READ_ONLY = "read_only"
    SAFE_ACTION = "safe_action"
    APPROVAL_REQUIRED = "approval_required"
    HIGH_RISK = "high_risk"

    @classmethod
    def parse(cls, value: Any) -> AgentRiskCeiling:
        """Coerce string / enum input into ``AgentRiskCeiling``.

        Accepts the enum value (case-insensitive) or a member. Unknown values
        raise ``ValueError`` so misconfigured YAML fails loudly at load time.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            norm = value.strip().lower()
            for member in cls:
                if member.value == norm:
                    return member
        raise ValueError(f"Unknown AgentRiskCeiling: {value!r}")


class WorkspaceKind(str, Enum):
    """Workspace isolation level for an AgentProfile.

    Mirrors `WorkspaceSpec.kind` from `aegis_ai/agents/backends/openhands/config.py`:
    - ``READ_ONLY``  — read-only mount, no writes
    - ``ISOLATED``   — sandbox copy, can be modified
    - ``PERSISTENT`` — write directly to a persistent directory
    """

    READ_ONLY = "read_only"
    ISOLATED = "isolated"
    PERSISTENT = "persistent"

    @classmethod
    def parse(cls, value: Any) -> WorkspaceKind:
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            norm = value.strip().lower()
            for member in cls:
                if member.value == norm:
                    return member
        raise ValueError(f"Unknown WorkspaceKind: {value!r}")


@dataclass
class AgentProfile:
    """A single named agent profile (instruction.md §21).

    Attributes:
        id: Stable identifier (e.g. ``"coding"``, ``"research"``).
        backend: Backend name registered in `aegis_ai.agents.backends`
            (e.g. ``"openhands"``, ``"local"``).
        llm_profile_name: Name of an `llm.yaml` profile (e.g.
            ``"tool_planning"``). Resolved by `LLMSettingsResolver` at use
            time, not at load time.
        tools: Tool identifiers exposed to the agent
            (e.g. ``["filesystem", "terminal", "git", "github"]``).
        max_runtime_sec: Hard upper bound for one task (seconds).
        max_iterations: Upper bound on agent internal iterations per task.
        risk_ceiling: Maximum `RiskCategory` of capabilities this profile
            may invoke. Higher = needs more approval.
        workspace_kind: Whether the agent gets read-only / isolated /
            persistent workspace.
        allowed_capabilities: Capability IDs the profile may call. Empty
            means "use risk_ceiling + CapabilityCatalog to decide".
        denied_capabilities: Capability IDs explicitly denied for this
            profile (deny takes precedence over allow).
        requires_approval_for: Capability IDs that always need explicit
            user approval even if the risk_ceiling would allow them.
        cost_budget_usd: Optional per-task USD cost ceiling. None = no
            per-task limit (subject to global `CostTracker`).
        description: Human-readable summary for UI / logs.
        metadata: Free-form metadata (version, owner, etc.).
    """

    id: str
    backend: str
    llm_profile_name: str
    tools: list[str] = field(default_factory=list)
    max_runtime_sec: int = 1800
    max_iterations: int = 100
    risk_ceiling: AgentRiskCeiling = AgentRiskCeiling.APPROVAL_REQUIRED
    workspace_kind: WorkspaceKind = WorkspaceKind.ISOLATED
    allowed_capabilities: list[str] = field(default_factory=list)
    denied_capabilities: list[str] = field(default_factory=list)
    requires_approval_for: list[str] = field(default_factory=list)
    cost_budget_usd: float | None = None
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def allows_capability(self, capability_id: str) -> bool:
        """Return True if this profile permits calling ``capability_id``.

        Order of evaluation:
        1. ``denied_capabilities`` wins (always False).
        2. If ``allowed_capabilities`` is non-empty, require explicit match.
        3. Otherwise, allow.
        """
        if capability_id in self.denied_capabilities:
            return False
        if self.allowed_capabilities:
            return capability_id in self.allowed_capabilities
        return True

    def requires_approval(self, capability_id: str) -> bool:
        """Return True if ``capability_id`` is in ``requires_approval_for``."""
        return capability_id in self.requires_approval_for

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-friendly dict (for audit / logging)."""
        return {
            "id": self.id,
            "backend": self.backend,
            "llm_profile_name": self.llm_profile_name,
            "tools": list(self.tools),
            "max_runtime_sec": self.max_runtime_sec,
            "max_iterations": self.max_iterations,
            "risk_ceiling": self.risk_ceiling.value,
            "workspace_kind": self.workspace_kind.value,
            "allowed_capabilities": list(self.allowed_capabilities),
            "denied_capabilities": list(self.denied_capabilities),
            "requires_approval_for": list(self.requires_approval_for),
            "cost_budget_usd": self.cost_budget_usd,
            "description": self.description,
            "metadata": dict(self.metadata),
        }


@dataclass
class RoutingDecision:
    """Result of `AgentRouter.select()` (instruction.md §22).

    Attributes:
        profile: The selected `AgentProfile`. Never None — falls back to
            ``"general"`` when the requested profile is missing.
        requested_id: The profile id that was requested (may equal
            ``profile.id`` for direct lookup, or differ when fallback fired).
        fell_back: True when ``requested_id`` did not exist in the registry
            and ``profile`` is the fallback.
        reason: Human-readable rationale for the decision (used in audit).
        backend: Backend name resolved from the profile
            (e.g. ``"openhands"``). For convenience; also ``profile.backend``.
    """

    profile: AgentProfile
    requested_id: str
    fell_back: bool
    reason: str
    backend: str = ""

    def __post_init__(self) -> None:
        if not self.backend:
            self.backend = self.profile.backend


__all__ = [
    "AgentProfile",
    "AgentRiskCeiling",
    "WorkspaceKind",
    "RoutingDecision",
]
