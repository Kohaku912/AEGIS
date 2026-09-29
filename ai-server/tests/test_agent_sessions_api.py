"""Phase D4 + D5 DoD tests — Agent Sessions API (DASHBOARD_REFINED_PLAN.md §3 Phase D4 / D5).

DoD チェックリスト (D4):
- [x] `/api/ui/agent-sessions` が session 単位の一覧を返す
- [x] `/api/ui/agent-sessions/<id>` が詳細 (events + summary) を返す
- [x] `/api/ui/agent-sessions/<id>/events?kinds=` が kinds フィルタできる
- [x] 存在しない session は 404
- [x] EventManager 未接続でも no-op で 200 を返す
- [x] テスト: 6 件 pass

DoD チェックリスト (D5 — Policy 表示統合):
- [x] summary に `policy_allow_count` / `policy_ask_count` / `policy_deny_count` が含まれる
- [x] summary に `highest_risk` (READ_ONLY/SAFE_ACTION/APPROVAL_REQUIRED/HIGH_RISK/FORBIDDEN) が含まれる
- [x] summary に `approval_count` / `pending_approval` が含まれる (承認撤去後は常に 0 / False の互換シム)
- [x] `approval.*` event は集約対象から外れている (承認サブシステムは撤去済み)
- [x] AuditManager.append で `_POLICY_ACTIONS` の entry を EventBus に `policy.decision` として publish
- [x] AuditManager.append で非 policy action (例: llm, social_proxy) は publish しない
- [x] AuditManager の event_manager=None で no-op
- [x] テスト: 6 件 (D4) + 6 件 (D5) = 12 件 pass
"""
from __future__ import annotations

from typing import Any

import pytest
from flask import Flask

from aegis_ai.web.routes.agent_sessions import init_agent_sessions_routes


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _FakeEvent:
    def __init__(self, *, event_type: str, source: str, payload: dict[str, Any]) -> None:
        self.event_type = event_type
        self.event_id = str(payload.get("event_id") or "")
        self.source_server_id = source
        self._payload = dict(payload)
        self.timestamp = int(payload.get("occurred_at_ms") or 0)

    def payload(self) -> dict[str, Any]:
        return dict(self._payload)


class _FakeEventManager:
    """`EventManager` 互換の minimal fake.

    publish_event 経由で `_persisted_events` に積まれる。
    list_recent(limit) は persisted_events の末尾 (最新) を返す。
    """

    def __init__(self) -> None:
        self.persisted: list[dict[str, Any]] = []

    def publish_event(self, event_type: str, *, source: str, payload: dict[str, Any]) -> bool:
        record = {
            "event_id": payload.get("event_id", ""),
            "type": event_type,
            "source": source,
            "timestamp": int(payload.get("occurred_at_ms") or 0),
            "payload": dict(payload),
        }
        self.persisted.append(record)
        return True

    def list_recent(self, *, limit: int = 50, cursor: str | None = None) -> dict[str, Any]:
        events = list(self.persisted)
        if cursor:
            for i, e in enumerate(events):
                if e.get("event_id") == cursor:
                    events = events[i + 1 :]
                    break
        page = events[-limit:]
        next_cursor = page[0].get("event_id") if page and len(page) == limit else None
        return {"events": page, "next_cursor": next_cursor}


class _FakeRuntime:
    def __init__(self, em: _FakeEventManager | None) -> None:
        self.event_manager = em


class _Owner:
    def __init__(self, runtime: _FakeRuntime) -> None:
        self._runtime = runtime
        self.app = Flask(__name__)


# ---------------------------------------------------------------------------
# DoD tests
# ---------------------------------------------------------------------------


def _make_client(em: _FakeEventManager | None) -> Any:
    owner = _Owner(_FakeRuntime(em))
    init_agent_sessions_routes(owner)
    return owner.app.test_client()


def _publish(
    em: _FakeEventManager,
    *,
    kind: str,
    agent_session_id: str,
    task_id: str = "",
    text: str = "",
    event_id: str = "",
    occurred_at_ms: int = 0,
    decision: str = "",
    risk_level: str = "",
    approval_id: str = "",
) -> None:
    payload = {
        "task_id": task_id,
        "agent_session_id": agent_session_id,
        "parent_id": "",
        "state": kind.split(".", 1)[-1],
        "occurred_at_ms": occurred_at_ms,
        "_trace_ids": {
            "event_id": event_id,
            "task_id": task_id,
            "activity_id": "",
            "agent_session_id": agent_session_id,
            "trace_id": agent_session_id,
            "parent_id": "",
        },
    }
    if text:
        payload["text"] = text
    if decision:
        payload["decision"] = decision
    if risk_level:
        payload["risk_level"] = risk_level
    if approval_id:
        payload["approval_id"] = approval_id
    em.publish_event(kind, source="openhands_backend", payload=payload)


