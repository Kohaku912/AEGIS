# aegis_schema — Shared type definitions for AEGIS's capability protocol
#
# These Pydantic models mirror the protobuf definitions in protos/aegis/
# and serve as the Python runtime representation of the shared schema.
#
# All models support:
#   - JSON serialization via .model_dump_json()
#   - JSON Schema generation via .model_json_schema()
#   - Strict validation on construction
#
# This package used to also export a validator (``validation.py``:
# ``validate_capability`` / ``validate_capabilities_batch`` /
# ``validate_capability_json`` / ``ValidationResult``). It was deleted on
# 2026-09-29: it had no caller, no test, and no external consumer, and run
# over all 128 live capabilities it reported **zero** errors. See
# ``tests/test_schema_validator_stays_retired.py`` for the evidence, and
# ``tests/test_manifest_schemas.py`` for the checks that own this job.
#
# ``ApprovalRequirement`` was deleted on 2026-09-29 as well. It described "what
# approval is needed before executing a capability" and was the **only** model
# here with no protobuf counterpart, while having zero consumers repo-wide. See
# ``tests/test_schema_mirrors_the_protobuf_schema.py``.

from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    Parameter,
    RiskLevel,
    ServerInfo,
    ServerStatus,
    ServerType,
    Status,
    Tool,
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
    "Event",
    "Status",
]
