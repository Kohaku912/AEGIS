"""Integration models — defines external integration types and structure."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class IntegrationType(Enum):
    """External integration types."""
    LINE = auto()
    DISCORD = auto()
    EMAIL = auto()
    WEBHOOK = auto()


class IntegrationDirection(Enum):
    """Integration communication direction."""
    INBOUND = auto()
    OUTBOUND = auto()
    BOTH = auto()


class IntegrationStatus(Enum):
    """Integration status."""
    STUB = auto()           # Stub only — no real implementation
    DISABLED = auto()       # Disabled by user
    ENABLED = auto()        # Enabled but not configured
    CONFIGURED = auto()     # Configured and ready
    ACTIVE = auto()         # Active and running
    ERROR = auto()          # Error state


@dataclass
class IntegrationConfig:
    """Configuration for an external integration."""
    integration_id: str = ""
    type: IntegrationType = IntegrationType.LINE
    enabled: bool = False  # Default disabled
    direction: IntegrationDirection = IntegrationDirection.OUTBOUND
    required_secrets: list[str] = field(default_factory=list)
    privacy_level: str = "internal"  # "public", "internal", "sensitive", "local_only"
    allowed_event_types: list[str] = field(default_factory=list)
    allowed_capabilities: list[str] = field(default_factory=list)
    requires_user_confirmation: bool = True
    status: IntegrationStatus = IntegrationStatus.STUB
    metadata: dict[str, Any] = field(default_factory=dict)


# Default stub configurations
DEFAULT_INTEGRATIONS: dict[str, IntegrationConfig] = {
    "line": IntegrationConfig(
        integration_id="line",
        type=IntegrationType.LINE,
        enabled=False,
        direction=IntegrationDirection.BOTH,
        required_secrets=["line_channel_secret", "line_channel_access_token"],
        privacy_level="internal",
        requires_user_confirmation=True,
        status=IntegrationStatus.STUB,
    ),
    "discord": IntegrationConfig(
        integration_id="discord",
        type=IntegrationType.DISCORD,
        enabled=False,
        direction=IntegrationDirection.BOTH,
        required_secrets=["discord_bot_token"],
        privacy_level="internal",
        requires_user_confirmation=True,
        status=IntegrationStatus.STUB,
    ),
    "email": IntegrationConfig(
        integration_id="email",
        type=IntegrationType.EMAIL,
        enabled=False,
        direction=IntegrationDirection.OUTBOUND,
        required_secrets=["smtp_host", "smtp_port", "smtp_user", "smtp_password"],
        privacy_level="sensitive",
        requires_user_confirmation=True,
        status=IntegrationStatus.STUB,
    ),
    "webhook": IntegrationConfig(
        integration_id="webhook",
        type=IntegrationType.WEBHOOK,
        enabled=False,
        direction=IntegrationDirection.BOTH,
        required_secrets=["webhook_url", "webhook_secret"],
        privacy_level="internal",
        requires_user_confirmation=True,
        status=IntegrationStatus.STUB,
    ),
}
