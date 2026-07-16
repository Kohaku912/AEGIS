"""Normalized UI overview for Web, Android, and display surfaces."""

from __future__ import annotations

import time
import hashlib
from dataclasses import asdict, is_dataclass
from typing import Any

from aegis_ai.presentation.surface_contract import (
    presentation_event_from_presentation,
    presentation_event_from_ui_event,
    surface_roles,
)

_MAX_UI_STRING_CHARS = 2_000
_MAX_UI_LIST_ITEMS = 50
_MAX_UI_DICT_ITEMS = 80
_MAX_UI_DEPTH = 6
_MAX_STEP_RESULT_PREVIEW_CHARS = 240


def build_ui_overview(runtime: Any) -> dict[str, Any]:
    """Build the v2 UI overview from runtime managers.

    UI surfaces must not read audit files, chat history files, settings files, or
    memory internals directly. This projection keeps that boundary in one place.
    """

    generated_at = _now_ms()
    sections = {
        "core": _section("core", lambda: _core(runtime), generated_at),
        "connection": _section("connection", lambda: _connection(runtime), generated_at),
        "display_scene": _section("display_scene", lambda: _display_scene(runtime), generated_at),
        "presentations": _section("presentations", lambda: _presentations(runtime), generated_at),
        "presentation_events": _section("presentation_events", lambda: _presentation_events(runtime), generated_at),
        "surface_roles": _section("surface_roles", lambda: _surface_roles(), generated_at),
        "display_queue": _section("display_queue", lambda: _display_queue(runtime), generated_at),
        "tasks": _section("tasks", lambda: _tasks(runtime), generated_at),
        "activity": _section("activity", lambda: _activity(runtime), generated_at),
        "attention": _section("attention", lambda: _attention(runtime), generated_at),
        "current_task": _section("current_task", lambda: _current_task(runtime), generated_at),
        "servers": _section("servers", lambda: _servers(runtime), generated_at),
        "capabilities": _section("capabilities", lambda: _capabilities(runtime), generated_at),
        "user_situation": _section("user_situation", lambda: _user_state(runtime), generated_at),
        "user_state": _section("user_state", lambda: _user_state(runtime), generated_at),
        "mind": _section("mind", lambda: _mind_summary(runtime), generated_at),
        "mind_summary": _section("mind_summary", lambda: _mind_summary(runtime), generated_at),
        "memory": _section("memory", lambda: _memory(runtime), generated_at),
        "notifications": _section("notifications", lambda: _notifications(runtime), generated_at),
        "approvals": _section("approvals", lambda: _approvals(runtime), generated_at),
        "commitments": _section("commitments", lambda: _commitments(runtime), generated_at),
        "usage": _section("usage", lambda: _usage(runtime), generated_at),
        "errors": _section("errors", lambda: _errors(runtime), generated_at),
        "freshness": _section("freshness", lambda: _freshness(runtime), generated_at),
    }
    return {"schema_version": "ui-overview.v3", "generated_at": generated_at, **sections}


def normalize_ui_event(event: Any) -> dict[str, Any]:
    """Convert an internal event into the compact SSE/gRPC UI event format."""

    event_type = str(getattr(event, "event_type", "") or _get(event, "event_type", "event"))
    timestamp = int(getattr(event, "timestamp", 0) or _get(event, "timestamp", _now_ms()))
    payload = getattr(event, "payload", None)
    if payload is None:
        payload = _get(event, "payload", {})
    plain_payload = _bound_for_ui(_to_plain(payload), max_depth=5)
    fields = _event_fields(event_type, plain_payload)
    sequence = _event_sequence(event, event_type, timestamp, plain_payload)
    event_id = _event_id(event, event_type, timestamp, sequence, plain_payload)
    normalized = {
        "event_id": event_id,
        "sequence": sequence,
        "type": _ui_event_type(event_type),
        "event_type": event_type,
        "source_type": event_type,
        "occurred_at": timestamp,
        "received_at": _now_ms(),
        "generated_at": _now_ms(),
        "source_updated_at": timestamp,
        "priority": _event_priority(fields),
        "dedupe_key": _event_dedupe_key(event_type, fields),
        "persistence": _event_persistence(fields),
        "expires_at": _event_expires_at(timestamp, fields),
        "resolved_by": _event_resolved_by(event_type, fields),
        "affected_servers": [fields["server_id"]] if fields.get("server_id") else [],
        "affected_capabilities": [fields["capability_id"]] if fields.get("capability_id") else [],
        "safe_title": _event_title(event_type, fields),
        "safe_message": fields.get("message", ""),
        "visual_hint": _visual_hint(event_type, fields),
        "payload": plain_payload,
        **fields,
    }
    normalized["presentation_event"] = presentation_event_from_ui_event(normalized)
    normalized["scene_type"] = normalized["presentation_event"]["scene_type"]
    normalized["privacy_class"] = normalized["presentation_event"]["privacy_class"]
    normalized["recommended_surfaces"] = normalized["presentation_event"]["recommended_surfaces"]
    normalized["available_actions"] = normalized["presentation_event"]["available_actions"]
    return normalized


def _section(name: str, build, generated_at: int) -> dict[str, Any]:
    try:
        data = _bound_for_ui(_to_plain(build()))
        source_updated_at = _infer_source_updated_at(data) or generated_at
        return {
            "generated_at": generated_at,
            "source_updated_at": source_updated_at,
            "status": "ok",
            "stale": _is_stale(source_updated_at, generated_at),
            "error": "",
            "data": data,
        }
    except Exception as exc:
        return {
            "generated_at": generated_at,
            "source_updated_at": generated_at,
            "status": "error",
            "stale": True,
            "error": f"{name} unavailable: {exc}",
            "data": _empty_data(name),
        }


def _core(runtime: Any) -> dict[str, Any]:
    servers = _server_list(runtime)
    offline = [
        str(item.get("server_id", ""))
        for item in servers
        if str(item.get("status", "")).upper() in {"OFFLINE", "UNKNOWN"}
    ]
    degraded = [
        str(item.get("server_id", ""))
        for item in servers
        if str(item.get("status", "")).upper() in {"DEGRADED", "CRITICAL", "PERMISSION_MISSING"}
    ]
    pending_approvals = len(_pending_approvals(runtime))
    active_tasks = _running_tasks(runtime)
    mode = "WAITING" if pending_approvals else "EXECUTING" if active_tasks else "IDLE"
    health = "DEGRADED" if degraded else "OFFLINE" if offline and len(offline) >= len(servers or offline) else "ONLINE"
    return {
        "mode": mode,
        "health": health,
        "activity_level": 3 if active_tasks else 2 if pending_approvals else 1,
        "confidence": "medium" if degraded or offline else "high",
        "active_goal": _get(active_tasks[0], "goal", "") if active_tasks else "",
        "attention_level": "approval" if pending_approvals else "critical" if offline else "normal",
        "pending_approval_count": pending_approvals,
        "offline_servers": offline,
        "degraded_servers": degraded,
    }


