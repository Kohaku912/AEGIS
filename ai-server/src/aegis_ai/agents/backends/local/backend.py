"""Local subprocess backend — Phase 1 最小実装.

`AgentTask.goal` を echo するダミー backend. 既存 Capability を経由せず
直接 `AgentResult` を返すため、Phase 1 DoD の read-only テスト専用.

Phase 2 で `OpenHandsBackend` に差し替えるか、Phase 1 の LocalBackend
を sub-agent (OpenHands LocalWorkspace) で起動する実装に拡張する.
"""
from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
import time

from aegis_ai.agents.runtime.models import (
    AgentAction,
    AgentProgress,
    AgentResult,
    AgentTask,
    UsageMetrics,
)
from aegis_ai.task.task_manager import TaskStatus

logger = logging.getLogger("aegis_ai.agents.backends.local.backend")


class LocalBackend:
    """Local subprocess backend.

    Attributes:
        name: Backend identifier ("local").
        cli_module: Python module path of the CLI entrypoint. Default uses
            this package's `cli` module which echoes the goal.
    """

    name = "local"

    def __init__(
        self,
        cli_module: str = "aegis_ai.agents.backends.local.cli",
        python_executable: str | None = None,
    ) -> None:
        self._cli_module = cli_module
        self._python_executable = python_executable or sys.executable

    async def run(
        self,
        task: AgentTask,
        *,
        on_progress=None,  # Callable[[AgentProgress], Awaitable[None]] | None
    ) -> AgentResult:
        """Run the local CLI subprocess and return its AgentResult JSON."""
        started_ms = int(time.time() * 1000)
        if on_progress is not None:
            await on_progress(
                AgentProgress(
                    task_id=task.task_id,
                    stage="started",
                    message=f"local backend start: {task.goal[:80]}",
                    timestamp_ms=started_ms,
                )
            )
        try:
            payload = await asyncio.to_thread(self._run_subprocess, task)
        except FileNotFoundError as e:
            return self._error_result(task, code="cli_not_found", message=str(e), started_ms=started_ms)
        except subprocess.TimeoutExpired as e:
            return self._error_result(
                task,
                code="timeout",
                message=f"local backend timeout after {task.timeout_seconds}s",
                started_ms=started_ms,
            )
        except Exception as e:  # noqa: BLE001
            logger.exception("Local backend failed")
            return self._error_result(task, code="local_backend_error", message=str(e), started_ms=started_ms)

        finished_ms = int(time.time() * 1000)
        result = self._parse_result(task, payload, started_ms=finished_ms)
        if on_progress is not None:
            await on_progress(
                AgentProgress(
                    task_id=task.task_id,
                    stage="finished",
                    message=f"local backend finished: {result.status.value}",
                    timestamp_ms=finished_ms,
                )
            )
        return result

    async def cancel(self, task_id: str) -> bool:
        # Phase 1: synchronous subprocess; cancel is a no-op.
        # Phase 2 以降: 実行中 subprocess を task_id で管理し SIGTERM を送る.
        logger.info("LocalBackend.cancel(%s) called (no-op in Phase 1)", task_id)
        return False

    async def get_status(self, task_id: str) -> TaskStatus:
        # Phase 1: 状態を持たない. 完了 or 失敗のみ返せる.
        return TaskStatus.COMPLETED

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _run_subprocess(self, task: AgentTask) -> dict:
        request = {
            "task_id": task.task_id,
            "goal": task.goal,
            "context": task.context,
            "tools": task.tools,
            "max_steps": task.max_steps,
            "metadata": task.metadata,
        }
        proc = subprocess.run(
            [self._python_executable, "-m", self._cli_module],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=task.timeout_seconds,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"local cli exit={proc.returncode} stderr={proc.stderr.strip()[:500]}"
            )
        stdout = proc.stdout.strip()
        if not stdout:
            raise RuntimeError("local cli produced empty stdout")
        return json.loads(stdout)

    def _parse_result(self, task: AgentTask, payload: dict, started_ms: int) -> AgentResult:
        """Convert CLI JSON payload to AgentResult dataclass."""
        try:
            status = TaskStatus(payload.get("status", "completed"))
        except ValueError:
            status = TaskStatus.FAILED
        actions = [AgentAction(**a) for a in payload.get("actions", []) if isinstance(a, dict)]
        tool_calls = [AgentAction(**a) for a in payload.get("tool_calls", []) if isinstance(a, dict)]
        usage_data = payload.get("usage") or {}
        usage = UsageMetrics(
            input_tokens=int(usage_data.get("input_tokens", 0)),
            output_tokens=int(usage_data.get("output_tokens", 0)),
            cache_hit_tokens=int(usage_data.get("cache_hit_tokens", 0)),
            cost_usd=float(usage_data.get("cost_usd", 0.0)),
            model=str(usage_data.get("model", "")),
            provider=str(usage_data.get("provider", "")),
            tool_call_count=int(usage_data.get("tool_call_count", 0)),
            duration_ms=int(usage_data.get("duration_ms", 0)),
        )
        return AgentResult(
            task_id=task.task_id,
            status=status,
            summary=str(payload.get("summary", "")),
            actions=actions,
            artifacts=list(payload.get("artifacts", [])),
            tool_calls=tool_calls,
            errors=list(payload.get("errors", [])),
            approvals_requested=list(payload.get("approvals_requested", [])),
            suggested_memory=list(payload.get("suggested_memory", [])),
            suggested_follow_ups=list(payload.get("suggested_follow_ups", [])),
            usage=usage,
        )

    def _error_result(
        self, task: AgentTask, *, code: str, message: str, started_ms: int
    ) -> AgentResult:
        return AgentResult(
            task_id=task.task_id,
            status=TaskStatus.FAILED,
            summary=f"local backend error: {code}",
            errors=[{"code": code, "message": message, "recoverable": True}],
        )


__all__ = ["LocalBackend"]
