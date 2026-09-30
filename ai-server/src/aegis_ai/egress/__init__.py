"""Egress — the single enforcement point for AEGIS's single constraint.

The constraint, **re-scoped 2026-09-30** (owner):

    **Unpermitted** user information must never leave the local environment. Outbound
    connections are allowed, and user information may be sent externally **with the
    user's permission**.

So the rule this package is *for* is a permission check, not a deny-all wall.

⚠️ **The code below still implements the pre-re-scope deny-all rule.** "No consent
exception" is the current behaviour, not the re-scoped intent. Making the gate
permission-aware — while keeping the forced-approval gate retired and letting the
*voluntary* ask carry the constraint — is open work. Until it lands, this docstring must
not be read as describing a mechanism that already exists.

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
from aegis_ai.egress.startup import verify_egress_configuration

__all__ = [
    "EgressConfigurationError",
    "EgressDecision",
    "EgressDenied",
    "EgressGate",
    "EgressRequest",
    "EgressStatus",
    "classify_destination",
    "configure_egress_gate",
    "get_egress_gate",
    "is_local_destination",
    "verify_egress_configuration",
]
