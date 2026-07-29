"""Normalized UI overview for Web, Android, and display surfaces."""

from __future__ import annotations

import hashlib
import time
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
    # Single situation projection — avoid duplicate user_state / user_situation pages.
    situation = _section("situation", lambda: _user_state(runtime), generated_at)
    # Single mind projection — avoid duplicate mind / mind_summary.
    mind = _section("mind", lambda: _mind_summary(runtime), generated_at)
    tasks = _section("tasks", lambda: _tasks(runtime), generated_at)
    sections = {
        "core": _section("core", lambda: _core(runtime), generated_at),
        "connection": _section("connection", lambda: _connection(runtime), generated_at),
        "display_scene": _section("display_scene", lambda: _display_scene(runtime), generated_at),
        "presentations": _section("presentations", lambda: _presentations(runtime), generated_at),
        "presentation_events": _section("presentation_events", lambda: _presentation_events(runtime), generated_at),
        "surface_roles": _section("surface_roles", lambda: _surface_roles(), generated_at),
        "display_queue": _section("display_queue", lambda: _display_queue(runtime), generated_at),
        "tasks": tasks,
        # Alias: keep current_task pointing at tasks.primary without a second source.
        "current_task": {
            **tasks,
            "data": (tasks.get("data") or {}).get("primary")
            or _current_task(runtime),
        },
        "activity": _section("activity", lambda: _activity(runtime), generated_at),
        "attention": _section("attention", lambda: _attention(runtime), generated_at),
        "servers": _section("servers", lambda: _servers(runtime), generated_at),
        "capabilities": _section("capabilities", lambda: _capabilities(runtime), generated_at),
        "user_situation": situation,
        "user_state": situation,
        "situation": situation,
        "mind": mind,
        "mind_summary": mind,
        "memory": _section("memory", lambda: _memory(runtime), generated_at),
        "notifications": _section("notifications", lambda: _notifications(runtime), generated_at),
        "approvals": _section("approvals", lambda: _approvals(runtime), generated_at),
        "commitments": _section("commitments", lambda: _commitments(runtime), generated_at),
        "autonomous_logs": _section("autonomous_logs", lambda: _autonomous_logs(runtime), generated_at),
        "usage": _section("usage", lambda: _usage(runtime), generated_at),
        "errors": _section("errors", lambda: _errors(runtime), generated_at),
        "freshness": _section("freshness", lambda: _freshness(runtime), generated_at),
        # Judgment / progress surfaces (secretary dashboard)
        "agent_state": _section("agent_state", lambda: _agent_state(runtime), generated_at),
        "goals": _section("goals", lambda: _goals(runtime), generated_at),
        "initiative": _section("initiative", lambda: _initiative(runtime), generated_at),
        "continuations": _section("continuations", lambda: _continuations(runtime), generated_at),
        "repairs": _section("repairs", lambda: _repairs(runtime), generated_at),
        "social": _section("social", lambda: _social(runtime), generated_at),
        "behavioral_reports": _section("behavioral_reports", lambda: _behavioral_reports(runtime), generated_at),
        "open_loops": _section("open_loops", lambda: _open_loops(runtime), generated_at),
        "decision_context": _section("decision_context", lambda: _decision_context(runtime), generated_at),
        "generated_capabilities": _section(
            "generated_capabilities", lambda: _generated_capabilities(runtime), generated_at
        ),
        "executions": _section("executions", lambda: _executions(runtime), generated_at),
    }
    return {"schema_version": "ui-overview.v4", "generated_at": generated_at, **sections}


def build_display_power_state(runtime: Any) -> dict[str, Any]:
    """Build the compact state used by the dedicated display power watcher.

    This intentionally avoids the full Overview projection, audit/event history,
    memory, and capability catalog.  It is safe to poll frequently without
    competing with the Dashboard or Android command paths.
    """

    generated_at = _now_ms()
    task = _current_task(runtime)
    background_autonomous = (
        str(task.get("source") or "").lower() == "autonomous"
        and not task.get("capability_id")
        and not task.get("current_action")
    )
    power_task = {} if background_autonomous else task
    pending = _pending_approvals(runtime)
    servers = []
    for server_id, raw in _status_snapshot(runtime).items():
        item = _to_plain(raw)
        if not isinstance(item, dict):
            item = {"status": str(item)}
        servers.append(
            {
                "server_id": str(server_id),
                "status": str(item.get("status") or "unknown"),
                "updated_at": int(item.get("updated_at") or item.get("last_seen") or 0),
                "permission_missing": item.get("permission_missing") or [],
                "recovery_state": str(item.get("recovery_state") or ""),
            }
        )

    presentation_items: list[dict[str, Any]] = []
    manager = getattr(runtime, "presentation_manager", None)
    if manager is not None and hasattr(manager, "list_active"):
        presentation_items = [_presentation_projection(item) for item in manager.list_active(limit=3)]

    task_status = str(power_task.get("phase") or "").lower()
    keep_awake = task_status in {"running", "executing", "verifying"} or bool(pending)
    return {
        "schema_version": "display-power-state.v1",
        "generated_at": generated_at,
        "keep_awake": keep_awake,
        "current_task": {
            key: power_task.get(key)
            for key in (
                "task_id",
                "source",
                "phase",
                "capability_id",
                "current_action",
                "updated_at",
            )
        },
        "approvals": {
            "pending_count": len(pending),
            "ids": [str(_get(_to_plain(item), "approval_id", "")) for item in pending[:8]],
        },
        "servers": sorted(servers, key=lambda item: item["server_id"]),
        "presentations": [
            {key: item.get(key) for key in ("presentation_id", "id", "status", "surface_role", "updated_at")}
            for item in presentation_items
        ],
    }


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
            "source": "",
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
        "source": _get(task, "source", ""),
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
        if _is_activity_noise_event(event):
            continue
        _resolve_display_items(active, event)
        if event.get("persistence") == "ephemeral":
            continue
        key = str(event.get("dedupe_key") or event.get("event_id") or "")
        if not key:
            continue
        active[key] = _display_queue_item(event)
    items = sorted(
        active.values(),
        key=lambda item: (_priority_rank(item.get("priority", "P3")), -int(item.get("created_at", 0) or 0)),
    )
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
        if _is_activity_noise_event(event):
            continue
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
                "actor": event.get("payload", {}).get("actor", "aegis")
                if isinstance(event.get("payload", {}), dict)
                else "aegis",
                "source_manager": _activity_source_manager(event),
                "started_at": event.get("occurred_at", 0),
                "updated_at": event.get("occurred_at", 0),
                "summary": "",
                "events": [],
            },
        )
        group["updated_at"] = max(int(group.get("updated_at", 0) or 0), int(event.get("occurred_at", 0) or 0))
        group["severity"] = _max_severity(str(group.get("severity", "info")), str(event.get("severity", "info")))
        group["status"] = event.get("status") or group.get("status", "")
        message = event.get("safe_message") or event.get("message") or event.get("safe_title") or ""
        if message:
            group["summary"] = _truncate_text(message, limit=220)
        if len(group["events"]) < 8:
            group["events"].append(_activity_group_event_projection(event))
    ordered_groups = sorted(groups.values(), key=lambda item: int(item.get("updated_at", 0) or 0), reverse=True)
    # Never pad with system/status groups — that reintroduces device telemetry.
    display_groups = [group for group in ordered_groups if group.get("operation_type") != "system"]
    operations = _operations(runtime)
    aegis_recent = [
        _activity_event_projection(event)
        for event in events
        if not _is_activity_noise_event(event)
    ][:40]
    return {
        "recent": aegis_recent,
        "groups": display_groups[:24],
        "operations": operations,
        "count": len(aegis_recent),
        "source": "audit_manager+event_manager" if operations else "event_manager",
    }


