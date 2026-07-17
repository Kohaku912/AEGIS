"""Read-only resource APIs for the AEGIS management UI.

This module adapts Manager-owned state to one stable EntitySummary contract.  It
does not become a second state owner: every item is read from the Runtime's
Managers, CapabilityCatalog, or their existing query APIs.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from flask import Blueprint, jsonify, request

resource_bp = Blueprint("ui_resources", __name__)

_runtime: Any = None


def init_resource_routes(app: Any, runtime: Any) -> None:
    """Register normalized UI resource routes."""
    global _runtime
    _runtime = runtime
    app.register_blueprint(resource_bp)


def _get_runtime() -> Any:
    if _runtime is not None:
        return _runtime
    from aegis_ai.runtime import get_runtime

    return get_runtime()


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {
            str(key): ("***MASKED***" if _sensitive_key(str(key)) else _jsonable(item)) for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "to_dict"):
        return _jsonable(value.to_dict())
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _sensitive_key(key: str) -> bool:
    normalized = key.strip().lower()
    return normalized in {
        "password",
        "secret",
        "token",
        "api_key",
        "cookie",
        "credential",
        "authorization",
    } or normalized.endswith(("_password", "_secret", "_token", "_api_key", "_credential"))


def _timestamp(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)):
        seconds = float(value) / 1000 if float(value) > 10_000_000_000 else float(value)
        return datetime.fromtimestamp(seconds, tz=UTC).isoformat()
    return str(value)


def _value(record: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        if record.get(key) not in (None, ""):
            return record[key]
    return default


def _summary(
    resource_type: str,
    record: Any,
    *,
    fallback_id: str = "",
    fallback_title: str = "",
) -> dict[str, Any]:
    data = _jsonable(record)
    if not isinstance(data, dict):
        data = {"value": data}
    entity_id = str(
        _value(
            data,
            f"{resource_type}_id",
            "id",
            "task_id",
            "approval_id",
            "event_id",
            "audit_id",
            "capability_id",
            "commitment_id",
            "server_id",
            default=fallback_id,
        )
    )
    title = str(
        _value(
            data,
            "title",
            "name",
            "summary",
            "message",
            "description",
            "capability_id",
            "server_id",
            default=fallback_title or entity_id or resource_type,
        )
    )
    status = str(_value(data, "status", "state", "health", "result", default="unknown"))
    risk_level = str(_value(data, "risk_level", "risk", default=""))
    updated_at = _timestamp(
        _value(data, "updated_at", "timestamp", "created_at", "last_seen", "last_heartbeat", default="")
    )
    subtitle = str(_value(data, "source", "server_id", "capability_id", "type", "category", "actor", default=""))
    return {
        "id": entity_id,
        "type": resource_type,
        "title": title,
        "subtitle": subtitle,
        "status": status,
        "severity": _severity(status, risk_level, data),
        "created_at": _timestamp(_value(data, "created_at", "timestamp", default="")),
        "updated_at": updated_at,
        "owner": str(_value(data, "owner", "actor", "source", "server_id", default="AEGIS")),
        "tags": _badges(data),
        "risk_level": risk_level,
        "related_ids": _related_ids(data),
        "badges": _badges(data),
        "relations": [
            {"type": key.removesuffix("_id"), "id": str(data[key])}
            for key in ("task_id", "approval_id", "capability_id", "server_id", "conversation_id")
            if data.get(key)
        ],
        "available_actions": _available_actions(resource_type, status),
        "permissions": ["fresh-auth"] if resource_type in {"approval", "capability"} else ["view"],
        "detail": data,
    }


def _severity(status: str, risk: str, data: dict[str, Any]) -> str:
    explicit = str(data.get("severity") or "")
    if explicit:
        return explicit
    value = f"{status} {risk}".lower()
    if any(token in value for token in ("critical", "failed", "error", "offline", "forbidden")):
        return "critical"
    if any(token in value for token in ("degraded", "warning", "pending", "approval", "high_risk")):
        return "warning"
    return "normal"


def _available_actions(resource_type: str, status: str) -> list[dict[str, str]]:
    actions = [{"id": "inspect", "label": "Inspect", "level": "view"}]
    if resource_type == "task" and status.lower() == "running":
        actions.append({"id": "pause", "label": "Pause", "level": "safe"})
    if resource_type == "task" and status.lower() in {"failed", "paused", "blocked"}:
        actions.append({"id": "retry", "label": "Preview retry", "level": "controlled"})
    if resource_type == "server":
        actions.append({"id": "refresh", "label": "Refresh health", "level": "safe"})
    if resource_type == "capability":
        actions.append({"id": "edit-policy", "label": "Review effective policy", "level": "controlled"})
    if resource_type == "approval":
        actions.append({"id": "review", "label": "Review approval", "level": "dangerous"})
    return actions


def _related_ids(data: dict[str, Any]) -> list[str]:
    keys = ("task_id", "step_id", "approval_id", "capability_id", "server_id", "request_id", "trace_id")
    return [str(data[key]) for key in keys if data.get(key) not in (None, "")]


def _badges(data: dict[str, Any]) -> list[str]:
    badges: list[str] = []
    for key in ("status", "risk_level", "source", "memory_type", "enabled"):
        value = data.get(key)
        if value not in (None, "", False):
            badges.append(str(value))
    return badges[:4]


def _safe_limit() -> int:
    try:
        return max(1, min(200, int(request.args.get("limit", 50))))
    except ValueError:
        return 50


def _filter_page(items: Iterable[dict[str, Any]]) -> dict[str, Any]:
    records = list(items)
    query = str(request.args.get("q") or request.args.get("search") or "").strip().casefold()
    status = str(request.args.get("status") or "").strip().casefold()
    if query:
        records = [item for item in records if query in json.dumps(item, ensure_ascii=False, default=str).casefold()]
    if status:
        records = [item for item in records if str(item.get("status", "")).casefold() == status]
    severity = str(request.args.get("severity") or "").strip().casefold()
    if severity:
        records = [item for item in records if str(item.get("severity", "")).casefold() == severity]
    from_ms = _time_filter("from")
    to_ms = _time_filter("to")
    if from_ms or to_ms:
        records = [item for item in records if _in_time_range(item, from_ms, to_ms)]
    sort_key = str(request.args.get("sort") or "updated_at")
    reverse = str(request.args.get("order") or "desc").lower() != "asc"
    if sort_key in {"title", "status", "updated_at", "type"}:
        records.sort(key=lambda item: str(item.get(sort_key, "")), reverse=reverse)
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    limit = _safe_limit()
    cursor = str(request.args.get("cursor") or "")
    try:
        offset = max(0, int(cursor)) if cursor else (page - 1) * limit
    except ValueError:
        offset = next((index + 1 for index, item in enumerate(records) if item.get("id") == cursor), (page - 1) * limit)
    return {
        "items": records[offset : offset + limit],
        "page": page,
        "limit": limit,
        "total": len(records),
        "has_more": offset + limit < len(records),
        "next_cursor": str(offset + limit) if offset + limit < len(records) else "",
        "generated_at": datetime.now(tz=UTC).isoformat(),
    }


def _time_filter(name: str) -> int:
    value = str(request.args.get(name) or request.args.get(f"{name}_ms") or "")
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        try:
            return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)
        except ValueError:
            return 0


def _in_time_range(item: dict[str, Any], from_ms: int, to_ms: int) -> bool:
    value = item.get("updated_at") or item.get("created_at")
    try:
        timestamp = int(datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp() * 1000)
    except (TypeError, ValueError):
        return not from_ms and not to_ms
    return (not from_ms or timestamp >= from_ms) and (not to_ms or timestamp <= to_ms)


def _tasks(rt: Any) -> list[dict[str, Any]]:
    return [_summary("task", item) for item in rt.task_manager.list_tasks(limit=500)]


def _servers(rt: Any) -> list[dict[str, Any]]:
    snapshot = _jsonable(rt.status_manager.get_snapshot())
    if isinstance(snapshot, dict) and isinstance(snapshot.get("servers"), dict):
        snapshot = snapshot["servers"]
    if not isinstance(snapshot, dict):
        return []
    return [
        _summary("server", {"server_id": server_id, **(value if isinstance(value, dict) else {"status": value})})
        for server_id, value in snapshot.items()
    ]


def _approvals(rt: Any) -> list[dict[str, Any]]:
    manager = rt.approval_manager
    queue = getattr(manager, "_queue", None)
    values = queue.get_all() if queue is not None and hasattr(queue, "get_all") else manager.list_pending()
    return [_summary("approval", item) for item in values]


def _capabilities(rt: Any) -> list[dict[str, Any]]:
    return [
        _summary("capability", item, fallback_id=getattr(item, "capability_id", ""))
        for item in rt.capability_catalog.list_all()
    ]


def _memories(rt: Any) -> list[dict[str, Any]]:
    query = str(request.args.get("q") or request.args.get("search") or "")
    memory_type = str(request.args.get("memory_type") or request.args.get("type") or "")
    types = [memory_type] if memory_type else None
    values = rt.memory_manager.search_memory(query, types=types, limit=min(200, _safe_limit() * 4))
    results = []
    for item in values:
        identity = str(item.get("id") or item.get("memory_id") or "")
        if not identity:
            digest = hashlib.sha256(
                json.dumps(item, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
            ).hexdigest()[:20]
            identity = f"memory-{digest}"
        results.append(_summary("memory", {"id": identity, **item}))
    return results


def _events(rt: Any) -> list[dict[str, Any]]:
    result = _jsonable(rt.event_manager.list_recent(limit=200, cursor=None))
    values = result.get("events", result.get("items", [])) if isinstance(result, dict) else result
    return [_summary("event", item) for item in values or []]


def _audit(rt: Any) -> list[dict[str, Any]]:
    result = _jsonable(rt.audit_manager.list_recent(limit=200, cursor=None))
    values = result.get("entries", result.get("items", [])) if isinstance(result, dict) else result
    return [_summary("audit", item) for item in values or []]


def _commitments(rt: Any) -> list[dict[str, Any]]:
    return [_summary("commitment", item) for item in rt.commitment_manager.list_commitments(status=None)]


def _notifications(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "notification_manager", None)
    values = manager.list_recent(limit=200) if manager is not None else []
    return [_summary("notification", item) for item in values]


def _people(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "memory_manager", None)
    backend = manager.get_backend("person") if manager is not None else None
    values = backend.get_all() if backend is not None and hasattr(backend, "get_all") else []
    return [_summary("person", item) for item in values]


def _settings(rt: Any) -> list[dict[str, Any]]:
    store = getattr(rt, "settings_store", None)
    data = _jsonable(store.get()) if store is not None else {}
    if not isinstance(data, dict):
        return []
    return [
        _summary(
            "setting",
            {"id": section, "title": section.replace("_", " ").title(), "status": "effective", "values": values},
        )
        for section, values in data.items()
    ]


def _hooks(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "hook_engine", None)
    values = manager.list_hooks() if manager is not None and hasattr(manager, "list_hooks") else []
    return [_summary("hook", item) for item in values]


def _delegations(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "delegation_policy", None)
    values = manager.list_rules() if manager is not None and hasattr(manager, "list_rules") else []
    return [_summary("delegation", item, fallback_id=str(item.get("rule_id", ""))) for item in values]


def _autonomy(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "autonomous_loop", None)
    status = manager.get_status() if manager is not None and hasattr(manager, "get_status") else {"status": "disabled"}
    return [_summary("autonomy", {"id": "autonomous-loop", "title": "Autonomous Loop", **_jsonable(status)})]


def _sleep(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "sleep_manager", None)
    status = (
        manager.get_status() if manager is not None and hasattr(manager, "get_status") else {"status": "unavailable"}
    )
    return [
        _summary("sleep", {"id": "memory-consolidation", "title": "Memory Consolidation & Sleep", **_jsonable(status)})
    ]


def _user_models(rt: Any) -> list[dict[str, Any]]:
    store = getattr(rt, "user_model_store", None)
    model = store.get() if store is not None and hasattr(store, "get") else {}
    return [
        _summary(
            "user_model",
            {"id": "primary-user", "title": "Primary User Model", "status": "effective", **(_jsonable(model) or {})},
        )
    ]


def _situations(rt: Any) -> list[dict[str, Any]]:
    model = getattr(rt, "situation_model", None)
    state = model.get_state() if model is not None and hasattr(model, "get_state") else {}
    return [
        _summary(
            "situation", {"id": "current-situation", "title": "Current User Situation", **(_jsonable(state) or {})}
        )
    ]


def _prompts(rt: Any) -> list[dict[str, Any]]:
    registry = getattr(rt, "prompt_registry", None)
    values = registry.list_prompts() if registry is not None and hasattr(registry, "list_prompts") else []
    return [_summary("prompt", item) for item in values]


def _devices(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "android_manager", None)
    values: list[Any] = []
    if manager is not None and hasattr(manager, "get_status"):
        values.append({"id": "android-primary", "title": "Android Companion", **_jsonable(manager.get_status())})
    for server in _servers(rt):
        detail = server.get("detail", {})
        if isinstance(detail, dict) and detail.get("device_model"):
            values.append(detail)
    return [_summary("device", item) for item in values]


def _conversations(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "session_manager", None)
    values = manager.list_sessions() if manager is not None and hasattr(manager, "list_sessions") else []
    return [_summary("conversation", item) for item in values]


def _presentations(rt: Any) -> list[dict[str, Any]]:
    manager = getattr(rt, "presentation_manager", None)
    values = manager.list_summaries(limit=200) if manager is not None and hasattr(manager, "list_summaries") else []
    return [_summary("presentation", item) for item in values]


_LOADERS: dict[str, Callable[[Any], list[dict[str, Any]]]] = {
    "tasks": _tasks,
    "servers": _servers,
    "approvals": _approvals,
    "capabilities": _capabilities,
    "memories": _memories,
    "events": _events,
    "audit": _audit,
    "commitments": _commitments,
    "notifications": _notifications,
    "people": _people,
    "settings": _settings,
    "hooks": _hooks,
    "delegations": _delegations,
    "autonomy": _autonomy,
    "sleep": _sleep,
    "user-models": _user_models,
    "situations": _situations,
    "prompts": _prompts,
    "devices": _devices,
    "conversations": _conversations,
    "presentations": _presentations,
}


@resource_bp.get("/api/ui/entities")
def list_entities():
    """List normalized entities from one Manager-owned resource."""
    resource = str(request.args.get("resource") or "tasks").lower()
    loader = _LOADERS.get(resource)
    if loader is None:
        return jsonify({"error": "unsupported_resource", "supported": sorted(_LOADERS)}), 400
    try:
        return jsonify(_filter_page(loader(_get_runtime())))
    except Exception as exc:
        return jsonify({"error": "resource_unavailable", "message": str(exc), "items": []}), 503


@resource_bp.get("/api/ui/entities/<resource>/<entity_id>")
def get_entity(resource: str, entity_id: str):
    loader = _LOADERS.get(resource.lower())
    if loader is None:
        return jsonify({"error": "unsupported_resource"}), 400
    try:
        item = next((entry for entry in loader(_get_runtime()) if entry["id"] == entity_id), None)
        if item is None:
            return jsonify({"error": "not_found"}), 404
        return jsonify(item)
    except Exception as exc:
        return jsonify({"error": "resource_unavailable", "message": str(exc)}), 503


@resource_bp.get("/api/ui/search")
def global_search():
    """Search Manager-backed entities without exposing internal storage files."""
    query = str(request.args.get("q") or "").strip()
    if not query:
        return jsonify({"items": [], "total": 0, "generated_at": datetime.now(tz=UTC).isoformat()})
    results: list[dict[str, Any]] = []
    rt = _get_runtime()
    for resource, loader in _LOADERS.items():
        try:
            for item in loader(rt):
                if query.casefold() in json.dumps(item, ensure_ascii=False, default=str).casefold():
                    results.append(item)
        except Exception:
            continue
    return jsonify(_filter_page(results))


@resource_bp.get("/api/memories")
def list_memories():
    """Stable plural memory listing used by the Intelligence UI."""
    try:
        return jsonify(_filter_page(_memories(_get_runtime())))
    except Exception as exc:
        return jsonify({"error": "memory_unavailable", "message": str(exc), "items": []}), 503


@resource_bp.get("/api/approvals")
def list_approvals():
    """Return the complete persisted approval lifecycle, not pending only."""
    try:
        return jsonify(_filter_page(_approvals(_get_runtime())))
    except Exception as exc:
        return jsonify({"error": "approval_unavailable", "message": str(exc), "items": []}), 503


@resource_bp.get("/api/capabilities")
def list_capabilities():
    return jsonify(_filter_page(_capabilities(_get_runtime())))


@resource_bp.get("/api/capabilities/<path:capability_id>")
def capability_detail(capability_id: str):
    detail = _get_runtime().capability_catalog.describe(capability_id)
    if detail is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify(_summary("capability", detail, fallback_id=capability_id))


@resource_bp.get("/api/memories/<memory_id>")
def memory_detail(memory_id: str):
    rt = _get_runtime()
    direct = rt.memory_manager.get_memory(memory_id) if hasattr(rt.memory_manager, "get_memory") else None
    item = (
        _summary("memory", direct)
        if direct
        else next((value for value in _memories(rt) if value["id"] == memory_id), None)
    )
    return jsonify(item) if item else (jsonify({"error": "not_found"}), 404)


@resource_bp.patch("/api/memories/<memory_id>")
def update_memory(memory_id: str):
    payload = request.get_json(silent=True) or {}
    patch = payload.get("patch") if isinstance(payload.get("patch"), dict) else payload
    rt = _get_runtime()
    updated = rt.memory_manager.update_memory(memory_id, patch)
    if updated is None:
        return jsonify(
            {"error": "memory_not_editable", "message": "Only stable MemoryStore records can be edited."}
        ), 409
    _audit_resource_change(rt, "memory.updated", memory_id, {"changed_fields": sorted(patch)})
    return jsonify(_summary("memory", updated))


@resource_bp.delete("/api/memories/<memory_id>")
def forget_memory(memory_id: str):
    rt = _get_runtime()
    forgotten = rt.memory_manager.forget(memory_id)
    if not forgotten:
        return jsonify({"error": "memory_not_editable", "message": "The owning backend did not confirm removal."}), 409
    _audit_resource_change(rt, "memory.forgotten", memory_id, {"forgotten": True})
    return jsonify({"forgotten": True, "memory_id": memory_id})


@resource_bp.get("/api/servers/<server_id>")
def server_detail(server_id: str):
    item = next((value for value in _servers(_get_runtime()) if value["id"] == server_id), None)
    return jsonify(item) if item else (jsonify({"error": "not_found"}), 404)


@resource_bp.get("/api/llm/requests")
def llm_requests():
    from aegis_ai.observability.llm_usage.service import LLMUsageService

    rt = _get_runtime()
    service = LLMUsageService(
        audit_manager=getattr(rt, "audit_manager", None) or getattr(rt, "audit_log", None),
        prompt_registry=getattr(rt, "prompt_registry", None),
    )
    traces = [
        _summary("llm_request", trace)
        for trace in service.get_traces(period=request.args.get("period", "24h"), limit=500)
    ]
    return jsonify(_filter_page(traces))


@resource_bp.post("/api/policy/simulate")
def simulate_policy():
    """Evaluate the effective policy without invoking the capability."""
    rt = _get_runtime()
    payload = request.get_json(silent=True) or {}
    capability_id = str(payload.get("capability_id") or "").strip()
    context = str(payload.get("context") or "tool_invocation").strip().lower()
    params = payload.get("arguments") if isinstance(payload.get("arguments"), dict) else {}
    if not capability_id:
        return jsonify({"error": "capability_id_required"}), 400
    manifest = rt.capability_catalog.resolve(capability_id)
    if manifest is None:
        return jsonify({"error": "capability_not_found"}), 404
    capability = rt.tool_registry.get_capability(manifest.capability_id)
    if capability is None:
        return jsonify(
            {
                "simulation": {
                    "capability_id": manifest.capability_id,
                    "decision": "DENY",
                    "reason": "The effective capability is disabled, forbidden, or unavailable in ToolRegistry.",
                    "effective_risk": str(manifest.risk_level),
                    "requires_approval": bool(manifest.requires_approval),
                    "fresh_auth_required": True,
                    "matching_rule": "Capability availability gate",
                    "context": context,
                    "executed": False,
                }
            }
        )
    evaluators = {
        "tool_invocation": rt.policy_engine.evaluate_tool_invocation,
        "event_trigger": rt.policy_engine.evaluate_event_trigger,
        "autonomous_task": rt.policy_engine.evaluate_autonomous_task,
    }
    evaluator = evaluators.get(context)
    if evaluator is None:
        return jsonify({"error": "unsupported_context", "supported": sorted(evaluators)}), 400
    result = evaluator(capability, params)
    approval_type = getattr(result.required_approval_type, "name", None)
    return jsonify(
        {
            "simulation": {
                "capability_id": result.capability_id or manifest.capability_id,
                "decision": result.decision.name,
                "reason": result.reason,
                "effective_risk": result.risk_level.name,
                "requires_approval": result.decision.name == "ASK_APPROVAL",
                "fresh_auth_required": result.risk_level.name in {"APPROVAL_REQUIRED", "HIGH_RISK", "FORBIDDEN"},
                "matching_rule": "PolicyEngine deterministic effective-policy evaluation",
                "required_approval_type": approval_type,
                "approval_expires_at_ms": result.expires_at_ms or None,
                "audit_required": bool(result.audit_required),
                "context": context,
                "arguments": _jsonable(params),
                "target": _jsonable(payload.get("target")),
                "environment": _jsonable(payload.get("environment")),
                "executed": False,
            }
        }
    )


@resource_bp.post("/api/tasks/<task_id>/actions")
def task_action(task_id: str):
    """Preview task mutations; only the explicitly safe pause action executes here."""
    rt = _get_runtime()
    task = rt.task_manager.get_task(task_id)
    if task is None:
        return jsonify({"error": "not_found"}), 404
    payload = request.get_json(silent=True) or {}
    action = str(payload.get("action") or "inspect")
    levels = {
        "inspect": "view",
        "pause": "safe",
        "resume": "controlled",
        "retry": "controlled",
        "cancel": "dangerous",
        "skip-step": "dangerous",
        "archive": "controlled",
    }
    level = levels.get(action)
    if level is None:
        return jsonify({"error": "unsupported_action"}), 400
    preview = _action_preview("task", task_id, action, level, task)
    if not bool(payload.get("confirmed")) or level in {"controlled", "dangerous"}:
        preview["requires_confirmation"] = level != "view"
        preview["requires_approval"] = level == "dangerous"
        preview["requires_fresh_auth"] = level in {"controlled", "dangerous"}
        return jsonify({"preview": preview}), 202 if level != "view" else 200
    result = rt.task_manager.pause_task(task_id) if action == "pause" else task
    return jsonify({"result": result, "preview": preview})


@resource_bp.post("/api/servers/<server_id>/actions")
def server_action(server_id: str):
    payload = request.get_json(silent=True) or {}
    action = str(payload.get("action") or "refresh")
    if action != "refresh":
        return jsonify(
            {"preview": _action_preview("server", server_id, action, "controlled", {}), "requires_fresh_auth": True}
        ), 202
    snapshot = _get_runtime().status_manager.check_now()
    return jsonify({"result": snapshot.get(server_id), "verified": server_id in snapshot})


@resource_bp.patch("/api/hooks/<hook_id>")
def update_hook(hook_id: str):
    """Preview and persist a HookEngine rule through its owning Manager."""
    rt = _get_runtime()
    manager = getattr(rt, "hook_engine", None)
    if manager is None:
        return jsonify({"error": "hook_engine_unavailable"}), 503
    payload = request.get_json(silent=True) or {}
    patch = dict(payload.get("patch") or {})
    patch["hook_id"] = hook_id
    before = manager.get_hook(hook_id) if hasattr(manager, "get_hook") else None
    preview = _mutation_preview("hook", hook_id, before, patch)
    if not bool(payload.get("confirmed")):
        return jsonify({"preview": preview, "requires_confirmation": True, "requires_fresh_auth": True}), 202
    updated = manager.upsert_hook(patch)
    return jsonify({"result": _summary("hook", updated), "preview": preview, "verified": True})


@resource_bp.patch("/api/delegations/<rule_id>")
def update_delegation(rule_id: str):
    """Preview and persist a restrictive DelegationPolicyStore rule."""
    rt = _get_runtime()
    manager = getattr(rt, "delegation_policy", None)
    if manager is None:
        return jsonify({"error": "delegation_policy_unavailable"}), 503
    payload = request.get_json(silent=True) or {}
    patch = dict(payload.get("patch") or {})
    patch["rule_id"] = rule_id
    before = next((item for item in manager.list_rules() if item.get("rule_id") == rule_id), None)
    preview = _mutation_preview("delegation", rule_id, before, patch)
    if not bool(payload.get("confirmed")):
        return jsonify({"preview": preview, "requires_confirmation": True, "requires_fresh_auth": True}), 202
    updated = manager.upsert_rule(patch)
    return jsonify(
        {"result": _summary("delegation", updated, fallback_id=rule_id), "preview": preview, "verified": True}
    )


def _action_preview(resource: str, entity_id: str, action: str, level: str, current: dict[str, Any]) -> dict[str, Any]:
    return {
        "target": {"type": resource, "id": entity_id, "current_status": current.get("status", "unknown")},
        "change": action,
        "impact": "State transition is recorded by the owning Manager.",
        "risk": level,
        "rollback": "Available only when the owning Manager supports the reverse transition.",
        "verification": "Re-read the Manager entity and related Audit/Event records after execution.",
    }


def _mutation_preview(resource: str, entity_id: str, before: Any, patch: dict[str, Any]) -> dict[str, Any]:
    return {
        "target": {"type": resource, "id": entity_id},
        "change": {"fields": sorted(patch), "before": _jsonable(before), "after": _jsonable(patch)},
        "impact": f"The owning {resource} Manager will persist and immediately apply this rule.",
        "risk": "controlled",
        "rollback": "Restore the previous field values through the same reviewed editor.",
        "verification": f"Re-read the {resource} resource and inspect its Manager audit event.",
    }


def _audit_resource_change(rt: Any, action: str, resource_id: str, detail: dict[str, Any]) -> None:
    audit = getattr(rt, "audit_log", None)
    if audit is None or not hasattr(audit, "log_decision"):
        return
    audit.log_decision(
        action,
        resource_id,
        "ALLOW",
        actor="dashboard",
        reason="Fresh-authenticated management action",
        detail=detail,
    )


@resource_bp.post("/api/ui/control-actions")
def control_action():
    """Preview and execute the small set of master control-plane actions."""
    rt = _get_runtime()
    payload = request.get_json(silent=True) or {}
    action = str(payload.get("action") or "")
    definitions = {
        "refresh-all-servers": (
            "safe",
            "Refresh every registered server health check",
            "StatusManager snapshot refresh",
        ),
        "pause-autonomy": (
            "controlled",
            "Stop autonomous scheduling",
            "AutonomousLoop remains stopped until explicitly started",
        ),
        "pause-all-tasks": (
            "controlled",
            "Pause all running tasks",
            "Running TaskManager records transition to paused",
        ),
        "emergency-stop": ("safe", "Activate the global emergency stop", "New execution is interrupted until cleared"),
    }
    definition = definitions.get(action)
    if definition is None:
        return jsonify({"error": "unsupported_action"}), 400
    risk, change, impact = definition
    preview = {
        "target": "AEGIS Runtime",
        "change": change,
        "impact": impact,
        "risk": risk,
        "rollback": "Use the corresponding resume or clear action after reviewing system state.",
        "verification": "Re-read Runtime Manager state and confirm related Audit/Event records.",
    }
    if not bool(payload.get("confirmed")):
        return jsonify(
            {
                "preview": preview,
                "requires_confirmation": True,
                "requires_fresh_auth": True,
                "requires_approval": risk == "dangerous",
            }
        ), 202
    if action == "refresh-all-servers":
        result = rt.status_manager.check_now()
    elif action == "pause-autonomy":
        if rt.autonomous_loop is not None:
            rt.autonomous_loop.stop()
        result = {"paused": True}
    elif action == "pause-all-tasks":
        paused = [rt.task_manager.pause_task(task["task_id"]) for task in rt.task_manager.list_running()]
        result = {"paused_tasks": [item for item in paused if item]}
    else:
        result = rt.interruption_controller.set_emergency_stop(True)
    audit = getattr(rt, "audit_log", None)
    if audit is not None and hasattr(audit, "log_decision"):
        audit.log_decision(
            "ui.control_action",
            action,
            "ALLOW",
            reason=change,
            actor="dashboard",
            detail={"preview": preview, "result": _jsonable(result)},
        )
    return jsonify({"result": _jsonable(result), "preview": preview, "verified": True})
