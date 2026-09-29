"""Egress — the single enforcement point for AEGIS's single constraint.

The only constraint in AEGIS is:

    **The user's information must never leave the local environment.**

Every outbound transmission must pass through this gate. External destinations are
denied by default, with no consent exception.

See ``AGENTS.md`` (Security Policy), ``docs/GOAL-CHANGE.md`` and
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