_OPERATION_KIND_LABELS = {
    "chat": "User instruction",
    "autonomous": "Autonomous run",
    "task": "Task",
    "approval": "Approval",
    "system": "System",
}

_ACTIVITY_NOISE_EVENT_TYPES = {
    "status.changed",
    "status.updated",
    "connection.updated",
    "connection.changed",
    "server.heartbeat",
    "health.updated",
    "device.telemetry",
    "android.heartbeat",
    "android.user_activity",
    "android.user_activity.changed",
    "android.foreground_app.changed",
    "android.current_app_changed",
    "android.connected",
    "android.disconnected",
    "android.device_state",
    "android.permission.changed",
    "android.presence.changed",
    "android.semantic_layout.changed",
    "pc.user_activity.snapshot",
    "browser.user_activity.changed",
}

_ANDROID_ACTIVITY_ALLOWLIST = {
    "android.approval.decided",
    "android.approval.decision",
    "android.chat",
}


def _operations(runtime: Any) -> list[dict[str, Any]]:
    """Build AEGIS-centric operation timeline (one chat turn / autonomous cycle / task)."""
    ops: list[dict[str, Any]] = []
    seen: set[str] = set()

    audit = getattr(runtime, "audit_manager", None)
    if audit is not None and hasattr(audit, "list_groups"):
        try:
            result = audit.list_groups(page=1, per_page=40, max_entries=300)
            groups = result.get("groups", []) if isinstance(result, dict) else []
        except Exception:
            groups = []
        for group in groups:
            op = _operation_from_audit_group(group)
            if op is None:
                continue
            operation_id = str(op.get("operation_id") or "")
            if not operation_id or operation_id in seen:
                continue
            seen.add(operation_id)
            ops.append(op)

    for cycle in (_autonomous_logs(runtime).get("cycles") or [])[:12]:
        timestamp_ms = int(cycle.get("timestamp_ms") or 0)
        operation_id = f"autonomous-cycle:{timestamp_ms}"
        if operation_id in seen:
            continue
        if _has_nearby_operation(ops, timestamp_ms, kind="autonomous", window_ms=120_000):
            continue
        if not cycle.get("actions") and not cycle.get("decision") and not cycle.get("skip_reason"):
            continue
        seen.add(operation_id)
        ops.append(_operation_from_autonomous_cycle(cycle))

    ops.sort(key=lambda item: int(item.get("updated_at") or 0), reverse=True)
    return ops[:24]


def _operation_from_audit_group(group: dict[str, Any]) -> dict[str, Any] | None:
    kind = str(group.get("group_type") or "system")
    tool_count = int(group.get("tool_count") or 0)
    approval_count = int(group.get("approval_count") or 0)
    error_count = int(group.get("error_count") or 0)
    title = str(group.get("title") or "")
    summary = str(group.get("summary") or "")
    blob = f"{title} {summary}".lower()
    if any(
        token in blob
        for token in (
            "heartbeat",
            "user_activity",
            "foreground_app",
            "activitychange",
            "activity_change",
            "activity changed",
            "device telemetry",
        )
    ):
        return None
    if kind == "system" and not (tool_count or approval_count):
        return None
    if kind == "system" and tool_count:
        kind = "task"

    steps: list[dict[str, Any]] = []
    for entry in group.get("entries") or []:
        if not isinstance(entry, dict) or _is_operation_noise_entry(entry):
            continue
        action = str(entry.get("action") or "")
        capability_id = str(entry.get("capability_id") or "")
        narrative = _narrative_from_audit_entry(entry)
        if not (action or capability_id or narrative):
            continue
        failed = bool(
            action.endswith("_failed")
            or str(entry.get("decision") or "").lower() in {"error", "failed", "deny", "denied"}
            or (isinstance(entry.get("detail"), dict) and entry.get("detail", {}).get("error"))
        )
        steps.append(
            {
                "action": action,
                "capability_id": capability_id,
                "summary": _truncate_text(narrative, limit=220),
                "narrative": _truncate_text(narrative, limit=220),
                "decision": str(entry.get("decision") or ""),
                "timestamp_ms": int(entry.get("timestamp_ms") or 0),
                "status": "failed" if failed else "ok",
            }
        )
        if len(steps) >= 12:
            break

    if kind == "system" and not steps:
        return None

    title = str(group.get("title") or kind)[:160]
    summary = _humanize_activity_text(str(group.get("summary") or ""))[:280]
    what_happened = _what_happened_from_steps(steps, summary)
    op = {
        "operation_id": str(group.get("group_id") or ""),
        "kind": kind,
        "kind_label": _OPERATION_KIND_LABELS.get(kind, kind.title()),
        "title": title,
        "summary": summary,
        "what_happened": what_happened,
        "narrative": what_happened,
        "status": str(group.get("status") or "success"),
        "started_at": int(group.get("start_ms") or 0),
        "updated_at": int(group.get("end_ms") or 0),
        "tool_count": tool_count,
        "error_count": error_count,
        "approval_count": approval_count,
        "entry_count": int(group.get("entry_count") or len(steps)),
        "steps": steps,
        "priority": "P1" if error_count else ("P2" if kind in {"chat", "approval"} else "P3"),
    }
    op["causal_chain"] = _causal_chain_from_operation(op)
    return op


