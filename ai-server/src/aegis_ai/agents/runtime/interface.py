"""AgentBackend Protocol — AEGIS ↔ Agent 間の統一 interface.

AEGIS 本体はこの Protocol を満たす backend を `runtime.agent_backend` に保持し、
以下の 3 メソッドだけ呼び出す (instruction.md §8 公開 API):
- `run(task, on_progress=...)` → AgentResult
- `cancel(task_id)` → bool
- `get_status(task_id)` → TaskStatus

Protocol 内に外部 SDK の型を漏らさない. バックエンド具象は
`aegis_ai/agents/backends/<name>/` 配下に閉じ込める.
"""
from __future__ import annotations

from typing import Awaitable, Callable, Protocol, runtime_checkable

from aegis_ai.agents.runtime.models import (
    AgentProgress,
    AgentResult,
    AgentTask,
)
from aegis_ai.task.task_manager import TaskStatus


@runtime_checkable
class AgentBackend(Protocol):
    """AEGIS ↔ Agent 間の境界プロトコル.

    OpenHands / 将来の他 Agent ともにこの Protocol を満たす.
    `name` は CapabilityCatalog の backend 識別子 (Phase 5 で AgentRouter が使用).
    """

    name: str

    async def run(
        self,
        task: AgentTask,
        *,
        on_progress: Callable[[AgentProgress], Awaitable[None]] | None = None,
    ) -> AgentResult: ...

    async def cancel(self, task_id: str) -> bool: ...

    async def get_status(self, task_id: str) -> TaskStatus: ...


__all__ = ["AgentBackend"]
