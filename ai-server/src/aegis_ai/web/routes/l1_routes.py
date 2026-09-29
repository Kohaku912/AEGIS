"""L1 (Perception / Router) Dashboard routes — DASHBOARD_V3_PLAN.md Phase L6.

L1 (常時稼働 / 知覚 / ルーティング層) のイベントを EventManager.persisted
events から読み取り専用で取得し、Dashboard の L1 専用パネルに供給する。

API:
- `GET /api/l1/events?kinds=...&limit=200` — L1 events 取得 (l1.observation / l1.decision / l1.escalation / l1.capability.*)
- `GET /api/l1/events/recent?limit=1`     — 最新 1 件 (Dashboard Overview / Live Overlay 用)
- `GET /api/l1/events/stats`              — kind 別件数集計

Publisher への書き込みは一切しない (読み取り専用)。
EventManager 未接続でも 200 + empty で no-op。
"""
from __future__ import annotations

import logging
import time
from typing import Any

from flask import Blueprint, jsonify, request

logger = logging.getLogger("aegis_ai.web.routes.l1_routes")

# Phase L6 — L1 専用パネルが対象とする event kind.
# EventManager._PERSIST_EVENT_TYPES の L1 関連 5 種類を列挙.
_L1_KINDS: frozenset[str] = frozenset({
    "l1.observation",
    "l1.decision",
    "l1.escalation",
    "l1.capability.invoked",
    "l1.capability.completed",
})

_DEFAULT_LIMIT = 200
_MAX_LIMIT = 2000
_THROUGHPUT_WINDOW_MS = 60_000


