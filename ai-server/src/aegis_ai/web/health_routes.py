"""Dashboard health routes."""

from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, jsonify, render_template


def init_health_routes(owner: Any, data_dir: str) -> None:
    bp = Blueprint("dashboard_health", __name__)

    def _manager():
        from aegis_ai.health.alert_manager import HealthAlertManager

        return HealthAlertManager(
            data_dir=os.path.join(data_dir, "health"),
            tool_broker=getattr(owner._runtime, "tool_broker", None),
            llm_provider=getattr(owner._runtime, "llm_gateway", None),
            status_manager=getattr(owner._runtime, "status_manager", None),
            data_path=data_dir,
        )

    @bp.route("/dashboard/health")
    def dashboard_health():
        return render_template("dashboard/health.html")

    @bp.route("/api/health/alerts")
    def health_alerts():
        try:
            ham = _manager()
            ham.check_system_health()
            return jsonify(ham.to_dict())
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/health/acknowledge/<alert_id>", methods=["POST"])
    def health_acknowledge(alert_id: str):
        try:
            from aegis_ai.health.alert_manager import HealthAlertManager

            ham = HealthAlertManager(data_dir=os.path.join(data_dir, "health"))
            return jsonify({"success": ham.acknowledge(alert_id)})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/health/check", methods=["POST"])
    def health_check():
        try:
            ham = _manager()
            new_alerts = ham.check_system_health()
            return jsonify({"new_alerts": len(new_alerts), "alerts": [a.to_dict() for a in new_alerts]})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    owner.app.register_blueprint(bp)