def _operation_from_autonomous_cycle(cycle: dict[str, Any]) -> dict[str, Any]:
    actions = cycle.get("actions") if isinstance(cycle.get("actions"), list) else []
    steps: list[dict[str, Any]] = []
    what_parts: list[str] = []
    for action in actions[:12]:
        if not isinstance(action, dict):
            continue
        capability_id = str(action.get("capability_id") or "")
        done = str(action.get("what_was_done") or "").strip()
        result_summary = str(action.get("result_summary") or "").strip()
        narrative = result_summary or done or _capability_short_label(capability_id)
        steps.append(
            {
                "action": done or capability_id,
                "capability_id": capability_id,
                "summary": _truncate_text(narrative, limit=220),
                "narrative": _truncate_text(narrative, limit=220),
                "decision": "",
                "timestamp_ms": int(cycle.get("timestamp_ms") or 0),
                "status": "ok" if action.get("success") else "failed",
            }
        )
        if narrative:
            what_parts.append(narrative)

    if not what_parts and cycle.get("skip_reason"):
        what_parts.append(f"Did not act: {cycle.get('skip_reason')}")
    if not what_parts and cycle.get("decision"):
        what_parts.append(str(cycle.get("decision")))

    summary = _truncate_text(" ".join(what_parts), limit=280)
    what_happened = _truncate_text(
        " ".join(what_parts) if what_parts else "No actions this cycle.",
        limit=280,
    )
    op = {
        "operation_id": f"autonomous-cycle:{int(cycle.get('timestamp_ms') or 0)}",
        "kind": "autonomous",
        "kind_label": _OPERATION_KIND_LABELS.get("autonomous", "Autonomous"),
        "title": str(cycle.get("decision") or "Autonomous cycle")[:160],
        "summary": summary,
        "what_happened": what_happened,
        "narrative": what_happened,
        "status": "skipped" if cycle.get("skip_reason") else ("success" if not any(s.get("status") == "failed" for s in steps) else "failed"),
        "started_at": int(cycle.get("timestamp_ms") or 0),
        "updated_at": int(cycle.get("timestamp_ms") or 0),
        "tool_count": len(steps),
        "error_count": sum(1 for s in steps if s.get("status") == "failed"),
        "approval_count": 0,
        "entry_count": len(steps),
        "steps": steps,
        "skip_reason": str(cycle.get("skip_reason") or ""),
        "decision": str(cycle.get("decision") or ""),
        "priority": "P3",
    }
    op["causal_chain"] = _causal_chain_from_operation(op)
    return op


def _causal_chain_from_operation(op: dict[str, Any]) -> list[dict[str, Any]]:
    """Human-readable Trigger → … → Learning chain for one operation."""
    steps = list(op.get("steps") or [])
    skip = str(op.get("skip_reason") or "")
    decision = str(op.get("decision") or "")
    failed = [s for s in steps if s.get("status") == "failed"]
    ok = [s for s in steps if s.get("status") != "failed"]

    def stage(name: str, summary: str, status: str = "present", detail: str = "") -> dict[str, Any]:
        return {
            "stage": name,
            "label": name.replace("_", " ").title(),
            "summary": summary[:220] if summary else "",
            "status": status,  # present | missing | skipped
            "detail": detail[:220],
        }

    chain = [
        stage("trigger", str(op.get("kind_label") or op.get("kind") or "Operation"), "present", str(op.get("title") or "")),
        stage(
            "decision_context",
            "See Decision Context page for AgentState obligations and situation",
            "present" if op.get("kind") else "missing",
        ),
        stage(
            "candidates_and_non_action",
            skip or decision or ("Tool steps selected" if steps else "No tool selection recorded"),
            "present" if (skip or decision or steps) else "missing",
            skip,
        ),
        stage(
            "goal",
            str(op.get("title") or op.get("summary") or ""),
            "present" if op.get("title") else "missing",
        ),
        stage(
            "execution",
            f"{len(ok)} succeeded, {len(failed)} failed" if steps else (skip or "No execution"),
            "present" if steps else ("skipped" if skip else "missing"),
            " → ".join(str(s.get("narrative") or s.get("summary") or s.get("capability_id") or s.get("action") or "") for s in steps[:4]),
        ),
        stage(
            "result",
            str(op.get("what_happened") or op.get("narrative") or op.get("summary") or ""),
            "present" if (op.get("what_happened") or op.get("summary")) else "missing",
        ),
        stage(
            "verification",
            "Failed steps present" if failed else ("Execution completed" if ok else "Not verified"),
            "present" if (failed or ok) else "missing",
        ),
        stage(
            "presentation",
            "Reported to user surfaces when presentable",
            "present" if str(op.get("kind")) in {"chat", "approval"} else "missing",
        ),
        stage(
            "follow_up",
            "Open loops / continuations may own remaining work",
            "present" if int(op.get("approval_count") or 0) else "missing",
        ),
        stage(
            "learning",
            "Repair / failure lessons recorded when applicable",
            "present" if failed else "missing",
        ),
    ]
    return chain


def _narrative_from_audit_entry(entry: dict[str, Any]) -> str:
    """Extract a human sentence describing what happened in one audit entry."""
    detail = entry.get("detail") if isinstance(entry.get("detail"), dict) else {}
    action = str(entry.get("action") or "")
    for key in (
        "response_preview",
        "what_was_done",
        "result_summary",
        "result_preview",
        "llm_reason",
        "user_facing_summary",
        "summary",
        "message",
    ):
        value = str(detail.get(key) or "").strip()
        if value:
            return _humanize_activity_text(value)
    for key in ("detail_summary", "reason"):
        value = _humanize_activity_text(str(entry.get(key) or ""))
        if value:
            return value
    if action in {"llm_call", "llm_tool_call", "llm_vision_call"}:
        return "LLM produced a response"
    if action in {"tool_execution", "tool_invoked"} or action.startswith("tool."):
        return _capability_short_label(str(entry.get("capability_id") or detail.get("capability_id") or ""))
    return ""


