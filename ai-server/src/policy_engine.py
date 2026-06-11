"""Policy Engine — deterministic safety enforcement for all tool invocations.

NOT an LLM. NOT configurable by prompt. This is a structural safety gate that:
1. Classifies every action as ALLOW / ASK_APPROVAL / DENY
2. Uses RiskLevel from the capability schema
3. Supports custom rules for specific capabilities
4. Cannot be bypassed by any code path in ToolBroker

Architecture reference: docs/architecture.md §5.9, §7
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

from ellie_schema.models import Capability, RiskLevel


class PolicyDecision(Enum):
    """Outcome of a policy evaluation."""
    ALLOW = auto()           # Execute immediately
    ASK_APPROVAL = auto()    # Must present Approval UI to user
    DENY = auto()            # Blocked — never execute


@dataclass
class PolicyResult:
    """Result of evaluating a capability against the policy."""
    decision: PolicyDecision
    reason: str = ""
    capability_id: str = ""
    risk_level: RiskLevel = RiskLevel.UNSPECIFIED


# Type alias for custom rules
RuleFunc = Callable[[Capability, dict[str, Any]], PolicyResult | None]
# A rule returns:
#   PolicyResult — decision made, stop evaluation
#   None — rule doesn't apply, continue to next rule


class PolicyEngine:
    """Deterministic safety rules engine.

    Architecture constraint (§7.3):
    - NOT an LLM prompt
    - Deterministic rules only
    - Fail-closed: unreachable PolicyEngine = all DENY
    - Every decision logged (Audit Log integration point)

    Usage:
        engine = PolicyEngine()
        result = engine.evaluate(capability, params)
        if result.decision == PolicyDecision.ALLOW:
            execute(capability, params)
        elif result.decision == PolicyDecision.ASK_APPROVAL:
            show_approval_ui(capability, result.reason)
        else:
            raise ToolDeniedError(result.reason)
    """

    # Default risk-level → decision mapping
    # This can be overridden per-capability by add_rule()
    DEFAULT_RISK_MAP: dict[RiskLevel, PolicyDecision] = {
        RiskLevel.UNSPECIFIED:  PolicyDecision.DENY,
        RiskLevel.READ_ONLY:    PolicyDecision.ALLOW,
        RiskLevel.SAFE_ACTION:  PolicyDecision.ALLOW,
        RiskLevel.APPROVAL_REQUIRED: PolicyDecision.ASK_APPROVAL,
        RiskLevel.HIGH_RISK:    PolicyDecision.ASK_APPROVAL,
        RiskLevel.FORBIDDEN:    PolicyDecision.DENY,
    }

    def __init__(self) -> None:
        self._rules: dict[str, list[RuleFunc]] = {}        # per-capability rules
        self._global_rules: list[RuleFunc] = []             # rules for all capabilities
        self._blocked_ids: set[str] = set()                 # permanently blocked capabilities
        self._blocked_patterns: list[re.Pattern] = []       # blocked ID patterns
        self._risk_overrides: dict[str, RiskLevel] = {}     # capability → risk override

    # ── Public API ──────────────────────────────────────────

    def evaluate(
        self,
        capability: Capability,
        params: dict[str, Any] | None = None,
    ) -> PolicyResult:
        """Evaluate whether a capability invocation is allowed.

        Args:
            capability: The capability being invoked.
            params: Optional parameters for the invocation.

        Returns:
            PolicyResult with decision and reason.
        """
        params = params or {}
        cap_id = capability.id

        # 1. Check permanently blocked
        if cap_id in self._blocked_ids:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Capability '{cap_id}' is permanently blocked.",
                capability_id=cap_id,
                risk_level=capability.risk_level,
            )

        # 2. Check blocked patterns
        for pattern in self._blocked_patterns:
            if pattern.match(cap_id):
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"Capability '{cap_id}' matches blocked pattern '{pattern.pattern}'.",
                    capability_id=cap_id,
                    risk_level=capability.risk_level,
                )

        # 3. Check per-capability custom rules first
        for rule in self._rules.get(cap_id, []):
            result = rule(capability, params)
            if result is not None:
                return result

        # 4. Check global custom rules
        for rule in self._global_rules:
            result = rule(capability, params)
            if result is not None:
                return result

        # 5. Fall back to risk-level-based decision
        effective_risk = self._risk_overrides.get(cap_id, capability.risk_level)
        decision = self.DEFAULT_RISK_MAP.get(effective_risk, PolicyDecision.DENY)

        reason_map = {
            PolicyDecision.ALLOW: f"Risk level {effective_risk.name} — allowed.",
            PolicyDecision.ASK_APPROVAL: (
                f"Risk level {effective_risk.name} — requires user approval "
                f"before executing '{cap_id}'."
            ),
            PolicyDecision.DENY: (
                f"Risk level {effective_risk.name} — '{cap_id}' is denied."
            ),
        }

        return PolicyResult(
            decision=decision,
            reason=reason_map.get(decision, "No reason provided."),
            capability_id=cap_id,
            risk_level=effective_risk,
        )

    # ── Configuration API ───────────────────────────────────

    def block_capability(self, capability_id: str) -> None:
        """Permanently block a capability by ID. Cannot be unblocked at runtime."""
        self._blocked_ids.add(capability_id)

    def block_pattern(self, pattern: str) -> None:
        """Block all capabilities whose ID matches a regex pattern."""
        self._blocked_patterns.append(re.compile(pattern))

    def set_risk_override(self, capability_id: str, risk_level: RiskLevel) -> None:
        """Override the risk level for a specific capability.

        Use with caution. Raising risk is safe; lowering risk requires
        architectural review (per AGENTS.md security policy).
        """
        if risk_level < RiskLevel.READ_ONLY:
            raise ValueError("Cannot override to UNSPECIFIED risk level")
        self._risk_overrides[capability_id] = risk_level

    def add_rule(self, capability_id: str, rule: RuleFunc) -> None:
        """Add a custom rule for a specific capability.

        Rules are evaluated in order. First rule returning a non-None
        PolicyResult wins.
        """
        if capability_id not in self._rules:
            self._rules[capability_id] = []
        self._rules[capability_id].append(rule)

    def add_global_rule(self, rule: RuleFunc) -> None:
        """Add a custom rule that applies to ALL capabilities."""
        self._global_rules.append(rule)


# ── Convenience: create a default PolicyEngine with sensible defaults ────────

def create_default_policy_engine() -> PolicyEngine:
    """Create a PolicyEngine with default safety rules.

    Blocks obviously dangerous patterns:
    - *.delete_all — batch deletion
    - *.rm_* — remove operations
    - *.purchase — purchases
    - *.send_sns — SNS posting
    """
    engine = PolicyEngine()

    # Block dangerous ID patterns by default
    engine.block_pattern(r".*\.delete_all$")
    engine.block_pattern(r".*\.rm_.*")
    engine.block_pattern(r".*\.purchase.*")
    engine.block_pattern(r".*\.send_sns$")

    return engine
