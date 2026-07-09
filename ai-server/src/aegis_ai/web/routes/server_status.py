"""Dashboard server-status routes."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, render_template


def init_server_status_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_server_status", __name__)

    @bp.route("/dashboard/servers")
    def servers():
        status = owner._get_server_status()
        return render_template(
            "dashboard/servers.html",
            servers=status["servers"],
            summary=status["summary"],
        )

    @bp.route("/api/servers")
    def api_servers():
        return jsonify(owner._get_server_status())

    owner.app.register_blueprint(bp)
