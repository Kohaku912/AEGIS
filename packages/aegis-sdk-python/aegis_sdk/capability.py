"""Capability definition helper — safe, validated capability creation.

Usage:
    from aegis_sdk import define_capability

    cap = define_capability(
        server_prefix="weather",
        action="get_forecast",
        name="Get Weather Forecast",
        description="Retrieve weather forecast for a location.",
        risk_level=RiskLevel.READ_ONLY,
        input_schema={"type": "object", "properties": {"location": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"temp_c": {"type": "number"}}},
        tags=["weather", "observe", "read_only"],
    )
"""

from __future__ import annotations

from typing import Any

from aegis_schema.models import Capability, RiskLevel, ServerType


def define_capability(
    server_prefix: str,
    action: str,
    name: str,
    description: str,
    risk_level: RiskLevel,
    input_schema: dict[str, Any] | None = None,
    output_schema: dict[str, Any] | None = None,
    side_effects: list[str] | None = None,
    tags: list[str] | None = None,
    timeout_ms: int = 10000,
    requires_approval: bool | None = None,
    server_type: ServerType = ServerType.DEV,
    version: str = "0.1.0",
) -> Capability:
    """Define a capability with safety validation.

    Args:
        server_prefix: Server prefix (e.g. "weather", "my_server").
        action: Action name (e.g. "get_forecast", "read_sensor").
        name: Human-readable name.
        description: What this capability does.
        risk_level: Safety level (READ_ONLY, SAFE_ACTION, APPROVAL_REQUIRED, HIGH_RISK).
        input_schema: JSON Schema for input parameters.
        output_schema: JSON Schema for output.
        side_effects: List of side effects (required for Level 2+).
        tags: Searchable tags.
        timeout_ms: Maximum execution time.
        requires_approval: Override approval requirement.
        server_type: Server type classification.
        version: Capability version.

    Returns:
        A validated Capability object.

    Raises:
        ValueError: If validation fails.
    """
    from aegis_sdk.safety import validate_capability_definition

    cap_id = f"{server_prefix}.{action}"

    # Validate
    errors = validate_capability_definition(
        cap_id=cap_id,
        name=name,
        description=description,
        risk_level=risk_level,
        side_effects=side_effects or [],
        tags=tags or [],
    )
    if errors:
        raise ValueError(f"Capability validation failed: {'; '.join(errors)}")

    # Auto-set requires_approval for Level 2+
    if requires_approval is None:
        requires_approval = risk_level >= RiskLevel.APPROVAL_REQUIRED

    import json

    return Capability(
        id=cap_id,
        name=name,
        description=description,
        server_type=server_type,
        risk_level=risk_level,
        requires_approval=requires_approval,
        side_effects=side_effects or [],
        tags=tags or [],
        input_schema=json.dumps(input_schema or {}),
        output_schema=json.dumps(output_schema or {}),
        timeout_ms=timeout_ms,
        version=version,
    )
