"""Agent Sessions routes (Phase D4-D5 / instruction.md §9, §10, §11).

Agent 1 実行 = 1 `agent_session_id` (Phase D3 で導入) 単位で events を
集約し、Dashboard の tabs (Overview / Thinking / Tools / MCP / Files /
Terminal / Errors / Raw) に流す。

このモジュールは EventManager.persisted events を
**読み取り専用** で走査する。Publisher への書き込みは一切しない。

API:
- `GET /api/ui/agent-sessions`                        — session 一覧
- `GET /api/ui/agent-sessions/<id>`                   — 詳細 (summary + 関連 events)
- `GET /api/ui/agent-sessions/<id>/events?kinds=...` — kinds フィルタで events 取得

設計判断:
- persisted events の source of truth は EventManager (`list_recent`)。
  新たな永続化層を増やさない (Phase D9 Retention 実装に任せる)。
- `agent.*` 8 種類に閉じず、`tool.execution.*` / `task.*` /
  `policy.decision` (Phase D5) も trace_id / agent_session_id で link
  しているものは対象にする (関連 event を 1 つの session にまとめる)。
- session_id 抽出は payload の `_trace_ids.agent_session_id` を優先し、
  なければ `agent_session_id` フィールドに fallback。両方空なら
  "unassigned" bucket に分類。
- limit / kinds パラメータでレスポンスサイズを制御。
- Phase D5 summary 拡張: allow_count / deny_count / highest_risk を
  1 session 単位で集計。`ask_count` / `approval_count` / `pending_approval`
  はキーだけ残し、常に 0 / False を返す (承認撤去後の互換シム)。
"""

from __future__ import annotations

import logging
import time
from typing import Any, Iterable

from flask import Blueprint, jsonify, request

logger = logging.getLogger("aegis_ai.web.routes.agent_sessions")

# 集約対象の event_type (Phase D4 で 9 tabs に分配する).
# `agent.*` 8 種類 + `tool.execution.*` + `task.*` を link.
# Phase D5 で `policy.decision` (AuditManager → EventBus) を追加.
# 9 tabs のうち Files / Terminal は `agent.tool.*` の `tool` フィールドが
# `file.*` / `terminal.*` で始まる event を抽出して表現する.
_AGGREGATABLE_KINDS: frozenset[str] = frozenset({
    "agent.started",
    "agent.thinking",
    "agent.tool.started",
    "agent.tool.completed",
    "agent.waiting",
    "agent.verifying",
    "agent.completed",
    "agent.failed",
    "tool.execution.started",
    "tool.execution.completed",
    "tool.execution.failed",
    "task.created",
    "task.updated",
    "task.completed",
    "task.failed",
    "task.cancelled",
    # Phase D5 — Policy 表示統合
    "policy.decision",
})

# Phase D5 — policy.decision イベントの decision 値 → 集計キー
# (PolicyDecision = ALLOW / ALLOW_WITH_AUDIT / DENY / UNAVAILABLE)
_POLICY_ALLOW_LIKE: frozenset[str] = frozenset({
    "ALLOW", "ALLOW_WITH_AUDIT",
})
_POLICY_DENY: frozenset[str] = frozenset({
    "DENY",
})
# risk_level 値の大小 (Phase D5 summary の highest_risk 計算用)
# APPROVAL_REQUIRED は「リスク注記」として残る (ALLOW_WITH_AUDIT に写像される)。
_RISK_ORDER: dict[str, int] = {
    "READ_ONLY": 1,
    "SAFE_ACTION": 2,
    "APPROVAL_REQUIRED": 3,
    "HIGH_RISK": 4,
    "FORBIDDEN": 5,
    "UNSPECIFIED": 0,
}

_DEFAULT_LIMIT = 200
_MAX_LIMIT = 2000
_UNASSIGNED = "unassigned"
_FAILED_KINDS: frozenset[str] = frozenset({
    "agent.failed",
    "tool.execution.failed",
})


