"""Agent event publisher (Phase D1 / instruction.md §12).

`AgentEventPublisher` は `EventManager.publish_event` の薄いラッパで、
OpenHands backend / remote backend / 将来追加の backend から
agent.* 8 種類のイベントを **同じ shape** で publish するためのヘルパ。

設計判断:
- EventManager 自体は publisher-agnostic に保ち、ここでは publish_event に
  `agent.{kind}` を渡すだけ。
- 1 agent 実行 = 1 `agent_session_id`。同一 session 内では parent_id を
  直前 event の event_id に連鎖させるが、これは caller 側の責務。
  ここでは id を作らず、受け取った id をそのまま payload に積む。
- payload は **常に dict**。`None` チェック / 文字列 truncation はここで
  行う (呼び出し側に散らさない)。
- `source` は呼び出し側が明示する (例: "openhands_backend" / "remote_openhands_backend")。
- 失敗時: 例外を logger.warning で記録し False を返す。Dashboard 側の障害で
  Agent 実行を止めない。
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger("aegis_ai.event.agent_events")

# Phase D1 で publish する 8 種類の agent event type。
# EventManager._PERSIST_EVENT_TYPES と整合性を保つ (Phase D1 DoD: 両方を更新).
AGENT_EVENT_KINDS: tuple[str, ...] = (
    "agent.started",
    "agent.thinking",
    "agent.tool.started",
    "agent.tool.completed",
    "agent.waiting",
    "agent.verifying",
    "agent.completed",
    "agent.failed",
)


class AgentEventPublisher:
    """agent.* 8 種類の publish ヘルパ.

    Usage:
        publisher = AgentEventPublisher(event_manager, source="openhands_backend")
        publisher.emit_started(task_id="t-1", session_id="s-1", goal="...")
        publisher.emit_thinking(task_id="t-1", session_id="s-1", text="...")
        ...

    `event_manager` が None のときは no-op (Phase 1 / 2 のように EventManager が
    未接続のテストで落ちない).
    """

    def __init__(self, event_manager: Any | None, *, source: str) -> None:
        self._em = event_manager
        self._source = source
        # Phase D3 — Trace ID 6 種 (instruction.md §16) の session 内自動採番.
        # session 開始時に caller が `start_session()` を呼んで agent_session_id
        # と trace_id を確保する. session 内の event は連番の activity_id を
        # 持ち、直前 event の event_id を parent_id に連鎖する.
        self._session_counter: int = 0
        self._last_event_id: str = ""
        self._session_id: str = ""
        self._session_trace_id: str = ""
        self._session_task_id: str = ""

    def start_session(self, *, task_id: str, agent_session_id: str = "", trace_id: str = "") -> str:
        """新規 session 開始. agent_session_id が空なら生成、trace_id も確保.

        戻り値: 確保した agent_session_id. caller はこれを全 emit_* に渡すか、
        `current_session_id()` で取得する.
        """
        import uuid

        self._session_id = agent_session_id or uuid.uuid4().hex
        # 同一 session 配下では trace_id は session_id と一致させる (1 実行 = 1 trace).
        self._session_trace_id = trace_id or self._session_id
        self._session_task_id = str(task_id or "")
        self._session_counter = 0
        self._last_event_id = ""
        return self._session_id

    def end_session(self) -> None:
        """Session 状態をリセット (次回の start_session() 用)."""
        self._session_id = ""
        self._session_trace_id = ""
        self._session_task_id = ""
        self._session_counter = 0
        self._last_event_id = ""

    def current_session_id(self) -> str:
        return self._session_id

    def current_trace_id(self) -> str:
        return self._session_trace_id

    def _next_event_id(self) -> str:
        """session 内で連番の activity_id を採番し、event_id 候補を生成."""
        import uuid

        self._session_counter += 1
        return f"ev-{self._session_id[:8]}-{self._session_counter:04d}-{uuid.uuid4().hex[:6]}"

    # ---- High-level API (Phase D1 仕様) -------------------------------

    def emit_started(
        self,
        *,
        task_id: str,
        agent_session_id: str,
        goal: str = "",
        parent_id: str = "",
    ) -> bool:
        return self._publish(
            "agent.started",
            task_id=task_id,
            agent_session_id=agent_session_id,
            parent_id=parent_id,
            state_text="started",
            goal=_truncate(goal, 2000),
        )

    def emit_thinking(
        self,
        *,
        task_id: str,
        agent_session_id: str,
        text: str,
        parent_id: str = "",
    ) -> bool:
        return self._publish(
            "agent.thinking",
            task_id=task_id,
            agent_session_id=agent_session_id,
            parent_id=parent_id,
            state_text="thinking",
            text=_truncate(text, 4000),
        )

    def emit_tool_started(
        self,
        *,
        task_id: str,
        agent_session_id: str,
        tool: str,
        args: Any = None,
        parent_id: str = "",
    ) -> bool:
        return self._publish(
            "agent.tool.started",
            task_id=task_id,
            agent_session_id=agent_session_id,
            parent_id=parent_id,
            state_text="tool_started",
            tool=str(tool or "unknown"),
            args=_safe_args(args),
        )

    def emit_tool_completed(
        self,
        *,
        task_id: str,
        agent_session_id: str,
        tool: str,
        ok: bool,
        output: Any = None,
        error: str = "",
        duration_ms: int = 0,
        parent_id: str = "",
    ) -> bool:
        return self._publish(
            "agent.tool.completed",
            task_id=task_id,
            agent_session_id=agent_session_id,
            parent_id=parent_id,
            state_text="tool_completed",
            tool=str(tool or "unknown"),
            ok=bool(ok),
            output=_safe_args(output),
            error=_truncate(error, 1000),
            duration_ms=int(duration_ms or 0),
        )

    def emit_waiting(
        self,
        *,
        task_id: str,
        agent_session_id: str,
        approval_id: str,
        tool: str = "",
        parent_id: str = "",
    ) -> bool:
        return self._publish(
            "agent.waiting",
            task_id=task_id,
            agent_session_id=agent_session_id,
            parent_id=parent_id,
            state_text="waiting",
            approval_id=str(approval_id or ""),
            tool=str(tool or ""),
        )

    def emit_verifying(
        self,
        *,
        task_id: str,
        agent_session_id: str,
        command: str,
        parent_id: str = "",
    ) -> bool:
        return self._publish(
            "agent.verifying",
            task_id=task_id,
            agent_session_id=agent_session_id,
            parent_id=parent_id,
            state_text="verifying",
            command=_truncate(command, 1000),
        )

    def emit_completed(
        self,
        *,
        task_id: str,
        agent_session_id: str,
        summary: str = "",
        parent_id: str = "",
    ) -> bool:
        return self._publish(
            "agent.completed",
            task_id=task_id,
            agent_session_id=agent_session_id,
            parent_id=parent_id,
            state_text="completed",
            summary=_truncate(summary, 4000),
        )

    def emit_failed(
        self,
        *,
        task_id: str,
        agent_session_id: str,
        error: str,
        code: str = "",
        parent_id: str = "",
    ) -> bool:
        return self._publish(
            "agent.failed",
            task_id=task_id,
            agent_session_id=agent_session_id,
            parent_id=parent_id,
            state_text="failed",
            error=_truncate(error, 2000),
            code=str(code or ""),
        )

    # ---- Internal -----------------------------------------------------

    def _publish(
        self,
        kind: str,
        *,
        task_id: str,
        agent_session_id: str,
        parent_id: str,
        state_text: str,
        **extra: Any,
    ) -> bool:
        if kind not in AGENT_EVENT_KINDS:
            logger.warning("unknown agent event kind: %s", kind)
            return False
        if self._em is None:
            return False
        # Phase D3 — Trace ID 6 種 (instruction.md §16) を payload に統合.
        # event_id は _next_event_id() で採番し、parent_id 連鎖と activity_id に使う.
        effective_task = str(task_id or self._session_task_id or "")
        effective_session = str(agent_session_id or self._session_id or "")
        effective_trace = self._session_trace_id or effective_session
        event_id = self._next_event_id() if self._session_id else ""
        activity_id = f"activity-{self._session_counter:04d}" if self._session_id else ""
        effective_parent = str(parent_id or self._last_event_id or "")
        payload: dict[str, Any] = {
            "task_id": effective_task,
            "agent_session_id": effective_session,
            "parent_id": effective_parent,
            "state": str(state_text or kind.split(".", 1)[-1]),
            "occurred_at_ms": int(time.time() * 1000),
            "_trace_ids": {
                "event_id": event_id,
                "task_id": effective_task,
                "activity_id": activity_id,
                "agent_session_id": effective_session,
                "trace_id": effective_trace,
                "parent_id": effective_parent,
            },
        }
        if event_id:
            payload["event_id"] = event_id
        payload.update(extra)
        try:
            result = self._em.publish_event(kind, source=self._source, payload=payload)
            if result and event_id:
                # 次の emit_* で parent_id として使えるよう記憶.
                self._last_event_id = event_id
            return bool(result)
        except Exception:  # noqa: BLE001
            logger.warning(
                "AgentEventPublisher.publish failed for %s (source=%s)",
                kind, self._source, exc_info=True,
            )
            return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _truncate(value: Any, max_len: int) -> str:
    """文字列を max_len で切る。None は空文字."""
    if value is None:
        return ""
    text = str(value)
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 1)] + "…"


def _safe_args(value: Any) -> Any:
    """Tool の args / output を JSON-able な形で返す.

    巨大データはそのまま返すが、文字列は 4000 文字で truncation。
    dict / list はそのまま (呼び出し側がすでに serializable 想定).
    """
    if value is None:
        return None
    if isinstance(value, str):
        return _truncate(value, 4000)
    if isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, dict):
        # 値を再帰的に truncation
        return {str(k): _safe_args(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_args(v) for v in value]
    return _truncate(repr(value), 4000)