def _humanize_activity_text(text: str) -> str:
    """Turn legacy key=value audit summaries into readable prose when possible."""
    raw = (text or "").strip()
    if not raw:
        return ""
    # Unwrap response=..., model=... dumps from older audit summaries.
    for prefix, markers in (
        ("response=", (", model=", ", tokens=", ", duration=", ", prompt=", ", tools=")),
        ("result=", (", capability=", ", status=", ", model=")),
        ("reason=", (", source=", ", model=")),
    ):
        if raw.startswith(prefix):
            rest = raw[len(prefix) :]
            for marker in markers:
                if marker in rest:
                    rest = rest.split(marker, 1)[0]
                    break
            return rest.strip()
    # Drop pure technical dumps like "capability=x, status=success".
    if "=" in raw and all(("=" in part) for part in raw.split(", ") if part.strip()):
        preferred_keys = ("response", "result", "reason", "title", "summary", "message")
        parts = [part.strip() for part in raw.split(", ")]
        for part in parts:
            for key in preferred_keys:
                if part.startswith(f"{key}="):
                    return part.split("=", 1)[1].strip()
        return ""
    return raw


def _capability_short_label(capability_id: str) -> str:
    cap = (capability_id or "").strip()
    if not cap:
        return ""
    leaf = cap.rsplit(".", 1)[-1].replace("_", " ")
    return f"Ran {leaf}" if leaf else cap


def _what_happened_from_steps(steps: list[dict[str, Any]], fallback: str = "") -> str:
    """Build a natural-language 'what AEGIS did' line for Activity."""
    if not steps:
        return _truncate_text(_humanize_activity_text(fallback) or "No detailed steps recorded.", limit=320)

    # Prefer LLM response narratives over tool metadata.
    llm_like = [
        step
        for step in steps
        if str(step.get("action") or "") in {"llm_call", "llm_tool_call", "llm_vision_call"}
        and (step.get("narrative") or step.get("summary"))
    ]
    if llm_like:
        # Last LLM answer is usually the user-facing summary of the whole operation.
        text = _humanize_activity_text(str(llm_like[-1].get("narrative") or llm_like[-1].get("summary") or ""))
        if text:
            return _truncate_text(text, limit=320)

    preferred = [
        step
        for step in steps
        if step.get("narrative")
        or step.get("summary")
        or step.get("capability_id")
        or str(step.get("action") or "") in {"tool_execution", "tool_invoked"}
        or str(step.get("action") or "").startswith("tool.")
    ] or steps

    parts: list[str] = []
    for step in preferred[:5]:
        narrative = _humanize_activity_text(str(step.get("narrative") or step.get("summary") or ""))
        if narrative:
            parts.append(narrative)
            continue
        capability_id = str(step.get("capability_id") or "")
        label = _capability_short_label(capability_id)
        if label:
            parts.append(label)
            continue
        action = str(step.get("action") or "")
        if action:
            parts.append(action.replace("_", " "))
    if parts:
        # Sentence-style join instead of capability_id: dump → dump.
        return _truncate_text(" ".join(parts), limit=320)
    return _truncate_text(_humanize_activity_text(fallback) or "No detailed steps recorded.", limit=320)


def _has_nearby_operation(
    ops: list[dict[str, Any]],
    timestamp_ms: int,
    *,
    kind: str,
    window_ms: int,
) -> bool:
    if not timestamp_ms:
        return False
    for op in ops:
        if str(op.get("kind") or "") != kind:
            continue
        updated_at = int(op.get("updated_at") or op.get("started_at") or 0)
        if abs(updated_at - timestamp_ms) <= window_ms:
            return True
    return False


def _is_activity_noise_event(event: dict[str, Any]) -> bool:
    """Return True for device/status telemetry that is not an AEGIS operation."""
    event_type = str(
        event.get("event_type") or event.get("source_type") or event.get("type") or ""
    ).lower()
    title = str(
        event.get("safe_title") or event.get("title") or event.get("safe_message") or event.get("message") or ""
    ).lower()
    haystack = f"{event_type} {title}"

    if event_type in _ANDROID_ACTIVITY_ALLOWLIST:
        return False
    if event_type in _ACTIVITY_NOISE_EVENT_TYPES:
        return True
    if event_type.startswith("android."):
        # Device telemetry / phone signals are not AEGIS actions.
        return True
    if any(
        token in haystack
        for token in (
            "heartbeat",
            "telemetry",
            "user_activity",
            "foreground_app",
            "current_app",
            "activitychange",
            "activity_change",
            "activity changed",
        )
    ):
        return True
    if event.get("server_id") == "android-server" and not (
        event.get("task_id") or event.get("approval_id") or event.get("capability_id")
    ):
        return True
    operation_type = _activity_operation_type(event)
    if operation_type != "system":
        return False
    # Pure server status without task/approval/capability is device noise for Recent Operations.
    return not (event.get("task_id") or event.get("approval_id") or event.get("capability_id"))


def _is_operation_noise_entry(entry: dict[str, Any]) -> bool:
    action = str(entry.get("action") or "").lower()
    detail = entry.get("detail") if isinstance(entry.get("detail"), dict) else {}
    title = str(
        entry.get("audit_group_title")
        or detail.get("title")
        or detail.get("summary")
        or entry.get("detail_summary")
        or ""
    ).lower()
    if action in {"status_changed", "status.changed", "connection.updated", "health_check", "server_heartbeat"}:
        return True
    if "heartbeat" in action or "telemetry" in action or "user_activity" in action:
        return True
    if any(token in title for token in ("heartbeat", "user_activity", "foreground_app", "activity change")):
        return True
    return False


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
    if hasattr(manager, "get_current_user_state"):
        return manager.get_current_user_state()
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
    return _usage_projection(
        {"summary": "LLM usage is available from the LLM Usage service.", "input_tokens": 0, "output_tokens": 0}
    )


