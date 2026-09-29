"""AEGIS MCP Gateway (Phase 7).

Converts AEGIS Capabilities into MCP (Model Context Protocol) tool
schemas, and provides a thin ``tools/call`` shim that funnels every
invocation through the canonical ``ToolBroker.execute()`` so the
Policy / Approval / Audit chain is preserved.

Design notes (instruction.md §14, §15, §36 Phase 7):

- **The actual capability execution entry is still ``ToolBroker.execute``**.
  This module does NOT bypass it. Even when the request arrives via
  MCP wire format, the call lands in ``ToolBroker.execute()`` and is
  subject to the same Policy / Approval / Audit pipeline as any
  other internal invocation.
- **No external SDK import**. ``fastmcp`` / ``mcp`` / ``pydantic`` are
  NOT imported here. The wire format is plain JSON, so the gateway is
  testable without a live MCP transport.
- **Profile-aware visibility**. The list of tools returned by
  ``tools/list`` is filtered through ``AgentProfile.allows_capability``
  and the risk ceiling (see ``CapabilityCatalog.list_for_agent``).
- **Agent never writes files directly**. All writes must go through
  an AEGIS capability (e.g. ``ai-server.workspace.apply_patch``), and
  that capability's manifest is the thing the broker enforces against.

Public API:

- ``list_tools_for_agent(profile, catalog=None)`` — list of MCP tool
  schemas the agent can use.
- ``call_tool_for_agent(tool_name, arguments, *, profile, runtime)`` —
  call one tool. Returns a JSON-RPC-shaped
  response dict with ``content`` and ``isError`` (MCP 2025-06-18).
- ``mcp_tools_list_payload(profile)`` — full ``tools/list`` JSON-RPC
  payload (id/result envelope).
- ``mcp_tools_call_payload(tool_name, arguments, ...)`` — full
  ``tools/call`` JSON-RPC payload.
"""
from __future__ import annotations

import logging
from typing import Any, Mapping

logger = logging.getLogger("aegis_ai.tools.mcp_gateway")

# MCP wire format constants (MCP spec 2025-06-18).
_JSONRPC_VERSION = "2.0"
_MCP_PROTOCOL_VERSION = "2025-06-18"
_SERVER_NAME = "aegis-mcp-gateway"
_SERVER_VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_catalog(catalog: Any | None) -> Any:
    """Return a usable CapabilityCatalog (default singleton)."""
    if catalog is not None:
        return catalog
    from aegis_ai.capability_catalog import CapabilityCatalog

    # ``CapabilityCatalog.instance()`` resolves the capabilities dir via
    # ``aegis_ai.paths`` and caches the catalog for the process.
    return CapabilityCatalog.instance()


def _normalize_arguments(arguments: Any) -> dict[str, Any]:
    """MCP tools/call passes ``arguments`` as an object. Accept either."""
    if arguments is None:
        return {}
    if isinstance(arguments, Mapping):
        return dict(arguments)
    if isinstance(arguments, dict):
        return arguments
    raise ValueError(
        f"tools/call arguments must be an object, got {type(arguments).__name__}"
    )