def init_agent_sessions_routes(owner: Any) -> None:
    """Agent Sessions の 3 つの Blueprint route を owner.app に登録する."""
    bp = Blueprint("agent_sessions_api", __name__)

    @bp.route("/api/ui/agent-sessions", methods=["GET"])
    def list_agent_sessions():
        runtime = owner._runtime
        limit = _clamp_limit(request.args.get("limit"))
        events = _fetch_persisted_events(runtime, limit=limit)
        sessions = _group_by_session(events)
        return jsonify(
            {
                "generated_at": _now_ms(),
                "count": len(sessions),
                "sessions": sessions,
            }
        )

    @bp.route("/api/ui/agent-sessions/<agent_session_id>", methods=["GET"])
    def get_agent_session(agent_session_id: str):
        runtime = owner._runtime
        limit = _clamp_limit(request.args.get("limit"))
        events = _fetch_persisted_events(runtime, limit=limit)
        session_events = _filter_by_session(events, agent_session_id)
        if not session_events:
            # 404 の代わりに 200 + empty summary を返すと UI 側で 404 扱いにできる。
            return jsonify(
                {
                    "generated_at": _now_ms(),
                    "agent_session_id": agent_session_id,
                    "found": False,
                    "summary": _empty_summary(agent_session_id),
                    "events": [],
                }
            ), 404
        summary = _build_summary(agent_session_id, session_events)
        return jsonify(
            {
                "generated_at": _now_ms(),
                "agent_session_id": agent_session_id,
                "found": True,
                "summary": summary,
                "events": session_events,
                "causal_chain": _build_causal_chain(session_events),
            }
        )

    @bp.route("/api/ui/agent-sessions/<agent_session_id>/events", methods=["GET"])
    def get_agent_session_events(agent_session_id: str):
        runtime = owner._runtime
        kinds = _parse_kinds(request.args.get("kinds"))
        limit = _clamp_limit(request.args.get("limit"))
        events = _fetch_persisted_events(runtime, limit=limit)
        session_events = _filter_by_session(events, agent_session_id)
        if kinds:
            session_events = [e for e in session_events if _event_kind(e) in kinds]
        return jsonify(
            {
                "generated_at": _now_ms(),
                "agent_session_id": agent_session_id,
                "count": len(session_events),
                "kinds": sorted(kinds) if kinds else None,
                "events": session_events,
            }
        )

    owner.app.register_blueprint(bp)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_ms() -> int:
    return int(time.time() * 1000)


def _clamp_limit(raw: str | None) -> int:
    if raw is None or raw == "":
        return _DEFAULT_LIMIT
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return _DEFAULT_LIMIT
    return max(1, min(value, _MAX_LIMIT))


