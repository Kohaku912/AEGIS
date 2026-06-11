"""Registration client — registers server and capabilities with AEGIS Core.

Handles:
- Server registration
- Capability registration
- Heartbeat
- Retry/backoff
"""

from __future__ import annotations

import logging
import time
from typing import Any

from aegis_schema.models import (
    Capability,
    ServerInfo,
    ServerStatus,
    ServerType,
)

logger = logging.getLogger("aegis_sdk.registration")


class RegistrationClient:
    """Registers a capability server with AEGIS Core.

    Usage:
        client = RegistrationClient(
            server_id="weather-server",
            server_type=ServerType.ROOM,
            host="localhost",
            port=50060,
        )
        client.register_server(registry)
        client.register_capability(registry, cap)
    """

    def __init__(
        self,
        server_id: str,
        server_type: ServerType,
        host: str = "localhost",
        port: int = 50060,
        version: str = "0.1.0",
    ) -> None:
        self._server_id = server_id
        self._server_type = server_type
        self._host = host
        self._port = port
        self._version = version
        self._registered = False
        self._capability_ids: list[str] = []

    @property
    def server_id(self) -> str:
        return self._server_id

    @property
    def is_registered(self) -> bool:
        return self._registered

    def register_server(self, registry: Any) -> bool:
        """Register server with ToolRegistry.

        Returns True if registration succeeded.
        """
        try:
            server_info = ServerInfo(
                server_id=self._server_id,
                server_type=self._server_type,
                version=self._version,
                status=ServerStatus.ONLINE,
                capability_ids=self._capability_ids,
                host=self._host,
                port=self._port,
                started_at_ms=int(time.time() * 1000),
                last_heartbeat_ms=int(time.time() * 1000),
            )
            registry.register_server(server_info)
            self._registered = True
            logger.info("Server '%s' registered with %d capabilities",
                       self._server_id, len(self._capability_ids))
            return True
        except Exception as e:
            logger.error("Failed to register server '%s': %s", self._server_id, e)
            return False

    def register_capability(self, registry: Any, capability: Capability) -> bool:
        """Register a capability with ToolRegistry.

        Returns True if registration succeeded.
        """
        try:
            registry.register_capability(capability)
            if capability.id not in self._capability_ids:
                self._capability_ids.append(capability.id)
            logger.info("Capability '%s' registered", capability.id)
            return True
        except Exception as e:
            logger.error("Failed to register capability '%s': %s", capability.id, e)
            return False

    def register_capabilities(self, registry: Any, capabilities: list[Capability]) -> int:
        """Register multiple capabilities. Returns count of successful registrations."""
        success_count = 0
        for cap in capabilities:
            if self.register_capability(registry, cap):
                success_count += 1
        return success_count

    def unregister(self, registry: Any) -> None:
        """Unregister server and all capabilities."""
        registry.unregister_server(self._server_id)
        for cap_id in self._capability_ids:
            registry.unregister_capability(cap_id)
        self._registered = False
        self._capability_ids.clear()
        logger.info("Server '%s' unregistered", self._server_id)

    def heartbeat(self, registry: Any) -> bool:
        """Send heartbeat to update last_heartbeat_ms."""
        server = registry.get_server(self._server_id)
        if server:
            server.last_heartbeat_ms = int(time.time() * 1000)
            return True
        return False

    def get_server_info(self) -> ServerInfo:
        """Get current server info."""
        return ServerInfo(
            server_id=self._server_id,
            server_type=self._server_type,
            version=self._version,
            status=ServerStatus.ONLINE if self._registered else ServerStatus.OFFLINE,
            capability_ids=self._capability_ids,
            host=self._host,
            port=self._port,
            started_at_ms=int(time.time() * 1000),
            last_heartbeat_ms=int(time.time() * 1000),
        )
