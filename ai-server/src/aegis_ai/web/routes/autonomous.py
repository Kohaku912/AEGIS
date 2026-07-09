"""Dashboard autonomous-loop routes."""

from __future__ import annotations

import json
import os
from typing import Any

from flask import Blueprint, jsonify, request


def init_autonomous_routes(owner: Any, data_dir: str) -> None:
    bp = Blueprint("dashboard_autonomous_api", __name__)

    @bp.route("/api/autonomous/status")
    def autonomous_status():
        try:
            if owner._autonomous_loop:
                return jsonify(owner._autonomous_loop.get_status())
            return jsonify({"running": False, "error": "Loop not initialized"})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/autonomous/trigger", methods=["POST"])
    def autonomous_trigger():
        try:
            if owner._autonomous_loop:
                return jsonify(owner._autonomous_loop.trigger_now())
            return jsonify({"error": "Loop not initialized"})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/autonomous/start", methods=["POST"])
    def autonomous_start():
        try:
            if owner._autonomous_loop:
                owner._autonomous_loop.start()
                return jsonify({"status": "started"})
            return jsonify({"error": "Loop not initialized"})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/autonomous/stop", methods=["POST"])
    def autonomous_stop():
        try:
            if owner._autonomous_loop:
                owner._autonomous_loop.stop()
                return jsonify({"status": "stopped"})
            return jsonify({"error": "Loop not initialized"})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/autonomous/threshold", methods=["POST"])
    def autonomous_threshold():
        data = request.get_json(silent=True) or {}
        threshold = data.get("threshold")
        if threshold is None:
            return jsonify({"error": "threshold required"}), 400
        try:
            if owner._autonomous_loop:
                owner._autonomous_loop.set_threshold(float(threshold))
                return jsonify({"ok": True, "threshold": owner._autonomous_loop.get_threshold()})
            return jsonify({"error": "Loop not initialized"})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/autonomous/threshold", methods=["GET"])
    def autonomous_threshold_get():
        try:
            if owner._autonomous_loop:
                return jsonify({"threshold": owner._autonomous_loop.get_threshold()})
            return jsonify({"threshold": 2.0})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/desires")
    def desires_status():
        try:
            from aegis_ai.desire.desire_system import DesireSystem

            desire = DesireSystem(data_dir=os.path.join(data_dir, "desires"))
            return jsonify(desire.get_stats())
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/desires/pressure")
    def desires_pressure():
        try:
            from aegis_ai.desire.desire_system import DesireSystem

            ds = DesireSystem(data_dir=os.path.join(data_dir, "desires"))
            return jsonify(ds.get_pressure_state())
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/autonomous/skip-reasons")
    def autonomous_skip_reasons():
        try:
            skip_reasons = []
            audit_path = os.path.join(data_dir, "audit.jsonl")
            if os.path.exists(audit_path):
                with open(audit_path, encoding="utf-8") as f:
                    for line in f:
                        if "autonomous_preflight" in line or "autonomous_no_action" in line:
                            skip_reasons.append(json.loads(line.strip()))
            return jsonify({"skip_reasons": skip_reasons[-20:]})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    owner.app.register_blueprint(bp)
