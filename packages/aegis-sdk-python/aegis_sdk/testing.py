"""Test harness — mock AEGIS Core for testing capability servers.

Provides:
- MockAEGISCore: Simulates ToolRegistry, EventBus, PolicyEngine
- run_capability_registration_check: Test helper for capability registration
- run_policy_flow_check: Test helper for policy enforcement
- run_event_push_check: Test helper for event push
"""

from __future__ import annotations

from typing import Any

from aegis_schema.models import (
    Capability,
    Event,
    ServerInfo,
)

from event_bus import EventBus
from policy_engine import PolicyDecision, create_default_policy_engine
from tool_broker import ToolBroker
from tool_registry import ToolRegistry

# ``ASK_APPROVAL`` was removed on 2026-09-27, so the decision space is now
# ALLOW / ALLOW_WITH_AUDIT / DENY / UNAVAILABLE. Both ALLOW and
# ALLOW_WITH_AUDIT execute — ALLOW_WITH_AUDIT only records the detail.
_EXPECTED_STATUS_BY_DECISION: dict[PolicyDecision, str] = {
    PolicyDecision.ALLOW: "SUCCESS",
    PolicyDecision.ALLOW_WITH_AUDIT: "SUCCESS",
    PolicyDecision.DENY: "DENIED",
    PolicyDecision.UNAVAILABLE: "UNAVAILABLE",
}


class MockAEGISCore:
    """Simulates AEGIS Core for testing capability servers.

    Usage:
        core = MockAEGISCore()
        core.register_server(server_info)
        core.register_capability(cap)
        core.publish_event(event)
        result = core.invoke_capability("dev.hello", {})
    """

    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self.event_bus = EventBus()
        self.policy = create_default_policy_engine()
        self.broker = ToolBroker(self.registry, self.policy)

    def register_server(self, server_info: ServerInfo) -> None:
        self.registry.register_server(server_info)

    def register_capability(self, capability: Capability) -> None:
        self.registry.register_capability(capability)

    def publish_event(self, event: Event) -> bool:
        return self.event_bus.publish(event)

    def invoke_capability(
        self, capability_id: str, params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result = self.broker.invoke_tool(capability_id, params or {})
        return {
            "success": result.success,
            "status": result.status.name,
            "output": result.output,
            "error": result.error,
            "policy_decision": result.policy_result.decision.name if result.policy_result else None,
        }

    def get_recent_events(self, n: int = 50) -> list[Event]:
        return self.event_bus.list_recent_events(n)


def run_capability_registration_check(
    core: MockAEGISCore,
    server_info: ServerInfo,
    capabilities: list[Capability],
) -> list[str]:
    """Test capability registration flow.

    Returns a list of errors. Empty list means all tests passed.
    """
    errors: list[str] = []

    # Register capabilities first (so they exist when server registers)
    for cap in capabilities:
        core.register_capability(cap)

    # Update server_info with capability IDs and register server
    server_info.capability_ids = [c.id for c in capabilities]
    core.register_server(server_info)

    server = core.registry.get_server(server_info.server_id)
    if not server:
        errors.append(f"Server '{server_info.server_id}' not found after registration")
        return errors

    # Verify all capabilities are registered
    for cap in capabilities:
        registered = core.registry.get_capability(cap.id)
        if not registered:
            errors.append(f"Capability '{cap.id}' not found after registration")

    # Verify server has capabilities
    server_caps = core.registry.get_capabilities_for_server(server_info.server_id)
    if len(server_caps) != len(capabilities):
        errors.append(
            f"Expected {len(capabilities)} capabilities, got {len(server_caps)}"
        )

    return errors


def run_policy_flow_check(
    core: MockAEGISCore,
    capability: Capability,
    expected_decision: PolicyDecision,
) -> list[str]:
    """Test policy enforcement for a capability.

    Returns a list of errors. Empty list means all tests passed.
    """
    errors: list[str] = []

    core.register_capability(capability)
    result = core.invoke_capability(capability.id)

    actual_status = result.get("status")

    expected_status = _EXPECTED_STATUS_BY_DECISION.get(expected_decision)
    if expected_status is None:
        errors.append(
            f"Unsupported expected_decision {expected_decision!r}; known values: "
            f"{sorted(decision.name for decision in _EXPECTED_STATUS_BY_DECISION)}"
        )
        return errors

    if actual_status != expected_status:
        errors.append(
            f"Expected {expected_status} for '{capability.id}', got {actual_status}"
        )

    return errors


def run_event_push_check(
    core: MockAEGISCore,
    event: Event,
    expected_accepted: bool = True,
) -> list[str]:
    """Test event publishing.

    Returns a list of errors. Empty list means all tests passed.
    """
    errors: list[str] = []

    accepted = core.publish_event(event)
    if accepted != expected_accepted:
        errors.append(
            f"Expected event accepted={expected_accepted}, got {accepted}"
        )

    if expected_accepted:
        recent = core.get_recent_events(10)
        if not any(e.event_id == event.event_id for e in recent):
            errors.append("Event not found in recent events after publish")

    return errors