def test_list_agent_sessions_groups_by_session() -> None:
    """DoD 1: `/api/ui/agent-sessions` が session 単位の一覧を返す."""
    em = _FakeEventManager()
    _publish(em, kind="agent.started", agent_session_id="sess-A", task_id="task-A", event_id="e1", occurred_at_ms=1000)
    _publish(em, kind="agent.thinking", agent_session_id="sess-A", text="hi", event_id="e2", occurred_at_ms=1100)
    _publish(em, kind="agent.completed", agent_session_id="sess-A", event_id="e3", occurred_at_ms=2000)
    _publish(em, kind="agent.started", agent_session_id="sess-B", event_id="e4", occurred_at_ms=3000)

    client = _make_client(em)
    res = client.get("/api/ui/agent-sessions")
    assert res.status_code == 200
    body = res.get_json()
    assert body["count"] == 2
    # sess-B (last_event_ms=3000) が先頭
    assert body["sessions"][0]["agent_session_id"] == "sess-B"
    assert body["sessions"][0]["event_count"] == 1
    assert body["sessions"][1]["agent_session_id"] == "sess-A"
    assert body["sessions"][1]["event_count"] == 3
    # sess-A は completed で終わる
    assert body["sessions"][1]["status"] == "completed"
    assert "agent.started" in body["sessions"][1]["kinds"]


def test_get_agent_session_returns_events_and_summary() -> None:
    """DoD 2: `/api/ui/agent-sessions/<id>` が events + summary を返す."""
    em = _FakeEventManager()
    _publish(em, kind="agent.started", agent_session_id="sess-X", task_id="task-7", event_id="x1", occurred_at_ms=100)
    _publish(em, kind="agent.thinking", agent_session_id="sess-X", text="let me think", event_id="x2", occurred_at_ms=200)
    _publish(em, kind="agent.tool.started", agent_session_id="sess-X", event_id="x3", occurred_at_ms=300)
    _publish(em, kind="agent.completed", agent_session_id="sess-X", event_id="x4", occurred_at_ms=400)

    client = _make_client(em)
    res = client.get("/api/ui/agent-sessions/sess-X")
    assert res.status_code == 200
    body = res.get_json()
    assert body["found"] is True
    assert body["agent_session_id"] == "sess-X"
    assert body["summary"]["status"] == "completed"
    assert body["summary"]["task_id"] == "task-7"
    assert body["summary"]["event_count"] == 4
    assert body["summary"]["milestones"][0]["label"] == "start"
    assert body["summary"]["milestones"][-1]["label"] == "done"
    assert body["summary"]["root_cause"]["category"] == "completed"
    assert body["causal_chain"][-1]["kind"] == "agent.completed"
    # events は古い順 (list_recent 仕様). event_id は _trace_ids 内
    event_ids = [
        e.get("payload", {}).get("_trace_ids", {}).get("event_id", "")
        for e in body["events"]
    ]
    assert event_ids == ["x1", "x2", "x3", "x4"]


def test_get_agent_session_404_when_missing() -> None:
    """DoD 4: 存在しない session は 404."""
    em = _FakeEventManager()
    _publish(em, kind="agent.started", agent_session_id="sess-A", event_id="e1")

    client = _make_client(em)
    res = client.get("/api/ui/agent-sessions/sess-NONEXISTENT")
    assert res.status_code == 404
    body = res.get_json()
    assert body["found"] is False
    assert body["agent_session_id"] == "sess-NONEXISTENT"
    assert body["summary"]["event_count"] == 0


def test_get_agent_session_events_filters_by_kinds() -> None:
    """DoD 3: `/api/ui/agent-sessions/<id>/events?kinds=` が kinds フィルタできる."""
    em = _FakeEventManager()
    _publish(em, kind="agent.started", agent_session_id="sess-Q", event_id="q1", occurred_at_ms=1)
    _publish(em, kind="agent.thinking", agent_session_id="sess-Q", text="t1", event_id="q2", occurred_at_ms=2)
    _publish(em, kind="agent.thinking", agent_session_id="sess-Q", text="t2", event_id="q3", occurred_at_ms=3)
    _publish(em, kind="agent.tool.started", agent_session_id="sess-Q", event_id="q4", occurred_at_ms=4)
    _publish(em, kind="agent.completed", agent_session_id="sess-Q", event_id="q5", occurred_at_ms=5)

    client = _make_client(em)
    res = client.get("/api/ui/agent-sessions/sess-Q/events?kinds=agent.thinking,agent.tool.started")
    assert res.status_code == 200
    body = res.get_json()
    assert body["count"] == 3
    assert sorted(body["kinds"]) == ["agent.thinking", "agent.tool.started"]
    kinds_returned = [e["type"] for e in body["events"]]
    assert kinds_returned.count("agent.thinking") == 2
    assert kinds_returned.count("agent.tool.started") == 1
    assert "agent.started" not in kinds_returned


