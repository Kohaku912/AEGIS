"""Surface presentation contract for multi-device UI rendering.

This module is intentionally a projection layer. It does not decide whether an
operation is safe and it does not execute actions; PolicyEngine, ApprovalManager,
and the capability execution path keep those responsibilities. The goal here is
to turn runtime events into one shared, privacy-aware presentation event shape
that each surface can render differently.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


SURFACE_IDS = (
    "dedicated_display",
    "web_dashboard",
    "mobile_app",
    "pc_overlay",
    "android_notification",
    "room_display",
    "developer_console",
    "smart_glasses",
)


@dataclass(frozen=True)
class SurfaceRole:
    surface_id: str
    role: str
    interactive: bool
    privacy_levels: list[str]
    priorities: list[str]
    max_text_chars: int
    max_display_ms: int
    actions: list[str]
    scenes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "role": self.role,
            "interactive": self.interactive,
            "privacy_levels": self.privacy_levels,
            "priorities": self.priorities,
            "max_text_chars": self.max_text_chars,
            "max_display_ms": self.max_display_ms,
            "actions": self.actions,
            "scenes": self.scenes,
        }


@dataclass(frozen=True)
class PresentationEvent:
    event_id: str
    scene_type: str
    priority: str
    severity: str
    source: str
    title: str
    summary: str
    detail: str = ""
    affected_entities: list[str] = field(default_factory=list)
    task_id: str = ""
    approval_id: str = ""
    persistence: str = "ephemeral"
    expires_at: int = 0
    privacy_class: str = "normal"
    recommended_surfaces: list[str] = field(default_factory=list)
    visual_hint: dict[str, Any] = field(default_factory=dict)
    available_actions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "scene_type": self.scene_type,
            "priority": self.priority,
            "severity": self.severity,
            "source": self.source,
            "title": self.title,
            "summary": self.summary,
            "detail": self.detail,
            "affected_entities": self.affected_entities,
            "task_id": self.task_id,
            "approval_id": self.approval_id,
            "persistence": self.persistence,
            "expires_at": self.expires_at,
            "privacy_class": self.privacy_class,
            "recommended_surfaces": self.recommended_surfaces,
            "visual_hint": self.visual_hint,
            "available_actions": self.available_actions,
        }


SURFACE_ROLES: dict[str, SurfaceRole] = {
    "dedicated_display": SurfaceRole(
        surface_id="dedicated_display",
        role="Read-only spatial state display for current operation, attention, and recovery.",
        interactive=False,
        privacy_levels=["public", "normal", "redacted"],
        priorities=["P0", "P1", "P2", "P3"],
        max_text_chars=420,
        max_display_ms=0,
        actions=[],
        scenes=["idle", "observing", "planning", "executing", "approval", "critical", "recovery", "complete"],
    ),
    "web_dashboard": SurfaceRole(
        surface_id="web_dashboard",
        role="Master board for management, investigation, approval, settings, replay, and recovery.",
        interactive=True,
        privacy_levels=["public", "normal", "sensitive", "developer"],
        priorities=["P0", "P1", "P2", "P3"],
        max_text_chars=8_000,
        max_display_ms=0,
        actions=["open_task", "open_approval", "approve", "reject", "dismiss", "recover", "open_replay"],
        scenes=["command", "work", "approval", "systems", "memory", "activity", "settings"],
    ),
    "mobile_app": SurfaceRole(
        surface_id="mobile_app",
        role="Portable chat, approval, urgent attention, task status, and device permissions.",
        interactive=True,
        privacy_levels=["public", "normal", "redacted"],
        priorities=["P0", "P1", "P2"],
        max_text_chars=1_200,
        max_display_ms=0,
        actions=["open_chat", "open_task", "open_approval", "approve", "reject", "open_device"],
        scenes=["home", "chat", "approval", "task", "devices", "permissions"],
    ),
    "pc_overlay": SurfaceRole(
        surface_id="pc_overlay",
        role="Minimal PC-local status strip, operation progress, approval warning, or error hint.",
        interactive=True,
        privacy_levels=["public", "normal"],
        priorities=["P0", "P1", "P2"],
        max_text_chars=240,
        max_display_ms=12_000,
        actions=["pause", "open_dashboard", "approve_related_pc_action", "reject_related_pc_action"],
        scenes=["status_strip", "pc_operation", "approval", "warning", "critical"],
    ),
    "android_notification": SurfaceRole(
        surface_id="android_notification",
        role="Notification entry point for approval, critical, important, and ambient mobile updates.",
        interactive=True,
        privacy_levels=["public", "normal", "redacted"],
        priorities=["P0", "P1", "P2", "P3"],
        max_text_chars=280,
        max_display_ms=0,
        actions=["open_mobile_app", "open_approval", "open_task"],
        scenes=["notification", "heads_up", "full_screen"],
    ),
    "room_display": SurfaceRole(
        surface_id="room_display",
        role="Privacy-safe room context, schedule, environment, and critical ambient alerts.",
        interactive=False,
        privacy_levels=["public", "redacted"],
        priorities=["P0", "P3"],
        max_text_chars=360,
        max_display_ms=0,
        actions=[],
        scenes=["context_horizon", "room_alert", "ambient"],
    ),
    "developer_console": SurfaceRole(
        surface_id="developer_console",
        role="Precise internal state, raw overview, event stream, latency, prompts, policy, and stack traces.",
        interactive=True,
        privacy_levels=["public", "normal", "sensitive", "developer"],
        priorities=["P0", "P1", "P2", "P3"],
        max_text_chars=32_000,
        max_display_ms=0,
        actions=["open_raw_event", "open_audit", "open_trace", "open_policy", "open_replay"],
        scenes=["event_stream", "raw_overview", "replay", "diagnostics"],
    ),
    "smart_glasses": SurfaceRole(
        surface_id="smart_glasses",
        role="Future short-lived peripheral hints for reality-adjacent actions only.",
        interactive=True,
        privacy_levels=["public", "redacted"],
        priorities=["P0", "P1"],
        max_text_chars=120,
        max_display_ms=5_000,
        actions=["open_mobile_app"],
        scenes=["edge_hint", "caption", "short_approval"],
    ),
}


def surface_roles() -> list[dict[str, Any]]:
    """Return all surface role definitions as JSON-safe dicts."""

    return [SURFACE_ROLES[surface_id].to_dict() for surface_id in SURFACE_IDS if surface_id in SURFACE_ROLES]


def presentation_event_from_ui_event(event: dict[str, Any]) -> dict[str, Any]:
    """Project a normalized UI event to the multi-device PresentationEvent shape."""

    priority = str(event.get("priority") or "P3")
    severity = str(event.get("severity") or "info")
    event_type = str(event.get("type") or event.get("event_type") or "event")
    visual_hint = event.get("visual_hint") if isinstance(event.get("visual_hint"), dict) else {}
    approval_id = str(event.get("approval_id") or "")
    task_id = str(event.get("task_id") or "")
    scene_type = _scene_type(event_type, priority, severity, approval_id, visual_hint)
    source = _source_for_event(event_type, event)
    affected_entities = _affected_entities(event)
    recommended = _recommended_surfaces(event_type, priority, severity, event, scene_type)
    presentation_event = PresentationEvent(
        event_id=str(event.get("event_id") or event.get("dedupe_key") or f"{event_type}:{int(time.time() * 1000)}"),
        scene_type=scene_type,
        priority=priority,
        severity=severity,
        source=source,
        title=str(event.get("safe_title") or event.get("title") or event_type),
        summary=str(event.get("safe_message") or event.get("message") or event_type),
        detail=_detail_for_event(event),
        affected_entities=affected_entities,
        task_id=task_id,
        approval_id=approval_id,
        persistence=str(event.get("persistence") or _persistence_for_priority(priority)),
        expires_at=int(event.get("expires_at") or 0),
        privacy_class=_privacy_class(event),
        recommended_surfaces=recommended,
        visual_hint=dict(visual_hint),
        available_actions=_available_actions(event, recommended),
    )
    return presentation_event.to_dict()


def presentation_event_from_presentation(item: dict[str, Any]) -> dict[str, Any]:
    """Project a stored PresentationSpec summary to PresentationEvent."""

    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
    delivery = item.get("delivery") if isinstance(item.get("delivery"), dict) else {}
    targets = [str(value) for value in delivery.get("targets", []) if str(value)]
    priority = _priority_from_importance(str(item.get("importance") or item.get("priority") or "normal"))
    scene_type = str(metadata.get("scene_type") or _scene_from_modality(str(item.get("modality") or "")))
    return PresentationEvent(
        event_id=str(item.get("presentation_id") or item.get("id") or ""),
        scene_type=scene_type,
        priority=priority,
        severity=_severity_from_priority(priority),
        source=str(item.get("source") or "presentation_manager"),
        title=str(item.get("title") or "Presentation"),
        summary=str(item.get("summary") or ""),
        detail=str(metadata.get("detail") or ""),
        affected_entities=[str(value) for value in metadata.get("affected_entities", [])] if isinstance(metadata.get("affected_entities"), list) else [],
        task_id=str(metadata.get("task_id") or ""),
        approval_id=str(metadata.get("approval_id") or ""),
        persistence="until_resolved" if item.get("ttl_seconds") in (0, "0", None, "") else "attention_dock",
        expires_at=int(item.get("expires_at") or item.get("expires_at_ms") or 0),
        privacy_class=str(metadata.get("privacy_class") or "normal"),
        recommended_surfaces=_normalize_targets(targets) or ["web_dashboard", "dedicated_display"],
        visual_hint=dict(metadata.get("visual_hint") or {}),
        available_actions=[],
    ).to_dict()


def _scene_type(event_type: str, priority: str, severity: str, approval_id: str, visual_hint: dict[str, Any]) -> str:
    effect = str(visual_hint.get("effect") or "")
    status = event_type.lower()
    if approval_id or "approval.created" in status:
        return "approval"
    if priority == "P0" or severity == "critical" or effect == "fracture":
        return "critical"
    if effect == "recovery" or "recovered" in status:
        return "recovery"
    if "tool.execution.started" in status or "task.updated" in status:
        return "executing"
    if "observation" in status or "status.changed" in status or "connection.changed" in status:
        return "observing"
    if "planning" in status:
        return "planning"
    if "completed" in status:
        return "complete"
    return "idle"


def _source_for_event(event_type: str, event: dict[str, Any]) -> str:
    if event.get("server_id"):
        return str(event["server_id"])
    if event.get("capability_id"):
        return str(event["capability_id"]).split(".", 1)[0]
    if event_type.startswith("approval."):
        return "approval_manager"
    if event_type.startswith("task."):
        return "task_manager"
    if event_type.startswith("presentation."):
        return "presentation_manager"
    return str(event.get("source_type") or event_type)


def _affected_entities(event: dict[str, Any]) -> list[str]:
    entities: list[str] = []
    for key in ("server_id", "capability_id", "task_id", "approval_id"):
        value = str(event.get(key) or "")
        if value and value not in entities:
            entities.append(value)
    for key in ("affected_servers", "affected_capabilities"):
        values = event.get(key)
        if isinstance(values, list):
            for value in values:
                text = str(value)
                if text and text not in entities:
                    entities.append(text)
    return entities[:12]


def _recommended_surfaces(
    event_type: str,
    priority: str,
    severity: str,
    event: dict[str, Any],
    scene_type: str,
) -> list[str]:
    capability_id = str(event.get("capability_id") or "")
    server_id = str(event.get("server_id") or "")
    surfaces = ["web_dashboard", "developer_console"]
    if priority in {"P0", "P1"}:
        surfaces.extend(["dedicated_display", "mobile_app", "android_notification"])
    elif priority == "P2":
        surfaces.extend(["dedicated_display", "mobile_app"])
    else:
        surfaces.append("dedicated_display")
    if scene_type == "approval":
        surfaces.extend(["mobile_app", "android_notification"])
    if capability_id.startswith("pc-server.") or server_id == "pc-server":
        if priority in {"P0", "P1", "P2"}:
            surfaces.append("pc_overlay")
    if priority == "P0" and not _privacy_class(event) == "sensitive":
        surfaces.append("room_display")
    return _dedupe_surfaces(surfaces)


def _available_actions(event: dict[str, Any], surfaces: list[str]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    approval_id = str(event.get("approval_id") or "")
    task_id = str(event.get("task_id") or "")
    if task_id:
        actions.append({"id": "open_task", "label": "Open task", "surface": "web_dashboard", "target_id": task_id})
    if approval_id:
        actions.append({"id": "open_approval", "label": "Open approval", "surface": "web_dashboard", "target_id": approval_id})
        if "mobile_app" in surfaces:
            actions.append({"id": "open_mobile_approval", "label": "Open on mobile", "surface": "mobile_app", "target_id": approval_id})
    if str(event.get("priority") or "") == "P0":
        actions.append({"id": "open_diagnostics", "label": "Open diagnostics", "surface": "developer_console"})
    return actions


def _detail_for_event(event: dict[str, Any]) -> str:
    detail = event.get("detail") or event.get("status") or ""
    if detail:
        return str(detail)
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    for key in ("error", "reason", "recovery_hint", "status_detail"):
        if payload.get(key):
            return str(payload[key])
    return ""


def _privacy_class(event: dict[str, Any]) -> str:
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    value = str(event.get("privacy_class") or payload.get("privacy_class") or "").lower()
    if value in {"public", "normal", "sensitive", "developer", "redacted"}:
        return value
    if event.get("approval_id") or "args" in payload or "arguments" in payload:
        return "sensitive"
    return "normal"


def _persistence_for_priority(priority: str) -> str:
    if priority in {"P0", "P1"}:
        return "until_resolved"
    if priority == "P2":
        return "attention_dock"
    return "ephemeral"


def _priority_from_importance(importance: str) -> str:
    value = importance.lower()
    if value in {"critical", "urgent"}:
        return "P0"
    if value == "high":
        return "P2"
    return "P3"


def _severity_from_priority(priority: str) -> str:
    if priority == "P0":
        return "critical"
    if priority in {"P1", "P2"}:
        return "warning"
    return "info"


def _scene_from_modality(modality: str) -> str:
    value = modality.lower()
    if value in {"hud", "overlay_short"}:
        return "executing"
    if value in {"chart_panel", "diagram_panel", "gltf_model"}:
        return "planning"
    return "idle"


def _normalize_targets(targets: list[str]) -> list[str]:
    mapping = {
        "dashboard": "web_dashboard",
        "web": "web_dashboard",
        "display": "dedicated_display",
        "dedicated_display": "dedicated_display",
        "android": "mobile_app",
        "android_overlay": "mobile_app",
        "android_notification": "android_notification",
        "pc_overlay": "pc_overlay",
        "room_display": "room_display",
        "developer_console": "developer_console",
        "xr_scene": "smart_glasses",
    }
    return _dedupe_surfaces([mapping.get(target, target) for target in targets if target])


def _dedupe_surfaces(surfaces: list[str]) -> list[str]:
    seen: list[str] = []
    for surface in surfaces:
        if surface in SURFACE_IDS and surface not in seen:
            seen.append(surface)
    return seen