def _attention(runtime: Any) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for approval in _pending_approvals(runtime):
        item = _approval_projection(approval)
        items.append(
            {
                "id": item.get("approval_id", ""),
                "kind": "approval",
                "severity": "warning",
                "title": "Approval required",
                "message": item.get("summary") or item.get("capability_id", ""),
                "created_at": item.get("created_at", 0),
                "expires_at": item.get("expires_at", 0),
                "recovery_hint": "Review the action and approve or reject it.",
            }
        )
    for server in _server_list(runtime):
        status = str(server.get("status", "")).upper()
        if status in {"OFFLINE", "DEGRADED"}:
            items.append(
                {
                    "id": f"server:{server.get('server_id', '')}",
                    "kind": "server",
                    "severity": "critical" if status == "OFFLINE" else "warning",
                    "title": f"{server.get('server_id', 'server')} {status}",
                    "message": server.get("status_detail") or server.get("degraded_reason") or status,
                    "created_at": server.get("health_checked_at", 0),
                    "recovery_hint": server.get("recovery_hint", ""),
                }
            )
    for notification in _recent_notifications(runtime, unread_only=True, limit=8):
        items.append(
            {
                "id": notification.get("notification_id") or notification.get("id", ""),
                "kind": "notification",
                "severity": notification.get("severity", "info"),
                "title": notification.get("title", "Notification"),
                "message": notification.get("message", ""),
                "created_at": notification.get("created_at", 0),
                "recovery_hint": notification.get("recovery_hint", ""),
            }
        )
    return {"items": sorted(items, key=_attention_sort_key)[:12], "count": len(items)}


def _current_task(runtime: Any) -> dict[str, Any]:
    running = _running_tasks(runtime)
    waiting = _waiting_tasks(runtime)
    task = running[0] if running else waiting[0] if waiting else None
    if not task:
        return {
            "task_id": "",
            "title": "No active task",
            "phase": "idle",
            "original_instruction": "",
            "plan_summary": "",
            "dependency_edges": [],
            "current_action": "",
            "next_action": "",
            "blocked_reason": "",
            "verification_summary": "",
            "final_output": "",
            "audit_group_id": "",
            "conversation_id": "",
            "cost_summary": "",
            "steps": [],
        }
    raw_steps = _get(task, "steps", []) or []
    current_step = next((s for s in raw_steps if _get(s, "status", "") in {"running", "needs_approval"}), None)
    return {
        "task_id": _get(task, "task_id", ""),
        "title": _get(task, "title", "") or _get(task, "goal", "") or "Task",
        "phase": _get(task, "status", ""),
        "original_instruction": _task_original_instruction(task),
        "plan_summary": _task_plan_summary(task, raw_steps),
        "dependency_edges": _task_dependency_edges(raw_steps),
        "current_action": _truncate_text(_get(current_step, "description", "") if current_step else ""),
        "next_action": _truncate_text(_get(task, "next_action", "")),
        "blocked_reason": _truncate_text(_get(task, "blocked_reason", "")),
        "capability_id": _get(current_step, "capability_id", "") if current_step else "",
        "started_at": _get(task, "created_at", 0),
        "updated_at": _get(task, "updated_at", 0),
        "verification_summary": _verification_summary(raw_steps),
        "final_output": _final_output_summary(task, raw_steps),
        "audit_group_id": _get(task, "audit_group_id", "") or _get(task, "request_id", ""),
        "conversation_id": _get(task, "conversation_id", "") or _get(task, "chat_id", ""),
        "cost_summary": _cost_summary(task),
        "steps": [_task_step_projection(step) for step in raw_steps[:12]],
        "step_count": len(raw_steps),
    }


def _connection(runtime: Any) -> dict[str, Any]:
    servers = _server_list(runtime)
    online = sum(1 for server in servers if str(server.get("status", "")).upper() == "ONLINE")
    attention = [server for server in servers if _server_needs_attention(server)]
    return {
        "quality": "degraded" if attention else "good",
        "online_count": online,
        "total_count": len(servers),
        "attention_count": len(attention),
        "surface": "runtime",
        "last_updated_at": max([int(server.get("health_checked_at", 0) or 0) for server in servers] or [_now_ms()]),
    }


def _display_scene(runtime: Any) -> dict[str, Any]:
    core = _core(runtime)
    attention = _attention(runtime).get("items", [])
    phase = _mission_phase(core, _current_task(runtime), len(_pending_approvals(runtime)))
    return {
        "mode": core.get("mode", "IDLE"),
        "phase": phase,
        "density": "standard",
        "recovery_state": "stable" if core.get("health") == "ONLINE" else "attention",
        "privacy_redaction_reason": "privacy mode hides task titles and messages" if False else "",
        "priority": "P1" if core.get("pending_approval_count", 0) else "P2" if attention else "P3",
        "privacy_mode": False,
        "offline": core.get("health") == "OFFLINE",
        "stale": False,
        "takeover": _display_takeover(attention),
        "ambient": {
            "core_health": core.get("health", "ONLINE"),
            "activity_level": core.get("activity_level", 1),
            "background": _display_background(core, phase),
        },
    }


def _presentations(runtime: Any) -> dict[str, Any]:
    manager = getattr(runtime, "presentation_manager", None)
    items: list[dict[str, Any]] = []
    if manager is not None and hasattr(manager, "list_active"):
        items = [_presentation_projection(item) for item in manager.list_active(limit=30)]
    takeover = [item for item in items if str(item.get("priority", "")).lower() in {"critical", "urgent"}][:1]
    overlays = [item for item in items if str(item.get("priority", "")).lower() in {"high", "important"}][:5]
    persistent = [item for item in items if _number(item.get("ttl_seconds", 0), 0) <= 0][:8]
    ambient = [item for item in items if item not in takeover and item not in overlays and item not in persistent][:12]
    return {
        "takeover": takeover,
        "overlays": overlays,
        "persistent": persistent,
        "ambient": ambient,
        "items": items,
        "count": len(items),
    }


def _presentation_events(runtime: Any) -> dict[str, Any]:
    presentation_items = _presentations(runtime).get("items", [])
    events = _recent_ui_events(runtime, limit=50)
    projected = [presentation_event_from_presentation(item) for item in presentation_items]
    projected.extend(presentation_event_from_ui_event(event) for event in events[:30])
    return {
        "items": _dedupe_presentation_events(projected)[:40],
        "count": len(projected),
        "source": "presentation_surface_contract",
    }


def _surface_roles() -> dict[str, Any]:
    roles = [_compact_surface_role(role) for role in surface_roles()]
    return {
        "items": roles,
        "count": len(roles),
        "source": "presentation_surface_contract",
    }


def _compact_surface_role(role: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface_id": role.get("surface_id", ""),
        "role": _truncate_text(role.get("role", ""), limit=120),
        "interactive": bool(role.get("interactive", False)),
        "privacy_levels": role.get("privacy_levels", [])[:4] if isinstance(role.get("privacy_levels"), list) else [],
        "priorities": role.get("priorities", [])[:4] if isinstance(role.get("priorities"), list) else [],
        "max_text_chars": role.get("max_text_chars", 0),
        "max_display_ms": role.get("max_display_ms", 0),
        "actions": role.get("actions", [])[:5] if isinstance(role.get("actions"), list) else [],
        "scenes": role.get("scenes", [])[:8] if isinstance(role.get("scenes"), list) else [],
    }


def _display_queue(runtime: Any) -> dict[str, Any]:
    events = _recent_ui_events(runtime, limit=160)
    active: dict[str, dict[str, Any]] = {}
    for event in reversed(events):
        _resolve_display_items(active, event)
        if event.get("persistence") == "ephemeral":
            continue
        key = str(event.get("dedupe_key") or event.get("event_id") or "")
        if not key:
            continue
        active[key] = _display_queue_item(event)
    items = sorted(active.values(), key=lambda item: (_priority_rank(item.get("priority", "P3")), -int(item.get("created_at", 0) or 0)))
    return {
        "items": items[:30],
        "count": len(items),
        "source": "event_manager",
        "persisted": True,
    }


