"""L3 Routes tests — DASHBOARD_V3_PLAN.md Phase L6 (Backend).

DoD チェックリスト:
- [x] `/api/l3/events` が L3 events (l3.* 3 種) を新しい順 (DESC) で返す
- [x] `?kinds=` で絞り込み可能
- [x] `?limit=` で件数制御 (clamp)
- [x] L3 以外の event kind は除外
- [x] `/api/l3/events/recent` が最新 1 件 (デフォルト) を返す
- [x] `/api/l3/events/stats` が kind 別件数を返す
- [x] EventManager 未接続でも 200 + empty で no-op
"""
from __future__ import annotations

from typing import Any

from flask import Flask

from aegis_ai.web.routes.l3_routes import init_l3_routes


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeEventManager:
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
# Helpers
# ---------------------------------------------------------------------------


def _make_client(em: _FakeEventManager | None) -> Any:
    owner = _Owner(_FakeRuntime(em))
    init_l3_routes(owner)
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
        "layer": "L3",
    }
    payload.update(extra)
    em.publish_event(kind, source="l3_reasoner", payload=payload)


# ---------------------------------------------------------------------------
# DoD tests
# ---------------------------------------------------------------------------


def test_list_l3_events_returns_desc_order() -> None:
    em = _FakeEventManager()
    _publish(em, kind="l3.invoked", event_id="e1", occurred_at_ms=1000)
    _publish(em, kind="l3.completed", event_id="e2", occurred_at_ms=1100)
    _publish(em, kind="l3.failed", event_id="e3", occurred_at_ms=1200)

    client = _make_client(em)
    res = client.get("/api/l3/events")
    assert res.status_code == 200
    body = res.get_json()
    assert body["layer"] == "L3"
    assert body["count"] == 3
    event_ids = [e.get("event_id") for e in body["events"]]
    assert event_ids == ["e3", "e2", "e1"]


def test_list_l3_events_excludes_non_l3_kinds() -> None:
    em = _FakeEventManager()
    _publish(em, kind="l3.invoked", event_id="e1")
    _publish(em, kind="l2.thinking", event_id="e2")
    _publish(em, kind="l1.observation", event_id="e3")
    _publish(em, kind="agent.started", event_id="e4")
    _publish(em, kind="approval.created", event_id="e5")

    client = _make_client(em)
    res = client.get("/api/l3/events")
    body = res.get_json()
    assert body["count"] == 1
    assert body["events"][0]["event_id"] == "e1"


def test_list_l3_events_kind_filter() -> None:
    em = _FakeEventManager()
    _publish(em, kind="l3.invoked", event_id="e1")
    _publish(em, kind="l3.completed", event_id="e2")
    _publish(em, kind="l3.failed", event_id="e3")

    client = _make_client(em)
    res = client.get("/api/l3/events?kinds=l3.failed")
    body = res.get_json()
    assert body["count"] == 1
    assert body["events"][0]["type"] == "l3.failed"


def test_list_l3_events_limit_clamp() -> None:
    em = _FakeEventManager()
    for i in range(10):
        _publish(em, kind="l3.invoked", event_id=f"e{i}", occurred_at_ms=1000 + i)

    client = _make_client(em)
    res = client.get("/api/l3/events?limit=3")
    body = res.get_json()
    assert body["count"] == 3
    assert [e["event_id"] for e in body["events"]] == ["e9", "e8", "e7"]


def test_list_l3_events_recent_default_one() -> None:
    em = _FakeEventManager()
    _publish(em, kind="l3.invoked", event_id="e1", occurred_at_ms=1000)
    _publish(em, kind="l3.completed", event_id="e2", occurred_at_ms=1100)

    client = _make_client(em)
    res = client.get("/api/l3/events/recent")
    body = res.get_json()
    assert body["layer"] == "L3"
    assert body["count"] == 1
    assert body["events"][0]["event_id"] == "e2"


def test_l3_events_stats_counts_by_kind() -> None:
    em = _FakeEventManager()
    _publish(em, kind="l3.invoked", event_id="e1")
    _publish(em, kind="l3.invoked", event_id="e2")
    _publish(em, kind="l3.completed", event_id="e3")
    _publish(em, kind="l3.failed", event_id="e4")
    _publish(em, kind="l3.failed", event_id="e5")
    _publish(em, kind="l2.thinking", event_id="e6")  # 除外

    client = _make_client(em)
    res = client.get("/api/l3/events/stats")
    body = res.get_json()
    assert body["layer"] == "L3"
    assert body["total"] == 5
    assert body["by_kind"] == {
        "l3.invoked": 2,
        "l3.completed": 1,
        "l3.failed": 2,
    }


def test_l3_routes_no_event_manager_returns_empty() -> None:
    client = _make_client(None)

    res = client.get("/api/l3/events")
    body = res.get_json()
    assert body["count"] == 0

    res = client.get("/api/l3/events/recent")
    body = res.get_json()
    assert body["count"] == 0

    res = client.get("/api/l3/events/stats")
    body = res.get_json()
    assert body["total"] == 0
    assert all(v == 0 for v in body["by_kind"].values())