def _autonomous_logs(runtime: Any) -> dict[str, Any]:
    """Group autonomous execution logs by cycle."""
    import json as _json
    import os

    loop = getattr(runtime, "autonomous_loop", None)
    data_dir = getattr(loop, "_data_dir", None) if loop else None
    if data_dir is None:
        return {"cycles": [], "count": 0}

    log_path = str(data_dir / "execution_log.jsonl")
    if not os.path.exists(log_path):
        return {"cycles": [], "count": 0}

    cycles = []
    try:
        with open(log_path, "rb") as f:
            size = os.path.getsize(log_path)
            max_bytes = 4 * 1024 * 1024
            offset = max(0, size - max_bytes)
            f.seek(offset)
            payload = f.read(max_bytes)
        if offset:
            newline = payload.find(b"\n")
            payload = payload[newline + 1 :] if newline >= 0 else b""
        lines = payload.splitlines()[-100:]
        for raw_line in lines:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            entry = _json.loads(line)
            ts = entry.get("timestamp_ms", 0)
            tasks = entry.get("tasks", [])
            results = entry.get("results", [])
            decision = entry.get("last_decision", "")
            skip_reason = entry.get("last_skip_reason", "")

            actions = []
            for i, task in enumerate(tasks):
                result = results[i] if i < len(results) else {}
                actions.append(
                    {
                        "capability_id": task.get("capability_id", ""),
                        "action": task.get("action_goal", task.get("action", "")),
                        "desire": task.get("desire", ""),
                        "what_was_done": task.get("what_was_done", ""),
                        "result_summary": task.get("result_summary", result.get("result", "")),
                        "changed_state": task.get("changed_state", ""),
                        "success": result.get("success", False),
                    }
                )

            cycles.append(
                {
                    "timestamp_ms": ts,
                    "decision": decision,
                    "skip_reason": skip_reason,
                    "action_count": len(actions),
                    "actions": actions,
                }
            )
    except Exception:
        return {"cycles": [], "count": 0}

    cycles.sort(key=lambda c: c["timestamp_ms"], reverse=True)
    return {
        "cycles": cycles[:20],
        "count": len(cycles),
        "count_is_recent_window": True,
    }


def _errors(runtime: Any) -> dict[str, Any]:
    """Errors surface is RepairManager history (not raw audit JSON)."""
    repair = getattr(runtime, "repair_manager", None)
    items: list[dict[str, Any]] = []
    if repair is not None and hasattr(repair, "list_history"):
        for entry in repair.list_history(limit=30) or []:
            if not isinstance(entry, dict):
                continue
            items.append(
                {
                    "id": str(entry.get("repair_id") or entry.get("id") or entry.get("capability_id") or ""),
                    "title": str(entry.get("category") or "Repair"),
                    "message": str(entry.get("error") or entry.get("summary") or ""),
                    "severity": "warning" if entry.get("retried") else "critical",
                    "capability_id": str(entry.get("capability_id") or ""),
                    "status": str(entry.get("status") or entry.get("outcome") or "recorded"),
                    "created_at": int(entry.get("timestamp_ms") or entry.get("created_at") or 0),
                    "summary": str(entry.get("lesson") or entry.get("action") or ""),
                    "next_action": str(entry.get("next_action") or entry.get("recovery_hint") or ""),
                    "raw": entry,
                }
            )
    if not items:
        # Fallback: keep a thin audit error list only when repair history is empty.
        audit = getattr(runtime, "audit_manager", None) or getattr(runtime, "audit_log", None)
        if audit is not None and hasattr(audit, "list_recent"):
            result = _call_with_limit(audit.list_recent, 40)
            raw_entries = result.get("entries", result if isinstance(result, list) else [])
            for entry in raw_entries:
                if str(entry.get("action", "")).endswith("_failed") or _get(entry.get("detail", {}), "error", ""):
                    items.append(_error_projection(entry))
                    if len(items) >= 20:
                        break
    status = {}
    if repair is not None and hasattr(repair, "get_status"):
        try:
            status = repair.get_status() or {}
        except Exception:
            status = {}
    return {"items": items, "count": len(items), "repair_status": status, "source": "repair_manager"}


def _agent_state(runtime: Any) -> dict[str, Any]:
    agent_state = getattr(runtime, "agent_state", None)
    if agent_state is None or not hasattr(agent_state, "snapshot"):
        return {"summary": "AgentState is not configured.", "obligations": [], "context": {}}
    try:
        ctx = agent_state.snapshot("dashboard")
        data = ctx.to_dict() if hasattr(ctx, "to_dict") else dict(ctx)
        obligations = data.get("obligations") or []
        return {
            "summary": ctx.to_context_string() if hasattr(ctx, "to_context_string") else "",
            "identity": data.get("identity") or "",
            "mission_version": data.get("mission_version") or "",
            "obligations": obligations[:20],
            "active_tasks": (data.get("active_tasks") or [])[:10],
            "learnings": (data.get("learnings") or [])[:10],
            "corrections": (data.get("corrections") or [])[:10],
            "repair_history": (data.get("repair_history") or [])[-10:],
            "situation": data.get("situation") or {},
            "context": {
                "context_id": data.get("context_id"),
                "built_at_ms": data.get("built_at_ms"),
                "triggering_query": data.get("triggering_query"),
            },
        }
    except Exception as exc:
        return {"summary": f"AgentState unavailable: {exc}", "obligations": [], "context": {}}


def _decision_context(runtime: Any) -> dict[str, Any]:
    """Actual DecisionContext from AgentState — not Context Builder field placeholders."""
    state = _agent_state(runtime)
    initiative = _initiative(runtime)
    return {
        "summary": state.get("summary") or "",
        "situation": state.get("situation") or {},
        "obligations": state.get("obligations") or [],
        "identity": state.get("identity") or "",
        "recent_non_actions": (initiative.get("recent_non_actions") or [])[:10],
        "funnel": initiative.get("funnel") or {},
        "context_meta": state.get("context") or {},
    }


