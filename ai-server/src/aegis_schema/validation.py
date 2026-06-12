"""Validation utilities for AEGIS capability schema.

Provides functions to validate individual capabilities, batches of capabilities,
and raw JSON input against the schema.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from pydantic import ValidationError as PydanticValidationError

from aegis_schema.models import Capability, RiskLevel, ServerType


@dataclass
class ValidationResult:
    """Result of validating one or more capabilities."""
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validated: list[Capability] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.valid = False
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def merge(self, other: ValidationResult) -> None:
        self.valid = self.valid and other.valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.validated.extend(other.validated)

    def summary(self) -> str:
        lines = []
        if self.valid:
            lines.append(f"✅ All valid ({len(self.validated)} capabilities)")
        else:
            lines.append(f"❌ Validation failed: {len(self.errors)} error(s)")
        for err in self.errors:
            lines.append(f"  ERROR: {err}")
        for warn in self.warnings:
            lines.append(f"  WARN:  {warn}")
        return "\n".join(lines)


def validate_capability(cap: Capability) -> ValidationResult:
    """Validate a single Capability model for logical consistency.

    Pydantic already validates field types/regex during construction.
    This function performs additional cross-field and semantic validation.
    """
    result = ValidationResult(validated=[cap])

    # Risk level checks
    if cap.risk_level == RiskLevel.UNSPECIFIED:
        result.add_error(f"Capability '{cap.id}': risk_level is UNSPECIFIED")
    if cap.risk_level == RiskLevel.FORBIDDEN:
        result.add_error(
            f"Capability '{cap.id}': FORBIDDEN capabilities should not be registered. "
            "If this capability exists, remove it from the registry."
        )

    # Server type check
    if cap.server_type == ServerType.UNSPECIFIED:
        result.add_error(f"Capability '{cap.id}': server_type is UNSPECIFIED")

    # Timeout sanity
    if cap.timeout_ms == 0:
        result.add_warning(
            f"Capability '{cap.id}': timeout_ms is 0 (server default). "
            "Consider setting an explicit timeout."
        )
    if cap.timeout_ms > 300000:  # > 5 minutes
        result.add_warning(
            f"Capability '{cap.id}': timeout_ms is {cap.timeout_ms}ms "
            f"({cap.timeout_ms / 60000:.1f} min). Is this intentional?"
        )

    # Schema validation
    for schema_field, schema_name in [
        (cap.input_schema, "input_schema"),
        (cap.output_schema, "output_schema"),
    ]:
        if schema_field and schema_field != "{}":
            try:
                parsed = json.loads(schema_field)
                if not isinstance(parsed, dict):
                    result.add_error(
                        f"Capability '{cap.id}': {schema_name} is valid JSON "
                        "but not a JSON object"
                    )
            except json.JSONDecodeError as e:
                result.add_error(
                    f"Capability '{cap.id}': {schema_name} is not valid JSON: {e}"
                )

    # Side effects consistency
    if cap.risk_level <= RiskLevel.READ_ONLY and cap.side_effects:
        result.add_warning(
            f"Capability '{cap.id}': risk_level is {cap.risk_level.name} "
            f"but side_effects are declared: {cap.side_effects}. "
            "READ_ONLY capabilities should have no side effects."
        )

    # Tags should include the risk level as a tag for searchability
    expected_risk_tag = f"risk:{cap.risk_level.name.lower()}"
    if expected_risk_tag not in cap.tags:
        result.add_warning(
            f"Capability '{cap.id}': tags should include '{expected_risk_tag}' "
            "for Policy Engine filtering"
        )

    # Description should be meaningful
    if len(cap.description) < 10:
        result.add_warning(
            f"Capability '{cap.id}': description is very short "
            f"({len(cap.description)} chars). Add more detail."
        )

    return result


def validate_capabilities_batch(capabilities: list[Capability]) -> ValidationResult:
    """Validate a batch of capabilities, including cross-capability checks."""
    result = ValidationResult()

    # Check for duplicate IDs
    seen_ids: dict[str, int] = {}
    for i, cap in enumerate(capabilities):
        if cap.id in seen_ids:
            result.add_error(
                f"Duplicate capability ID '{cap.id}' at positions "
                f"{seen_ids[cap.id]} and {i}"
            )
        seen_ids[cap.id] = i

    # Validate each capability individually
    for cap in capabilities:
        result.merge(validate_capability(cap))

    # Cross-capability: check for suspicious patterns
    pc_caps = [c for c in capabilities if c.server_type == ServerType.PC]
    android_caps = [c for c in capabilities if c.server_type == ServerType.ANDROID]
    browser_caps = [c for c in capabilities if c.server_type == ServerType.BROWSER]
    room_caps = [c for c in capabilities if c.server_type == ServerType.ROOM]
    dev_caps = [c for c in capabilities if c.server_type == ServerType.DEV]

    # At least one capability per server type by convention (not enforced)
    for stype, caps, name in [
        (ServerType.PC, pc_caps, "PC"),
        (ServerType.ANDROID, android_caps, "Android"),
        (ServerType.BROWSER, browser_caps, "Browser"),
        (ServerType.ROOM, room_caps, "Room"),
        (ServerType.DEV, dev_caps, "Dev"),
    ]:
        if not caps:
            result.add_warning(f"No capabilities registered for {name} server")

    # Check for high-risk capabilities without approval
    for cap in capabilities:
        if cap.risk_level >= RiskLevel.HIGH_RISK and not cap.requires_approval:
            result.add_warning(
                f"Capability '{cap.id}': risk_level={cap.risk_level.name} "
                "but requires_approval=false. Is this intentional?"
            )

    return result


def validate_capability_json(json_str: str) -> ValidationResult:
    """Parse and validate a capability from a JSON string.

    Returns a ValidationResult. If parsing succeeds, the Capability object
    is in result.validated[0].
    """
    result = ValidationResult()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON: {e}")
        return result

    if not isinstance(data, dict):
        result.add_error("JSON must be an object, not an array or scalar")
        return result

    try:
        cap = Capability.model_validate(data)
    except PydanticValidationError as e:
        result.add_error(f"Schema validation failed: {e}")
        return result

    # Run semantic validation
    result.merge(validate_capability(cap))

    return result
