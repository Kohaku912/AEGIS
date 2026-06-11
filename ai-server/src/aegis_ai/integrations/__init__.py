"""External Integrations — safe gateway for external messaging.

Provides:
- IntegrationRegistry: Manages integration configurations
- IntegrationPolicy: Enforces safety rules
- LINEStub, DiscordStub, EmailStub, WebhookStub: Stub implementations
- IntegrationConfig, IntegrationType, IntegrationDirection: Models

Safety: All external outbound is default disabled.
Real implementations require user confirmation.
"""

from aegis_ai.integrations.discord_stub import DiscordStub  # noqa: F401
from aegis_ai.integrations.email_stub import EmailStub  # noqa: F401
from aegis_ai.integrations.line_stub import LINEStub  # noqa: F401
from aegis_ai.integrations.models import (  # noqa: F401
    IntegrationConfig,
    IntegrationDirection,
    IntegrationStatus,
    IntegrationType,
)
from aegis_ai.integrations.policy import IntegrationPolicy  # noqa: F401
from aegis_ai.integrations.registry import IntegrationRegistry  # noqa: F401
from aegis_ai.integrations.webhook_stub import WebhookStub  # noqa: F401