def init_l1_routes(owner: Any) -> None:
    """L1 Dashboard の Blueprint route を owner.app に登録する."""
    bp = Blueprint("dashboard_l1_api", __name__)

    @bp.route("/api/l1/events", methods=["GET"])
    def list_l1_events():
        runtime = owner._runtime
        kinds = _parse_kinds(request.args.get("kinds"))
        limit = _clamp_limit(request.args.get("limit"))
        events = _fetch_persisted_events(runtime, limit=limit)
        l1_events = [e for e in events if _event_kind(e) in _L1_KINDS]
        if kinds:
            l1_events = [e for e in l1_events if _event_kind(e) in kinds]
        # Dashboard は新しい順 (DESC) で欲しいので reverse する.
        l1_events = list(reversed(l1_events))
        return jsonify(
            {
                "generated_at": _now_ms(),
                "layer": "L1",
                "count": len(l1_events),
                "kinds": sorted(kinds) if kinds else sorted(_L1_KINDS),
                "events": l1_events,
            }
        )

    @bp.route("/api/l1/events/recent", methods=["GET"])
    def list_l1_events_recent():
        """最新 1 件を返す (Dashboard Overview / Live Overlay 用)."""
        runtime = owner._runtime
        limit = _clamp_limit(request.args.get("limit"), default=1, maximum=20)
        events = _fetch_persisted_events(runtime, limit=limit)
        l1_events = [e for e in events if _event_kind(e) in _L1_KINDS]
        l1_events = list(reversed(l1_events))[:limit]
        return jsonify(
            {
                "generated_at": _now_ms(),
                "layer": "L1",
                "count": len(l1_events),
                "events": l1_events,
            }
        )

    @bp.route("/api/l1/events/stats", methods=["GET"])
    def l1_events_stats():
        runtime = owner._runtime
        events = _fetch_persisted_events(runtime, limit=_MAX_LIMIT)
        l1_events = [e for e in events if _event_kind(e) in _L1_KINDS]
        stats: dict[str, int] = {kind: 0 for kind in sorted(_L1_KINDS)}
        for e in l1_events:
            kind = _event_kind(e)
            if kind in stats:
                stats[kind] += 1
        now_ms = _now_ms()
        recent_l1 = [e for e in l1_events if _event_timestamp_ms(e) >= now_ms - _THROUGHPUT_WINDOW_MS]
        top_event_types: dict[str, int] = {}
        for event in recent_l1:
            payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
            event_type = _source_event_type(payload)
            if not event_type:
                continue
            top_event_types[event_type] = top_event_types.get(event_type, 0) + 1
        recent_audit = _fetch_recent_audit_entries(
            runtime,
            limit=1000,
            action="llm_call",
            since_ms=now_ms - _THROUGHPUT_WINDOW_MS,
            actor="llm",
        )
        llm_calls_60s = 0
        event_driven_llm_calls_60s = 0
        for entry in _dedupe_llm_call_entries(recent_audit):
            llm_calls_60s += 1
            detail = entry.get("detail") if isinstance(entry.get("detail"), dict) else {}
            profile_id = str(entry.get("profile_id") or detail.get("profile_id") or detail.get("profile") or "")
            if (
                profile_id == "l1_default"
                and str(detail.get("source") or "") == "l1_router.observe"
            ):
                event_driven_llm_calls_60s += 1
        return jsonify(
            {
                "generated_at": _now_ms(),
                "layer": "L1",
                "total": len(l1_events),
                "by_kind": stats,
                "window_ms": _THROUGHPUT_WINDOW_MS,
                "llm_calls_60s": llm_calls_60s,
                "event_driven_llm_calls_60s": event_driven_llm_calls_60s,
                "l1_observations_60s": sum(1 for e in recent_l1 if _event_kind(e) == "l1.observation"),
                "l1_decisions_60s": sum(1 for e in recent_l1 if _event_kind(e) == "l1.decision"),
                "top_event_types_60s": dict(
                    sorted(top_event_types.items(), key=lambda item: (-item[1], item[0]))[:10]
                ),
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


def _event_timestamp_ms(event: dict[str, Any]) -> int:
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    raw = (
        event.get("timestamp_ms")
        or event.get("timestamp")
        or payload.get("occurred_at_ms")
        or payload.get("timestamp_ms")
        or 0
    )
    try:
        return int(raw or 0)
    except (TypeError, ValueError):
        return 0


def _source_event_type(payload: dict[str, Any]) -> str:
    return str(
        payload.get("event_type")
        or payload.get("source_event_type")
        or payload.get("original_event_type")
        or ""
    )


def _fetch_persisted_events(runtime: Any, *, limit: int) -> list[dict[str, Any]]:
    """EventManager.persisted events を古い順で取得 (limit 件)."""
    em = getattr(runtime, "event_manager", None)
    if em is None:
        return []
    disk_fn = getattr(em, "read_recent_persisted", None)
    if callable(disk_fn):
        try:
            result = disk_fn(limit=limit)
        except TypeError:
            try:
                result = disk_fn(limit)
            except Exception:  # noqa: BLE001
                logger.debug("event_manager.read_recent_persisted failed", exc_info=True)
            else:
                return result if isinstance(result, list) else []
        except Exception:  # noqa: BLE001
            logger.debug("event_manager.read_recent_persisted failed", exc_info=True)
        else:
            return result if isinstance(result, list) else []
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


def _fetch_recent_audit_entries(
    runtime: Any,
    *,
    limit: int,
    action: str = "",
    since_ms: int = 0,
    actor: str = "",
) -> list[dict[str, Any]]:
    manager = getattr(runtime, "audit_manager", None)
    if manager is None:
        return []
    fn = getattr(manager, "read_recent_for_dashboard", None)
    if not callable(fn):
        return []
    try:
        result = fn(
            max_entries=limit,
            action=action,
            since_ms=since_ms,
            actor=actor,
        )
    except TypeError:
        try:
            result = fn(max_entries=limit)
        except Exception:  # noqa: BLE001
            logger.debug("audit_manager.read_recent_for_dashboard failed", exc_info=True)
            return []
    except Exception:  # noqa: BLE001
        logger.debug("audit_manager.read_recent_for_dashboard failed", exc_info=True)
        return []
    return result if isinstance(result, list) else []


def _dedupe_llm_call_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_request: dict[str, dict[str, Any]] = {}
    ordered: list[dict[str, Any]] = []
    for entry in entries:
        detail = entry.get("detail") if isinstance(entry.get("detail"), dict) else {}
        request_id = str(entry.get("request_id") or detail.get("request_id") or entry.get("entry_id") or "")
        if not request_id:
            ordered.append(entry)
            continue
        current = by_request.get(request_id)
        if current is None:
            by_request[request_id] = entry
            ordered.append(entry)
            continue
        current_detail = current.get("detail") if isinstance(current.get("detail"), dict) else {}
        current_score = len(current_detail) + (10 if str(current.get("profile_id") or current_detail.get("profile_id") or current_detail.get("profile") or "") else 0)
        new_score = len(detail) + (10 if str(entry.get("profile_id") or detail.get("profile_id") or detail.get("profile") or "") else 0)
        if new_score <= current_score:
            continue
        by_request[request_id] = entry
        for idx, existing in enumerate(ordered):
            existing_detail = existing.get("detail") if isinstance(existing.get("detail"), dict) else {}
            existing_request_id = str(existing.get("request_id") or existing_detail.get("request_id") or existing.get("entry_id") or "")
            if existing_request_id == request_id:
                ordered[idx] = entry
                break
    return ordered
