"""Capability Registry — server and capability registration.

This is the canonical module for the Capability Registry concept.
It re-exports from the ToolRegistry implementation (src/tool_registry.py)
which provides the full implementation.

Architecture reference: docs/architecture.md §5.8

The Capability Registry:
- Stores server info and capability metadata
- Provides search and filtering
- Does NOT execute tools (that's ToolBroker's job)
- Does NOT enforce safety (that's PolicyEngine's job)
"""

from tool_registry import (  # noqa: F401
    RegistryStats,
    ToolRegistry,
)

# Alias for clarity — ToolRegistry IS the CapabilityRegistry
CapabilityRegistry = ToolRegistry

__all__ = [
    "CapabilityRegistry",
    "RegistryStats",
    "ToolRegistry",
]
