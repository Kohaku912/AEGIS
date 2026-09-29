"""L1 Routes tests — DASHBOARD_V3_PLAN.md Phase L6 (Backend).

DoD チェックリスト:
- [x] `/api/l1/events` が L1 events (l1.* 5 種) を新しい順 (DESC) で返す
- [x] `?kinds=` で絞り込み可能
- [x] `?limit=` で件数制御 (clamp)
- [x] L1 以外の event kind は除外
- [x] `/api/l1/events/recent` が最新 1 件 (デフォルト) を返す
- [x] `/api/l1/events/stats` が kind 別件数を返す
- [x] EventManager 未接続でも 200 + empty で no-op
"""
from __future__ import annotations

from typing import Any

from flask import Flask

from aegis_ai.event.event_manager import EventManager
from aegis_ai.event.helpers import build_event
from aegis_ai.web.routes.l1_routes import init_l1_routes
from event_bus import EventBus


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeEventManager:
    """`EventManager` 互換の minimal fake.

    publish_event 経由で `_persisted_events` に積まれる。
    list_recent(limit) は persisted_events の末尾 (最新) を古い順で返す。
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
    def __init__(self, em: _FakeEventManager | None, audit_manager: Any = None) -> None:
        self.event_manager = em
        self.audit_manager = audit_manager


class _Owner:
    def __init__(self, runtime: _FakeRuntime) -> None:
        self._runtime = runtime
        self.app = Flask(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeAuditManager:
    def __init__(self, entries: list[dict[str, Any]] | None = None) -> None:
        self.entries = list(entries or [])

    def read_recent_for_dashboard(
        self,
        *,
        max_entries: int = 400,
        action: str = "",
        since_ms: int = 0,
        actor: str = "",
        profile_id: str = "",
    ) -> list[dict[str, Any]]:
        filtered = list(self.entries)
        if action:
            filtered = [entry for entry in filtered if str(entry.get("action") or "") == action]
        if since_ms:
            filtered = [entry for entry in filtered if int(entry.get("timestamp_ms") or 0) >= since_ms]
        if actor:
            filtered = [entry for entry in filtered if str(entry.get("actor") or "") == actor]
        if profile_id:
            filtered = [entry for entry in filtered if str(entry.get("profile_id") or "") == profile_id]
        return filtered[-max_entries:]


def _make_client(em: _FakeEventManager | None, audit_manager: Any = None) -> Any:
    owner = _Owner(_FakeRuntime(em, audit_manager=audit_manager))
    init_l1_routes(owner)
    return owner.app.test_client()


def _publish(
    em: _FakeEventManager,
    *,
    kind: str,
    event_id: str,
    occurred_at_ms: int = 0,
    **extra: Any,
) -> None:
    payload = {
        "event_id": event_id,
        "occurred_at_ms": occurred_at_ms,
        "layer": "L1",
    }
    payload.update(extra)
    em.publish_event(kind, source="l1_router", payload=payload)


# ---------------------------------------------------------------------------
# DoD tests
# ---------------------------------------------------------------------------


def test_list_l1_events_returns_desc_order() -> None:
    """DoD 1: `/api/l1/events` が新しい順 (DESC) で返す."""
    em = _FakeEventManager()
    _publish(em, kind="l1.observation", event_id="e1", occurred_at_ms=1000)
    _publish(em, kind="l1.decision", event_id="e2", occurred_at_ms=1100)
    _publish(em, kind="l1.escalation", event_id="e3", occurred_at_ms=1200)
    _publish(em, kind="l1.capability.invoked", event_id="e4", occurred_at_ms=1300)
    _publish(em, kind="l1.capability.completed", event_id="e5", occurred_at_ms=1400)

    client = _make_client(em)
    res = client.get("/api/l1/events")
    assert res.status_code == 200
    body = res.get_json()
    assert body["layer"] == "L1"
    assert body["count"] == 5
    # DESC 順: 新しい event_id が先頭
    event_ids = [e.get("event_id") for e in body["events"]]
    assert event_ids == ["e5", "e4", "e3", "e2", "e1"]


def test_list_l1_events_excludes_non_l1_kinds() -> None:
    """DoD 4: L1 以外の event kind は除外."""
    em = _FakeEventManager()
    _publish(em, kind="l1.observation", event_id="e1")
    _publish(em, kind="l2.thinking", event_id="e2")  # L2 は除外
    _publish(em, kind="l3.invoked", event_id="e3")  # L3 は除外
    _publish(em, kind="agent.started", event_id="e4")  # agent.* は除外
    _publish(em, kind="task.created", event_id="e5")  # task.* は除外

    client = _make_client(em)
    res = client.get("/api/l1/events")
    body = res.get_json()
    assert body["count"] == 1
    assert body["events"][0]["event_id"] == "e1"


def test_list_l1_events_kind_filter() -> None:
    """DoD 2: `?kinds=` で絞り込み可能."""
    em = _FakeEventManager()
    _publish(em, kind="l1.observation", event_id="e1")
    _publish(em, kind="l1.decision", event_id="e2")
    _publish(em, kind="l1.escalation", event_id="e3")
    _publish(em, kind="l1.capability.invoked", event_id="e4")

    client = _make_client(em)
    res = client.get("/api/l1/events?kinds=l1.observation,l1.escalation")
    body = res.get_json()
    assert body["count"] == 2
    kinds_returned = {e["type"] for e in body["events"]}
    assert kinds_returned == {"l1.observation", "l1.escalation"}


def test_list_l1_events_limit_clamp() -> None:
    """DoD 3: `?limit=` で件数制御 (clamp)."""
    em = _FakeEventManager()
    for i in range(10):
        _publish(em, kind="l1.observation", event_id=f"e{i}", occurred_at_ms=1000 + i)

    client = _make_client(em)
    res = client.get("/api/l1/events?limit=3")
    body = res.get_json()
    assert body["count"] == 3
    # 新しい 3 件
    assert [e["event_id"] for e in body["events"]] == ["e9", "e8", "e7"]


def test_list_l1_events_recent_default_one() -> None:
    """DoD 5: `/api/l1/events/recent` が最新 1 件 (デフォルト) を返す."""
    em = _FakeEventManager()
    _publish(em, kind="l1.observation", event_id="e1", occurred_at_ms=1000)
    _publish(em, kind="l1.decision", event_id="e2", occurred_at_ms=1100)

    client = _make_client(em)
    res = client.get("/api/l1/events/recent")
    body = res.get_json()
    assert body["layer"] == "L1"
    assert body["count"] == 1
    assert body["events"][0]["event_id"] == "e2"


def test_list_l1_events_recent_with_limit() -> None:
    """`/api/l1/events/recent?limit=N` で N 件返す."""
    em = _FakeEventManager()
    for i in range(5):
        _publish(em, kind="l1.observation", event_id=f"e{i}", occurred_at_ms=1000 + i)

    client = _make_client(em)
    res = client.get("/api/l1/events/recent?limit=3")
    body = res.get_json()
    assert body["count"] == 3
    assert [e["event_id"] for e in body["events"]] == ["e4", "e3", "e2"]


def test_l1_events_stats_counts_by_kind() -> None:
    """DoD 6: `/api/l1/events/stats` が kind 別件数を返す."""
    em = _FakeEventManager()
    _publish(em, kind="l1.observation", event_id="e1")
    _publish(em, kind="l1.observation", event_id="e2")
    _publish(em, kind="l1.decision", event_id="e3")
    _publish(em, kind="l1.escalation", event_id="e4")
    _publish(em, kind="l1.capability.invoked", event_id="e5")
    _publish(em, kind="l1.capability.completed", event_id="e6")
    _publish(em, kind="l1.capability.completed", event_id="e7")
    _publish(em, kind="l2.thinking", event_id="e8")  # 除外

    now_ms = 1_700_000_000_000
    audit = _FakeAuditManager(
        [
            {
                "timestamp_ms": now_ms - 1000,
                "action": "llm_call",
                "actor": "llm",
                "profile_id": "l1_default",
                "detail": {"source": "l1_router.observe"},
            },
            {
                "timestamp_ms": now_ms - 2000,
                "action": "llm_call",
                "actor": "llm",
                "profile_id": "chat_balanced",
                "detail": {"source": "chat_tools.tool_gate"},
            },
        ]
    )
    client = _make_client(em, audit_manager=audit)
    from aegis_ai.web.routes import l1_routes as mod

    orig_now_ms = mod._now_ms
    mod._now_ms = lambda: now_ms
    try:
        res = client.get("/api/l1/events/stats")
    finally:
        mod._now_ms = orig_now_ms
    body = res.get_json()
    assert body["layer"] == "L1"
    assert body["total"] == 7
    assert body["by_kind"] == {
        "l1.observation": 2,
        "l1.decision": 1,
        "l1.escalation": 1,
        "l1.capability.invoked": 1,
        "l1.capability.completed": 2,
    }
    assert body["window_ms"] == 60000
    assert body["llm_calls_60s"] == 2
    assert body["event_driven_llm_calls_60s"] == 1
    assert body["l1_observations_60s"] == 0
    assert body["l1_decisions_60s"] == 0
    assert body["top_event_types_60s"] == {}


def test_l1_routes_no_event_manager_returns_empty() -> None:
    """DoD 7: EventManager 未接続でも 200 + empty で no-op."""
    client = _make_client(None)

    res = client.get("/api/l1/events")
    assert res.status_code == 200
    body = res.get_json()
    assert body["count"] == 0
    assert body["events"] == []

    res = client.get("/api/l1/events/recent")
    body = res.get_json()
    assert body["count"] == 0
    assert body["events"] == []

    res = client.get("/api/l1/events/stats")
    body = res.get_json()
    assert body["total"] == 0
    # 0 で初期化されている
    assert all(v == 0 for v in body["by_kind"].values())
    assert body["llm_calls_60s"] == 0
    assert body["event_driven_llm_calls_60s"] == 0
    assert body["l1_observations_60s"] == 0
    assert body["l1_decisions_60s"] == 0
    assert body["top_event_types_60s"] == {}


def test_l1_events_stats_reports_recent_throughput_and_top_event_types() -> None:
    em = _FakeEventManager()
    now_ms = 1_700_000_000_000
    _publish(
        em,
        kind="l1.observation",
        event_id="e1",
        occurred_at_ms=now_ms - 500,
        original_event_type="android.current_app_changed",
    )
    _publish(
        em,
        kind="l1.decision",
        event_id="e2",
        occurred_at_ms=now_ms - 400,
        original_event_type="android.current_app_changed",
    )
    _publish(
        em,
        kind="l1.observation",
        event_id="e3",
        occurred_at_ms=now_ms - 70_000,
        original_event_type="memory.written",
    )
    audit = _FakeAuditManager(
        [
            {
                "timestamp_ms": now_ms - 1000,
                "action": "llm_call",
                "actor": "llm",
                "profile_id": "l1_default",
                "detail": {"source": "l1_router.observe"},
            },
            {
                "timestamp_ms": now_ms - 900,
                "action": "llm_call",
                "actor": "llm",
                "profile_id": "l1_default",
                "detail": {"source": "l1_router.observe"},
            },
            {
                "timestamp_ms": now_ms - 80_000,
                "action": "llm_call",
                "actor": "llm",
                "profile_id": "l1_default",
                "detail": {"source": "l1_router.observe"},
            },
        ]
    )
    client = _make_client(em, audit_manager=audit)
    from aegis_ai.web.routes import l1_routes as mod

    orig_now_ms = mod._now_ms
    mod._now_ms = lambda: now_ms
    try:
        res = client.get("/api/l1/events/stats")
    finally:
        mod._now_ms = orig_now_ms
    body = res.get_json()
    assert body["llm_calls_60s"] == 2
    assert body["event_driven_llm_calls_60s"] == 2
    assert body["l1_observations_60s"] == 1
    assert body["l1_decisions_60s"] == 1
    assert body["top_event_types_60s"] == {"android.current_app_changed": 2}


def test_l1_events_stats_reads_recent_persisted_events_from_disk(tmp_path) -> None:
    data_dir = tmp_path / "data"
    dashboard_em = EventManager(EventBus(), data_dir=str(data_dir))
    writer_em = EventManager(EventBus(), data_dir=str(data_dir))
    now_ms = 1_700_000_000_000
    source_type = "pc.user_activity.snapshot"

    writer_em.record_summary(
        build_event(
            "l1.observation",
            source="l1_router",
            payload={
                "event_id": "disk-e1",
                "occurred_at_ms": now_ms - 500,
                "original_event_type": source_type,
                "layer": "L1",
            },
            event_id="disk-obs",
            timestamp_ms=now_ms - 500,
        )
    )
    writer_em.record_summary(
        build_event(
            "l1.decision",
            source="l1_router",
            payload={
                "event_id": "disk-e1",
                "occurred_at_ms": now_ms - 400,
                "original_event_type": source_type,
                "layer": "L1",
            },
            event_id="disk-dec",
            timestamp_ms=now_ms - 400,
        )
    )

    audit = _FakeAuditManager(
        [
            {
                "timestamp_ms": now_ms - 300,
                "action": "llm_call",
                "actor": "llm",
                "profile_id": "l1_default",
                "detail": {"source": "l1_router.observe"},
            }
        ]
    )
    client = _make_client(dashboard_em, audit_manager=audit)
    from aegis_ai.web.routes import l1_routes as mod

    orig_now_ms = mod._now_ms
    mod._now_ms = lambda: now_ms
    try:
        res = client.get("/api/l1/events/stats")
    finally:
        mod._now_ms = orig_now_ms
    body = res.get_json()
    assert body["llm_calls_60s"] == 1
    assert body["event_driven_llm_calls_60s"] == 1
    assert body["l1_observations_60s"] == 1
    assert body["l1_decisions_60s"] == 1
    assert body["top_event_types_60s"] == {source_type: 2}


def test_l1_routes_default_limit_200() -> None:
    """デフォルト limit は 200."""
    em = _FakeEventManager()
    for i in range(250):
        _publish(em, kind="l1.observation", event_id=f"e{i}")

    client = _make_client(em)
    res = client.get("/api/l1/events")
    body = res.get_json()
    assert body["count"] == 200
