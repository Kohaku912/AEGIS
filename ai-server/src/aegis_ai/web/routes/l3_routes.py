"""L3 (Deep Reasoner) Dashboard routes — DASHBOARD_V3_PLAN.md Phase L6.

L3 (深層推論層) のイベントを EventManager.persisted events から
読み取り専用で取得し、Dashboard の L3 専用パネルに供給する。

API:
- `GET /api/l3/events?kinds=...&limit=200` — L3 events 取得 (l3.invoked / l3.completed / l3.failed)
- `GET /api/l3/events/recent?limit=1`     — 最新 1 件 (Dashboard Overview / Live Overlay 用)
- `GET /api/l3/events/stats`              — kind 別件数集計

Publisher への書き込みは一切しない (読み取り専用)。
EventManager 未接続でも 200 + empty で no-op。
"""
from __future__ import annotations

import logging
import time
from typing import Any

from flask import Blueprint, jsonify, request

logger = logging.getLogger("aegis_ai.web.routes.l3_routes")

# Phase L6 — L3 専用パネルが対象とする event kind.
# EventManager._PERSIST_EVENT_TYPES の L3 関連 3 種類を列挙.
_L3_KINDS: frozenset[str] = frozenset({
    "l3.invoked",
    "l3.completed",
    "l3.failed",
})

_DEFAULT_LIMIT = 200
_MAX_LIMIT = 2000


def init_l3_routes(owner: Any) -> None:
    """L3 Dashboard の Blueprint route を owner.app に登録する."""
    bp = Blueprint("dashboard_l3_api", __name__)

    @bp.route("/api/l3/events", methods=["GET"])
    def list_l3_events():
        runtime = owner._runtime
        kinds = _parse_kinds(request.args.get("kinds"))
        limit = _clamp_limit(request.args.get("limit"))
        events = _fetch_persisted_events(runtime, limit=limit)
        l3_events = [e for e in events if _event_kind(e) in _L3_KINDS]
        if kinds:
            l3_events = [e for e in l3_events if _event_kind(e) in kinds]
        l3_events = list(reversed(l3_events))
        return jsonify(
            {
                "generated_at": _now_ms(),
                "layer": "L3",
                "count": len(l3_events),
                "kinds": sorted(kinds) if kinds else sorted(_L3_KINDS),
                "events": l3_events,
            }
        )

    @bp.route("/api/l3/events/recent", methods=["GET"])
    def list_l3_events_recent():
        runtime = owner._runtime
        limit = _clamp_limit(request.args.get("limit"), default=1, maximum=20)
        events = _fetch_persisted_events(runtime, limit=limit)
        l3_events = [e for e in events if _event_kind(e) in _L3_KINDS]
        l3_events = list(reversed(l3_events))[:limit]
        return jsonify(
            {
                "generated_at": _now_ms(),
                "layer": "L3",
                "count": len(l3_events),
                "events": l3_events,
            }
        )

    @bp.route("/api/l3/events/stats", methods=["GET"])
    def l3_events_stats():
        runtime = owner._runtime
        events = _fetch_persisted_events(runtime, limit=_MAX_LIMIT)
        l3_events = [e for e in events if _event_kind(e) in _L3_KINDS]
        stats: dict[str, int] = {kind: 0 for kind in sorted(_L3_KINDS)}
        for e in l3_events:
            kind = _event_kind(e)
            if kind in stats:
                stats[kind] += 1
        return jsonify(
            {
                "generated_at": _now_ms(),
                "layer": "L3",
                "total": len(l3_events),
                "by_kind": stats,
            }
        )

    owner.app.register_blueprint(bp)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_ms() -> int:
    return int(time.time() * 1000)


def _clamp_limit(raw: str | None, *, default: int = _DEFAULT_LIMIT, maximum: int = _MAX_LIMIT) -> int:
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return max(1, min(value, maximum))


def _parse_kinds(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {piece.strip() for piece in raw.split(",") if piece.strip()}


def _event_kind(event: dict[str, Any]) -> str:
    return str(event.get("type") or event.get("event_type") or "")


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
    return events