def _result_to_mcp_content(result: Any) -> list[dict[str, Any]]:
    """Translate a ``ToolBroker.execute()`` result to MCP ``content``.

    MCP ``content`` is a list of typed items. The most common type is
    ``text`` (a UTF-8 string). We use it for everything; structured
    data is JSON-serialised so the agent can re-parse it if needed.
    """
    import json

    text: str
    if result is None:
        text = ""
    elif isinstance(result, str):
        text = result
    elif isinstance(result, (dict, list, tuple)):
        try:
            text = json.dumps(result, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            text = str(result)
    else:
        text = str(result)
    return [{"type": "text", "text": text}]


# ---------------------------------------------------------------------------
# tools/list
# ---------------------------------------------------------------------------


def list_tools_for_agent(
    profile: Any,
    *,
    catalog: Any | None = None,
    feature_flags: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Return the list of MCP tool schemas visible to ``profile``.

    Thin wrapper around ``CapabilityCatalog.mcp_tool_schemas`` that
    picks the right catalog instance by default.
    """
    cat = _get_catalog(catalog)
    return cat.mcp_tool_schemas(profile, feature_flags=feature_flags)


def mcp_tools_list_payload(
    profile: Any,
    *,
    request_id: Any = 1,
    catalog: Any | None = None,
) -> dict[str, Any]:
    """Return the full JSON-RPC ``tools/list`` payload.

    Shape:

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "result": {
        "tools": [ ... ],
        "nextCursor": null
      }
    }
    ```
    """
    tools = list_tools_for_agent(profile, catalog=catalog)
    return {
        "jsonrpc": _JSONRPC_VERSION,
        "id": request_id,
        "result": {
            "tools": tools,
            "nextCursor": None,
        },
    }


# ---------------------------------------------------------------------------
# tools/call
# ---------------------------------------------------------------------------


def call_tool_for_agent(
    tool_name: str,
    arguments: Any,
    *,
    profile: Any,
    runtime: Any,
) -> dict[str, Any]:
    """Call a single MCP tool and return a JSON-RPC-style response.

    Returns:

    ```python
    {
        "content": [{"type": "text", "text": "..."}],
        "isError": False,
    }
    ```

    On a policy / approval gate error, ``isError`` is True and the
    message is surfaced via ``content[0].text``.

    This function NEVER raises for policy / approval decisions — those
    are encoded into the response so the agent can react. Unexpected
    exceptions are caught and converted to ``isError=True`` so the
    gateway remains a reliable single entry point.
    """
    try:
        args = _normalize_arguments(arguments)
    except ValueError as exc:
        return _mcp_error_response(f"invalid arguments: {exc}")

    # Visibility re-check at call time (defence in depth: the list
    # could be cached and a profile could have changed in between).
    try:
        if not _profile_allows_for_call(profile, tool_name):
            return _mcp_error_response(
                f"tool '{tool_name}' is not allowed for the current profile"
            )
    except Exception as exc:  # noqa: BLE001
        return _mcp_error_response(f"profile check failed: {exc}")

    try:
        result = _invoke_via_broker(
            tool_name,
            args,
            profile=profile,
            runtime=runtime,
        )
    except _PolicyDenied as exc:
        return _mcp_error_response(f"policy denied: {exc}")
    except Exception as exc:  # noqa: BLE001
        logger.warning("mcp_gateway call_tool failed for %s: %s", tool_name, exc, exc_info=True)
        return _mcp_error_response(f"{type(exc).__name__}: {exc}")

    is_error = False
    try:
        status = getattr(result, "status", None)
        success = getattr(result, "success", None)
        if success is False:
            is_error = True
        elif status is not None and getattr(status, "value", "") not in {"", "success"}:
            is_error = True
    except Exception:
        is_error = False

    response = {
        "content": _result_to_mcp_content(result),
        "isError": is_error,
    }
    if is_error:
        response["error_code"] = str(getattr(getattr(result, "status", None), "value", "") or "execution_error")
        response["error"] = str(getattr(result, "error", "") or "tool execution failed")
    return response


def mcp_tools_call_payload(
    tool_name: str,
    arguments: Any,
    *,
    profile: Any,
    runtime: Any,
    request_id: Any = 1,
) -> dict[str, Any]:
    """Return the full JSON-RPC ``tools/call`` payload."""
    body = call_tool_for_agent(
        tool_name,
        arguments,
        profile=profile,
        runtime=runtime,
    )
    return {
        "jsonrpc": _JSONRPC_VERSION,
        "id": request_id,
        "result": body,
    }


# ---------------------------------------------------------------------------
# server info (initialize handshake)
# ---------------------------------------------------------------------------


def mcp_initialize_payload(*, request_id: Any = 1) -> dict[str, Any]:
    """Return the ``initialize`` handshake payload.

    MCP clients expect a small server-info envelope at startup.
    """
    return {
        "jsonrpc": _JSONRPC_VERSION,
        "id": request_id,
        "result": {
            "protocolVersion": _MCP_PROTOCOL_VERSION,
            "serverInfo": {"name": _SERVER_NAME, "version": _SERVER_VERSION},
            "capabilities": {"tools": {"listChanged": False}},
        },
    }


# ---------------------------------------------------------------------------
# Internal: visibility + invocation
# ---------------------------------------------------------------------------


class _PolicyDenied(Exception):
    """Raised by ``PolicyEngine`` when the call is denied outright."""


def _profile_allows_for_call(profile: Any, tool_name: str) -> bool:
    """Re-check at call time. Mirrors ``CapabilityCatalog.list_for_agent``."""
    from aegis_ai.capability_catalog import _profile_allows  # type: ignore

    return bool(_profile_allows(profile, tool_name))


def _invoke_via_broker(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    profile: Any,
    runtime: Any,
) -> Any:
    """Dispatch through ``ToolBroker.execute()``.

    The broker path is the canonical capability entry. We use the
    facade ``aegis_ai.tool_broker.ToolBroker`` (which itself proxies to
    the real ``src/tool_broker.py``) so we never depend on the
    top-level module.

    The broker expects a ``ToolExecutionRequest`` object. We build the
    smallest request that exercises the full Policy / Audit chain. If
    the request dataclass is unavailable in this build (very old code),
    we fall back to a duck-typed shim so the gateway still functions.
    """
    from aegis_ai.tool_broker import ToolBroker  # type: ignore

    broker: Any = getattr(runtime, "tool_broker", None)
    if broker is None:
        # Fall back to instantiating a default broker. This keeps the
        # gateway usable in tests and minimal deployments. We pass a
        # fresh ``ToolRegistry`` so the broker is self-contained.
        from aegis_ai.tool_registry import ToolRegistry  # type: ignore

        broker = ToolBroker(registry=ToolRegistry())

    request: Any
    try:
        # Preferred path: use the real ToolExecutionRequest so every
        # downstream consumer (Policy / Approval / Audit / OTel) sees
        # the same shape it would see for any other call.
        from tool_broker import ToolExecutionRequest  # type: ignore

        request = ToolExecutionRequest(
            capability_id=tool_name,
            arguments=arguments,
        )
    except Exception:  # noqa: BLE001
        # Fallback: construct a minimal duck-typed request. The broker
        # only uses ``.capability_id`` and ``.arguments`` for the
        # simple path; richer fields default safely.
        class _ShimRequest:
            def __init__(self, cap: str, args: dict[str, Any]) -> None:
                self.capability_id = cap
                self.arguments = args
                self.source = None
                self.context: dict[str, Any] = {}
                self.dry_run = False
                self.idempotency_key = ""
                self.request_id = ""
                self.created_at = 0

        request = _ShimRequest(tool_name, arguments)

    # The agent's profile is recorded for audit. The actual policy
    # gate lives inside ``broker.execute()``.
    context: dict[str, Any] = {
        "caller": "mcp_gateway",
        "agent_profile": getattr(profile, "id", "unknown"),
    }
    # Attach context to the request if it has a slot for it.
    if hasattr(request, "context") and isinstance(request.context, dict):
        request.context.update(context)
    elif hasattr(request, "metadata") and isinstance(request.metadata, dict):
        request.metadata.update(context)

    result = broker.execute(request)
    return result


def _mcp_error_response(message: str) -> dict[str, Any]:
    """Build an MCP ``isError=True`` response."""
    return {
        "content": [{"type": "text", "text": str(message)}],
        "isError": True,
    }


__all__ = [
    "list_tools_for_agent",
    "call_tool_for_agent",
    "mcp_tools_list_payload",
    "mcp_tools_call_payload",
    "mcp_initialize_payload",
]
