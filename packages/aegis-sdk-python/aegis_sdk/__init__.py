"""AEGIS Plugin SDK — tools for building AEGIS capability servers.

Provides:
- define_capability: Safe capability definition helper
- RegistrationClient: Server/capability registration
- EventClient: Event publishing with structured helpers
- SafetyValidator: Capability safety validation
- MockAEGISCore: Test harness for capability servers
"""

from aegis_sdk.capability import define_capability  # noqa: F401
from aegis_sdk.events import EventClient, make_dedupe_key, make_event  # noqa: F401
from aegis_sdk.registration import RegistrationClient  # noqa: F401
from aegis_sdk.safety import (  # noqa: F401
    check_forbidden_proximity,
    validate_capability_definition,
)
from aegis_sdk.testing import (  # noqa: F401
    MockAEGISCore,
    run_capability_registration_check,
    run_event_push_check,
    run_policy_flow_check,
)
