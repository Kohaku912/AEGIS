"""RemoteOpenHandsBackend — Phase 8 (Agent Server 分離).

`AgentBackend` Protocol を満たし、OpenHands SDK 呼び出しを **別プロセス
(`aegis-openhands-agent.service`) に HTTP で委譲する** 実装。

AEGIS 本体プロセスには `openhands-sdk` をインストールしなくてよい
(Phase 8 DoD). SDK が必要な処理は agent server 側で実行され、結果と
progress は JSON / SSE で受け取る。

agent server が落ちている / 接続できないときは `AgentResult` を
`status=BLOCKED, error.code="agent_unavailable"` で返す (Phase 8 DoD:
AEGIS 側は落ちない).

このファイルから `from openhands.*` をしてはならない (§6 / §35.4).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any, Callable

from aegis_ai.agents.backends.openhands.event_summary import (
    is_generic_openhands_summary,
    summarize_openhands_events,
)
from aegis_ai.agents.backends.openhands.workspace import (
    RemoteAPIError,
    RemoteAPIWorkspace,
    Workspace,
)
from aegis_ai.agents.runtime.interface import AgentBackend
from aegis_ai.agents.runtime.models import (
    AgentAction,
    AgentError,
    AgentProgress,
    AgentResult,
    UsageMetrics,
)
from aegis_ai.agents.runtime.session_store import SessionStore
from aegis_ai.event.agent_events import AgentEventPublisher
from aegis_ai.task.task_manager import TaskStatus

logger = logging.getLogger("aegis_ai.agents.backends.openhands.remote_backend")


class RemoteOpenHandsBackend(AgentBackend):
    """`AgentBackend` の remote 実装.

    Args:
        server_url: agent server の URL (`http://host:port`).
        workspace: 事前に build した `Workspace` (RemoteAPIWorkspace 推奨).
        session_store: 会話再開用 JSONL store. None なら `root` から生成.
        session_root: `session_store` 未指定時に JSONL を保存する root ディレクトリ.
        timeout_seconds: 1 task 実行の上限.
    """

    name = "remote_openhands"

    def __init__(
        self,
        *,
        server_url: str | None = None,
        workspace: Workspace | None = None,
        session_store: SessionStore | None = None,
        session_root: str | None = None,
        timeout_seconds: float = 600.0,
        progress_callback: Callable[[AgentProgress], None] | None = None,
        http_post: Callable[..., Any] | None = None,
        event_manager: Any | None = None,
    ) -> None:
        self._server_url = server_url or os.environ.get("AGENT_SERVER_URL") or ""
        if workspace is None:
            workspace = RemoteAPIWorkspace(
                server_url=self._server_url,
                http_post=http_post,
            )
        if not isinstance(workspace, RemoteAPIWorkspace):
            # Caller passed a non-remote workspace. Override with remote one
            # using the same server URL. This keeps the facade safe even
            # when the caller wires the wrong kind.
            workspace = RemoteAPIWorkspace(server_url=self._server_url, http_post=http_post)
        elif http_post is not None:
            # Inject the test HTTP poster into the existing remote workspace
            workspace._http_post = http_post  # type: ignore[attr-defined]
        self._workspace = workspace
        if session_store is None:
            session_store = SessionStore(
                root=session_root or os.environ.get("AGENT_SESSION_ROOT", "data/agent_sessions"),
            )
        self._session_store = session_store
        self._timeout = float(timeout_seconds)
        self._progress_callback = progress_callback
        self._cancelled: set[str] = set()
        # Phase D1 — agent.* イベントを EventBus に流す publisher.
        self._agent_publisher = AgentEventPublisher(
            event_manager, source="remote_openhands_backend"
        )

    @property
    def session_store(self) -> SessionStore:
        return self._session_store

    @property
    def workspace(self) -> Workspace:
        return self._workspace

    # ---- AgentBackend Protocol ------------------------------------------

    async def run(
        self,
        task: Any,  # AgentTask
        *,
        on_progress: Callable[[AgentProgress], None] | None = None,
    ) -> AgentResult:
        # Phase D3 — start_session() で 1 実行 = 1 agent_session_id / trace_id を確保.
        agent_session_id = self._agent_publisher.start_session(task_id=task.task_id)
        # Phase D1 — agent.started を最初に発行.
        self._agent_publisher.emit_started(
            task_id=task.task_id,
            agent_session_id=agent_session_id,
            goal=getattr(task, "goal", "") or getattr(task, "description", ""),
        )

        started_ms = int(time.time() * 1000)
        server_url = self._server_url
        if not server_url:
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error="AGENT_SERVER_URL is not configured",
                code="agent_unavailable",
            )
            self._agent_publisher.end_session()
            return self._error_result(
                task,
                code="agent_unavailable",
                message="AGENT_SERVER_URL is not configured",
                started_ms=started_ms,
            )

        # health check first — fail fast before doing real work
        health = self._workspace.healthcheck(
            timeout_seconds=min(max(self._timeout, 5.0), 30.0)
        )
        if health.get("status") == "unreachable":
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error=f"agent server unreachable at {server_url}: {health.get('error', 'no response')}",
                code="agent_unavailable",
            )
            self._agent_publisher.end_session()
            return self._error_result(
                task,
                code="agent_unavailable",
                message=(
                    f"agent server unreachable at {server_url}: "
                    f"{health.get('error', 'no response')}"
                ),
                started_ms=started_ms,
            )

        payload = _build_request_payload(task, self._workspace)
        try:
            response = await asyncio.to_thread(
                self._workspace.post_json,
                "/mcp",
                {"method": "tools/call", "params": payload},
                timeout_seconds=_request_timeout_seconds(task, self._timeout),
            )
            if isinstance(response, dict) and "result" in response and isinstance(response.get("result"), dict):
                response = dict(response.get("result") or {})
            elif isinstance(response, dict) and "error" in response and isinstance(response.get("error"), dict):
                err = dict(response.get("error") or {})
                response = {
                    "is_error": True,
                    "error_code": str(err.get("code") or "agent_server_error"),
                    "error": str(err.get("message") or "agent server returned error"),
                    "events": [],
                }
        except RemoteAPIError as exc:
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error=f"agent server call failed: {exc}",
                code="agent_unavailable",
            )
            self._agent_publisher.end_session()
            return self._error_result(
                task,
                code="agent_unavailable",
                message=f"agent server call failed: {exc}",
                started_ms=started_ms,
            )
        except Exception as exc:  # noqa: BLE001
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error=f"unexpected error contacting agent server: {exc!r}",
                code="execution_error",
            )
            self._agent_publisher.end_session()
            return self._error_result(
                task,
                code="execution_error",
                message=f"unexpected error contacting agent server: {exc!r}",
                started_ms=started_ms,
            )

        # Persist events to session store for resume (best-effort)
        events = response.get("events", []) or []
        try:
            self._session_store.extend(task.task_id, events)
        except Exception:  # noqa: BLE001
            logger.warning("session_store.extend failed for %s", task.task_id, exc_info=True)

        result = self._result_from_response(task, response, started_ms)
        # Phase D1 — 最終ステータスを反映.
        if result.status == TaskStatus.COMPLETED:
            self._agent_publisher.emit_completed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                summary=result.summary,
            )
        else:
            # FAILED / BLOCKED のときは emit_failed を補完発行.
            err = result.errors[0].message if result.errors else "agent failed"
            code = result.errors[0].code if result.errors else "execution_error"
            self._agent_publisher.emit_failed(
                task_id=task.task_id,
                agent_session_id=agent_session_id,
                error=err,
                code=code,
            )
        self._agent_publisher.end_session()
        return result

    async def cancel(self, task_id: str) -> bool:
        """best-effort cancel. agent server 側に cancel を通知する."""
        self._cancelled.add(task_id)
        try:
            await asyncio.to_thread(
                self._workspace.post_json,
                f"/cancel/{task_id}",
                {},
            )
            return True
        except RemoteAPIError:
            return False
        except Exception:  # noqa: BLE001
            return False

    async def get_status(self, task_id: str) -> TaskStatus:
        """SessionStore に events があれば last event の status を返す。"""
        events = self._session_store.load(task_id)
        if not events:
            return TaskStatus.PENDING
        last = events[-1]
        kind = str(last.get("kind", ""))
        if kind == "completed":
            return TaskStatus.COMPLETED
        if kind == "failed":
            return TaskStatus.FAILED
        if kind == "cancelled":
            return TaskStatus.CANCELLED
        return TaskStatus.RUNNING

    # ---- helpers --------------------------------------------------------

    def _result_from_response(
        self,
        task: Any,
        response: dict[str, Any],
        started_ms: int,
    ) -> AgentResult:
        events = response.get("events", []) or []
        is_error = bool(response.get("is_error", False))
        error_code = str(response.get("error_code", "agent_unavailable"))
        actions = _actions_from_events(events)
        summary = _summary_from_response(response, events)
        finished_ms = int(time.time() * 1000)
        if is_error and error_code == "cancelled":
            status = TaskStatus.CANCELLED
        else:
            status = TaskStatus.BLOCKED if is_error else TaskStatus.COMPLETED
        if is_error:
            errors = [
                AgentError(
                    code=error_code,
                    message=str(response.get("error", "agent server returned error")),
                    recoverable=False,
                )
            ]
        else:
            errors = []
        return AgentResult(
            task_id=task.task_id,
            status=status,
            summary=summary,
            actions=actions,
            artifacts=[],
            tool_calls=[a.capability_id for a in actions],
            errors=errors,
            approvals_requested=0,
            suggested_memory=[],
            suggested_follow_ups=[],
            usage=UsageMetrics(
                input_tokens=int(response.get("usage", {}).get("input_tokens", 0) or 0),
                output_tokens=int(response.get("usage", {}).get("output_tokens", 0) or 0),
                cache_hit_tokens=int(response.get("usage", {}).get("cache_hit_tokens", 0) or 0),
                cost_usd=float(response.get("usage", {}).get("cost_usd", 0.0) or 0.0),
                model=str(
                    response.get("model", "")
                    or response.get("usage", {}).get("model", "")
                    or ""
                ),
                provider=str(response.get("provider", "") or ""),
                tool_call_count=len(actions),
                duration_ms=int(response.get("duration_ms", finished_ms - started_ms) or 0),
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
            status=TaskStatus.BLOCKED,
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

    def _emit_agent_events_from_oh(
        self, task_id: str, events: list[dict[str, Any]],
    ) -> None:
        """OpenHands event (message / action / observation) → agent.* publish.

        Phase D1 — instruction.md §12.
        既存 `tool.execution.*` / `task.*` とは別 namespace なので二重発行ではない.
        失敗しても Agent 実行は止めない.
        """
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
# helpers
# ---------------------------------------------------------------------------


def _build_request_payload(task: Any, workspace: Workspace) -> dict[str, Any]:
    """agent server の `/mcp tools/call` に渡す payload を組み立てる.

    仕様 (Phase 8): agent server は MCP JSON-RPC 形式で `tools/call` を受け、
    capability_id で AEGIS 側 capability を実行する (Phase 7 MCP gateway と
    同じ protocol). task 全体は 1 つの `agent.run` capability に wrap される.
    """
    md = getattr(task, "metadata", None) or {}
    goal = getattr(task, "description", "") or getattr(task, "goal", "")
    return {
        "name": "agent.run",
        "arguments": {
            "goal": goal,
            "session_id": task.task_id,
            "workspace": {
                "mode": getattr(workspace.spec, "mode", "isolated") if hasattr(workspace, "spec") else "isolated",
                "path": getattr(workspace.spec, "path", None) if hasattr(workspace, "spec") else None,
            },
            "llm": md.get("llm", {}) if isinstance(md.get("llm"), dict) else {},
            "tools": list(md.get("tools", []) or []),
            "metadata": {
                k: v
                for k, v in md.items()
                if k not in ("llm", "tools", "workspace")
            },
        },
    }


def _request_timeout_seconds(task: Any, default_timeout: float) -> float:
    """Use the task budget for the agent.run HTTP request, plus small slack."""
    task_timeout = float(getattr(task, "timeout_seconds", 0) or 0)
    if task_timeout <= 0:
        return float(default_timeout)
    return max(float(default_timeout), task_timeout + 15.0)


def _actions_from_events(events: list[dict[str, Any]]) -> list[AgentAction]:
    actions: list[AgentAction] = []
    step = 0
    for ev in events:
        if ev.get("kind") != "action":
            continue
        step += 1
        tool = ev.get("tool") or "unknown"
        try:
            arguments = json.loads(ev.get("arguments", "{}")) if isinstance(ev.get("arguments"), str) else ev.get("arguments", {})
        except json.JSONDecodeError:
            arguments = {}
        actions.append(
            AgentAction(
                step_id=f"step-{step}",
                capability_id=str(tool),
                arguments=arguments if isinstance(arguments, dict) else {},
                arguments_hash="",
                result=None,
                error=None,
                duration_ms=int(ev.get("duration_ms", 0) or 0),
            )
        )
    return actions


def _summary_from_response(response: dict[str, Any], events: list[dict[str, Any]]) -> str:
    summary = response.get("summary")
    if (
        isinstance(summary, str)
        and summary
        and not is_generic_openhands_summary(summary)
    ):
        return summary[:4000]
    return summarize_openhands_events(events, prefix="RemoteOpenHands")


__all__ = ["RemoteOpenHandsBackend"]
