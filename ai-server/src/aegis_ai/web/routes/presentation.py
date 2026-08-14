"""Dashboard and local display presentation routes."""

from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint, abort, jsonify, request

logger = logging.getLogger("aegis_ai.web.presentation_routes")

_DISPLAY_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def init_presentation_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_presentation", __name__)

    @bp.route("/display/presentations/data")
    def display_presentations_data():
        _require_local_display_request()
        try:
            limit = min(max(int(request.args.get("limit", 20)), 1), 50)
            manager = owner._runtime.presentation_manager
            presentations = manager.list_active(limit=limit)
            return jsonify(
                {
                    "presentations": [_display_projection(item) for item in presentations],
                    "status": manager.get_status() if hasattr(manager, "get_status") else {},
                }
            )
        except Exception as exc:
            logger.warning("Presentation display data load failed: %s", exc)
            return jsonify({"presentations": [], "status": {}, "error": str(exc)}), 500

    owner.app.register_blueprint(bp)


def _require_local_display_request() -> None:
    """Keep the physical display route off Cloudflare and LAN/WAN hosts."""

    host = _request_host_without_port()
    if host not in _DISPLAY_LOOPBACK_HOSTS:
        abort(403)


def _request_host_without_port() -> str:
    host = (request.host or "").strip().lower()
    if host.startswith("["):
        return host.split("]", 1)[0].lstrip("[")
    return host.split(":", 1)[0]


def _display_projection(presentation: dict[str, Any]) -> dict[str, Any]:
    """Return the read-only fields needed by the dedicated display."""

    content = presentation.get("content") if isinstance(presentation.get("content"), dict) else {}
    delivery = presentation.get("delivery") if isinstance(presentation.get("delivery"), dict) else {}
    placement = presentation.get("placement") if isinstance(presentation.get("placement"), dict) else {}
    metadata = presentation.get("metadata") if isinstance(presentation.get("metadata"), dict) else {}
    return {
        "presentation_id": presentation.get("presentation_id", ""),
        "source": presentation.get("source", ""),
        "intent": presentation.get("intent", ""),
        "importance": presentation.get("importance", "normal"),
        "modality": presentation.get("modality", "text_card"),
        "title": presentation.get("title", ""),
        "summary": presentation.get("summary", ""),
        "content": content,
        "status": presentation.get("status", ""),
        "created_at_ms": presentation.get("created_at_ms", 0),
        "updated_at_ms": presentation.get("updated_at_ms", 0),
        "targets": delivery.get("targets", []),
        "zone": placement.get("zone", ""),
        "notification_id": metadata.get("notification_id", ""),
    }
