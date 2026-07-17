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

    @bp.route("/api/autonomous/logs")
    def autonomous_logs():
        """Return execution logs grouped by autonomous cycle."""
        try:
            log_path = os.path.join(data_dir, "autonomous", "execution_log.jsonl")
            if not os.path.exists(log_path):
                return jsonify({"cycles": [], "count": 0})

            cycles = []
            with open(log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    ts = entry.get("timestamp_ms", 0)
                    tasks = entry.get("tasks", [])
                    results = entry.get("results", [])
                    decision = entry.get("last_decision", "")
                    skip_reason = entry.get("last_skip_reason", "")

                    actions = []
                    for i, task in enumerate(tasks):
                        result = results[i] if i < len(results) else {}
                        actions.append({
                            "capability_id": task.get("capability_id", ""),
                            "action": task.get("action_goal", task.get("action", "")),
                            "desire": task.get("desire", ""),
                            "what_was_done": task.get("what_was_done", ""),
                            "result_summary": task.get("result_summary", result.get("result", "")),
                            "changed_state": task.get("changed_state", ""),
                            "success": result.get("success", False),
                        })

                    cycles.append({
                        "timestamp_ms": ts,
                        "decision": decision,
                        "skip_reason": skip_reason,
                        "action_count": len(actions),
                        "actions": actions,
                        "candidate_capability_ids": entry.get("candidate_capability_ids", []),
                        "decision_axes": entry.get("decision_axes", {}),
                    })

            cycles.sort(key=lambda c: c["timestamp_ms"], reverse=True)
            return jsonify({"cycles": cycles[:50], "count": len(cycles)})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/autonomous/logs/<int:timestamp_ms>")
    def autonomous_log_detail(timestamp_ms: int):
        """Return detailed log for a specific autonomous cycle."""
        try:
            log_path = os.path.join(data_dir, "autonomous", "execution_log.jsonl")
            if not os.path.exists(log_path):
                return jsonify({"error": "No execution log found"})

            with open(log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    if abs(entry.get("timestamp_ms", 0) - timestamp_ms) < 1000:
                        return jsonify(entry)

            return jsonify({"error": "Cycle not found"})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @bp.route("/api/audit/grouped")
    def audit_grouped():
        """Return audit entries grouped by autonomous cycle or chat turn."""
        try:
            audit_path = os.path.join(data_dir, "audit.jsonl")
            if not os.path.exists(audit_path):
                return jsonify({"groups": [], "count": 0})

            entries = []
            with open(audit_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entries.append(json.loads(line))

            groups: dict[str, dict[str, Any]] = {}
            for entry in entries:
                group_id = entry.get("group_id", "")
                if not group_id:
                    group_id = f"ungrouped_{entry.get('timestamp_ms', 0)}"

                if group_id not in groups:
                    groups[group_id] = {
                        "group_id": group_id,
                        "group_type": entry.get("group_type", "unknown"),
                        "group_title": entry.get("group_title", ""),
                        "started_at": entry.get("timestamp_ms", 0),
                        "entries": [],
                    }

                group = groups[group_id]
                group["entries"].append({
                    "action": entry.get("action", ""),
                    "capability_id": entry.get("capability_id", ""),
                    "decision": entry.get("decision", ""),
                    "reason": entry.get("reason", ""),
                    "timestamp_ms": entry.get("timestamp_ms", 0),
                    "actor": entry.get("actor", ""),
                })
                group["started_at"] = min(group["started_at"], entry.get("timestamp_ms", 0))

            sorted_groups = sorted(groups.values(), key=lambda g: g["started_at"], reverse=True)
            return jsonify({"groups": sorted_groups[:30], "count": len(groups)})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    owner.app.register_blueprint(bp)
