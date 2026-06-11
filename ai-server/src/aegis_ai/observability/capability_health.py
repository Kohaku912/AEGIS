"""Capability Health — tracks capability usage, success/failure, and latency."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CapabilityHealthEntry:
    """Usage statistics for a single capability."""
    capability_id: str = ""
    total_invocations: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_latency_ms: float = 0.0
    last_used_ms: int = 0
    last_error: str = ""


class CapabilityHealthView:
    """Aggregates capability health from ToolRegistry and usage tracking."""

    def __init__(self, tool_registry: Any = None) -> None:
        self._registry = tool_registry
        self._usage: dict[str, CapabilityHealthEntry] = {}

    def record_invocation(
        self, capability_id: str, success: bool, latency_ms: float, error: str = "",
    ) -> None:
        """Record a capability invocation result."""
        if capability_id not in self._usage:
            self._usage[capability_id] = CapabilityHealthEntry(capability_id=capability_id)

        entry = self._usage[capability_id]
        entry.total_invocations += 1
        if success:
            entry.success_count += 1
        else:
            entry.failure_count += 1
            entry.last_error = error
        entry.last_used_ms = int(time.time() * 1000)

        # Running average
        n = entry.total_invocations
        entry.avg_latency_ms = ((n - 1) * entry.avg_latency_ms + latency_ms) / n

    def get_capability_health(self, capability_id: str) -> dict[str, Any]:
        """Get health for a specific capability."""
        entry = self._usage.get(capability_id)
        if not entry:
            return {"capability_id": capability_id, "total_invocations": 0}
        return {
            "capability_id": entry.capability_id,
            "total_invocations": entry.total_invocations,
            "success_count": entry.success_count,
            "failure_count": entry.failure_count,
            "avg_latency_ms": round(entry.avg_latency_ms, 2),
            "last_used_ms": entry.last_used_ms,
            "last_error": entry.last_error,
        }

    def get_all_capabilities(self) -> list[dict[str, Any]]:
        """Get health for all capabilities with registry metadata."""
        if not self._registry:
            return []

        caps = self._registry.list_capabilities()
        result = []
        for cap in caps:
            health = self.get_capability_health(cap.id)
            health.update({
                "name": cap.name,
                "risk_level": cap.risk_level.name,
                "server_type": cap.server_type.name,
            })
            result.append(health)
        return result