def _goals(runtime: Any) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    tm = getattr(runtime, "task_manager", None)
    if tm is not None and hasattr(tm, "list_tasks"):
        for task in tm.list_tasks(limit=80) or []:
            graph = task.get("goal_graph") if isinstance(task, dict) else None
            if not graph and isinstance(task, dict) and not task.get("goal"):
                continue
            if not isinstance(task, dict):
                continue
            graph = graph if isinstance(graph, dict) else {}
            verification = list(graph.get("verification") or [])
            unmet = [
                item
                for item in verification
                if str(item.get("status") or "") not in {"passed", "ok", "success"}
            ]
            items.append(
                {
                    "task_id": str(task.get("task_id") or ""),
                    "title": str(task.get("title") or task.get("goal") or "Goal"),
                    "goal": str(task.get("goal") or graph.get("goal") or ""),
                    "status": str(task.get("status") or ""),
                    "success_condition": str(
                        task.get("success_condition")
                        or graph.get("success_condition")
                        or ""
                    ),
                    "verification": verification[:8],
                    "unmet_conditions": unmet[:8],
                    "evidence": list(graph.get("evidence") or [])[:8],
                    "value_to_user": str(task.get("value_to_user") or graph.get("value_to_user") or ""),
                    "updated_at": int(task.get("updated_at") or task.get("created_at") or 0),
                }
            )
    open_items = [item for item in items if item["status"] not in {"completed", "cancelled", "expired"}]
    return {
        "items": items[:40],
        "open": open_items[:20],
        "count": len(items),
        "open_count": len(open_items),
        "summary": f"{len(open_items)} open goal(s) with verification evidence",
    }


def _initiative(runtime: Any) -> dict[str, Any]:
    engine = getattr(runtime, "initiative_engine", None)
    if engine is None or not hasattr(engine, "diagnostics"):
        return {"funnel": {}, "recent_non_actions": [], "recent_decisions": [], "summary": "InitiativeEngine not configured."}
    try:
        diag = engine.diagnostics() or {}
    except Exception as exc:
        return {"funnel": {}, "recent_non_actions": [], "recent_decisions": [], "summary": str(exc)}
    records = list(diag.get("recent_decisions") or [])
    non_actions = [
        {
            "reason": str(item.get("reason") or ""),
            "decision": str(item.get("decision") or "no_action"),
            "created_at": int(item.get("created_at") or 0),
            "detail": item.get("detail") if isinstance(item.get("detail"), dict) else {},
            "candidate": (item.get("candidate") or {}) if isinstance(item.get("candidate"), dict) else {},
        }
        for item in records
        if item.get("record_type") in {"non_action", "candidate_decision"}
        and str(item.get("decision") or "") not in {"execute_now", ""}
    ]
    return {
        "funnel": diag.get("funnel") or {},
        "no_action_reasons": diag.get("no_action_reasons") or {},
        "recent_non_actions": non_actions[-30:],
        "recent_decisions": records[-30:],
        "updated_at": int(diag.get("updated_at") or 0),
        "summary": _initiative_summary(diag.get("funnel") or {}, diag.get("no_action_reasons") or {}),
    }


def _initiative_summary(funnel: dict[str, Any], reasons: dict[str, Any]) -> str:
    triggered = int(funnel.get("triggers_observed", 0) or 0)
    executed = int(funnel.get("actions_executed", 0) or 0)
    presented = int(funnel.get("results_presented", 0) or 0)
    top_reason = next(iter(reasons.keys()), "")
    parts = [f"Triggers {triggered}", f"executed {executed}", f"presented {presented}"]
    if top_reason:
        parts.append(f"top non-action: {top_reason}")
    return "; ".join(parts)


def _continuations(runtime: Any) -> dict[str, Any]:
    manager = getattr(runtime, "continuation_manager", None)
    if manager is None:
        return {"open": [], "due": [], "diagnostics": {}, "summary": "ContinuationManager not configured."}
    open_items = manager.list_open() if hasattr(manager, "list_open") else []
    due = manager.due() if hasattr(manager, "due") else []
    diagnostics = manager.diagnostics() if hasattr(manager, "diagnostics") else {}
    return {
        "open": open_items[:40],
        "due": due[:20],
        "diagnostics": diagnostics,
        "count": len(open_items),
        "summary": f"{len(open_items)} open continuation(s), {len(due)} due for follow-up",
    }


def _repairs(runtime: Any) -> dict[str, Any]:
    repair = getattr(runtime, "repair_manager", None)
    if repair is None:
        return {"items": [], "status": {}, "summary": "RepairManager not configured."}
    history = repair.list_history(limit=40) if hasattr(repair, "list_history") else []
    status = repair.get_status() if hasattr(repair, "get_status") else {}
    return {
        "items": history,
        "status": status,
        "count": len(history),
        "summary": f"{len(history)} recent repair event(s)",
    }


def _social(runtime: Any) -> dict[str, Any]:
    """SocialManager: inbox + AGORA decision state (Communications surface)."""
    social = getattr(runtime, "social_manager", None)
    if social is None:
        return {
            "inbox": [],
            "status": {},
            "agora": {},
            "summary": "SocialManager not configured.",
        }
    inbox = social.list_items(limit=40) if hasattr(social, "list_items") else []
    status = social.get_status() if hasattr(social, "get_status") else {}
    pending = [
        item
        for item in inbox
        if str(item.get("status") or "").lower()
        in {"pending", "proposed", "awaiting_approval", "needs_decision", "new"}
    ]
    decided = [
        {
            "item_id": item.get("item_id"),
            "channel": item.get("channel"),
            "status": item.get("status"),
            "decision_reason": item.get("decision_reason") or item.get("reason") or "",
            "body_preview": str(item.get("body") or item.get("summary") or "")[:160],
            "updated_at": item.get("updated_at") or item.get("created_at"),
        }
        for item in inbox[:30]
    ]
    return {
        "inbox": inbox[:40],
        "pending_decisions": pending[:20],
        "decided": decided,
        "status": status,
        "agora": {
            "pending_count": len(pending),
            "total": int(status.get("total") or len(inbox)),
            "counts": status.get("counts") or {},
        },
        "summary": f"{len(pending)} social item(s) awaiting decision; {int(status.get('total') or 0)} total",
    }


def _behavioral_reports(runtime: Any) -> dict[str, Any]:
    evaluation = getattr(runtime, "behavioral_evaluation", None)
    if evaluation is None or not hasattr(evaluation, "snapshot"):
        return {"metrics": {}, "evidence": {}, "summary": "BehavioralEvaluation not configured."}
    try:
        snap = evaluation.snapshot() or {}
    except Exception as exc:
        return {"metrics": {}, "evidence": {}, "summary": str(exc)}
    metrics = {
        key: value
        for key, value in snap.items()
        if key != "evidence" and not isinstance(value, (dict, list))
    }
    return {
        "metrics": metrics,
        "evidence": snap.get("evidence") or {},
        "summary": (
            f"Restraint {float(metrics.get('restraint') or 0):.0%}, "
            f"goal achievement {float(metrics.get('goal_achievement') or 0):.0%}, "
            f"continuity {float(metrics.get('continuity') or 0):.0%}"
        ),
    }


