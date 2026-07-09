"""Dashboard memory routes."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, render_template


def init_memory_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_memory", __name__)

    @bp.route("/dashboard/memory")
    def dashboard_memory():
        from aegis_ai.web.dashboard_routes import _load_memory_snapshot

        return render_template("dashboard/memory.html", **_load_memory_snapshot())

    @bp.route("/api/memory/reload", methods=["POST"])
    def memory_reload():
        from aegis_ai.web.dashboard_routes import _load_memory_snapshot

        snapshot = _load_memory_snapshot()
        return jsonify({
            "ok": True,
            "summary": snapshot.get("summary", {}),
            "chroma_synced": 0,
        })

    owner.app.register_blueprint(bp)