def test_agent_sessions_api_handles_missing_event_manager() -> None:
    """DoD 5: EventManager 未接続でも no-op で 200 を返す."""
    client = _make_client(None)
    res = client.get("/api/ui/agent-sessions")
    assert res.status_code == 200
    body = res.get_json()
    assert body["count"] == 0
    assert body["sessions"] == []

    res2 = client.get("/api/ui/agent-sessions/sess-X")
    # 404 (not found) を返すが、例外は出さない
    assert res2.status_code == 404

    res3 = client.get("/api/ui/agent-sessions/sess-X/events")
    assert res3.status_code == 200
    assert res3.get_json()["count"] == 0


def test_list_agent_sessions_unassigned_bucket_for_missing_session_id() -> None:
    """payload の agent_session_id が空の event は "unassigned" bucket に分類される."""
    em = _FakeEventManager()
    # agent_session_id フィールドが無い (旧 event) を publish
    em.publish_event(
        "agent.started",
        source="openhands_backend",
        payload={
            "task_id": "t-old",
            "state": "started",
            "occurred_at_ms": 1,
        },
    )

    client = _make_client(em)
    res = client.get("/api/ui/agent-sessions")
    body = res.get_json()
    assert body["count"] == 1
    assert body["sessions"][0]["agent_session_id"] == "unassigned"


# ---------------------------------------------------------------------------
# Phase D5 — Policy / Approval 表示統合
# ---------------------------------------------------------------------------


def test_summary_aggregates_policy_decisions_and_highest_risk() -> None:
    """summary に policy_allow_count / policy_deny_count / highest_risk が含まれる."""
    em = _FakeEventManager()
    _publish(em, kind="agent.started", agent_session_id="sess-D5", task_id="t-D5", text="start", event_id="x1", occurred_at_ms=10)
    _publish(
        em,
        kind="policy.decision",
        agent_session_id="sess-D5",
        task_id="t-D5",
        event_id="x2",
        occurred_at_ms=20,
        decision="ALLOW_WITH_AUDIT",
        risk_level="READ_ONLY",
    )
    _publish(
        em,
        kind="policy.decision",
        agent_session_id="sess-D5",
        task_id="t-D5",
        event_id="x3",
        occurred_at_ms=30,
        decision="ALLOW",
        risk_level="SAFE_ACTION",
    )
    _publish(
        em,
        kind="policy.decision",
        agent_session_id="sess-D5",
        task_id="t-D5",
        event_id="x4",
        occurred_at_ms=40,
        decision="DENY",
        risk_level="FORBIDDEN",
    )
    _publish(em, kind="agent.completed", agent_session_id="sess-D5", task_id="t-D5", text="done", event_id="x5", occurred_at_ms=50)

    client = _make_client(em)
    res = client.get("/api/ui/agent-sessions/sess-D5")
    assert res.status_code == 200
    body = res.get_json()
    assert body["found"] is True
    summary = body["summary"]
    assert summary["policy_allow_count"] == 2
    assert summary["policy_ask_count"] == 0
    assert summary["policy_deny_count"] == 1
    # FORBIDDEN が SAFE_ACTION / READ_ONLY より大きいので highest_risk は FORBIDDEN
    assert summary["highest_risk"] == "FORBIDDEN"
    # 承認は撤去済み — 集計キーは互換シムとして常に 0 / False
    assert summary["approval_count"] == 0
    assert summary["pending_approval"] is False


def test_summary_never_reports_pending_approval() -> None:
    """承認撤去後はどの policy.decision でも pending_approval は False のまま."""
    em = _FakeEventManager()
    _publish(em, kind="agent.started", agent_session_id="sess-D5b", task_id="t-D5b", event_id="y1", occurred_at_ms=1)
    _publish(
        em,
        kind="policy.decision",
        agent_session_id="sess-D5b",
        task_id="t-D5b",
        event_id="y2",
        occurred_at_ms=2,
        decision="DENY",
        risk_level="APPROVAL_REQUIRED",
    )

    client = _make_client(em)
    res = client.get("/api/ui/agent-sessions/sess-D5b")
    summary = res.get_json()["summary"]
    assert summary["pending_approval"] is False
    assert summary["approval_count"] == 0
    assert summary["policy_ask_count"] == 0
    assert summary["policy_deny_count"] == 1
    assert summary["root_cause"]["category"] == "policy_denied"
    assert "blocking" in summary["causal_summary"].lower()


