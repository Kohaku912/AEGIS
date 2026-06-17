"""Manager Routes — Flask API routes for all centralized managers.

Provides:
- /api/tasks — Task management
- /api/events — Event queries
- /api/audit — Audit queries
- /api/status — Server status
- /api/notifications — Notification management
- /api/memory — Memory operations
- /api/memory/sleep — Sleep management
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint, jsonify, request

logger = logging.getLogger("aegis_ai.web.manager_routes")

manager_bp = Blueprint("managers", __name__)

_runtime = None


def init_manager_routes(app, runtime):
    """Register manager routes on the Flask app."""
    global _runtime
    _runtime = runtime
    app.register_blueprint(manager_bp)


def _get_runtime():
    if _runtime is not None:
        return _runtime
    from aegis_ai.runtime import get_runtime
    return get_runtime()


# ── Task Routes ───────────────────────────────────────────────

@manager_bp.route("/api/tasks")
def list_tasks():
    try:
        rt = _get_runtime()
        status = request.args.get("status")
        source = request.args.get("source")
        limit = int(request.args.get("limit", 100))
        tasks = rt.task_manager.list_tasks(status=status, source=source, limit=limit)
        return jsonify({"tasks": tasks})
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/tasks/<task_id>")
def get_task(task_id):
    try:
        rt = _get_runtime()
        task = rt.task_manager.get_task(task_id)
        if task is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(task)
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/tasks/running")
def tasks_running():
    try:
        rt = _get_runtime()
        return jsonify({"tasks": rt.task_manager.list_running()})
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/tasks/waiting-approval")
def tasks_waiting():
    try:
        rt = _get_runtime()
        return jsonify({"tasks": rt.task_manager.list_waiting_approval()})
    except Exception as e:
        return jsonify({"error": str(e)})


# ── Event Routes ──────────────────────────────────────────────

@manager_bp.route("/api/events")
def list_events():
    try:
        rt = _get_runtime()
        limit = int(request.args.get("limit", 50))
        cursor = request.args.get("cursor")
        result = rt.event_manager.list_recent(limit=limit, cursor=cursor)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/events/<event_id>")
def get_event(event_id):
    try:
        rt = _get_runtime()
        event = rt.event_manager.get_event(event_id)
        if event is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(event)
    except Exception as e:
        return jsonify({"error": str(e)})


# ── Audit Routes ──────────────────────────────────────────────

@manager_bp.route("/api/audit")
def list_audit():
    try:
        rt = _get_runtime()
        limit = int(request.args.get("limit", 100))
        cursor = request.args.get("cursor")
        action = request.args.get("action")
        errors_only = request.args.get("errors_only") == "true"
        result = rt.audit_manager.list_recent(
            limit=limit, cursor=cursor, action=action, errors_only=errors_only
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/audit/<audit_id>")
def get_audit_detail(audit_id):
    try:
        rt = _get_runtime()
        entry = rt.audit_manager.get_detail(audit_id)
        if entry is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(entry)
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/audit/summary")
def audit_summary():
    try:
        rt = _get_runtime()
        hours = int(request.args.get("hours", 24))
        return jsonify(rt.audit_manager.summarize(period_hours=hours))
    except Exception as e:
        return jsonify({"error": str(e)})


# ── Status Routes ─────────────────────────────────────────────

@manager_bp.route("/api/status")
def get_status():
    try:
        rt = _get_runtime()
        return jsonify(rt.status_manager.get_snapshot())
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/status/<server_id>")
def get_server_status(server_id):
    try:
        rt = _get_runtime()
        status = rt.status_manager.get_server_status(server_id)
        if status is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/status/check-now", methods=["POST"])
def check_now():
    try:
        rt = _get_runtime()
        snapshot = rt.status_manager.check_now()
        return jsonify(snapshot)
    except Exception as e:
        return jsonify({"error": str(e)})


# ── Notification Routes ───────────────────────────────────────

@manager_bp.route("/api/notifications")
def list_notifications():
    try:
        rt = _get_runtime()
        unread = request.args.get("unread") == "true"
        limit = int(request.args.get("limit", 50))
        if unread:
            notifs = rt.notification_manager.list_unread(limit=limit)
        else:
            notifs = rt.notification_manager.list_recent(limit=limit)
        return jsonify({"notifications": notifs})
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/notifications/<notif_id>/read", methods=["POST"])
def mark_notification_read(notif_id):
    try:
        rt = _get_runtime()
        notif = rt.notification_manager.mark_read(notif_id)
        if notif is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(notif)
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/notifications/<notif_id>/dismiss", methods=["POST"])
def dismiss_notification(notif_id):
    try:
        rt = _get_runtime()
        notif = rt.notification_manager.dismiss(notif_id)
        if notif is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(notif)
    except Exception as e:
        return jsonify({"error": str(e)})


# ── Memory Routes ─────────────────────────────────────────────

@manager_bp.route("/api/memory/search")
def search_memory():
    try:
        rt = _get_runtime()
        query = request.args.get("q", "")
        limit = int(request.args.get("limit", 20))
        results = rt.memory_manager.search_memory(query, limit=limit)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/memory/stats")
def memory_stats():
    try:
        rt = _get_runtime()
        return jsonify(rt.memory_manager.get_stats())
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/memory/sleep/status")
def sleep_status():
    try:
        rt = _get_runtime()
        return jsonify(rt.sleep_manager.get_status())
    except Exception as e:
        return jsonify({"error": str(e)})


@manager_bp.route("/api/memory/sleep", methods=["POST"])
def trigger_sleep():
    try:
        rt = _get_runtime()
        success = rt.sleep_manager.start_sleep(reason="manual")
        return jsonify({"started": success})
    except Exception as e:
        return jsonify({"error": str(e)})
