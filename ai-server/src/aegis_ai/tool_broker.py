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

__all__ = ["InvokeResult", "InvokeStatus", "ToolBroker"]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    from tool_broker import InvokeResult, InvokeStatus, ToolBroker

    exports = {
        "InvokeResult": InvokeResult,
        "InvokeStatus": InvokeStatus,
        "ToolBroker": ToolBroker,
    }
    return exports[name]