def _generated_capabilities(runtime: Any) -> dict[str, Any]:
    """Generated page: only generated capability manifests."""
    catalog = getattr(runtime, "capability_catalog", None) or getattr(runtime, "catalog", None)
    items: list[dict[str, Any]] = []
    if catalog is not None and hasattr(catalog, "list_all"):
        try:
            manifests = catalog.list_all(origin="generated")
        except TypeError:
            manifests = [
                m
                for m in (catalog.list_all() or [])
                if str(getattr(m, "origin", "") or getattr(m, "source", "")).lower()
                in {"generated", "codegen", "dynamic"}
            ]
        for manifest in manifests[:80]:
            items.append(_capability_projection(manifest))
    return {"items": items, "count": len(items), "summary": f"{len(items)} generated capability(ies)"}


def _executions(runtime: Any) -> dict[str, Any]:
    """Executions page: real execution history (activity operations + autonomous cycles)."""
    activity = _activity(runtime)
    operations = list(activity.get("operations") or [])
    cycles = (_autonomous_logs(runtime).get("cycles") or [])[:20]
    return {
        "operations": operations[:40],
        "autonomous_cycles": cycles,
        "count": len(operations),
        "summary": f"{len(operations)} recent operation(s), {len(cycles)} autonomous cycle(s)",
    }


def _open_loops(runtime: Any) -> dict[str, Any]:
    """Unified open work: tasks, commitments, approvals, social obligations, incidents."""
    loops: list[dict[str, Any]] = []

    for task in _running_tasks(runtime) + _waiting_tasks(runtime):
        loops.append(
            _loop_item(
                kind="task",
                loop_id=f"task:{task.get('task_id')}",
                title=str(task.get("title") or task.get("goal") or "Task"),
                owner="AEGIS",
                next_action=str(task.get("next_action") or task.get("current_action") or ""),
                waiting_reason=str(task.get("blocked_reason") or ""),
                due_at=int(task.get("due_at") or 0),
                success_condition=str(task.get("success_condition") or task.get("verification_summary") or ""),
                status=str(task.get("phase") or task.get("status") or "open"),
                evidence={"task_id": task.get("task_id"), "capability_id": task.get("capability_id")},
            )
        )

    for approval in _pending_approvals(runtime):
        proj = _approval_projection(approval)
        loops.append(
            _loop_item(
                kind="approval",
                loop_id=f"approval:{proj.get('approval_id')}",
                title=str(proj.get("summary") or proj.get("capability_id") or "Approval"),
                owner="User",
                next_action="Approve or reject",
                waiting_reason=str(proj.get("reason") or "Waiting for user approval"),
                due_at=int(proj.get("expires_at") or 0),
                success_condition="User decision recorded",
                status="waiting_approval",
                evidence=proj,
            )
        )

    commitments = _commitments(runtime).get("items") or []
    for item in commitments[:30]:
        if not isinstance(item, dict):
            continue
        loops.append(
            _loop_item(
                kind="commitment",
                loop_id=f"commitment:{item.get('commitment_id') or item.get('id')}",
                title=str(item.get("title") or item.get("summary") or "Commitment"),
                owner=str(item.get("person") or item.get("owner") or "User"),
                next_action=str(item.get("next_action") or item.get("notification_plan") or "Follow up"),
                waiting_reason=str(item.get("status") or ""),
                due_at=int(item.get("due_at") or item.get("due_at_ms") or 0),
                success_condition=str(item.get("success_condition") or "Commitment fulfilled"),
                status=str(item.get("status") or "open"),
                evidence=item,
            )
        )

    for item in (_social(runtime).get("pending_decisions") or [])[:20]:
        loops.append(
            _loop_item(
                kind="social_obligation",
                loop_id=f"social:{item.get('item_id')}",
                title=str(item.get("body") or item.get("summary") or "Social item")[:120],
                owner="AEGIS",
                next_action=str(item.get("suggested_action") or "Decide whether to reply"),
                waiting_reason=str(item.get("decision_reason") or "Awaiting social decision"),
                due_at=int(item.get("due_at") or 0),
                success_condition="Reply delivered or deliberate skip recorded",
                status=str(item.get("status") or "pending"),
                evidence=item,
            )
        )

    agent = _agent_state(runtime)
    for obligation in agent.get("obligations") or []:
        if not isinstance(obligation, dict):
            continue
        kind = str(obligation.get("kind") or "obligation")
        if kind in {"commitment", "social_obligation"}:
            continue  # already covered
        loops.append(
            _loop_item(
                kind="incident" if kind == "incident" else "obligation",
                loop_id=f"obligation:{obligation.get('obligation_id')}",
                title=str(obligation.get("summary") or kind),
                owner="AEGIS",
                next_action="Resolve open obligation",
                waiting_reason=kind,
                due_at=int(obligation.get("due_at_ms") or 0),
                success_condition="Obligation cleared from AgentState",
                status="open",
                evidence=obligation,
            )
        )

    for cont in (_continuations(runtime).get("open") or [])[:20]:
        loops.append(
            _loop_item(
                kind="continuation",
                loop_id=f"continuation:{cont.get('continuation_id')}",
                title=str(cont.get("goal") or "Continuation"),
                owner=str(cont.get("waiting_for") or "AEGIS"),
                next_action=str(cont.get("stage") or "Advance"),
                waiting_reason=str(cont.get("rationale") or cont.get("waiting_for") or ""),
                due_at=int(cont.get("follow_up_due_at") or 0),
                success_condition="Continuation reaches terminal verified state",
                status=str(cont.get("state") or "open"),
                evidence=cont,
            )
        )

    loops.sort(key=lambda item: (0 if item["waiting_reason"] else 1, item.get("due_at") or 2**62))
    return {
        "items": loops[:80],
        "count": len(loops),
        "by_kind": _count_by(loops, "kind"),
        "summary": f"{len(loops)} open loop(s) across tasks, approvals, commitments, social, and incidents",
    }


