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
from flask import Blueprint, jsonify, request

logger = logging.getLogger("aegis_ai.web.manager_routes")

manager_bp = Blueprint("managers", __name__)

_runtime = None


def init_manager_routes(app, runtime):
    """Register manager routes on the Flask app."""
    global _runtime
    _runtime = runtime
    app.register_blueprint(manager_bp)
    from aegis_ai.web.resource_routes import init_resource_routes

    init_resource_routes(app, runtime)


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
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/tasks/<task_id>")
def get_task(task_id):
    try:
        rt = _get_runtime()
        task = rt.task_manager.get_task(task_id)
        if task is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(task)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/tasks/running")
def tasks_running():
    try:
        rt = _get_runtime()
        return jsonify({"tasks": rt.task_manager.list_running()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/tasks/waiting-approval")
def tasks_waiting():
    try:
        rt = _get_runtime()
        return jsonify({"tasks": rt.task_manager.list_waiting_approval()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/tasks/<task_id>/continue", methods=["POST"])
def continue_task(task_id):
    try:
        rt = _get_runtime()
        engine = getattr(rt, "execution_engine", None)
        if engine is None:
            return jsonify({"error": "Execution engine unavailable"}), 503
        response = engine.continue_task(task_id)
        return jsonify({"ok": True, "text": response.text, "task_id": response.task_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/events/<event_id>")
def get_event(event_id):
    try:
        rt = _get_runtime()
        event = rt.event_manager.get_event(event_id)
        if event is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(event)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/journal/events")
def list_journal_events():
    try:
        rt = _get_runtime()
        store = getattr(rt.event_manager, "_journal", None) if getattr(rt, "event_manager", None) else None
        if store is None or not hasattr(store, "list_recent"):
            return jsonify({"items": [], "total": 0, "page": 1, "limit": 50, "source": "journal"})
        page = max(1, int(request.args.get("page", 1)))
        limit = min(200, max(1, int(request.args.get("limit", 50))))
        event_type = str(request.args.get("event_type") or "").strip()
        rows = store.list_recent(limit=500)
        if event_type:
            rows = [row for row in rows if str(row.get("event_type") or "") == event_type]
        rows.reverse()
        total = len(rows)
        start = (page - 1) * limit
        page_rows = rows[start:start + limit]
        from aegis_ai.journal.projector import journal_event_for_ui

        return jsonify({
            "items": [journal_event_for_ui(row) for row in page_rows],
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": max(1, (total + limit - 1) // limit),
            "source": "journal",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Audit Routes ──────────────────────────────────────────────

@manager_bp.route("/api/audit")
def list_audit():
    try:
        rt = _get_runtime()
        limit = int(request.args.get("limit", 100))
        page = max(1, int(request.args.get("page", 1)))
        cursor = request.args.get("cursor")
        action = request.args.get("action")
        errors_only = request.args.get("errors_only") == "true"
        result = rt.audit_manager.list_recent(
            limit=limit, page=page, cursor=cursor, action=action, errors_only=errors_only
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/audit/<audit_id>")
def get_audit_detail(audit_id):
    try:
        rt = _get_runtime()
        entry = rt.audit_manager.get_detail(audit_id)
        if entry is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(entry)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/audit/summary")
def audit_summary():
    try:
        rt = _get_runtime()
        hours = int(request.args.get("hours", 24))
        return jsonify(rt.audit_manager.summarize(period_hours=hours))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Status Routes ─────────────────────────────────────────────

@manager_bp.route("/api/status")
def get_status():
    try:
        rt = _get_runtime()
        snapshot = rt.status_manager.get_snapshot()
        _overlay_android_status(rt, snapshot)
        return jsonify(snapshot)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/status/<server_id>")
def get_server_status(server_id):
    try:
        rt = _get_runtime()
        status = rt.status_manager.get_server_status(server_id)
        if status is None:
            return jsonify({"error": "Not found"}), 404
        status = dict(status)
        if server_id == "android-server":
            wrapped = {"android-server": status}
            _overlay_android_status(rt, wrapped)
            status = wrapped["android-server"]
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _overlay_android_status(rt, snapshot: dict) -> None:
    manager = getattr(rt, "android_manager", None)
    if manager is None or "android-server" not in snapshot:
        return
    try:
        android_status = manager.get_status()
    except Exception:
        return
    if not android_status.get("online"):
        return
    item = dict(snapshot["android-server"])
    item["status"] = "online"
    item["error"] = None
    item["host"] = item.get("host") or "reverse-stream"
    item["connection_mode"] = android_status.get("connection_mode", "reverse_stream")
    item["last_check_ms"] = android_status.get("last_seen") or item.get("last_check_ms", 0)
    snapshot["android-server"] = item


@manager_bp.route("/api/android/status")
def get_android_status():
    try:
        rt = _get_runtime()
        manager = getattr(rt, "android_manager", None)
        if manager is None:
            return jsonify({"online": False, "error": "Android manager not initialized"}), 503
        return jsonify(manager.get_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/status/check-now", methods=["POST"])
def check_now():
    try:
        rt = _get_runtime()
        snapshot = rt.status_manager.check_now()
        _overlay_android_status(rt, snapshot)
        return jsonify(snapshot)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/notifications/<notif_id>/read", methods=["POST"])
def mark_notification_read(notif_id):
    try:
        rt = _get_runtime()
        notif = rt.notification_manager.mark_read(notif_id)
        if notif is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(notif)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/notifications/<notif_id>/dismiss", methods=["POST"])
def dismiss_notification(notif_id):
    try:
        rt = _get_runtime()
        notif = rt.notification_manager.dismiss(notif_id)
        if notif is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(notif)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/memory/stats")
def memory_stats():
    try:
        rt = _get_runtime()
        return jsonify(rt.memory_manager.get_stats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/memory/sleep/status")
def sleep_status():
    try:
        rt = _get_runtime()
        return jsonify(rt.sleep_manager.get_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/memory/sleep", methods=["POST"])
def trigger_sleep():
    try:
        rt = _get_runtime()
        success = rt.sleep_manager.start_sleep(reason="manual")
        return jsonify({"started": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Personal AI Routes

@manager_bp.route("/api/user-model", methods=["GET", "POST"])
def user_model():
    try:
        rt = _get_runtime()
        if request.method == "POST":
            payload = request.get_json(silent=True) or {}
            rt.user_model_store.update(payload.get("patch") or payload, reason=payload.get("reason", "dashboard"))
        return jsonify({"model": rt.user_model_store.get().to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/hooks", methods=["GET", "POST"])
def hooks():
    try:
        rt = _get_runtime()
        if request.method == "POST":
            return jsonify({"hook": rt.hook_engine.upsert_hook(request.get_json(silent=True) or {})})
        return jsonify({"hooks": rt.hook_engine.list_hooks()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/hooks/<hook_id>", methods=["GET", "DELETE", "POST"])
def hook_detail(hook_id):
    try:
        rt = _get_runtime()
        if request.method == "DELETE":
            return jsonify({"deleted": rt.hook_engine.delete_hook(hook_id)})
        if request.method == "POST":
            payload = request.get_json(silent=True) or {}
            payload["hook_id"] = hook_id
            return jsonify({"hook": rt.hook_engine.upsert_hook(payload)})
        hook = rt.hook_engine.get_hook(hook_id)
        if hook is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(hook)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/hooks/run-due", methods=["POST"])
def hooks_run_due():
    try:
        rt = _get_runtime()
        return jsonify({"results": rt.hook_engine.run_due_once()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/hooks/<hook_id>/stop", methods=["POST"])
def hook_stop(hook_id):
    try:
        rt = _get_runtime()
        payload = request.get_json(silent=True) or {}
        hook = rt.hook_engine.stop_hook(hook_id, reason=payload.get("reason", "dashboard"))
        if hook is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"hook": hook})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/commitments", methods=["GET", "POST"])
def commitments():
    try:
        rt = _get_runtime()
        if request.method == "POST":
            return jsonify({"commitment": rt.commitment_manager.upsert_commitment(request.get_json(silent=True) or {})})
        return jsonify({"commitments": rt.commitment_manager.list_commitments(status=request.args.get("status"))})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/commitments/<commitment_id>/transition", methods=["POST"])
def commitment_transition(commitment_id):
    try:
        rt = _get_runtime()
        payload = request.get_json(silent=True) or {}
        item = rt.commitment_manager.transition(
            commitment_id,
            payload.get("status", "completed"),
            reason=payload.get("reason", ""),
            postpone_until_ms=int(payload.get("postpone_until_ms") or 0),
        )
        if item is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"commitment": item})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/delegation-policy", methods=["GET", "POST"])
def delegation_policy():
    try:
        rt = _get_runtime()
        if request.method == "POST":
            return jsonify({"rule": rt.delegation_policy.upsert_rule(request.get_json(silent=True) or {})})
        return jsonify(rt.delegation_policy.get_summary())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/delegation-policy/<rule_id>", methods=["DELETE"])
def delegation_policy_delete(rule_id):
    try:
        rt = _get_runtime()
        return jsonify({"deleted": rt.delegation_policy.delete_rule(rule_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/situation", methods=["GET", "POST"])
def situation():
    try:
        rt = _get_runtime()
        if request.method == "POST":
            payload = request.get_json(silent=True) or {}
            return jsonify(rt.situation_model.update_from_observation(payload.get("source", "dashboard"), payload.get("payload", {})))
        return jsonify(rt.situation_model.get_state())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/user-state/current")
def user_state_current():
    try:
        rt = _get_runtime()
        return jsonify(rt.user_state_manager.get_current_user_state())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/user-state/events")
def user_state_events():
    try:
        rt = _get_runtime()
        limit = max(1, min(20, int(request.args.get("limit", 20))))
        source = request.args.get("source") or None
        return jsonify({"events": rt.user_state_manager.get_recent_events(limit=limit, source=source)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/user-state/days")
def user_state_days():
    try:
        rt = _get_runtime()
        return jsonify(rt.user_state_manager.list_days())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/user-state/archive/run", methods=["POST"])
def user_state_archive_run():
    try:
        rt = _get_runtime()
        return jsonify(rt.user_state_manager.archive_due_logs())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/user-state/poll-pc", methods=["POST"])
def user_state_poll_pc():
    try:
        rt = _get_runtime()
        return jsonify(rt.user_state_manager.poll_pc_once(rt.server_executor))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/user-state/ingest", methods=["POST"])
def user_state_ingest():
    try:
        rt = _get_runtime()
        payload = request.get_json(silent=True) or {}
        source = str(payload.get("source") or "dashboard")
        event_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
        return jsonify({"event": rt.user_state_manager.ingest_event(source, event_payload)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _pdc():
    rt = _get_runtime()
    core = getattr(rt, "personal_data_core", None)
    if core is not None:
        return core
    # Image runtimes may predate PersonalDataCore wiring; lazy-attach so Timeline
    # routes work without replacing the whole runtime module.
    try:
        from aegis_ai.personal_data import PersonalDataCore

        data_dir = getattr(rt, "data_dir", None) or "data"
        core = PersonalDataCore(
            data_dir,
            event_manager=getattr(rt, "event_manager", None),
            settings_store=getattr(rt, "settings_store", None),
            audit_manager=getattr(rt, "audit_manager", None),
            memory_manager=getattr(rt, "memory_manager", None),
            server_executor=getattr(rt, "server_executor", None),
        )
        try:
            setattr(rt, "personal_data_core", core)
        except Exception:
            pass
        event_manager = getattr(rt, "event_manager", None)
        if event_manager is not None:
            event_manager._personal_data_core = core
        return core
    except Exception:
        logger.exception("Failed to initialize PersonalDataCore for manager routes")
        return None


@manager_bp.route("/api/personal-data/timeline")
def personal_data_timeline():
    core = _pdc()
    if core is None:
        return jsonify({"items": [], "total": 0, "event_types": [], "source": "personal_data"})
    try:
        from_ms = int(request.args.get("from") or 0)
        to_ms = int(request.args.get("to") or 0)
        device = _normalize_pdc_device(str(request.args.get("device") or ""))
        event_type = str(request.args.get("event_type") or request.args.get("type") or "")
        page = max(1, int(request.args.get("page") or 1))
        # User log: allow paging / bulk fetch of the full Personal Data Core history.
        limit = min(50_000, max(1, int(request.args.get("limit") or 50)))
        result = core.timeline(
            from_ms=from_ms,
            to_ms=to_ms,
            device=device,
            event_type=event_type,
            limit=limit,
            offset=(page - 1) * limit,
        )
        result["page"] = page
        result["limit"] = limit
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _normalize_pdc_device(device: str) -> str:
    value = (device or "").strip().lower()
    if value in {"", "all", "*"}:
        return ""
    if value in {"pc-server", "pc_server"}:
        return "pc"
    if value in {"android-server", "android_server"}:
        return "android"
    if value in {"room-server", "room_server"}:
        return "room"
    if value in {"ai-server", "aegis-ai", "aegis_ai"}:
        return "aegis"
    return value


@manager_bp.route("/api/personal-data/events/<event_id>")
def personal_data_event(event_id):
    core = _pdc()
    if core is None:
        return jsonify({"error": "unavailable"}), 503
    item = core.get_event(event_id)
    if item is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(item)


@manager_bp.route("/api/personal-data/search")
def personal_data_search():
    core = _pdc()
    if core is None:
        return jsonify({"items": [], "query": "", "total": 0, "source": "personal_data"})
    try:
        limit = min(10_000, max(1, int(request.args.get("limit") or 50)))
        result = core.search(
            str(request.args.get("q") or ""),
            from_ms=int(request.args.get("from") or 0),
            to_ms=int(request.args.get("to") or 0),
            limit=limit,
        )
        items = result.get("items") or []
        result["total"] = int(result.get("total") or len(items))
        result["limit"] = limit
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/personal-data/evidence/<evidence_id>")
def personal_data_evidence(evidence_id):
    core = _pdc()
    if core is None:
        return jsonify({"error": "unavailable"}), 503
    got = core.get_evidence_bytes(evidence_id)
    if got is None:
        return jsonify({"error": "Not found"}), 404
    data, meta = got
    from flask import Response
    return Response(data, mimetype=str(meta.get("mime") or "application/octet-stream"))


@manager_bp.route("/api/personal-data/policy", methods=["GET", "POST"])
def personal_data_policy():
    core = _pdc()
    if core is None:
        return jsonify({"error": "unavailable"}), 503
    if request.method == "GET":
        return jsonify(core.policy().model_dump())
    payload = request.get_json(silent=True) or {}
    rt = _get_runtime()
    settings = rt.settings_store.get()
    privacy = settings.privacy
    for key, value in payload.items():
        field = key if key.startswith("personal_data_") else f"personal_data_{key}"
        if hasattr(privacy, field):
            setattr(privacy, field, value)
    rt.settings_store.save(settings)
    return jsonify(core.policy().model_dump())


@manager_bp.route("/api/personal-data/export", methods=["POST"])
def personal_data_export():
    core = _pdc()
    if core is None:
        return jsonify({"error": "unavailable"}), 503
    payload = request.get_json(silent=True) or {}
    return jsonify(core.export_range(int(payload.get("from") or 0), int(payload.get("to") or 0)))


@manager_bp.route("/api/personal-data/delete", methods=["POST"])
def personal_data_delete():
    core = _pdc()
    if core is None:
        return jsonify({"error": "unavailable"}), 503
    payload = request.get_json(silent=True) or {}
    ids = payload.get("event_ids") or payload.get("ids") or []
    return jsonify(core.delete_events([str(item) for item in ids]))


@manager_bp.route("/api/personal-data/room/frame", methods=["POST"])
def personal_data_room_frame():
    core = _pdc()
    if core is None:
        return jsonify({"error": "unavailable"}), 503
    jpeg = request.get_data() or b""
    if request.content_type and "json" in request.content_type:
        payload = request.get_json(silent=True) or {}
        import base64
        jpeg = base64.b64decode(payload.get("image_base64") or "")
        loc = payload.get("location") if isinstance(payload.get("location"), dict) else {}
        return jsonify(core.ingest_room_frame(jpeg, location=loc))
    return jsonify(core.ingest_room_frame(jpeg))


@manager_bp.route("/api/personal-data/room/audio", methods=["POST"])
def personal_data_room_audio():
    core = _pdc()
    if core is None:
        return jsonify({"error": "unavailable"}), 503
    return jsonify(core.ingest_room_audio(request.get_data() or b""))


@manager_bp.route("/api/interruption", methods=["GET"])
def interruption():
    try:
        rt = _get_runtime()
        return jsonify(rt.interruption_controller.get_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/autonomous/diagnostics", methods=["GET"])
def autonomous_diagnostics():
    """Return initiative funnel, continuations, social outcomes, and delivery evidence."""
    try:
        rt = _get_runtime()
        approvals = rt.approval_manager.list_all(limit=200)
        surfaces = {
            request.approval_id: request.surface_delivery_evidence
            for request in approvals
            if request.surface_delivery_evidence
        }
        return jsonify(
            {
                "initiative": rt.initiative_engine.diagnostics(),
                "continuations": rt.continuation_manager.diagnostics(),
                "social": rt.social_manager.get_status(),
                "browser": rt.exploration_agenda.diagnostics(),
                "preferences": {"recent": rt.preference_store.list(limit=50)},
                "daily_plan": rt.daily_planning_manager.get(),
                "behavioral_evaluation": rt.behavioral_evaluation.snapshot(),
                "approval_surfaces": surfaces,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/social/inbox", methods=["GET"])
def social_inbox():
    try:
        rt = _get_runtime()
        status = str(request.args.get("status") or "")
        limit = min(500, max(1, int(request.args.get("limit", 200))))
        return jsonify({"items": rt.social_manager.list_items(status=status, limit=limit)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/continuations", methods=["GET"])
def continuations():
    try:
        rt = _get_runtime()
        return jsonify(rt.continuation_manager.diagnostics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/autonomous/daily-plan", methods=["GET", "POST"])
def autonomous_daily_plan():
    try:
        rt = _get_runtime()
        if request.method == "POST":
            payload = request.get_json(silent=True) or {}
            return jsonify(rt.daily_planning_manager.generate(date=payload.get("date")))
        return jsonify({"plan": rt.daily_planning_manager.get(date=request.args.get("date"))})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/interruption/flush", methods=["POST"])
def interruption_flush():
    try:
        rt = _get_runtime()
        return jsonify({"items": rt.interruption_controller.flush_batch()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/interruption/emergency-stop", methods=["POST"])
def interruption_emergency_stop():
    try:
        rt = _get_runtime()
        payload = request.get_json(silent=True) or {}
        return jsonify(rt.interruption_controller.set_emergency_stop(bool(payload.get("active", True))))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/repair", methods=["GET"])
def repair():
    try:
        rt = _get_runtime()
        return jsonify(rt.repair_manager.get_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/repair/disable", methods=["POST"])
def repair_disable():
    try:
        rt = _get_runtime()
        payload = request.get_json(silent=True) or {}
        return jsonify(rt.repair_manager.set_disabled(bool(payload.get("disabled", True))))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/social/drafts", methods=["GET", "POST"])
def social_drafts():
    try:
        rt = _get_runtime()
        if request.method == "POST":
            payload = request.get_json(silent=True) or {}
            return jsonify({"draft": rt.social_proxy.create_draft(
                channel=payload.get("channel", ""),
                to=payload.get("to", ""),
                subject=payload.get("subject", ""),
                body=payload.get("body", ""),
                payload=payload.get("payload", {}),
            )})
        return jsonify({"drafts": rt.social_proxy.list_drafts()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Presentation Routes ──────────────────────────────────────────

@manager_bp.route("/api/presentations", methods=["GET"])
def list_presentations():
    try:
        rt = _get_runtime()
        limit = int(request.args.get("limit", 100))
        return jsonify({"presentations": rt.presentation_manager.list_active(limit=limit)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/presentations/xr/pending", methods=["GET"])
def xr_pending_presentations():
    try:
        rt = _get_runtime()
        limit = int(request.args.get("limit", 50))
        adapter = rt.presentation_manager._router._xr
        return jsonify({"presentations": adapter.drain(limit)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/presentations/xr/count", methods=["GET"])
def xr_pending_count():
    try:
        rt = _get_runtime()
        adapter = rt.presentation_manager._router._xr
        return jsonify({"count": adapter.count()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/presentations/<presentation_id>", methods=["GET"])
def get_presentation(presentation_id):
    try:
        rt = _get_runtime()
        pres = rt.presentation_manager.get(presentation_id)
        if pres is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(pres)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/presentations/<presentation_id>/action", methods=["POST"])
def presentation_action(presentation_id):
    try:
        rt = _get_runtime()
        payload = request.get_json(silent=True) or {}
        return jsonify(rt.presentation_manager.user_action(presentation_id, payload))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/presentations/<presentation_id>/dismiss", methods=["POST"])
def presentation_dismiss(presentation_id):
    try:
        rt = _get_runtime()
        return jsonify(rt.presentation_manager.dismiss(presentation_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manager_bp.route("/api/presentations/stream")
def presentation_stream():
    """SSE endpoint for live presentation updates."""
    import queue
    q: queue.Queue = queue.Queue()

    def _on_event(event_type: str, payload: dict) -> None:
        if event_type.startswith("presentation."):
            q.put({"event": event_type, "data": payload})

    rt = _get_runtime()
    if rt.event_manager is not None:
        rt.event_manager.subscribe(_on_event)

    def generate():
        try:
            while True:
                try:
                    item = q.get(timeout=30)
                    import json
                    yield f"data: {json.dumps(item)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        except GeneratorExit:
            pass

    from flask import Response
    return Response(generate(), mimetype="text/event-stream")
