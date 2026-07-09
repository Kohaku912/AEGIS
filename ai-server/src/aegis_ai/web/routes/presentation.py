"""Dashboard presentation page route."""

from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint, render_template

logger = logging.getLogger("aegis_ai.web.presentation_routes")


def init_presentation_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_presentation", __name__)

    @bp.route("/dashboard/presentations")
    def dashboard_presentations():
        presentations: list[dict[str, Any]] = []
        stats = {"total_active": 0, "total_delivered": 0, "total_dismissed": 0}
        try:
            presentations = owner._runtime.presentation_manager.list_all(limit=200)
            for presentation in presentations:
                status = str(presentation.get("status", "")).lower()
                if status in {"pending", "queued", "active"}:
                    stats["total_active"] += 1
                elif status == "delivered":
                    stats["total_delivered"] += 1
                elif status == "dismissed":
                    stats["total_dismissed"] += 1
        except Exception as exc:
            logger.warning("Presentations load failed: %s", exc)
        return render_template("dashboard/presentations.html", presentations=presentations, stats=stats)

    owner.app.register_blueprint(bp)
