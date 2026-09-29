"""OpenHandsBackend — Phase 2.

`AgentBackend` Protocol を満たし、OpenHands SDK で実際に会話駆動する実装。
このファイルから `from openhands.*` をしてはならない (§6 import 境界).
すべての OpenHands 呼び出しは `adapter.py` 経由。

`AegisRuntime.agent_backend = OpenHandsBackend()` に差し替えるだけで
Local → OpenHands に swap できる (§36 Phase 2 DoD).
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from typing import Any, Callable

from aegis_ai.agents.backends.openhands.adapter import (
    build_agent,
    build_llm,
    build_prompt_from_task,
    build_workspace,
    is_openhands_available,
    run_conversation,
)
from aegis_ai.agents.backends.openhands.config import WorkspaceSpec
from aegis_ai.agents.backends.openhands.event_summary import summarize_openhands_events
from aegis_ai.agents.runtime.interface import AgentBackend
from aegis_ai.agents.runtime.models import (
    AgentAction,
    AgentError,
    AgentProgress,
    AgentResult,
    UsageMetrics,
)
from aegis_ai.event.agent_events import AgentEventPublisher
from aegis_ai.task.task_manager import TaskStatus

logger = logging.getLogger("aegis_ai.agents.backends.openhands.backend")


class OpenHandsBackend(AgentBackend):
    """OpenHands SDK 経由の `AgentBackend` 実装.

    設計判断:
    - `run()` は blocking な `Conversation.run()` を `asyncio.to_thread` で
      別スレッドに逃がす (Phase 3 で TaskExecutionEngine から await される).
    - cancel / get_status は Phase 2 では最小限 (no-op 寄り).
    - LLM 設定は `AgentTask.metadata["llm"]` に dict で渡す.
    - workspace は `AgentTask.metadata["workspace"]` に `WorkspaceSpec` か dict.
    - tool 一覧は `AgentTask.metadata["tools"]` (list[str]). 省略時 default.
    """

    name = "openhands"

    def __init__(
        self,
        *,
        default_workspace: WorkspaceSpec | None = None,
        base_dir: str | None = None,
        default_tools: list[str] | None = None,
        progress_callback: Callable[[AgentProgress], None] | None = None,
        event_manager: Any | None = None,
    ) -> None:
        self._default_workspace = default_workspace or WorkspaceSpec()
        self._base_dir = base_dir or os.getcwd()
        self._default_tools = default_tools or ["terminal", "file_editor", "task_tracker"]
        self._progress_callback = progress_callback
        self._cancelled: set[str] = set()
        self._live_conversations: dict[str, Any] = {}
        self._live_lock = threading.RLock()
        # Phase D1 — agent.* イベントを EventBus に流す publisher.
        # event_manager 未注入 (テスト等) でも no-op で動く.
        self._agent_publisher = AgentEventPublisher(
            event_manager, source="openhands_backend"
        )

    # ---- AgentBackend Protocol ------------------------------------------

    async def run(
        self,
        task: Any,  # AgentTask
        *,
        on_progress: Callable[[AgentProgress], None] | None = None,
    ) -> AgentResult:
        # Phase D3 — start_session() で 1 実行 = 1 agent_session_id / trace_id を確保.
        # session 内の全 emit_* は _trace_ids dict 経由で 6 種 Trace ID を自動付与する.
        agent_session_id = self._agent_publisher.start_session(task_id=task.task_id)
        # Phase D1 — agent.started を最初に発行 (D2 Live Overlay / D4 Trace の起点).
        self._agent_publisher.emit_started(
            task_id=task.task_id,
            agent_session_id=agent_session_id,
            goal=getattr(task, "goal", "") or getattr(task, "description", ""),
        )

        if not is_openhands_available():
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error="openhands-sdk is not installed",
                code="backend_unavailable",
            )
            self._agent_publisher.end_session()
            return self._error_result(
                task,
                code="backend_unavailable",
                message=(
                    "openhands-sdk is not installed. "
                    "Install with: pip install openhands-sdk"
                ),
            )

        started_ms = int(time.time() * 1000)
        try:
            llm = build_llm(_llm_config_from_task(task))
            tools = _tools_from_task(task, self._default_tools)
            agent = build_agent(llm, tools)
            workspace = build_workspace(
                _workspace_from_task(task, self._default_workspace),
                self._base_dir,
            )
            prompt = build_prompt_from_task(task)
        except Exception as exc:  # noqa: BLE001
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error=f"OpenHands setup failed: {exc!r}",
                code="setup_failed",
            )
            self._agent_publisher.end_session()
            return self._error_result(
                task,
                code="setup_failed",
                message=f"OpenHands setup failed: {exc!r}",
                started_ms=started_ms,
            )

        progress = on_progress or self._progress_callback
        def _remember_conversation(conversation: Any) -> None:
            with self._live_lock:
                self._live_conversations[task.task_id] = conversation
            if task.task_id in self._cancelled:
                try:
                    conversation.interrupt()
                except Exception:  # noqa: BLE001
                    logger.debug("failed to interrupt pre-cancelled conversation", exc_info=True)

        try:
            raw = await asyncio.to_thread(
                run_conversation,
                agent=agent,
                workspace=workspace,
                prompt=prompt,
                timeout_seconds=task.timeout_seconds,
                on_progress=(
                    (lambda d: self._emit_progress(progress, task.task_id, d))
                    if progress is not None
                    else None
                ),
                on_conversation_ready=_remember_conversation,
                should_interrupt=lambda: task.task_id in self._cancelled,
            )
        except Exception as exc:  # noqa: BLE001
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error=f"OpenHands run failed: {exc!r}",
                code="execution_error",
            )
            self._agent_publisher.end_session()
            return self._error_result(
                task,
                code="execution_error",
                message=f"OpenHands run failed: {exc!r}",
                started_ms=started_ms,
            )
        finally:
            with self._live_lock:
                self._live_conversations.pop(task.task_id, None)

        result = self._result_from_raw(task, raw, started_ms)
        # Phase D1 — agent.completed を最後にもう 1 つ.
        # 失敗終了していたら emit_failed で上書きせず .completed だけ出す.
        if result.status == TaskStatus.COMPLETED:
            self._agent_publisher.emit_completed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                summary=result.summary,
            )
        elif result.status == TaskStatus.CANCELLED:
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error=result.summary or "agent cancelled",
                code="cancelled",
            )
        elif result.status in (TaskStatus.FAILED, TaskStatus.BLOCKED):
            # error_result() 内で emit_failed 済みなので二重発行しない.
            pass
        self._agent_publisher.end_session()
        self._cancelled.discard(task.task_id)
        return result

    async def cancel(self, task_id: str) -> bool:
        """Phase 2 では LocalBackend と同じく best-effort なフラグだけ.

        別 thread で動いている `Conversation.run()` 自体は SDK 側に cancel API
        がないため強制停止できない。Phase 8 で RemoteAPIWorkspace に置き換える
        ときに真の cancel を実装する。
        """
        self._cancelled.add(task_id)
        with self._live_lock:
            conversation = self._live_conversations.get(task_id)
        if conversation is not None:
            try:
                conversation.interrupt()
            except Exception:  # noqa: BLE001
                logger.debug("OpenHands conversation interrupt failed", exc_info=True)
        return True

    async def get_status(self, task_id: str) -> TaskStatus:
        """Phase 2 では完了前提. 詳細は Phase 3 で SessionStore 接続."""
        return TaskStatus.COMPLETED

    # ---- result shaping -------------------------------------------------

    def _result_from_raw(
        self, task: Any, raw: dict[str, Any], started_ms: int
    ) -> AgentResult:
        events = raw.get("events", [])
        actions = _actions_from_events(events)
        cancelled = bool(raw.get("cancelled", False))
        summary = _summary_from_events(events)
        if cancelled and (
            not summary
            or summary.startswith("OpenHands completed with ")
        ):
            summary = "OpenHands run cancelled"
        finished_ms = int(time.time() * 1000)
        return AgentResult(
            task_id=task.task_id,
            status=TaskStatus.CANCELLED if cancelled else TaskStatus.COMPLETED,
            summary=summary,
            actions=actions,
            artifacts=[],
            tool_calls=[a.capability_id for a in actions],
            errors=(
                [AgentError(code="cancelled", message=summary, recoverable=False)]
                if cancelled
                else []
            ),
            approvals_requested=0,
            suggested_memory=[],
            suggested_follow_ups=[],
            usage=UsageMetrics(
                input_tokens=0,
                output_tokens=0,
                cache_hit_tokens=0,
                cost_usd=0.0,
                model="",
                provider="",
                tool_call_count=len(actions),
                duration_ms=raw.get("elapsed_ms", finished_ms - started_ms),
            ),
        )

    def _error_result(
        self,
        task: Any,
        *,
        code: str,
        message: str,
        started_ms: int | None = None,
    ) -> AgentResult:
        finished_ms = int(time.time() * 1000)
        return AgentResult(
            task_id=task.task_id,
            status=TaskStatus.FAILED,
            summary=message,
            actions=[],
            artifacts=[],
            tool_calls=[],
            errors=[AgentError(code=code, message=message, recoverable=False)],
            approvals_requested=0,
            suggested_memory=[],
            suggested_follow_ups=[],
            usage=UsageMetrics(
                input_tokens=0,
                output_tokens=0,
                cache_hit_tokens=0,
                cost_usd=0.0,
                model="",
                provider="",
                tool_call_count=0,
                duration_ms=finished_ms - (started_ms or finished_ms),
            ),
        )

    def _emit_progress(
        self,
        callback: Callable[[AgentProgress], None] | None,
        task_id: str,
        data: dict[str, Any],
    ) -> None:
        if callback is None:
            return
        try:
            callback(
                AgentProgress(
                    task_id=task_id,
                    stage=str(data.get("stage", "progress")),
                    message=str(data.get("message", "")) or "ok",
                    data=dict(data),
                    timestamp_ms=int(time.time() * 1000),
                )
            )
        except Exception:  # noqa: BLE001
            logger.debug("progress callback raised", exc_info=True)

    def _emit_agent_events_from_oh(
        self, task_id: str, events: list[dict[str, Any]],
    ) -> None:
        """OpenHands event (message / action / observation) → agent.* publish.

        Phase D1 — instruction.md §12.
        既存 `tool.execution.*` / `task.*` とは別 namespace なので二重発行ではない.
        失敗しても Agent 実行は止めない.
        """
        # 直前 tool 名 (action → observation の対にするため).
        last_tool: str = ""
        last_action_ts_ms: int = 0
        for ev in events:
            kind = str(ev.get("kind") or "")
            if kind == "message":
                role = str(ev.get("role") or "")
                if role in ("assistant", "agent"):
                    self._agent_publisher.emit_thinking(
                        task_id=task_id,
                        agent_session_id=task_id,
                        text=str(ev.get("text") or ""),
                    )
            elif kind == "action":
                tool = str(ev.get("tool") or "unknown")
                last_tool = tool
                last_action_ts_ms = int(time.time() * 1000)
                self._agent_publisher.emit_tool_started(
                    task_id=task_id,
                    agent_session_id=task_id,
                    tool=tool,
                    args=ev.get("args"),
                )
            elif kind == "observation":
                # 直前の action の tool と対にする.
                tool = last_tool or str(ev.get("tool") or "unknown")
                self._agent_publisher.emit_tool_completed(
                    task_id=task_id,
                    agent_session_id=task_id,
                    tool=tool,
                    ok=True,
                    output=ev.get("output"),
                    error="",
                    duration_ms=int(time.time() * 1000) - last_action_ts_ms,
                )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _llm_config_from_task(task: Any) -> dict[str, Any]:
    md = getattr(task, "metadata", None) or {}
    llm = md.get("llm")
    if isinstance(llm, dict):
        return llm
    return {}


def _tools_from_task(task: Any, default: list[str]) -> list[str]:
    md = getattr(task, "metadata", None) or {}
    tools = md.get("tools")
    if isinstance(tools, list) and tools:
        return [str(t) for t in tools]
    return list(default)


def _workspace_from_task(task: Any, default: WorkspaceSpec) -> WorkspaceSpec:
    md = getattr(task, "metadata", None) or {}
    ws = md.get("workspace")
    if isinstance(ws, WorkspaceSpec):
        return ws
    if isinstance(ws, dict):
        return WorkspaceSpec(
            mode=ws.get("mode", default.mode),
            path=ws.get("path", default.path),
            mount_ro=ws.get("mount_ro", default.mount_ro),
            protected_paths=list(ws.get("protected_paths", default.protected_paths)),
            base_branch=ws.get("base_branch", default.base_branch),
            worktree_branch=ws.get("worktree_branch", default.worktree_branch),
        )
    return default


def _actions_from_events(events: list[dict[str, Any]]) -> list[AgentAction]:
    """OpenHands の action event → AEGIS AgentAction.

    Phase 2 では action の detail は保持しない (Phase 6 で capability と整合させる).
    ここでは tool_call 件数と ID だけ AgentAction 化する。
    """
    actions: list[AgentAction] = []
    step = 0
    for ev in events:
        if ev.get("kind") != "action":
            continue
        step += 1
        tool = ev.get("tool") or "unknown"
        actions.append(
            AgentAction(
                step_id=f"step-{step}",
                capability_id=f"openhands.tool.{tool}",
                arguments={},
                arguments_hash="",
                result=None,
                error=None,
                duration_ms=0,
            )
        )
    return actions


def _summary_from_events(events: list[dict[str, Any]]) -> str:
    """Prefer final assistant text, else summarize the observed tool activity."""
    return summarize_openhands_events(events, prefix="OpenHands")
