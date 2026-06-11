"""Tool Registry — central capability and server registration.

Manages:
- Server registration (ServerInfo)
- Capability registration (Capability)
- Capability search and filtering (by server_type, risk_level, tags, free text)
- Capability lookup by ID

The Tool Registry is the single source of truth for "what tools are available."
It does NOT execute tools — that's ToolBroker's job.
It does NOT enforce safety — that's PolicyEngine's job.

Architecture reference: docs/architecture.md §5.8
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ellie_schema.models import Capability, RiskLevel, ServerInfo, ServerStatus, ServerType


@dataclass
class RegistryStats:
    """Summary statistics for the registry."""
    total_capabilities: int = 0
    total_servers: int = 0
    online_servers: int = 0
    capabilities_by_server: dict[str, int] = field(default_factory=dict)
    capabilities_by_risk: dict[str, int] = field(default_factory=dict)


class ToolRegistry:
    """In-memory registry of servers and their capabilities.

    Thread-safe: no. Single-threaded asyncio usage assumed.

    Usage:
        registry = ToolRegistry()
        registry.register_capability(cap)
        caps = registry.list_capabilities(server_type=ServerType.PC)
    """

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}       # id → Capability
        self._servers: dict[str, ServerInfo] = {}             # server_id → ServerInfo
        self._server_caps: dict[str, set[str]] = {}           # server_id → set of cap IDs

    # ── Server Management ──────────────────────────────────

    def register_server(self, server_info: ServerInfo) -> None:
        """Register or update a server.

        Args:
            server_info: Server information.

        Raises:
            ValueError: If server_id is empty.
        """
        if not server_info.server_id:
            raise ValueError("server_id must not be empty")

        self._servers[server_info.server_id] = server_info
        if server_info.server_id not in self._server_caps:
            self._server_caps[server_info.server_id] = set()

        # Sync capability_ids from ServerInfo
        for cap_id in server_info.capability_ids:
            if cap_id in self._capabilities:
                self._server_caps[server_info.server_id].add(cap_id)

    def unregister_server(self, server_id: str) -> None:
        """Remove a server and all its capability associations.

        Note: Capability definitions themselves are NOT deleted.
        """
        self._servers.pop(server_id, None)
        self._server_caps.pop(server_id, None)

    def get_server(self, server_id: str) -> ServerInfo | None:
        """Get a registered server by ID."""
        return self._servers.get(server_id)

    def list_servers(
        self,
        server_type: ServerType | None = None,
        status: ServerStatus | None = None,
    ) -> list[ServerInfo]:
        """List servers, optionally filtered."""
        result = list(self._servers.values())
        if server_type is not None:
            result = [s for s in result if s.server_type == server_type]
        if status is not None:
            result = [s for s in result if s.status == status]
        return result

    # ── Capability Management ───────────────────────────────

    def register_capability(self, capability: Capability) -> None:
        """Register a capability.

        Args:
            capability: The capability to register.

        Raises:
            ValueError: If capability.risk_level is UNSPECIFIED or FORBIDDEN.
        """
        if capability.risk_level == RiskLevel.UNSPECIFIED:
            raise ValueError(
                f"Cannot register capability '{capability.id}': "
                "risk_level is UNSPECIFIED"
            )
        if capability.risk_level == RiskLevel.FORBIDDEN:
            raise ValueError(
                f"Cannot register capability '{capability.id}': "
                "risk_level is FORBIDDEN"
            )

        self._capabilities[capability.id] = capability

    def unregister_capability(self, capability_id: str) -> None:
        """Remove a capability from the registry."""
        self._capabilities.pop(capability_id, None)
        for caps in self._server_caps.values():
            caps.discard(capability_id)

    def get_capability(self, capability_id: str) -> Capability | None:
        """Get a capability by its exact ID."""
        return self._capabilities.get(capability_id)

    def find_capability(self, capability_id: str) -> Capability | None:
        """Alias for get_capability. Returns None if not found."""
        return self.get_capability(capability_id)

    def list_capabilities(
        self,
        server_type: ServerType | None = None,
        max_risk_level: RiskLevel | None = None,
        tags: list[str] | None = None,
    ) -> list[Capability]:
        """List capabilities with optional filters.

        Args:
            server_type: Filter by server type. None = all.
            max_risk_level: Return only capabilities with risk_level <= this.
            tags: Return capabilities that have ALL specified tags (AND match).
        """
        result = list(self._capabilities.values())

        if server_type is not None:
            result = [c for c in result if c.server_type == server_type]

        if max_risk_level is not None:
            result = [c for c in result if c.risk_level <= max_risk_level]

        if tags:
            for tag in tags:
                result = [c for c in result if tag in c.tags]

        return result

    def search(
        self,
        query: str,
        server_type: ServerType | None = None,
        max_risk_level: RiskLevel | None = None,
    ) -> list[Capability]:
        """Free-text search across capability name, description, and tags.

        Args:
            query: Search text (case-insensitive substring match).
            server_type: Optional server type filter.
            max_risk_level: Optional max risk filter.
        """
        query_lower = query.lower()
        result = []

        for cap in self._capabilities.values():
            # Check server_type filter
            if server_type is not None and cap.server_type != server_type:
                continue
            # Check risk filter
            if max_risk_level is not None and cap.risk_level > max_risk_level:
                continue
            # Search in name, description, tags, and ID
            searchable = (
                cap.name.lower() + " " +
                cap.description.lower() + " " +
                " ".join(cap.tags).lower() + " " +
                cap.id.lower()
            )
            if query_lower in searchable:
                result.append(cap)

        return result

    # ── Capabilities by Server ──────────────────────────────

    def get_capabilities_for_server(self, server_id: str) -> list[Capability]:
        """Get all capabilities registered to a specific server instance."""
        cap_ids = self._server_caps.get(server_id, set())
        return [self._capabilities[cid] for cid in cap_ids if cid in self._capabilities]

    def get_capabilities_by_server_type(self, server_type: ServerType) -> list[Capability]:
        """Get all capabilities for a given server type."""
        return self.list_capabilities(server_type=server_type)

    # ── Filtering by Risk ───────────────────────────────────

    def get_capabilities_by_risk(self, max_risk: RiskLevel) -> list[Capability]:
        """Get all capabilities at or below a given risk level."""
        return self.list_capabilities(max_risk_level=max_risk)

    def get_safe_capabilities(self) -> list[Capability]:
        """Get capabilities that can run without approval (READ_ONLY + SAFE_ACTION)."""
        return self.list_capabilities(max_risk_level=RiskLevel.SAFE_ACTION)

    def get_approval_capabilities(self) -> list[Capability]:
        """Get capabilities that require approval (APPROVAL_REQUIRED + HIGH_RISK)."""
        result = []
        for cap in self._capabilities.values():
            if cap.risk_level in (RiskLevel.APPROVAL_REQUIRED, RiskLevel.HIGH_RISK):
                result.append(cap)
        return result

    # ── Stats ───────────────────────────────────────────────

    def stats(self) -> RegistryStats:
        """Get registry summary statistics."""
        stats = RegistryStats(
            total_capabilities=len(self._capabilities),
            total_servers=len(self._servers),
            online_servers=sum(
                1 for s in self._servers.values()
                if s.status == ServerStatus.ONLINE
            ),
        )

        # Count by server type
        for cap in self._capabilities.values():
            key = cap.server_type.name
            stats.capabilities_by_server[key] = (
                stats.capabilities_by_server.get(key, 0) + 1
            )

        # Count by risk level
        for cap in self._capabilities.values():
            key = cap.risk_level.name
            stats.capabilities_by_risk[key] = (
                stats.capabilities_by_risk.get(key, 0) + 1
            )

        return stats

    def __len__(self) -> int:
        return len(self._capabilities)

    def __contains__(self, capability_id: str) -> bool:
        return capability_id in self._capabilities
