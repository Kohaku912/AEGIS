"""Capability definition helper — safe, validated capability creation.

Usage:
    from aegis_sdk import define_capability

    cap = define_capability(
        server_prefix="room-server",
        action="weather.get_forecast",
        name="Get Weather Forecast",
        description="Retrieve weather forecast for a location.",
        risk_level=RiskLevel.READ_ONLY,
        input_schema={"type": "object", "properties": {"location": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"temp_c": {"type": "number"}}},
        tags=["weather", "observe", "read_only"],
    )

``server_prefix`` names the AEGIS server that **hosts** the capability, and the id space is the
roster's, not the plugin author's: an id whose first segment is not an AEGIS server cannot be
registered or invoked, so the SDK **refuses it by name** at the call site rather than letting
pydantic report a ``server_type`` the caller never chose. Put your own namespace in ``action`` —
the segments after the first are yours, so the example above builds
``room-server.weather.get_forecast`` for a ``weather`` app hosted by ``room-server``.
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
    server_type: ServerType | None = None,
    version: str = "0.1.0",
) -> Capability:
    """Define a capability with safety validation.

    Args:
        server_prefix: Which AEGIS server hosts this capability. Must be one of
            ``aegis_sdk.ALLOWED_SERVER_PREFIXES`` — the roster's own spellings, e.g.
            ``"room-server"`` or its short alias ``"room"``. A prefix of your own is refused;
            see the module docstring.
        action: Action name (e.g. "get_forecast"). May be dotted — ``"weather.get_forecast"``
            yields ``room-server.weather.get_forecast`` — so an app keeps its own namespace
            inside the host server's.
        name: Human-readable name.
        description: What this capability does.
        risk_level: Safety level (READ_ONLY, SAFE_ACTION, APPROVAL_REQUIRED, HIGH_RISK).
        input_schema: JSON Schema for input parameters.
        output_schema: JSON Schema for output.
        side_effects: List of side effects (required for Level 2+).
        tags: Searchable tags.
        timeout_ms: Maximum execution time.
        requires_approval: Override approval requirement.
        server_type: Which server type this belongs to. Defaults to the type ``server_prefix``
            already names, so a caller does not restate it; passing a type the prefix does not
            name is an error.
        version: Capability version.

    Returns:
        A validated Capability object.

    Raises:
        ValueError: If validation fails.
    """
    from aegis_sdk.safety import SERVER_TYPE_BY_PREFIX, validate_capability_definition

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

    # The prefix passed validation, so it is in the map: this lookup cannot fail.
    if server_type is None:
        server_type = SERVER_TYPE_BY_PREFIX[server_prefix]
    elif server_type is not SERVER_TYPE_BY_PREFIX[server_prefix]:
        raise ValueError(
            f"server_prefix '{server_prefix}' names server_type "
            f"{SERVER_TYPE_BY_PREFIX[server_prefix].name}, but server_type="
            f"{server_type.name} was passed. Omit server_type — the prefix already says it — "
            f"or use the prefix that matches."
        )

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