def _activity(runtime: Any) -> dict[str, Any]:
    events = _recent_ui_events(runtime, limit=120)
    groups: dict[str, dict[str, Any]] = {}
    for event in events:
        group_id = _activity_group_id(event)
        group = groups.setdefault(
            group_id,
            {
                "group_id": group_id,
                "title": _activity_group_title(event),
                "severity": event.get("severity", "info"),
                "status": event.get("status", ""),
                "server_id": event.get("server_id", ""),
                "capability_id": event.get("capability_id", ""),
                "task_id": event.get("task_id", ""),
                "approval_id": event.get("approval_id", ""),
                "operation_type": _activity_operation_type(event),
                "actor": event.get("payload", {}).get("actor", "aegis") if isinstance(event.get("payload", {}), dict) else "aegis",
                "source_manager": _activity_source_manager(event),
                "started_at": event.get("occurred_at", 0),
                "updated_at": event.get("occurred_at", 0),
                "events": [],
            },
        )
        group["updated_at"] = max(int(group.get("updated_at", 0) or 0), int(event.get("occurred_at", 0) or 0))
        group["severity"] = _max_severity(str(group.get("severity", "info")), str(event.get("severity", "info")))
        group["status"] = event.get("status") or group.get("status", "")
        if len(group["events"]) < 8:
            group["events"].append(_activity_group_event_projection(event))
    ordered_groups = sorted(groups.values(), key=lambda item: int(item.get("updated_at", 0) or 0), reverse=True)
    return {
        "recent": [_activity_event_projection(event) for event in events[:40]],
        "groups": ordered_groups[:24],
        "count": len(events),
        "source": "event_manager",
    }


def _tasks(runtime: Any) -> dict[str, Any]:
    primary = _current_task(runtime)
    manager = getattr(runtime, "task_manager", None)
    active = _running_tasks(runtime)
    waiting = _waiting_tasks(runtime)
    scheduled: list[dict[str, Any]] = []
    recent: list[dict[str, Any]] = []
    if manager is not None and hasattr(manager, "list_tasks"):
        scheduled = [_to_plain(item) for item in manager.list_tasks(status="created", limit=20)]
        recent = [_to_plain(item) for item in manager.list_tasks(limit=50)]
    return {
        "primary": primary,
        "active": [_task_projection(item) for item in active],
        "waiting": [_task_projection(item) for item in waiting],
        "scheduled": [_task_projection(item) for item in scheduled],
        "recent": [_task_projection(item) for item in recent],
    }


def _servers(runtime: Any) -> dict[str, Any]:
    return {"items": _server_list(runtime)}


def _capabilities(runtime: Any) -> dict[str, Any]:
    catalog = getattr(runtime, "capability_catalog", None)
    items: list[dict[str, Any]] = []
    if catalog is not None and hasattr(catalog, "list_for_llm"):
        items = [_capability_projection(item) for item in catalog.list_for_llm()]
    by_server: dict[str, int] = {}
    approval_required = 0
    high_risk = 0
    for item in items:
        server_id = _server_from_capability_id(str(item.get("id", "")))
        by_server[server_id] = by_server.get(server_id, 0) + 1
        risk = str(item.get("risk", "")).lower()
        if item.get("requires_approval") or risk in {"high", "critical"}:
            approval_required += 1
        if risk in {"high", "critical"}:
            high_risk += 1
    return {
        "items": items[:120],
        "count": len(items),
        "by_server": by_server,
        "approval_required_count": approval_required,
        "high_risk_count": high_risk,
    }


def _user_state(runtime: Any) -> dict[str, Any]:
    manager = getattr(runtime, "user_state_manager", None)
    if manager is None:
        return {"available": False, "summary": "User state manager is not configured."}
    if hasattr(manager, "get_summary"):
        return manager.get_summary()
    if hasattr(manager, "get_current_state"):
        return manager.get_current_state()
    return {"available": True, "summary": "User state manager is online."}


def _mind_summary(runtime: Any) -> dict[str, Any]:
    desires = {}
    loop = getattr(runtime, "autonomous_loop", None)
    if loop is not None and hasattr(loop, "get_status"):
        desires = loop.get_status()
    memory_stats = {}
    manager = getattr(runtime, "memory_manager", None)
    if manager is not None and hasattr(manager, "get_stats"):
        memory_stats = manager.get_stats()
    return {"autonomy": desires, "memory": memory_stats}


def _memory(runtime: Any) -> dict[str, Any]:
    manager = getattr(runtime, "memory_manager", None)
    stats = {}
    if manager is not None and hasattr(manager, "get_stats"):
        stats = manager.get_stats()
    return {
        "summary": stats,
        "episodic": _get(stats, "episodic", {}),
        "semantic": _get(stats, "semantic", {}),
        "procedural": _get(stats, "procedural", {}),
        "last_consolidation": _get(stats, "last_consolidation", "") or _get(stats, "last_sleep_at", ""),
    }


def _notifications(runtime: Any) -> dict[str, Any]:
    recent = _recent_notifications(runtime, unread_only=False, limit=20)
    unread = _recent_notifications(runtime, unread_only=True, limit=20)
    return {"recent": recent, "unread_count": len(unread)}


def _approvals(runtime: Any) -> dict[str, Any]:
    items = [_approval_projection(item) for item in _pending_approvals(runtime)]
    return {"pending": items, "pending_count": len(items)}


def _commitments(runtime: Any) -> dict[str, Any]:
    manager = getattr(runtime, "commitment_manager", None) or getattr(runtime, "commitments_manager", None)
    if manager is None:
        return {"items": [], "summary": "Commitment manager is not configured."}
    if hasattr(manager, "list_due"):
        return {"items": manager.list_due(limit=20)}
    if hasattr(manager, "list_active"):
        return {"items": manager.list_active(limit=20)}
    return {"items": []}


def _usage(runtime: Any) -> dict[str, Any]:
    tracker = getattr(runtime, "cost_tracker", None)
    if tracker is not None and hasattr(tracker, "get_summary"):
        return _usage_projection(tracker.get_summary())
    if tracker is not None and hasattr(tracker, "summary"):
        return _usage_projection(tracker.summary())
    return _usage_projection({"summary": "LLM usage is available from the LLM Usage service.", "input_tokens": 0, "output_tokens": 0})


def _errors(runtime: Any) -> dict[str, Any]:
    audit = getattr(runtime, "audit_manager", None) or getattr(runtime, "audit_log", None)
    entries: list[dict[str, Any]] = []
    if audit is not None and hasattr(audit, "list_errors"):
        result = _call_with_limit(audit.list_errors, 20)
        entries = result.get("entries", result if isinstance(result, list) else [])
    elif audit is not None and hasattr(audit, "list_recent"):
        result = _call_with_limit(audit.list_recent, 80)
        raw_entries = result.get("entries", result if isinstance(result, list) else [])
        entries = [
            entry
            for entry in raw_entries
            if str(entry.get("action", "")).endswith("_failed") or _get(entry.get("detail", {}), "error", "")
        ][:20]
    return {
        "items": [_error_projection(item) for item in entries],
        "count": len(entries),
    }


def _freshness(runtime: Any) -> dict[str, Any]:
    now = _now_ms()
    snapshot = _status_snapshot(runtime)
    oldest = now
    for item in snapshot.values():
        checked = int(item.get("last_checked", 0) or item.get("updated_at", 0) or now)
        oldest = min(oldest, checked)
    return {"live": True, "oldest_source_updated_at": oldest, "age_ms": max(0, now - oldest)}


