"""Base interface for tool bridges (Phase 6 / Phase 9).

A `ToolBridge` maps an AEGIS Capability invocation (e.g.
``ai-server.git.push``) to its actual implementation. There are
two kinds of bridges:

1. **Native** — the capability is implemented directly via Python (no
   gRPC round-trip). Used for the read 3 個 (`repo_status`,
   `diff`, `test_results`) where the work is local
   filesystem inspection.

Each bridge is registered under a single capability id; the registry
lookup `bridge_for_capability()` returns the bridge (or `None` if the
id is unknown).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

logger = logging.getLogger("aegis_ai.tools.bridges.base")

_REGISTRY: dict[str, ToolBridge] = {}


@dataclass
class BridgeResult:
    """Standardized return value for a bridge invocation.

    Mirrors the shape produced by capability invocations so downstream
    callers (TaskExecutionEngine / AgentResult mapping) can consume
    each source uniformly.
    """

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    capability_id: str = ""
    # When the bridge forwards to gRPC, this is the raw reply payload.
    # Useful for tests that want to inspect transport-level details.
    raw: Any = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "success": self.success,
            "capability_id": self.capability_id,
        }
        out.update(self.data)
        if self.error:
            out["error"] = self.error
        return out


@dataclass
class ToolBridge:
    """Mapping from a capability_id to an implementation callable.

    Attributes:
        capability_id: Canonical AEGIS capability id, e.g.
            ``"ai-server.git.push"``.
        kind: ``"native"`` (implemented in-process) or ``"grpc"``
            (legacy passthrough; removed in Phase 9).
        invoke: Callable ``(params: dict, *, context: dict | None) ->
            BridgeResult``. ``context`` is provided by the executor and
            may include ``{"caller": ...}``.
        description: Human-readable summary used by `list_bridges()`.
    """

    capability_id: str
    kind: str
    invoke: Callable[..., BridgeResult]
    description: str = ""

    def __call__(
        self,
        params: Mapping[str, Any] | None = None,
        *,
        context: dict[str, Any] | None = None,
    ) -> BridgeResult:
        try:
            return self.invoke(dict(params or {}), context=context or {})
        except Exception as exc:  # noqa: BLE001 — bridges must not raise
            logger.warning(
                "bridge %s raised %s; returning error result",
                self.capability_id,
                exc,
                exc_info=True,
            )
            return BridgeResult(
                success=False,
                capability_id=self.capability_id,
                error=f"{type(exc).__name__}: {exc}",
            )


def register_bridge(bridge: ToolBridge) -> None:
    """Register a bridge by its capability id. Overwrites any existing one."""
    _REGISTRY[bridge.capability_id] = bridge


def bridge_for_capability(capability_id: str) -> ToolBridge | None:
    """Return the registered bridge for ``capability_id`` or None."""
    return _REGISTRY.get(capability_id)


def list_bridges() -> list[str]:
    """Return all registered capability ids (sorted)."""
    return sorted(_REGISTRY.keys())


def clear_bridges() -> None:
    """Drop all registered bridges. Intended for tests only."""
    _REGISTRY.clear()


__all__ = [
    "BridgeResult",
    "ToolBridge",
    "bridge_for_capability",
    "clear_bridges",
    "list_bridges",
    "register_bridge",
]
