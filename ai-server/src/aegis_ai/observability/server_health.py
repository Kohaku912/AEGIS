"""Server Health — tracks connected server status and health metrics."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ServerHealthEntry:
    """Health status of a connected server."""
    server_id: str = ""
    server_type: str = ""
    status: str = "UNKNOWN"
    last_heartbeat_ms: int = 0
    registered_capabilities: int = 0
    error_count: int = 0
    uptime_ms: int = 0


class ServerHealthView:
    """Aggregates server health from ToolRegistry."""

    def __init__(self, tool_registry: Any = None) -> None:
        self._registry = tool_registry

    def get_all_servers(self) -> list[dict[str, Any]]:
        """Get health status of all registered servers."""
        if not self._registry:
            return []

        servers = self._registry.list_servers()
        result = []
        now_ms = int(time.time() * 1000)

        for s in servers:
            caps = self._registry.get_capabilities_for_server(s.server_id)
            result.append({
                "server_id": s.server_id,
                "server_type": s.server_type.name,
                "status": s.status.name,
                "last_heartbeat_ms": s.last_heartbeat_ms,
                "heartbeat_age_seconds": (now_ms - s.last_heartbeat_ms) // 1000 if s.last_heartbeat_ms else -1,
                "registered_capabilities": len(caps),
                "version": s.version,
                "host": s.host,
                "port": s.port,
            })

        return result

    def get_summary(self) -> dict[str, Any]:
        """Get summary of server health."""
        servers = self.get_all_servers()
        online = sum(1 for s in servers if s["status"] == "ONLINE")
        return {
            "total_servers": len(servers),
            "online_servers": online,
            "offline_servers": len(servers) - online,
        }
