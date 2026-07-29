"""v2 UI overview and stream routes."""

from __future__ import annotations

import json
import queue
import time
from typing import Any

from flask import Blueprint, Response, jsonify, request

from aegis_ai.web.ui_overview import (
    _is_activity_noise_event,
    build_ui_overview,
    normalize_ui_event,
)


def init_ui_routes(owner: Any) -> None:
    bp = Blueprint("ui_v2_api", __name__)

    @bp.route("/api/ui/overview")
    def ui_overview():
        return jsonify(build_ui_overview(owner._runtime))

    @bp.route("/api/ui/stream")
    def ui_stream():
        event_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=200)
        event_manager = getattr(owner._runtime, "event_manager", None)
        subscriber_id = ""
        last_event_id = _last_event_id()

        def _handler(event: Any) -> None:
            try:
                normalized = normalize_ui_event(event)
                if _is_activity_noise_event(normalized):
                    return
                event_queue.put_nowait(normalized)
            except queue.Full:
                pass

        if event_manager is not None and hasattr(event_manager, "subscribe"):
            subscriber_id = event_manager.subscribe(_handler)

        def _generate():
            yield "retry: 3000\n\n"
            for event in _replay_events(event_manager, last_event_id):
                yield _sse(event.get("type", "activity.updated"), event)
            yield _sse("ui.snapshot", build_ui_overview(owner._runtime))
            last_heartbeat = time.time()
            try:
                while True:
                    try:
                        event = event_queue.get(timeout=10)
                        yield _sse(event.get("type", "activity.updated"), event)
                    except queue.Empty:
                        now = time.time()
                        if now - last_heartbeat >= 10:
                            yield ": keepalive\n\n"
                            last_heartbeat = now
            finally:
                if subscriber_id and event_manager is not None and hasattr(event_manager, "unsubscribe"):
                    event_manager.unsubscribe(subscriber_id)

        return Response(_generate(), mimetype="text/event-stream")

    owner.app.register_blueprint(bp)


def _sse(event: str, payload: dict[str, Any]) -> str:
    event_id = str(payload.get("event_id") or "")
    lines = []
    if event_id:
        lines.append(f"id: {event_id}")
    lines.append(f"event: {event}")
    lines.append(f"data: {json.dumps(payload, ensure_ascii=False)}")
    return "\n".join(lines) + "\n\n"


def _last_event_id() -> str:
    return (
        request.args.get("last_event_id", "")
        or request.headers.get("Last-Event-ID", "")
        or request.headers.get("Last-Event-Id", "")
    ).strip()


def _replay_events(event_manager: Any, last_event_id: str, limit: int = 100) -> list[dict[str, Any]]:
    if not last_event_id or event_manager is None or not hasattr(event_manager, "list_recent"):
        return []
    try:
        result = event_manager.list_recent(limit=limit, cursor=last_event_id)
    except TypeError:
        return []
    except Exception:
        return []
    items = result.get("events", []) if isinstance(result, dict) else []
    normalized: list[dict[str, Any]] = []
    for item in items:
        try:
            event = normalize_ui_event(item)
        except Exception:
            continue
        if _is_activity_noise_event(event):
            continue
        if event.get("event_id") != last_event_id:
            normalized.append(event)
    return normalized
