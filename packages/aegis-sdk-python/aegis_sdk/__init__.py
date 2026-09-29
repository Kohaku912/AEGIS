"""AEGIS Plugin SDK — tools for building AEGIS capability servers.

Provides:
- define_capability: Safe capability definition helper
- ALLOWED_SERVER_PREFIXES / SERVER_TYPE_BY_PREFIX: the id space, derived from the roster
- RegistrationClient: Server/capability registration
- EventClient: Event publishing with structured helpers
- SafetyValidator: Capability safety validation
- MockAEGISCore: Test harness for capability servers

A capability id is namespaced by the AEGIS server that hosts it, so ``server_prefix`` must be
one of ``ALLOWED_SERVER_PREFIXES``; a prefix of your own is refused by name. Your own namespace
goes in the segments after the first (``server_prefix="room-server"`` + ``action="myapp.thing"``).
"""

from aegis_sdk.capability import define_capability  # noqa: F401
from aegis_sdk.events import EventClient, make_dedupe_key, make_event  # noqa: F401
from aegis_sdk.registration import RegistrationClient  # noqa: F401
from aegis_sdk.safety import (  # noqa: F401
    ALLOWED_SERVER_PREFIXES,
    SERVER_TYPE_BY_PREFIX,
    check_forbidden_proximity,
    validate_capability_definition,
)
from aegis_sdk.testing import (  # noqa: F401
    MockAEGISCore,
    run_capability_registration_check,
    run_event_push_check,
    run_policy_flow_check,
)