def test_approval_events_are_no_longer_aggregated() -> None:
    """`approval.*` event は集約対象外。流し込んでも summary には現れない."""
    em = _FakeEventManager()
    _publish(em, kind="agent.started", agent_session_id="sess-D5c", task_id="t-D5c", event_id="z1", occurred_at_ms=1)
    _publish(
        em,
        kind="approval.created",
        agent_session_id="sess-D5c",
        task_id="t-D5c",
        event_id="z2",
        occurred_at_ms=2,
        approval_id="apr-1",
    )
    _publish(em, kind="agent.completed", agent_session_id="sess-D5c", task_id="t-D5c", event_id="z4", occurred_at_ms=4)

    client = _make_client(em)
    res = client.get("/api/ui/agent-sessions/sess-D5c")
    body = res.get_json()
    summary = body["summary"]
    assert summary["approval_count"] == 0
    assert summary["pending_approval"] is False
    assert "approval.created" not in summary["kinds"]
    assert all(not str(m["kind"]).startswith("approval.") for m in summary["milestones"])


def test_audit_manager_publishes_policy_decision_to_event_bus(tmp_path) -> None:
    """AuditManager.append で _POLICY_ACTIONS の entry を EventBus に `policy.decision` として publish."""
    from aegis_ai.audit import AuditEntry, AuditLog
    from aegis_ai.audit.audit_manager import AuditManager

    log = AuditLog(path=str(tmp_path / "audit.jsonl"))
    em = _FakeEventManager()
    am = AuditManager(audit_log=log, data_dir=str(tmp_path), event_manager=em)

    am.append(AuditEntry(
        action="tool_invoked",
        capability_id="mcp.github.create_issue",
        decision="ALLOW_WITH_AUDIT",
        reason="Risk level HIGH_RISK — allowed with audit.",
        risk_level="HIGH_RISK",
        task_id="t-aud-1",
        detail={"agent_session_id": "sess-aud-1"},
    ))

    # _FakeEventManager.persisted に `policy.decision` が publish される
    kinds = [e["type"] for e in em.persisted]
    assert "policy.decision" in kinds
    policy = next(e for e in em.persisted if e["type"] == "policy.decision")
    assert policy["payload"]["capability_id"] == "mcp.github.create_issue"
    assert policy["payload"]["decision"] == "ALLOW_WITH_AUDIT"
    assert policy["payload"]["risk_level"] == "HIGH_RISK"
    assert policy["payload"]["task_id"] == "t-aud-1"
    assert policy["payload"]["agent_session_id"] == "sess-aud-1"


def test_audit_manager_does_not_publish_non_policy_actions(tmp_path) -> None:
    """非 policy action (例: llm, social_proxy) は publish しない."""
    from aegis_ai.audit import AuditEntry, AuditLog
    from aegis_ai.audit.audit_manager import AuditManager

    log = AuditLog(path=str(tmp_path / "audit.jsonl"))
    em = _FakeEventManager()
    am = AuditManager(audit_log=log, data_dir=str(tmp_path), event_manager=em)

    am.append(AuditEntry(
        action="llm_request",
        capability_id="llm.deepseek",
        decision="EXECUTED",
        reason="ok",
    ))
    am.append(AuditEntry(
        action="social_proxy",
        capability_id="social.email",
        decision="success",
        reason="sent",
    ))

    kinds = [e["type"] for e in em.persisted]
    assert "policy.decision" not in kinds


def test_audit_manager_with_no_event_manager_is_noop(tmp_path) -> None:
    """event_manager=None でも append は例外なく成功し、policy.decision は publish しない."""
    from aegis_ai.audit import AuditEntry, AuditLog
    from aegis_ai.audit.audit_manager import AuditManager

    log = AuditLog(path=str(tmp_path / "audit.jsonl"))
    am = AuditManager(audit_log=log, data_dir=str(tmp_path), event_manager=None)

    # 例外を出さずに成功する
    am.append(AuditEntry(
        action="tool_invoked",
        capability_id="mcp.test",
        decision="ALLOW",
        reason="ok",
    ))
