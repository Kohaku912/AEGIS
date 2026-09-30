"""Egress — the single enforcement point for AEGIS's single constraint.

The constraint, **re-scoped 2026-09-30** (owner):

    **Unpermitted** user information must never leave the local environment. Outbound
    connections are allowed, and user information may be sent externally **with the
    user's permission**.

So the rule this package *is* is a permission check, not a deny-all wall, and the gate now
implements it with **two permission paths**:

1. **Standing configuration** — master switch, per-purpose feature flag, host allowlist.
2. **A permission the user gave about a specific destination** — see
   :mod:`aegis_ai.egress.permissions`, which adapts the confirmation store. The gate
   consults it and never asks, so the retired forced gate stays retired and the
   *voluntary* ask remains the only way the question reaches the user.

A request carrying **no user information** may connect out without either path — the
constraint is about user information, not connectivity.

See ``AGENTS.md`` (Security Policy), ``docs/GOAL-CHANGE.md``, ``docs/egress-gate.md`` and
``IMPROVEMENT_PROPOSAL.md`` §9.3 Phase 1.
"""

from aegis_ai.egress.gate import (
    EgressConfigurationError,
    EgressDecision,
    EgressDenied,
    EgressGate,
    EgressRequest,
    EgressStatus,
    classify_destination,
    configure_egress_gate,
    get_egress_gate,
    is_local_destination,
)
from aegis_ai.egress.permissions import (
    EGRESS_PERMISSION_CAPABILITY,
    ConfirmationGrantSource,
    EgressPermission,
    format_scope,
    parse_scope,
)
from aegis_ai.egress.startup import verify_egress_configuration

__all__ = [
    "EGRESS_PERMISSION_CAPABILITY",
    "ConfirmationGrantSource",
    "EgressConfigurationError",
    "EgressDecision",
    "EgressDenied",
    "EgressGate",
    "EgressPermission",
    "EgressRequest",
    "EgressStatus",
    "classify_destination",
    "configure_egress_gate",
    "format_scope",
    "get_egress_gate",
    "is_local_destination",
    "parse_scope",
    "verify_egress_configuration",
]