def _server_list(runtime: Any) -> list[dict[str, Any]]:
    from aegis_ai.web.dashboard_legacy import _runtime_server_status

    result = _runtime_server_status(runtime=runtime)
    servers = list(result.get("servers", []))

    android_mgr = getattr(runtime, "android_manager", None)
    if android_mgr is not None:
        try:
            android_status = android_mgr.get_status()
        except Exception:
            android_status = {}
        android_online = bool(android_status.get("online"))
        found = False
        for item in servers:
            if item.get("server_id") == "android-server":
                item["status"] = "ONLINE" if android_online else "OFFLINE"
                item["mode"] = android_status.get("connection_mode", "offline")
                item["status_detail"] = "Android device is connected." if android_online else "Android device is not connected."
                item["dependencies"] = {
                    "last_seen": android_status.get("last_seen", 0),
                    "device_model": android_status.get("device_model", ""),
                    "permission_status": android_status.get("permission_status", {}),
                    "capability_availability": android_status.get("capability_availability", {}),
                }
                found = True
                break
        if not found:
            servers.append({
                "server_id": "android-server",
                "status": "ONLINE" if android_online else "OFFLINE",
                "mode": android_status.get("connection_mode", "offline"),
                "status_detail": "Android device is connected." if android_online else "Android device is not connected.",
                "dependencies": {
                    "last_seen": android_status.get("last_seen", 0),
                    "device_model": android_status.get("device_model", ""),
                },
                "health_checked_at": _now_ms(),
            })

    return [_server_projection(item) for item in servers]


def _server_needs_attention(server: dict[str, Any]) -> bool:
    status = str(server.get("status", "")).upper()
    detail = " ".join(
        str(server.get(key, "") or "") for key in ("status_detail", "degraded_reason", "recovery_hint")
    ).lower()
    return status in {"OFFLINE", "DEGRADED", "CRITICAL", "UNCONFIGURED", "DISABLED", "RECOVERING"} or any(
        token in detail for token in ("permission", "missing", "recover")
    )


def _status_snapshot(runtime: Any) -> dict[str, dict[str, Any]]:
    manager = getattr(runtime, "status_manager", None)
    if manager is not None and hasattr(manager, "get_snapshot"):
        return manager.get_snapshot() or {}
    return {}


def _running_tasks(runtime: Any) -> list[dict[str, Any]]:
    manager = getattr(runtime, "task_manager", None)
    if manager is None:
        return []
    if hasattr(manager, "list_running"):
        return [_to_plain(item) for item in manager.list_running()]
    if hasattr(manager, "list_tasks"):
        return [_to_plain(item) for item in manager.list_tasks(status="running", limit=10)]
    return []


def _waiting_tasks(runtime: Any) -> list[dict[str, Any]]:
    manager = getattr(runtime, "task_manager", None)
    if manager is None:
        return []
    if hasattr(manager, "list_waiting_approval"):
        return [_to_plain(item) for item in manager.list_waiting_approval()]
    if hasattr(manager, "list_tasks"):
        return [_to_plain(item) for item in manager.list_tasks(status="needs_approval", limit=10)]
    return []


def _pending_approvals(runtime: Any) -> list[Any]:
    manager = getattr(runtime, "approval_manager", None)
    if manager is not None and hasattr(manager, "list_pending"):
        return list(manager.list_pending())
    return []


def _recent_notifications(runtime: Any, *, unread_only: bool, limit: int) -> list[dict[str, Any]]:
    manager = getattr(runtime, "notification_manager", None)
    if manager is None:
        return []
    method = "list_unread" if unread_only and hasattr(manager, "list_unread") else "list_recent"
    if hasattr(manager, method):
        return [_to_plain(item) for item in getattr(manager, method)(limit=limit)]
    return []


def _recent_ui_events(runtime: Any, *, limit: int) -> list[dict[str, Any]]:
    manager = getattr(runtime, "event_manager", None)
    if manager is None or not hasattr(manager, "list_recent"):
        return []
    try:
        result = manager.list_recent(limit=limit)
    except TypeError:
        result = manager.list_recent(limit)
    except Exception:
        return []
    raw_items = result.get("events", []) if isinstance(result, dict) else result
    items: list[dict[str, Any]] = []
    for raw in raw_items or []:
        try:
            items.append(normalize_ui_event(raw))
        except Exception:
            continue
    return sorted(items, key=lambda item: int(item.get("occurred_at", 0) or 0), reverse=True)


def _display_queue_item(event: dict[str, Any]) -> dict[str, Any]:
    presentation_event = event.get("presentation_event")
    if not isinstance(presentation_event, dict):
        presentation_event = presentation_event_from_ui_event(event)
    return {
        "id": event.get("dedupe_key") or event.get("event_id", ""),
        "event_id": event.get("event_id", ""),
        "priority": event.get("priority", "P3"),
        "severity": event.get("severity", "info"),
        "title": event.get("safe_title") or event.get("type", "AEGIS event"),
        "message": event.get("safe_message") or event.get("message", ""),
        "persistence": event.get("persistence", "ephemeral"),
        "created_at": event.get("occurred_at", 0),
        "updated_at": event.get("received_at", 0),
        "expires_at": event.get("expires_at", 0),
        "resolved_by": event.get("resolved_by", ""),
        "affected_servers": event.get("affected_servers", []),
        "affected_capabilities": event.get("affected_capabilities", []),
        "approval_id": event.get("approval_id", ""),
        "task_id": event.get("task_id", ""),
        "visual_hint": event.get("visual_hint", {}),
        "presentation_event": _compact_presentation_event(presentation_event),
        "scene_type": presentation_event.get("scene_type", ""),
        "privacy_class": presentation_event.get("privacy_class", ""),
        "recommended_surfaces": presentation_event.get("recommended_surfaces", []),
        "available_actions": presentation_event.get("available_actions", []),
    }


def _resolve_display_items(active: dict[str, dict[str, Any]], event: dict[str, Any]) -> None:
    event_type = str(event.get("type") or event.get("event_type") or "")
    status = str(event.get("status") or "").lower()
    approval_id = str(event.get("approval_id") or "")
    server_id = str(event.get("server_id") or "")
    capability_id = str(event.get("capability_id") or "")
    resolved_keys: list[str] = []
    for key, item in active.items():
        item_approval = str(item.get("approval_id") or "")
        item_servers = {str(value) for value in item.get("affected_servers", [])}
        item_caps = {str(value) for value in item.get("affected_capabilities", [])}
        if event_type == "approval.resolved" and approval_id and item_approval == approval_id:
            resolved_keys.append(key)
        elif status in {"online", "connected", "recovered", "completed"} and server_id and server_id in item_servers:
            resolved_keys.append(key)
        elif status in {"completed", "approved", "resolved"} and capability_id and capability_id in item_caps:
            resolved_keys.append(key)
    for key in resolved_keys:
        active.pop(key, None)