def _loop_item(
    *,
    kind: str,
    loop_id: str,
    title: str,
    owner: str,
    next_action: str,
    waiting_reason: str,
    due_at: int,
    success_condition: str,
    status: str,
    evidence: Any,
) -> dict[str, Any]:
    return {
        "id": loop_id,
        "kind": kind,
        "title": title[:200],
        "owner": owner,
        "next_action": next_action[:200],
        "waiting_reason": waiting_reason[:200],
        "due_at": due_at,
        "success_condition": success_condition[:200],
        "status": status,
        "confidence": 0.7 if evidence else 0.4,
        "evidence_summary": _evidence_summary(evidence),
        "evidence": evidence if isinstance(evidence, dict) else {"value": evidence},
    }


def _evidence_summary(evidence: Any) -> str:
    if not isinstance(evidence, dict):
        return ""
    for key in ("summary", "reason", "message", "decision_reason", "verification_summary", "body"):
        value = evidence.get(key)
        if value:
            return str(value)[:160]
    return ""


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        label = str(item.get(key) or "unknown")
        counts[label] = counts.get(label, 0) + 1
    return counts


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
                item["status_detail"] = (
                    "Android device is connected." if android_online else "Android device is not connected."
                )
                item["dependencies"] = {
                    "last_seen": android_status.get("last_seen", 0),
                    "device_model": android_status.get("device_model", ""),
                    "permission_status": android_status.get("permission_status", {}),
                    "capability_availability": android_status.get("capability_availability", {}),
                    "reconnect_count": int(android_status.get("reconnect_count", 0) or 0),
                    "heartbeat_failure_count": int(android_status.get("heartbeat_failure_count", 0) or 0),
                }
                found = True
                break
        if not found:
            servers.append(
                {
                    "server_id": "android-server",
                    "status": "ONLINE" if android_online else "OFFLINE",
                    "mode": android_status.get("connection_mode", "offline"),
                    "status_detail": "Android device is connected."
                    if android_online
                    else "Android device is not connected.",
                    "dependencies": {
                        "last_seen": android_status.get("last_seen", 0),
                        "device_model": android_status.get("device_model", ""),
                        "reconnect_count": int(android_status.get("reconnect_count", 0) or 0),
                        "heartbeat_failure_count": int(android_status.get("heartbeat_failure_count", 0) or 0),
                    },
                    "health_checked_at": _now_ms(),
                }
            )

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
        if current is None or _priority_rank(item.get("priority", "P3")) < _priority_rank(
            current.get("priority", "P3")
        ):
            seen[key] = item
    return sorted(
        seen.values(),
        key=lambda item: (_priority_rank(item.get("priority", "P3")), -int(item.get("expires_at", 0) or 0)),
    )


def _compact_presentation_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("event_id", ""),
        "scene_type": event.get("scene_type", ""),
        "priority": event.get("priority", "P3"),
        "severity": event.get("severity", "info"),
        "source": event.get("source", ""),
        "title": _truncate_text(event.get("title", ""), limit=120),
        "summary": _truncate_text(event.get("summary", ""), limit=180),
        "affected_entities": event.get("affected_entities", [])[:6]
        if isinstance(event.get("affected_entities"), list)
        else [],
        "task_id": event.get("task_id", ""),
        "approval_id": event.get("approval_id", ""),
        "privacy_class": event.get("privacy_class", "normal"),
        "recommended_surfaces": event.get("recommended_surfaces", [])[:5]
        if isinstance(event.get("recommended_surfaces"), list)
        else [],
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
        "actor": event.get("payload", {}).get("actor", "aegis")
        if isinstance(event.get("payload", {}), dict)
        else "aegis",
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
    for key in ("task_id", "approval_id"):
        value = str(event.get(key) or "")
        if value:
            return f"{key}:{value}"
    capability_id = str(event.get("capability_id") or "")
    if capability_id:
        return f"capability_id:{capability_id}"
    # Do not bucket all device/status noise under server_id (e.g. "android-server activity").
    return str(event.get("dedupe_key") or event.get("event_id") or event.get("type") or "activity")


def _activity_group_title(event: dict[str, Any]) -> str:
    if event.get("task_id"):
        return f"Task {event.get('task_id')}"
    if event.get("approval_id"):
        return "Approval lifecycle"
    if event.get("capability_id"):
        return str(event.get("capability_id"))
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
    capability_health = (
        data.get("capability_health")
        or dependencies.get("capability_health")
        or dependencies.get("capability_availability", {})
    )
    return {
        **data,
        "status": status,
        "latency_ms": _number(data.get("latency_ms", dependencies.get("latency_ms", -1)), -1),
        "last_healthy_at": data.get("last_healthy_at")
        or dependencies.get("last_healthy_at")
        or dependencies.get("last_seen")
        or data.get("health_checked_at", 0),
        "active_task_id": data.get("active_task_id", dependencies.get("active_task_id", "")),
        "permission_missing": permission_missing,
        "capability_health": _bound_for_ui(capability_health, max_depth=3, max_dict_items=40),
        "recovery_state": "attention"
        if status in {"OFFLINE", "DEGRADED", "CRITICAL"} or permission_missing
        else "stable",
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
        labels = [
            _get(step, "description", "") or _get(step, "capability_id", "") or _get(step, "name", "")
            for step in steps[:6]
        ]
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
        verification = (
            _get(step, "verification", None)
            or _get(step, "verification_result", None)
            or _get(step, "completion", None)
        )
        if verification:
            if isinstance(verification, str):
                return _truncate_text(verification, limit=360)
            status = (
                _get(verification, "status", "")
                or _get(verification, "summary", "")
                or _get(verification, "message", "")
            )
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
            keys = (
                ", ".join(str(key) for key in summary.get("keys", [])[:6])
                if isinstance(summary.get("keys"), list)
                else ""
            )
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
        "verification": _bound_for_ui(
            _get(step, "verification", None)
            or _get(step, "verification_result", None)
            or _get(step, "completion", None),
            max_depth=3,
        ),
        "completion_condition": _bound_for_ui(
            _get(step, "completion_condition", None) or _get(step, "postcondition", None), max_depth=3
        ),
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
        "message": _truncate_text(
            detail.get("error", "") or data.get("error", "") or data.get("message", ""), limit=320
        ),
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
    server_id = str(
        first("server_id", "server") or _server_from_capability_id(capability_id) or _server_from_event_type(event_type)
    )
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
    if isinstance(value, str):
        return _truncate_text(value, limit=max_string_chars)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if max_depth <= 0:
        return _truncate_text(_json_preview(value), limit=max_string_chars)
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
