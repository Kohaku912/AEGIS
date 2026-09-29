"""Tool Broker compatibility module.

ADR: the canonical implementation currently remains at top-level
``src/tool_broker.py`` because legacy imports, tests, and runtime wiring still
use ``from tool_broker import ...``. The package path is kept as a stable
facade for new code.

Responsibility boundary:
- ToolBroker owns capability execution, policy enforcement, manifest
  completion checks, observation collection, bounded retry, and repair hints.
- TaskExecutionEngine owns task/step state transitions and treats ToolBroker
  verification as the completion condition for each step.
- ``aegis_ai.verification`` owns reusable verification request/result types and
  generic strategy checks that ToolBroker can delegate to when no manifest
  completion condition exists.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "InvokeResult",
    "InvokeStatus",
    "ToolBroker",
    "execute_for_agent",
]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    if name == "execute_for_agent":
        return _execute_for_agent
    from tool_broker import InvokeResult, InvokeStatus, ToolBroker

    exports = {
        "InvokeResult": InvokeResult,
        "InvokeStatus": InvokeStatus,
        "ToolBroker": ToolBroker,
    }
    return exports[name]


def _execute_for_agent(
    capability_id: str,
    params: dict[str, Any] | None = None,
    *,
    profile: Any | None = None,
    context: dict[str, Any] | None = None,
) -> Any:
    """Thin agent-facing wrapper around ``ToolBroker.execute()``.

    Phase 7 (instruction.md §36): the MCP gateway calls this so the
    caller signature stays stable for downstream consumers while the
    actual execution still flows through the canonical broker.

    The wrapper:

    1. Builds a minimal ``ToolExecutionRequest`` (or a duck-typed
       shim) carrying the capability id and arguments.
    2. Records the agent profile in the request context.
    3. Delegates to ``ToolBroker.execute()`` so Policy / Audit are
       not bypassed.
    """
    from tool_broker import ToolBroker, ToolExecutionRequest

    merged_context: dict[str, Any] = dict(context or {})
    if profile is not None:
        merged_context.setdefault("agent_profile", getattr(profile, "id", "unknown"))
        merged_context.setdefault("caller", "agent")

    request = ToolExecutionRequest(
        capability_id=capability_id,
        arguments=dict(params or {}),
    )
    if hasattr(request, "context") and isinstance(request.context, dict):
        request.context.update(merged_context)
    elif hasattr(request, "metadata") and isinstance(request.metadata, dict):
        request.metadata.update(merged_context)

    # Prefer the process-wide singleton broker (registered by
    # ``AegisRuntime``). When none is registered — e.g. in isolated
    # tests, or in code paths that run before startup — fall back to
    # constructing a fresh broker with a default registry. This keeps
    # the gateway usable without forcing every caller to wire a broker.
    broker = ToolBroker.instance()
    if broker is None:
        from aegis_ai.tool_registry import ToolRegistry

        broker = ToolBroker(registry=ToolRegistry())
    return broker.execute(request)

