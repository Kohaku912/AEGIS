"""AEGIS tools — bridges between AEGIS Capabilities and external systems.

Phase 6 (instruction.md §36): bridges forward capability invocations
to the appropriate backend (native / dev-server gRPC / future MCP).
Phase 7 (§36): ``mcp_gateway`` exposes Capabilities as MCP tool schemas
without bypassing ``ToolBroker.execute()``.
"""
from aegis_ai.tools import bridges
from aegis_ai.tools import mcp_gateway

__all__ = ["bridges", "mcp_gateway"]
