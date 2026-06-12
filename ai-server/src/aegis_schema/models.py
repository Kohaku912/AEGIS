"""Pydantic models for AEGIS's shared capability protocol.

These models are the Python runtime representation of the protobuf schema
defined in protos/aegis/common.proto and protos/aegis/capability.proto.

All models use Pydantic v2 with strict validation.
"""

from __future__ import annotations

import re
from enum import IntEnum

from pydantic import BaseModel, Field, field_validator, model_validator

# ═══════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════

class RiskLevel(IntEnum):
    """Safety classification for capabilities and actions.

    Higher values = more dangerous. The Policy Engine uses this to decide
    whether to allow, ask for approval, or deny an action.
    """
    UNSPECIFIED = 0
    READ_ONLY = 1          # Observe only, no side effects
    SAFE_ACTION = 2        # Non-destructive, reversible
    APPROVAL_REQUIRED = 3  # Needs explicit user confirmation
    HIGH_RISK = 4          # Potentially dangerous
    FORBIDDEN = 5          # Never allowed autonomously


class ServerType(IntEnum):
    """Identifies which server in the AEGIS ecosystem."""
    UNSPECIFIED = 0
    AI = 1
    PC = 2
    ANDROID = 3
    BROWSER = 4
    ROOM = 5
    DEV = 6


class ServerStatus(IntEnum):
    """Current status of a server instance."""
    UNSPECIFIED = 0
    ONLINE = 1
    OFFLINE = 2
    DEGRADED = 3
    STARTING = 4


class EventPriority(IntEnum):
    """Processing priority for events on the Event Bus."""
    UNSPECIFIED = 0
    URGENT = 1
    NORMAL = 2
    BACKGROUND = 3


# ═══════════════════════════════════════════════════════════════
# Value Objects
# ═══════════════════════════════════════════════════════════════

class Parameter(BaseModel):
    """A typed parameter for capability input/output."""
    name: str = Field(..., description="Parameter name (e.g. 'url', 'duration_ms')")
    type: str = Field(
        ...,
        description="JSON type: 'string', 'number', 'integer', 'boolean', 'object', 'array'",
    )
    description: str = Field(default="", description="Human-readable description")
    required: bool = Field(default=False, description="Whether this parameter is mandatory")
    default_value: str = Field(
        default="",
        description="JSON-encoded default value (empty string if no default)",
    )
    validation: str = Field(
        default="",
        description="Optional JSON Schema snippet for validation constraints",
    )

    @field_validator("type")
    @classmethod
    def type_must_be_valid_json_type(cls, v: str) -> str:
        allowed = {"string", "number", "integer", "boolean", "object", "array"}
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}, got '{v}'")
        return v

    @field_validator("name")
    @classmethod
    def name_must_be_snake_case(cls, v: str) -> str:
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError(f"name must be snake_case, got '{v}'")
        return v


class Status(BaseModel):
    """Generic operation status."""
    code: int = Field(default=0, description="0 = success, non-zero = error code")
    message: str = Field(default="ok", description="Human-readable status/error message")
    detail: str = Field(default="", description="Optional machine-readable detail (JSON)")


# ═══════════════════════════════════════════════════════════════
# Core Protocol Messages
# ═══════════════════════════════════════════════════════════════

class Capability(BaseModel):
    """A single capability that a server can perform.

    Registered with the Tool Broker at server startup.
    The canonical ID format is: "{server_short}.{action}" (e.g. "pc.screenshot").
    """

    # Identity
    id: str = Field(
        ...,
        description="Unique ID: '{server}.{action}' (e.g. 'pc.screenshot')",
        pattern=r"^(pc|android|browser|room|dev|ai)\.[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$",
    )
    name: str = Field(..., min_length=1, max_length=128, description="Human-readable name")
    description: str = Field(..., min_length=1, max_length=1024, description="What this does")

    # Ownership
    server_type: ServerType = Field(..., description="Which server provides this")

    # Schema — inline JSON Schema strings
    input_schema: str = Field(
        default="{}",
        description="JSON Schema for input parameters",
    )
    output_schema: str = Field(
        default="{}",
        description="JSON Schema for expected output",
    )

    # Safety
    risk_level: RiskLevel = Field(
        default=RiskLevel.UNSPECIFIED,
        description="Minimum safety level required",
    )
    requires_approval: bool = Field(
        default=False,
        description="Explicit approval flag; true = Policy Engine MUST ask user",
    )
    side_effects: list[str] = Field(
        default_factory=list,
        description="Human-readable list of side effects",
    )

    # Operational
    timeout_ms: int = Field(
        default=30000,
        ge=0,
        le=3600000,  # max 1 hour
        description="Maximum execution time in ms (0 = server default)",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Search/discovery tags",
    )

    # Versioning
    version: str = Field(
        default="0.1.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version of this capability",
    )

    @field_validator("tags")
    @classmethod
    def tags_must_be_lowercase(cls, v: list[str]) -> list[str]:
        for tag in v:
            if not re.match(r"^[a-z][a-z0-9_:.-]*$", tag):
                raise ValueError(f"tag must be lowercase alphanumeric with :_.- only, got '{tag}'")
        return v

    @field_validator("side_effects")
    @classmethod
    def side_effects_not_empty_strings(cls, v: list[str]) -> list[str]:
        for se in v:
            if not se.strip():
                raise ValueError("side_effect must not be empty string")
        return v

    @model_validator(mode="after")
    def risk_level_consistency(self) -> Capability:
        """Enforce consistency between risk_level and requires_approval."""
        if self.risk_level == RiskLevel.UNSPECIFIED:
            raise ValueError("risk_level must not be UNSPECIFIED for a registered capability")
        if self.risk_level == RiskLevel.FORBIDDEN:
            raise ValueError(
                f"Capability '{self.id}' has risk_level=FORBIDDEN. "
                "FORBIDDEN capabilities must not be registered."
            )
        # requires_approval=true is redundant with APPROVAL_REQUIRED or higher
        if self.requires_approval and self.risk_level < RiskLevel.APPROVAL_REQUIRED:
            raise ValueError(
                f"Capability '{self.id}': requires_approval=true but risk_level is "
                f"{self.risk_level.name}. Set risk_level >= APPROVAL_REQUIRED or "
                f"requires_approval=false."
            )
        # APPROVAL_REQUIRED or higher should have explicit approval or be marked accordingly
        if self.risk_level >= RiskLevel.APPROVAL_REQUIRED and not self.requires_approval:
            # This is acceptable (relies on risk_level alone), but we note it
            pass
        return self

    @model_validator(mode="after")
    def id_server_type_consistency(self) -> Capability:
        """Ensure the capability ID prefix matches the declared server_type."""
        prefix_map = {
            ServerType.PC: "pc",
            ServerType.ANDROID: "android",
            ServerType.BROWSER: "browser",
            ServerType.ROOM: "room",
            ServerType.DEV: "dev",
            ServerType.AI: "ai",
        }
        expected_prefix = prefix_map.get(self.server_type)
        if expected_prefix and not self.id.startswith(expected_prefix + "."):
            raise ValueError(
                f"Capability ID '{self.id}' should start with '{expected_prefix}.' "
                f"for server_type={self.server_type.name}"
            )
        return self


