"""AEGIS tools — expose AEGIS Capabilities to agents.

Phase 7 (instruction.md §36): ``mcp_gateway`` exposes Capabilities as MCP tool
schemas without bypassing ``ToolBroker.execute()``.

Phase 6's ``tools/bridges/`` package was **deleted 2026-10-08** (DELEGATION.md
§4 item 53). It was never wired: ``register_default_bridges()`` and
``bridge_for_capability()`` had no caller outside its own test module, so the
registry stayed empty in production and the three ``ai-server.workspace.*``
capability ids it declared resolved nowhere (they are in no manifest, so
``CapabilityCatalog.resolve()`` could not return them). Pinned by
``ai-server/tests/test_tool_bridges_surface_is_gone.py``.
"""
from aegis_ai.tools import mcp_gateway

__all__ = ["mcp_gateway"]
