# aegis_schema — Shared type definitions for AEGIS's capability protocol
#
# These Pydantic models mirror the protobuf definitions in protos/aegis/
# and serve as the Python runtime representation of the shared schema.
#
# All models support:
#   - JSON serialization via .model_dump_json()
#   - JSON Schema generation via .model_json_schema()
#   - Strict validation on construction

from aegis_schema.models import (
    RiskLevel,
    ServerType,
    ServerStatus,
    EventPriority,
    Parameter,
    Capability,
    Tool,
    ServerInfo,
    ApprovalRequirement,
    Event,
    Status,
)
from aegis_schema.validation import (
    validate_capability,
    validate_capabilities_batch,
    validate_capability_json,
    ValidationResult,
)

__all__ = [
    # Enums
    "RiskLevel",
    "ServerType",
    "ServerStatus",
    "EventPriority",
    # Models
    "Parameter",
    "Capability",
    "Tool",
    "ServerInfo",
    "ApprovalRequirement",
    "Event",
    "Status",
    # Validation
    "validate_capability",
    "validate_capabilities_batch",
    "validate_capability_json",
    "ValidationResult",
]