class Tool(BaseModel):
    """A concrete instance of a capability with instance-specific configuration."""
    id: str = Field(..., description="Unique tool instance ID", min_length=1)
    capability_id: str = Field(..., description="References Capability.id", min_length=1)
    server_id: str = Field(..., description="Which server instance hosts this tool", min_length=1)
    config_json: str = Field(default="{}", description="Instance-specific config (JSON)")
    enabled: bool = Field(default=True, description="Whether this tool is currently available")
    display_name: str = Field(
        default="",
        description="User-facing name (can differ from capability name)",
    )


class ServerInfo(BaseModel):
    """Describes a running server instance and its capabilities."""
    server_id: str = Field(..., min_length=1, description="Unique server instance ID")
    server_type: ServerType = Field(..., description="Type of this server")
    version: str = Field(
        default="0.1.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Server software version (semver)",
    )
    status: ServerStatus = Field(default=ServerStatus.STARTING, description="Current status")
    capability_ids: list[str] = Field(
        default_factory=list,
        description="IDs of capabilities this server provides",
    )
    host: str = Field(default="localhost", description="Hostname or IP")
    port: int = Field(default=50051, ge=1, le=65535, description="gRPC port")
    started_at_ms: int = Field(default=0, ge=0, description="Unix timestamp (ms) when started")
    last_heartbeat_ms: int = Field(
        default=0,
        ge=0,
        description="Unix timestamp (ms) of last heartbeat",
    )
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Arbitrary key-value metadata",
    )


class ApprovalRequirement(BaseModel):
    """Describes what approval is needed before executing a capability."""
    capability_id: str = Field(..., min_length=1, description="Which capability this applies to")
    risk_level: RiskLevel = Field(..., description="Risk level of the capability")
    requires_user_approval: bool = Field(
        default=True,
        description="Whether user MUST approve",
    )
    approval_message: str = Field(
        default="",
        description="Message to show in Approval UI",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=0,
        le=86400,  # max 24 hours
        description="How long to wait for approval before auto-deny (0 = wait indefinitely)",
    )
    allow_session_remember: bool = Field(
        default=True,
        description="Whether 'remember for session' is offered",
    )


class Event(BaseModel):
    """An event pushed from a capability server to the AI Server Event Bus."""
    event_id: str = Field(..., min_length=1, description="Unique event ID (UUID recommended)")
    event_type: str = Field(
        ...,
        min_length=1,
        description="Event type (e.g. 'pc.screen_change')",
    )
    source_server_type: ServerType = Field(..., description="Which server type sent this")
    source_server_id: str = Field(..., min_length=1, description="Which server instance sent this")
    timestamp_ms: int = Field(
        default=0,
        ge=0,
        description="Unix timestamp (ms) when event occurred",
    )
    payload_json: str = Field(default="{}", description="Event payload (JSON)")
    priority: EventPriority = Field(
        default=EventPriority.NORMAL,
        description="Processing priority",
    )
    correlation_id: str = Field(
        default="",
        description="Optional — links related events",
    )
    attributes: dict[str, str] = Field(
        default_factory=dict,
        description="Arbitrary key-value attributes",
    )

    # ── Event Bus / Trigger Engine fields (added 2026-06-11) ──

    severity: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Event severity 0–10. 0=info, 5=warning, 8=error, 10=critical.",
    )
    dedupe_key: str = Field(
        default="",
        description="Deduplication key. Events with the same key within a time window "
                    "are treated as duplicates. Empty = no dedup.",
    )
    requires_attention: bool = Field(
        default=False,
        description="Whether this event requires immediate AI attention. "
                    "Set by the Trigger Engine after rule evaluation.",
    )
