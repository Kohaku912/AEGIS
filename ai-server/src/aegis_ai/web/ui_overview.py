"""Normalized UI overview for Web, Android, and display surfaces."""

from __future__ import annotations

import time
from dataclasses import asdict, is_dataclass
from typing import Any


def build_ui_overview(runtime: Any) -> dict[str, Any]:
    """Build the v2 UI overview from runtime managers.

    UI surfaces must not read audit files, chat history files, settings files, or
    memory internals directly. This projection keeps that boundary in one place.
    """

    generated_at = _now_ms()
    sections = {
        "core": _section("core", lambda: _core(runtime), generated_at),
        "attention": _section("attention", lambda: _attention(runtime), generated_at),
        "current_task": _section("current_task", lambda: _current_task(runtime), generated_at),
        "servers": _section("servers", lambda: _servers(runtime), generated_at),
        "user_state": _section("user_state", lambda: _user_state(runtime), generated_at),
        "mind_summary": _section("mind_summary", lambda: _mind_summary(runtime), generated_at),
        "notifications": _section("notifications", lambda: _notifications(runtime), generated_at),
        "approvals": _section("approvals", lambda: _approvals(runtime), generated_at),
        "commitments": _section("commitments", lambda: _commitments(runtime), generated_at),
        "usage": _section("usage", lambda: _usage(runtime), generated_at),
        "freshness": _section("freshness", lambda: _freshness(runtime), generated_at),
    }
    return {"schema_version": "ui-overview.v2", "generated_at": generated_at, **sections}


def normalize_ui_event(event: Any) -> dict[str, Any]:
    """Convert an internal event into the compact SSE/gRPC UI event format."""

    event_type = str(getattr(event, "event_type", "") or _get(event, "event_type", "event"))
    timestamp = int(getattr(event, "timestamp", 0) or _get(event, "timestamp", _now_ms()))
    payload = getattr(event, "payload", None)
    if payload is None:
        payload = _get(event, "payload", {})
    return {
        "type": _ui_event_type(event_type),
        "source_type": event_type,
        "generated_at": _now_ms(),
        "source_updated_at": timestamp,
        "payload": _to_plain(payload),
    }


def _section(name: str, build, generated_at: int) -> dict[str, Any]:
    try:
        data = _to_plain(build())
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
    snapshot = _status_snapshot(runtime)
    offline = [sid for sid, item in snapshot.items() if str(item.get("status", "")).lower() in {"offline", "unknown"}]
    degraded = [sid for sid, item in snapshot.items() if str(item.get("status", "")).lower() == "degraded"]
    pending_approvals = len(_pending_approvals(runtime))
    active_tasks = _running_tasks(runtime)
    mode = "WAITING" if pending_approvals else "EXECUTING" if active_tasks else "IDLE"
    health = "DEGRADED" if degraded else "OFFLINE" if offline and len(offline) >= len(snapshot or offline) else "ONLINE"
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
            "current_action": "",
            "next_action": "",
            "blocked_reason": "",
            "steps": [],
        }
    steps = _get(task, "steps", []) or []
    current_step = next((s for s in steps if _get(s, "status", "") in {"running", "needs_approval"}), None)
    return {
        "task_id": _get(task, "task_id", ""),
        "title": _get(task, "title", "") or _get(task, "goal", "") or "Task",
        "phase": _get(task, "status", ""),
        "current_action": _get(current_step, "description", "") if current_step else "",
        "next_action": _get(task, "next_action", ""),
        "blocked_reason": _get(task, "blocked_reason", ""),
        "capability_id": _get(current_step, "capability_id", "") if current_step else "",
        "started_at": _get(task, "created_at", 0),
        "updated_at": _get(task, "updated_at", 0),
        "steps": steps[:12],
    }


def _servers(runtime: Any) -> dict[str, Any]:
    return {"items": _server_list(runtime)}


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
        return tracker.get_summary()
    if tracker is not None and hasattr(tracker, "summary"):
        return tracker.summary()
    return {"summary": "LLM usage is available from the LLM Usage service.", "input_tokens": 0, "output_tokens": 0}


def _freshness(runtime: Any) -> dict[str, Any]:
    now = _now_ms()
    snapshot = _status_snapshot(runtime)
    oldest = now
    for item in snapshot.values():
        checked = int(item.get("last_checked", 0) or item.get("updated_at", 0) or now)
        oldest = min(oldest, checked)
    return {"live": True, "oldest_source_updated_at": oldest, "age_ms": max(0, now - oldest)}


def _server_list(runtime: Any) -> list[dict[str, Any]]:
    try:
        from aegis_ai.web.dashboard_routes import _runtime_server_status

        return list(_runtime_server_status(runtime=runtime).get("servers", []))
    except Exception:
        snapshot = _status_snapshot(runtime)
        return [
            {
                "server_id": server_id,
                "status": str(item.get("status", "unknown")).upper(),
                "status_detail": item.get("error", ""),
                "health_checked_at": item.get("updated_at", _now_ms()),
            }
            for server_id, item in snapshot.items()
        ]


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


def _approval_projection(approval: Any) -> dict[str, Any]:
    data = approval.to_dict() if hasattr(approval, "to_dict") else _to_plain(approval)
    return {
        "approval_id": data.get("approval_id", ""),
        "request_id": data.get("request_id", ""),
        "task_id": data.get("task_id", ""),
        "step_id": data.get("step_id", ""),
        "capability_id": data.get("capability_id", ""),
        "tool_name": data.get("tool_name", ""),
        "risk": data.get("risk_level", ""),
        "reason": data.get("approval_reason", ""),
        "summary": data.get("user_facing_summary", "") or data.get("arguments_summary", ""),
        "target": data.get("metadata", {}).get("target", ""),
        "preview": data.get("arguments_summary", ""),
        "created_at": data.get("created_at", 0),
        "expires_at": data.get("expires_at", 0),
        "status": data.get("status", "pending"),
    }


def _ui_event_type(event_type: str) -> str:
    mapping = {
        "status.changed": "status.changed",
        "task.created": "task.updated",
        "task.updated": "task.updated",
        "task.completed": "task.updated",
        "task.failed": "task.updated",
        "approval.created": "approval.created",
        "approval.approved": "approval.resolved",
        "approval.rejected": "approval.resolved",
        "approval.expired": "approval.resolved",
        "notification.sent": "notification.created",
        "android.permission.changed": "permission.changed",
        "android.connected": "connection.changed",
        "android.disconnected": "connection.changed",
    }
    return mapping.get(event_type, "activity.updated")


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


def _get(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _now_ms() -> int:
    return int(time.time() * 1000)
