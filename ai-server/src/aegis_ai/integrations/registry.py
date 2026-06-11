"""Integration Registry — manages external integration configurations."""

from __future__ import annotations

import copy
import logging

from aegis_ai.integrations.models import (
    DEFAULT_INTEGRATIONS,
    IntegrationConfig,
    IntegrationDirection,
    IntegrationStatus,
)

logger = logging.getLogger("aegis_ai.integrations.registry")


class IntegrationRegistry:
    """Manages external integration configurations.

    Usage:
        registry = IntegrationRegistry()
        registry.register(line_config)
        config = registry.get("line")
    """

    def __init__(self) -> None:
        self._integrations: dict[str, IntegrationConfig] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default stub integrations (deep copy to avoid mutation)."""
        for integration_id, config in DEFAULT_INTEGRATIONS.items():
            self._integrations[integration_id] = copy.deepcopy(config)

    def register(self, config: IntegrationConfig) -> None:
        """Register an integration configuration."""
        self._integrations[config.integration_id] = config
        logger.info("Integration '%s' registered (status=%s)", config.integration_id, config.status.name)

    def get(self, integration_id: str) -> IntegrationConfig | None:
        """Get an integration configuration by ID."""
        return self._integrations.get(integration_id)

    def list_all(self) -> list[IntegrationConfig]:
        """List all registered integrations."""
        return list(self._integrations.values())

    def list_enabled(self) -> list[IntegrationConfig]:
        """List enabled integrations."""
        return [c for c in self._integrations.values() if c.enabled]

    def list_outbound(self) -> list[IntegrationConfig]:
        """List outbound-capable integrations."""
        return [
            c for c in self._integrations.values()
            if c.direction in (IntegrationDirection.OUTBOUND, IntegrationDirection.BOTH)
        ]

    def is_enabled(self, integration_id: str) -> bool:
        """Check if an integration is enabled."""
        config = self._integrations.get(integration_id)
        return config is not None and config.enabled

    def enable(self, integration_id: str) -> bool:
        """Enable an integration. Returns False if not found."""
        config = self._integrations.get(integration_id)
        if not config:
            return False
        config.enabled = True
        config.status = IntegrationStatus.ENABLED
        return True

    def disable(self, integration_id: str) -> bool:
        """Disable an integration."""
        config = self._integrations.get(integration_id)
        if not config:
            return False
        config.enabled = False
        config.status = IntegrationStatus.DISABLED
        return True
