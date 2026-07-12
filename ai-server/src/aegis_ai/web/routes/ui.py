"""v2 UI overview and stream routes."""

from __future__ import annotations

import json
import queue
import time
from typing import Any

from flask import Blueprint, Response, jsonify

from aegis_ai.web.ui_overview import build_ui_overview, normalize_ui_event


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

        def _handler(event: Any) -> None:
            try:
                event_queue.put_nowait(normalize_ui_event(event))
            except queue.Full:
                pass

        if event_manager is not None and hasattr(event_manager, "subscribe"):
            subscriber_id = event_manager.subscribe(_handler)

        def _generate():
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
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