def _parse_kinds(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {piece.strip() for piece in raw.split(",") if piece.strip()}


def _fetch_persisted_events(runtime: Any, *, limit: int) -> list[dict[str, Any]]:
    """EventManager.persisted events を古い順で取得 (limit 件)."""
    em = getattr(runtime, "event_manager", None)
    if em is None:
        return []
    fn = getattr(em, "list_recent", None)
    if not callable(fn):
        return []
    try:
        result = fn(limit=limit)
    except Exception:  # noqa: BLE001
        logger.debug("event_manager.list_recent failed", exc_info=True)
        return []
    if not isinstance(result, dict):
        return []
    events = result.get("events") or []
    if not isinstance(events, list):
        return []
    # EventManager.list_recent は古い順で返すのでそのまま使う.
    return events


def _event_kind(event: dict[str, Any]) -> str:
    return str(event.get("type") or event.get("event_type") or "")


def _extract_session_id(event: dict[str, Any]) -> str:
    """payload の `_trace_ids.agent_session_id` → `agent_session_id` フィールドの順で探す."""
    payload = event.get("payload") if isinstance(event, dict) else None
    if not isinstance(payload, dict):
        return _UNASSIGNED
    trace = payload.get("_trace_ids")
    if isinstance(trace, dict):
        value = trace.get("agent_session_id")
        if value:
            return str(value)
    value = payload.get("agent_session_id")
    if value:
        return str(value)
    return _UNASSIGNED


def _filter_by_session(events: Iterable[dict[str, Any]], session_id: str) -> list[dict[str, Any]]:
    target = str(session_id or "")
    out: list[dict[str, Any]] = []
    for event in events:
        if _AGGREGATABLE_KINDS and _event_kind(event) not in _AGGREGATABLE_KINDS:
            continue
        if _extract_session_id(event) == target:
            out.append(event)
    return out


def _group_by_session(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """event list を agent_session_id 単位で集約し、summary を作る."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        kind = _event_kind(event)
        if _AGGREGATABLE_KINDS and kind not in _AGGREGATABLE_KINDS:
            continue
        sid = _extract_session_id(event)
        grouped.setdefault(sid, []).append(event)

    summaries: list[dict[str, Any]] = []
    for sid, items in grouped.items():
        summaries.append(_build_summary(sid, items))
    # 新しい順 (last_event_ms desc) で並べる
    summaries.sort(key=lambda s: int(s.get("last_event_ms") or 0), reverse=True)
    return summaries


def _build_summary(agent_session_id: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    """1 session の summary dict を作る."""
    kinds_set: set[str] = set()
    task_id = ""
    first_event_ms = 0
    last_event_ms = 0
    status = "unknown"
    summary_text = ""
    # Phase D5 — policy 集計
    policy_allow_count = 0
    policy_deny_count = 0
    highest_risk = ""
    highest_risk_value = 0
    for event in events:
        kind = _event_kind(event)
        kinds_set.add(kind)
        ts = _event_timestamp_ms(event)
        if ts:
            if first_event_ms == 0 or ts < first_event_ms:
                first_event_ms = ts
            if ts > last_event_ms:
                last_event_ms = ts
        payload = event.get("payload") if isinstance(event, dict) else None
        if isinstance(payload, dict):
            if not task_id:
                t = payload.get("task_id")
                if t:
                    task_id = str(t)
            if kind == "agent.completed" and not summary_text:
                summary_text = str(payload.get("summary") or "")
            # Phase D5 — policy.decision 集計
            if kind == "policy.decision":
                decision = str(payload.get("decision") or "").upper()
                risk = str(payload.get("risk_level") or "")
                if decision in _POLICY_ALLOW_LIKE:
                    policy_allow_count += 1
                elif decision in _POLICY_DENY:
                    policy_deny_count += 1
                risk_value = _RISK_ORDER.get(risk, 0)
                if risk_value > highest_risk_value:
                    highest_risk_value = risk_value
                    highest_risk = risk
        if kind == "agent.completed":
            status = "completed"
        elif kind == "agent.failed":
            status = "failed"
        elif kind == "agent.started" and status not in ("completed", "failed"):
            status = "running"

    if not status or status == "unknown":
        if kinds_set:
            status = "running"
    causal_chain = _build_causal_chain(events)
    milestones = _build_milestones(events)
    root_cause = _build_root_cause(events, status=status)
    return {
        "agent_session_id": agent_session_id,
        "task_id": task_id,
        "first_event_ms": first_event_ms,
        "last_event_ms": last_event_ms,
        "event_count": len(events),
        "kinds": sorted(kinds_set),
        "status": status,
        "summary": summary_text,
        # Phase D5 — policy 集計 (ask / approval 系は承認撤去後の互換シム)
        "policy_allow_count": policy_allow_count,
        "policy_ask_count": 0,
        "policy_deny_count": policy_deny_count,
        "highest_risk": highest_risk,
        "approval_count": 0,
        "pending_approval": False,
        "causal_summary": _build_causal_summary(
            status=status,
            root_cause=root_cause,
            chain_size=len(causal_chain),
        ),
        "root_cause": root_cause,
        "milestones": milestones,
    }


def _empty_summary(agent_session_id: str) -> dict[str, Any]:
    return {
        "agent_session_id": agent_session_id,
        "task_id": "",
        "first_event_ms": 0,
        "last_event_ms": 0,
        "event_count": 0,
        "kinds": [],
        "status": "unknown",
        "summary": "",
        # Phase D5 (ask / approval 系は承認撤去後の互換シム)
        "policy_allow_count": 0,
        "policy_ask_count": 0,
        "policy_deny_count": 0,
        "highest_risk": "",
        "approval_count": 0,
        "pending_approval": False,
        "causal_summary": "",
        "root_cause": None,
        "milestones": [],
    }


def _event_timestamp_ms(event: dict[str, Any]) -> int:
    """Event payload の occurred_at_ms / timestamp / generated_at を探す."""
    payload = event.get("payload") if isinstance(event, dict) else None
    if isinstance(payload, dict):
        for key in ("occurred_at_ms", "timestamp_ms", "ts_ms"):
            value = payload.get(key)
            if value:
                try:
                    return int(value)
                except (TypeError, ValueError):
                    pass
    for key in ("timestamp", "generated_at", "ts_ms"):
        value = event.get(key) if isinstance(event, dict) else None
        if value:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    return 0


def _event_payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload") if isinstance(event, dict) else None
    return payload if isinstance(payload, dict) else {}


def _event_trace_ids(event: dict[str, Any]) -> dict[str, str]:
    payload = _event_payload(event)
    trace = payload.get("_trace_ids")
    if not isinstance(trace, dict):
        trace = {}
    return {
        "trace_id": str(trace.get("trace_id") or ""),
        "parent_id": str(trace.get("parent_id") or payload.get("parent_id") or ""),
        "activity_id": str(trace.get("activity_id") or ""),
    }


def _event_key(event: dict[str, Any], index: int) -> str:
    payload = _event_payload(event)
    return str(payload.get("event_id") or event.get("event_id") or f"event-{index}")


def _event_summary_text(event: dict[str, Any]) -> str:
    payload = _event_payload(event)
    for key in ("summary", "text", "error", "reason", "tool", "capability_id", "decision"):
        value = payload.get(key)
        if value:
            return str(value)
    return ""


def _build_causal_chain(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        payload = _event_payload(event)
        trace = _event_trace_ids(event)
        normalized.append(
            {
                "key": _event_key(event, index),
                "kind": _event_kind(event),
                "timestamp_ms": _event_timestamp_ms(event),
                "summary": _event_summary_text(event),
                "status": str(payload.get("state") or payload.get("status") or _event_kind(event)),
                "trace_id": trace["trace_id"],
                "parent_id": trace["parent_id"],
                "activity_id": trace["activity_id"],
            }
        )
    normalized.sort(key=lambda item: int(item.get("timestamp_ms") or 0))
    parent_map = {str(item.get("key") or ""): item for item in normalized}
    for item in normalized:
        item["depth"] = _compute_chain_depth(str(item.get("parent_id") or ""), parent_map)
    return normalized


def _compute_chain_depth(
    parent_id: str,
    parent_map: dict[str, dict[str, Any]],
) -> int:
    depth = 0
    current_parent = str(parent_id or "")
    seen: set[str] = set()
    while current_parent and current_parent in parent_map and current_parent not in seen and depth < 8:
        seen.add(current_parent)
        depth += 1
        current_parent = str(parent_map[current_parent].get("parent_id") or "")
    return depth


def _policy_state(event: dict[str, Any]) -> str:
    if _event_kind(event) != "policy.decision":
        return ""
    decision = str(_event_payload(event).get("decision") or "").upper()
    if decision in _POLICY_DENY:
        return "deny"
    if decision in _POLICY_ALLOW_LIKE:
        return "allow"
    return ""


def _root_cause_from_event(event: dict[str, Any], *, category: str, confidence: float) -> dict[str, Any]:
    trace = _event_trace_ids(event)
    return {
        "kind": _event_kind(event),
        "summary": _event_summary_text(event),
        "timestamp_ms": _event_timestamp_ms(event),
        "trace_id": trace["trace_id"],
        "parent_id": trace["parent_id"],
        "activity_id": trace["activity_id"],
        "category": category,
        "confidence": confidence,
    }


def _build_root_cause(
    events: list[dict[str, Any]],
    *,
    status: str,
) -> dict[str, Any] | None:
    failed = next((event for event in reversed(events) if _event_kind(event) in _FAILED_KINDS), None)
    if failed is not None:
        return _root_cause_from_event(failed, category="failure", confidence=0.95)

    denied = next((event for event in reversed(events) if _policy_state(event) == "deny"), None)
    if denied is not None:
        return _root_cause_from_event(denied, category="policy_denied", confidence=0.9)

    if status == "completed":
        completed = next((event for event in reversed(events) if _event_kind(event) == "agent.completed"), None)
        if completed is not None:
            return _root_cause_from_event(completed, category="completed", confidence=0.75)

    latest = next(reversed(events), None) if events else None
    if latest is not None:
        return _root_cause_from_event(latest, category="progress", confidence=0.4)
    return None


def _milestone_variant(event: dict[str, Any]) -> str:
    kind = _event_kind(event)
    if kind == "agent.started":
        return "start"
    if kind == "agent.completed":
        return "completed"
    if kind in _FAILED_KINDS:
        return "failed"
    if _policy_state(event) == "deny":
        return "deny"
    return "progress"


def _milestone_label(event: dict[str, Any]) -> str:
    kind = _event_kind(event)
    if kind == "agent.started":
        return "start"
    if kind == "agent.completed":
        return "done"
    if kind in _FAILED_KINDS:
        return "failed"
    if _policy_state(event) == "deny":
        return "policy deny"
    return kind


def _build_milestones(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    milestone_events = [
        event
        for event in events
        if _event_kind(event)
        in {
            "agent.started",
            "agent.completed",
            "agent.failed",
            "tool.execution.failed",
        }
        or _policy_state(event) == "deny"
    ]
    milestones: list[dict[str, Any]] = []
    for index, event in enumerate(milestone_events):
        trace = _event_trace_ids(event)
        milestones.append(
            {
                "key": _event_key(event, index),
                "kind": _event_kind(event),
                "label": _milestone_label(event),
                "variant": _milestone_variant(event),
                "timestamp_ms": _event_timestamp_ms(event),
                "trace_id": trace["trace_id"],
                "parent_id": trace["parent_id"],
                "activity_id": trace["activity_id"],
            }
        )
    return milestones


def _build_causal_summary(
    *,
    status: str,
    root_cause: dict[str, Any] | None,
    chain_size: int,
) -> str:
    if root_cause is None:
        return ""
    summary = str(root_cause.get("summary") or "").strip()
    kind = str(root_cause.get("kind") or "event")
    category = str(root_cause.get("category") or "")
    if category in {"failure", "policy_denied"}:
        return f"Latest blocking event: {kind}{f' - {summary}' if summary else ''}."
    if status == "completed":
        return summary or "Session completed successfully."
    if chain_size > 0:
        return f"{chain_size} correlated event(s) are linked in this session."
    return summary


__all__ = ["init_agent_sessions_routes"]