def _dedupe_presentation_events(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for item in items:
        key = str(item.get("event_id") or item.get("approval_id") or item.get("task_id") or item.get("title") or "")
        if not key:
            continue
        current = seen.get(key)
        if current is None or _priority_rank(item.get("priority", "P3")) < _priority_rank(current.get("priority", "P3")):
            seen[key] = item
    return sorted(seen.values(), key=lambda item: (_priority_rank(item.get("priority", "P3")), -int(item.get("expires_at", 0) or 0)))


def _compact_presentation_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("event_id", ""),
        "scene_type": event.get("scene_type", ""),
        "priority": event.get("priority", "P3"),
        "severity": event.get("severity", "info"),
        "source": event.get("source", ""),
        "title": _truncate_text(event.get("title", ""), limit=120),
        "summary": _truncate_text(event.get("summary", ""), limit=180),
        "affected_entities": event.get("affected_entities", [])[:6] if isinstance(event.get("affected_entities"), list) else [],
        "task_id": event.get("task_id", ""),
        "approval_id": event.get("approval_id", ""),
        "privacy_class": event.get("privacy_class", "normal"),
        "recommended_surfaces": event.get("recommended_surfaces", [])[:5] if isinstance(event.get("recommended_surfaces"), list) else [],
        "visual_hint": event.get("visual_hint", {}),
    }


def _activity_event_projection(event: dict[str, Any]) -> dict[str, Any]:
    presentation_event = event.get("presentation_event")
    if not isinstance(presentation_event, dict):
        presentation_event = presentation_event_from_ui_event(event)
    return {
        "event_id": event.get("event_id", ""),
        "type": event.get("type", ""),
        "event_type": event.get("event_type", ""),
        "occurred_at": event.get("occurred_at", 0),
        "priority": event.get("priority", "P3"),
        "severity": event.get("severity", "info"),
        "status": event.get("status", ""),
        "server_id": event.get("server_id", ""),
        "capability_id": event.get("capability_id", ""),
        "task_id": event.get("task_id", ""),
        "approval_id": event.get("approval_id", ""),
        "operation_type": _activity_operation_type(event),
        "actor": event.get("payload", {}).get("actor", "aegis") if isinstance(event.get("payload", {}), dict) else "aegis",
        "source_manager": _activity_source_manager(event),
        "related": {
            "task_id": event.get("task_id", ""),
            "approval_id": event.get("approval_id", ""),
            "capability_id": event.get("capability_id", ""),
            "server_id": event.get("server_id", ""),
        },
        "title": event.get("safe_title", ""),
        "message": event.get("safe_message") or event.get("message", ""),
        "presentation_event": _compact_presentation_event(presentation_event),
        "scene_type": presentation_event.get("scene_type", ""),
        "privacy_class": presentation_event.get("privacy_class", ""),
        "recommended_surfaces": presentation_event.get("recommended_surfaces", []),
        "available_actions": presentation_event.get("available_actions", []),
    }


def _activity_group_event_projection(event: dict[str, Any]) -> dict[str, Any]:
    presentation_event = event.get("presentation_event")
    if not isinstance(presentation_event, dict):
        presentation_event = presentation_event_from_ui_event(event)
    return {
        "event_id": event.get("event_id", ""),
        "type": event.get("type", ""),
        "occurred_at": event.get("occurred_at", 0),
        "priority": event.get("priority", "P3"),
        "severity": event.get("severity", "info"),
        "status": event.get("status", ""),
        "title": event.get("safe_title", ""),
        "message": _truncate_text(event.get("safe_message") or event.get("message", ""), limit=160),
        "scene_type": presentation_event.get("scene_type", ""),
        "source": presentation_event.get("source", ""),
    }


def _activity_group_id(event: dict[str, Any]) -> str:
    for key in ("task_id", "approval_id", "capability_id", "server_id"):
        value = str(event.get(key) or "")
        if value:
            return f"{key}:{value}"
    return str(event.get("dedupe_key") or event.get("event_id") or event.get("type") or "activity")


def _activity_group_title(event: dict[str, Any]) -> str:
    if event.get("task_id"):
        return f"Task {event.get('task_id')}"
    if event.get("approval_id"):
        return "Approval lifecycle"
    if event.get("capability_id"):
        return str(event.get("capability_id"))
    if event.get("server_id"):
        return f"{event.get('server_id')} activity"
    return str(event.get("safe_title") or event.get("type") or "Activity")


def _max_severity(left: str, right: str) -> str:
    order = {"critical": 0, "warning": 1, "info": 2, "normal": 3}
    return left if order.get(left, 4) <= order.get(right, 4) else right


def _call_with_limit(method: Any, limit: int) -> Any:
    try:
        return method(limit=limit)
    except TypeError:
        return method(limit)


def _server_projection(server: Any) -> dict[str, Any]:
    data = _to_plain(server)
    dependencies = data.get("dependencies", {}) if isinstance(data.get("dependencies", {}), dict) else {}
    status = str(data.get("status", "")).upper()
    permission_missing = bool(data.get("permission_missing") or dependencies.get("permission_missing"))
    capability_health = data.get("capability_health") or dependencies.get("capability_health") or dependencies.get("capability_availability", {})
    return {
        **data,
        "status": status,
        "latency_ms": _number(data.get("latency_ms", dependencies.get("latency_ms", -1)), -1),
        "last_healthy_at": data.get("last_healthy_at") or dependencies.get("last_healthy_at") or dependencies.get("last_seen") or data.get("health_checked_at", 0),
        "active_task_id": data.get("active_task_id", dependencies.get("active_task_id", "")),
        "permission_missing": permission_missing,
        "capability_health": _bound_for_ui(capability_health, max_depth=3, max_dict_items=40),
        "recovery_state": "attention" if status in {"OFFLINE", "DEGRADED", "CRITICAL"} or permission_missing else "stable",
    }


def _approval_projection(approval: Any) -> dict[str, Any]:
    data = approval.to_dict() if hasattr(approval, "to_dict") else _to_plain(approval)
    metadata = data.get("metadata", {}) if isinstance(data.get("metadata", {}), dict) else {}
    arguments_summary = data.get("arguments_summary", "")
    return {
        "approval_id": data.get("approval_id", ""),
        "request_id": data.get("request_id", ""),
        "task_id": data.get("task_id", ""),
        "step_id": data.get("step_id", ""),
        "capability_id": data.get("capability_id", ""),
        "tool_name": data.get("tool_name", ""),
        "risk": data.get("risk_level", ""),
        "reason": data.get("approval_reason", ""),
        "summary": data.get("user_facing_summary", "") or arguments_summary,
        "target": metadata.get("target", ""),
        "preview": arguments_summary,
        "side_effects": metadata.get("side_effects", data.get("side_effects", "")),
        "previous_action": metadata.get("previous_action", ""),
        "similar_action_summary": metadata.get("similar_action_summary", ""),
        "expected_effect": metadata.get("expected_effect", ""),
        "fresh_auth_required": bool(metadata.get("fresh_auth_required", data.get("fresh_auth_required", False))),
        "created_at": data.get("created_at", 0),
        "expires_at": data.get("expires_at", 0),
        "status": data.get("status", "pending"),
    }


def _task_original_instruction(task: Any) -> str:
    for key in ("original_instruction", "user_message", "instruction", "prompt", "goal", "title"):
        value = _get(task, key, "")
        if value:
            return _truncate_text(value, limit=500)
    return ""


def _task_plan_summary(task: Any, steps: list[Any]) -> str:
    for key in ("plan_summary", "plan", "strategy", "description"):
        value = _get(task, key, "")
        if isinstance(value, str) and value:
            return _truncate_text(value, limit=700)
        if isinstance(value, list) and value:
            return _truncate_text("; ".join(str(item) for item in value[:6]), limit=700)
    if steps:
        labels = [_get(step, "description", "") or _get(step, "capability_id", "") or _get(step, "name", "") for step in steps[:6]]
        return _truncate_text(" -> ".join(str(label) for label in labels if label), limit=700)
    return ""


def _task_dependency_edges(steps: list[Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    previous = ""
    for index, step in enumerate(steps[:16]):
        step_id = str(_get(step, "step_id", "") or _get(step, "id", "") or f"step-{index + 1}")
        depends_on = _get(step, "depends_on", None)
        if isinstance(depends_on, list):
            for dep in depends_on[:6]:
                edges.append({"from": str(dep), "to": step_id, "type": "depends_on"})
        elif depends_on:
            edges.append({"from": str(depends_on), "to": step_id, "type": "depends_on"})
        elif previous:
            edges.append({"from": previous, "to": step_id, "type": "sequence"})
        previous = step_id
    return edges


def _verification_summary(steps: list[Any]) -> str:
    for step in reversed(steps):
        verification = _get(step, "verification", None) or _get(step, "verification_result", None) or _get(step, "completion", None)
        if verification:
            if isinstance(verification, str):
                return _truncate_text(verification, limit=360)
            status = _get(verification, "status", "") or _get(verification, "summary", "") or _get(verification, "message", "")
            return _truncate_text(status or _json_preview(_to_plain(verification)), limit=360)
    return ""


def _final_output_summary(task: Any, steps: list[Any]) -> str:
    for key in ("final_output", "result", "summary", "output"):
        value = _get(task, key, "")
        if value:
            return _truncate_text(value if isinstance(value, str) else _json_preview(_to_plain(value)), limit=700)
    for step in reversed(steps):
        result = _get(step, "result", None)
        if result:
            summary = _summarize_step_result(result)
            if summary.get("message") or summary.get("status"):
                return _truncate_text(summary.get("message") or summary.get("status") or "", limit=360)
            keys = ", ".join(str(key) for key in summary.get("keys", [])[:6]) if isinstance(summary.get("keys"), list) else ""
            size = summary.get("size_chars")
            return _truncate_text(f"Step result available ({size} chars){f'; keys: {keys}' if keys else ''}", limit=360)
    return ""


def _cost_summary(value: Any) -> str:
    candidates = _get(value, "cost_summary", "") or _get(value, "usage_summary", "")
    if candidates:
        return _truncate_text(candidates, limit=240)
    usage = _get(value, "usage", {}) or _get(value, "llm_usage", {})
    if isinstance(usage, dict) and usage:
        tokens = usage.get("total_tokens") or usage.get("tokens")
        cost = usage.get("cost") or usage.get("provider_reported_cost")
        parts = []
        if tokens not in (None, ""):
            parts.append(f"{tokens} tokens")
        if cost not in (None, ""):
            parts.append(f"{cost} cost")
        return ", ".join(parts)
    return ""


def _task_projection(task: Any) -> dict[str, Any]:
    data = _to_plain(task)
    steps = _get(data, "steps", []) or []
    return {
        "task_id": _get(data, "task_id", ""),
        "title": _get(data, "title", "") or _get(data, "goal", "") or "Task",
        "status": _get(data, "status", ""),
        "source": _get(data, "source", ""),
        "created_at": _get(data, "created_at", 0),
        "updated_at": _get(data, "updated_at", 0),
        "completed_at": _get(data, "completed_at", 0),
        "blocked_reason": _truncate_text(_get(data, "blocked_reason", "")),
        "original_instruction": _task_original_instruction(data),
        "plan_summary": _task_plan_summary(data, steps),
        "dependency_edges": _task_dependency_edges(steps),
        "verification_summary": _verification_summary(steps),
        "final_output": _final_output_summary(data, steps),
        "audit_group_id": _get(data, "audit_group_id", "") or _get(data, "request_id", ""),
        "cost_summary": _cost_summary(data),
        "step_count": len(steps),
        "steps": [_task_step_projection(step) for step in steps[:12]],
    }


def _usage_projection(summary: Any) -> dict[str, Any]:
    data = _to_plain(summary)
    if not isinstance(data, dict):
        data = {"summary": str(data)}
    input_tokens = _number(data.get("input_tokens", data.get("prompt_tokens", 0)), 0)
    output_tokens = _number(data.get("output_tokens", data.get("completion_tokens", 0)), 0)
    total_tokens = _number(data.get("total_tokens", input_tokens + output_tokens), input_tokens + output_tokens)
    cost = data.get("provider_reported_cost", data.get("cost", data.get("estimated_cost", "")))
    budget_state = data.get("budget_state") or data.get("status") or ("active" if total_tokens else "not_reported")
    summary_text = data.get("summary") or (
        f"{int(total_tokens)} tokens" if total_tokens else "LLM usage is not reported yet."
    )
    return {
        **data,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "provider_reported_cost": data.get("provider_reported_cost", ""),
        "estimated_cost": data.get("estimated_cost", cost),
        "cost": cost,
        "budget_state": budget_state,
        "autonomous_suppression": data.get("autonomous_suppression", data.get("suppression_reason", "")),
        "summary": summary_text,
    }


def _activity_operation_type(event: dict[str, Any]) -> str:
    event_type = str(event.get("event_type") or event.get("type") or "").lower()
    if event.get("approval_id") or "approval" in event_type:
        return "approval"
    if event.get("capability_id") or "tool.execution" in event_type or "capability" in event_type:
        return "capability"
    if "setting" in event_type:
        return "settings"
    if "llm" in event_type or "usage" in event_type:
        return "llm"
    if "security" in event_type or "auth" in event_type:
        return "security"
    if event.get("server_id") or "status" in event_type or "connection" in event_type:
        return "system"
    if "error" in event_type or str(event.get("severity", "")).lower() == "critical":
        return "error"
    return "event"


def _activity_source_manager(event: dict[str, Any]) -> str:
    event_type = str(event.get("event_type") or event.get("type") or "")
    if event.get("approval_id") or event_type.startswith("approval."):
        return "ApprovalManager"
    if event.get("task_id") or event_type.startswith("task."):
        return "TaskManager"
    if event.get("server_id") or event_type.startswith(("status.", "connection.")):
        return "StatusManager"
    if event_type.startswith("notification."):
        return "NotificationManager"
    if event_type.startswith(("llm.", "usage.")):
        return "LLMUsage"
    return "EventManager"


def _task_step_projection(step: Any) -> dict[str, Any]:
    result = _get(step, "result", None)
    error = _get(step, "error", "")
    return {
        "step_id": _get(step, "step_id", ""),
        "name": _get(step, "name", ""),
        "description": _truncate_text(_get(step, "description", "")),
        "capability_id": _get(step, "capability_id", ""),
        "status": _get(step, "status", ""),
        "approval_id": _get(step, "approval_id", ""),
        "created_at": _get(step, "created_at", 0),
        "updated_at": _get(step, "updated_at", 0),
        "error": _truncate_text(error),
        "result": _summarize_step_result(result),
        "verification": _bound_for_ui(_get(step, "verification", None) or _get(step, "verification_result", None) or _get(step, "completion", None), max_depth=3),
        "completion_condition": _bound_for_ui(_get(step, "completion_condition", None) or _get(step, "postcondition", None), max_depth=3),
        "cost_summary": _cost_summary(step),
    }


def _summarize_step_result(result: Any) -> dict[str, Any]:
    if result is None:
        return {"available": False, "type": "none", "preview": "", "truncated": False}
    plain = _to_plain(result)
    rendered = _json_preview(plain)
    summary: dict[str, Any] = {
        "available": True,
        "type": type(plain).__name__,
        "size_chars": len(rendered),
        "preview": _truncate_text(rendered, limit=_MAX_STEP_RESULT_PREVIEW_CHARS),
        "truncated": len(rendered) > _MAX_STEP_RESULT_PREVIEW_CHARS,
    }
    if isinstance(plain, dict):
        summary["keys"] = list(plain.keys())[:12]
        for key in ("success", "status", "status_code", "message", "error"):
            if key in plain:
                summary[key] = _bound_for_ui(plain[key], max_depth=2)
    elif isinstance(plain, list):
        summary["item_count"] = len(plain)
    return summary


def _capability_projection(capability: Any) -> dict[str, Any]:
    data = _to_plain(capability)
    capability_id = str(data.get("id", ""))
    return {
        "id": capability_id,
        "short_name": data.get("short_name", capability_id),
        "description": _truncate_text(data.get("description", ""), limit=240),
        "server_id": _server_from_capability_id(capability_id),
        "risk": data.get("risk", ""),
        "requires_approval": bool(data.get("requires_approval") or data.get("only_master")),
        "enabled": not bool(data.get("disabled", False)),
        "params": _bound_for_ui(data.get("params", []), max_depth=3, max_list_items=12),
    }


def _presentation_projection(presentation: Any) -> dict[str, Any]:
    data = presentation.to_dict() if hasattr(presentation, "to_dict") else _to_plain(presentation)
    return {
        "presentation_id": data.get("presentation_id", ""),
        "title": data.get("title", "") or data.get("summary", "") or "Presentation",
        "summary": _truncate_text(data.get("summary", "") or data.get("content", ""), limit=360),
        "status": data.get("status", ""),
        "priority": data.get("priority", "") or data.get("urgency", ""),
        "modality": data.get("modality", ""),
        "target_surface": data.get("target_surface", "") or data.get("target", ""),
        "created_at": data.get("created_at", 0),
        "updated_at": data.get("updated_at", 0),
        "ttl_seconds": _number(data.get("ttl_seconds", 0), 0),
    }


def _error_projection(entry: Any) -> dict[str, Any]:
    data = _to_plain(entry)
    detail = data.get("detail", {}) if isinstance(data.get("detail", {}), dict) else {}
    return {
        "id": data.get("id", "") or data.get("entry_id", ""),
        "action": data.get("action", ""),
        "source": data.get("source", ""),
        "message": _truncate_text(detail.get("error", "") or data.get("error", "") or data.get("message", ""), limit=320),
        "timestamp_ms": data.get("timestamp_ms", 0) or data.get("created_at", 0),
        "severity": "critical" if str(data.get("action", "")).endswith("_failed") else "warning",
    }


def _display_takeover(attention: list[dict[str, Any]]) -> dict[str, Any]:
    if not attention:
        return {"active": False}
    first = attention[0]
    severity = str(first.get("severity", "info")).lower()
    if severity == "critical":
        priority = "P0"
    elif first.get("kind") == "approval":
        priority = "P1"
    else:
        priority = "P2"
    return {
        "active": priority in {"P0", "P1"},
        "priority": priority,
        "title": first.get("title", ""),
        "message": first.get("message", ""),
        "severity": severity,
        "source_id": first.get("id", ""),
        "expires_at": first.get("expires_at", 0),
    }


def _display_background(core: dict[str, Any], phase: str) -> str:
    health = str(core.get("health", "")).upper()
    if health == "OFFLINE":
        return "offline"
    if health == "DEGRADED":
        return "critical-edge"
    return phase.lower().replace(" ", "-") or "idle"


def _mission_phase(core: dict[str, Any], task: dict[str, Any], pending_approvals: int) -> str:
    if pending_approvals > 0:
        return "Waiting for Approval"
    health = str(core.get("health", "")).upper()
    if health == "OFFLINE":
        return "Offline"
    if health == "DEGRADED":
        return "Stabilizing"
    if task.get("task_id") or str(core.get("mode", "")).upper() == "EXECUTING":
        return "Executing"
    return "Idle"


def _ui_event_type(event_type: str) -> str:
    mapping = {
        "status.changed": "status.changed",
        "task.created": "task.updated",
        "task.updated": "task.updated",
        "task.completed": "task.updated",
        "task.failed": "task.updated",
        "tool.execution.started": "tool.execution.started",
        "tool.execution.completed": "tool.execution.completed",
        "tool.execution.failed": "tool.execution.failed",
        "capability.execution.started": "tool.execution.started",
        "capability.execution.completed": "tool.execution.completed",
        "capability.execution.failed": "tool.execution.failed",
        "approval.created": "approval.created",
        "approval.approved": "approval.resolved",
        "approval.rejected": "approval.resolved",
        "approval.expired": "approval.resolved",
        "approval.executed": "approval.resolved",
        "approval.failed": "approval.resolved",
        "notification.sent": "notification.created",
        "android.permission.changed": "permission.changed",
        "android.connected": "connection.changed",
        "android.disconnected": "connection.changed",
    }
    return mapping.get(event_type, "activity.updated")


def _event_fields(event_type: str, payload: Any) -> dict[str, Any]:
    payload_dict = payload if isinstance(payload, dict) else {}
    nested = payload_dict.get("payload") if isinstance(payload_dict.get("payload"), dict) else {}
    detail = payload_dict.get("detail") if isinstance(payload_dict.get("detail"), dict) else {}
    candidates = [payload_dict, nested, detail]

    def first(*keys: str) -> Any:
        for source in candidates:
            for key in keys:
                value = source.get(key)
                if value not in (None, ""):
                    return value
        return ""

    capability_id = str(first("capability_id", "tool_id", "tool_name", "capability") or "")
    server_id = str(first("server_id", "server") or _server_from_capability_id(capability_id) or _server_from_event_type(event_type))
    status = str(first("status", "state", "decision") or _status_from_event_type(event_type))
    approval_id = str(first("approval_id", "request_id") or "")
    task_id = str(first("task_id") or "")
    message = str(first("message", "summary", "reason", "error") or event_type)
    severity = str(first("severity") or _severity_from_event(event_type, status))
    return {
        "capability_id": capability_id,
        "server_id": server_id,
        "status": status,
        "approval_id": approval_id,
        "task_id": task_id,
        "severity": severity,
        "event_type": event_type,
        "message": _truncate_text(message, limit=300),
    }


def _server_from_capability_id(capability_id: str) -> str:
    prefix = capability_id.split(".", 1)[0].strip().lower()
    if prefix in {"ai-server", "pc-server", "android-server", "browser-server", "room-server", "dev-server"}:
        return prefix
    return "ai-server" if capability_id else ""


def _server_from_event_type(event_type: str) -> str:
    lowered = event_type.lower()
    if lowered.startswith("android."):
        return "android-server"
    if lowered.startswith("pc."):
        return "pc-server"
    if lowered.startswith("browser."):
        return "browser-server"
    if lowered.startswith("room."):
        return "room-server"
    return ""


def _status_from_event_type(event_type: str) -> str:
    lowered = event_type.lower()
    if lowered.endswith(".started") or "executing" in lowered:
        return "running"
    if lowered.endswith(".completed") or lowered.endswith(".executed") or lowered.endswith(".approved"):
        return "completed"
    if lowered.endswith(".failed") or lowered.endswith(".rejected"):
        return "failed"
    if lowered.endswith(".created"):
        return "created"
    if "disconnected" in lowered:
        return "offline"
    if "connected" in lowered:
        return "online"
    return ""


def _severity_from_event(event_type: str, status: str) -> str:
    lowered = f"{event_type} {status}".lower()
    if any(token in lowered for token in ("failed", "offline", "error", "critical")):
        return "critical"
    if any(token in lowered for token in ("approval", "degraded", "warning", "permission")):
        return "warning"
    return "info"


def _event_sequence(event: Any, event_type: str, timestamp: int, payload: Any) -> int:
    explicit = getattr(event, "sequence", None) or _get(event, "sequence", 0)
    if explicit:
        return int(explicit)
    raw = f"{event_type}:{timestamp}:{_json_preview(payload)[:500]}".encode("utf-8", "replace")
    return int(hashlib.sha1(raw).hexdigest()[:12], 16)


def _event_id(event: Any, event_type: str, timestamp: int, sequence: int, payload: Any) -> str:
    explicit = getattr(event, "event_id", None) or _get(event, "event_id", "")
    if explicit:
        return str(explicit)
    raw = f"{event_type}:{timestamp}:{sequence}:{_json_preview(payload)[:500]}".encode("utf-8", "replace")
    return hashlib.sha1(raw).hexdigest()[:24]


def _event_priority(fields: dict[str, Any]) -> str:
    severity = str(fields.get("severity", "")).lower()
    status = str(fields.get("status", "")).lower()
    event_type = str(fields.get("event_type", "")).lower()
    if severity == "critical" or status in {"offline", "failed", "error"}:
        return "P0"
    if str(fields.get("approval_id", "")):
        return "P1"
    if severity == "warning" and "permission" not in event_type:
        return "P1"
    if severity == "warning" or status in {"degraded", "recovering", "created", "running"}:
        return "P2"
    return "P3"


def _event_dedupe_key(event_type: str, fields: dict[str, Any]) -> str:
    parts = [
        event_type,
        str(fields.get("server_id", "")),
        str(fields.get("capability_id", "")),
        str(fields.get("approval_id", "")),
        str(fields.get("task_id", "")),
        str(fields.get("status", "")),
    ]
    return ":".join(part for part in parts if part)


def _event_persistence(fields: dict[str, Any]) -> str:
    priority = _event_priority(fields)
    if priority in {"P0", "P1"}:
        return "until_resolved"
    if priority == "P2":
        return "attention_dock"
    return "ephemeral"


def _event_expires_at(timestamp: int, fields: dict[str, Any]) -> int:
    priority = _event_priority(fields)
    if priority in {"P0", "P1"}:
        return 0
    duration_ms = 15_000 if priority == "P2" else 5_000
    return timestamp + duration_ms


def _event_resolved_by(event_type: str, fields: dict[str, Any]) -> str:
    status = str(fields.get("status", "")).lower()
    if event_type.startswith("approval.") or fields.get("approval_id"):
        return "approval.resolved"
    if status in {"offline", "degraded", "failed", "error"}:
        return "status.changed:online"
    return ""


def _event_title(event_type: str, fields: dict[str, Any]) -> str:
    server_id = str(fields.get("server_id", ""))
    capability_id = str(fields.get("capability_id", ""))
    if fields.get("approval_id"):
        return "Approval required"
    if server_id:
        return f"{server_id} {fields.get('status') or event_type}"
    if capability_id:
        return capability_id
    return event_type


def _visual_hint(event_type: str, fields: dict[str, Any]) -> dict[str, Any]:
    status = str(fields.get("status", "")).lower()
    event_lower = event_type.lower()
    if fields.get("approval_id") or "approval" in event_lower:
        effect = "containment-resolved" if status in {"approved", "rejected", "executed", "resolved"} else "containment"
    elif status in {"offline", "disconnected"}:
        effect = "disconnect"
    elif status in {"online", "connected", "recovered"}:
        effect = "recovery"
    elif status in {"failed", "error"} or event_lower.endswith(".failed"):
        effect = "fracture"
    elif event_lower.endswith(".completed") or status == "completed":
        effect = "complete"
    else:
        effect = "pulse"
    return {
        "effect": effect,
        "arc": fields.get("server_id", ""),
        "color": _visual_color(effect, fields),
        "duration_ms": 4500 if effect in {"pulse", "complete"} else 8000,
    }


def _visual_color(effect: str, fields: dict[str, Any]) -> str:
    if effect == "recovery":
        return "green"
    if effect in {"fracture", "disconnect"} or str(fields.get("severity", "")).lower() == "critical":
        return "red"
    if effect.startswith("containment"):
        return "amber"
    return "cyan"


def _priority_rank(priority: Any) -> int:
    return {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(str(priority), 4)


def _attention_sort_key(item: dict[str, Any]) -> tuple[int, int]:
    severity = {"critical": 0, "warning": 1, "info": 2, "normal": 3}.get(str(item.get("severity", "")).lower(), 3)
    created_at = int(item.get("created_at", 0) or 0)
    return (severity, -created_at)


def _infer_source_updated_at(data: Any) -> int:
    if isinstance(data, dict):
        for key in ("updated_at", "created_at", "source_updated_at", "health_checked_at", "oldest_source_updated_at"):
            value = data.get(key)
            if isinstance(value, int) and value > 0:
                return value
        values = [_infer_source_updated_at(v) for v in data.values()]
        return max(values or [0])
    if isinstance(data, list):
        values = [_infer_source_updated_at(v) for v in data]
        return max(values or [0])
    return 0


def _is_stale(source_updated_at: int, generated_at: int) -> bool:
    return bool(source_updated_at and generated_at - source_updated_at > 120_000)


def _empty_data(name: str) -> Any:
    if name in {"attention", "servers", "notifications", "approvals", "commitments"}:
        return {"items": []}
    if name in {"activity", "display_queue", "presentation_events"}:
        return {"items": [], "recent": [], "groups": [], "count": 0}
    if name == "surface_roles":
        return {"items": [], "count": 0}
    return {}


def _to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(k): _to_plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_plain(v) for v in value]
    if hasattr(value, "to_dict"):
        return _to_plain(value.to_dict())
    if hasattr(value, "value") and value.__class__.__module__ == "enum":
        return value.value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _bound_for_ui(
    value: Any,
    *,
    max_depth: int = _MAX_UI_DEPTH,
    max_string_chars: int = _MAX_UI_STRING_CHARS,
    max_list_items: int = _MAX_UI_LIST_ITEMS,
    max_dict_items: int = _MAX_UI_DICT_ITEMS,
) -> Any:
    if max_depth <= 0:
        return _truncate_text(_json_preview(value), limit=max_string_chars)
    if isinstance(value, str):
        return _truncate_text(value, limit=max_string_chars)
    if isinstance(value, dict):
        items = list(value.items())
        bounded = {
            str(key): _bound_for_ui(
                item,
                max_depth=max_depth - 1,
                max_string_chars=max_string_chars,
                max_list_items=max_list_items,
                max_dict_items=max_dict_items,
            )
            for key, item in items[:max_dict_items]
        }
        if len(items) > max_dict_items:
            bounded["_truncated_keys"] = len(items) - max_dict_items
        return bounded
    if isinstance(value, list):
        bounded_list = [
            _bound_for_ui(
                item,
                max_depth=max_depth - 1,
                max_string_chars=max_string_chars,
                max_list_items=max_list_items,
                max_dict_items=max_dict_items,
            )
            for item in value[:max_list_items]
        ]
        if len(value) > max_list_items:
            bounded_list.append({"_truncated_items": len(value) - max_list_items})
        return bounded_list
    return value


def _truncate_text(value: Any, *, limit: int = _MAX_UI_STRING_CHARS) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else str(value)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}... [truncated {len(text) - limit} chars]"


def _json_preview(value: Any) -> str:
    try:
        import json

        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def _get(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _number(value: Any, default: float = 0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _now_ms() -> int:
    return int(time.time() * 1000)
