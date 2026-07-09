"""Presentation Manager — Runtime-owned manager for rich AEGIS output.

The Presentation Manager is the single entry-point for presenting information
to the user across multiple surfaces (Dashboard, PC overlay, Android overlay,
XR).  It owns:
- PresentationSpec creation from PresentationRequest
- JSONL persistence via PresentationObjectStore
- Delivery via DeviceRouter
- Event publication
- User action tracking

Safety is NOT enforced here — safety lives in the source capability.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from aegis_ai.presentation.device_router import DeviceRouter
from aegis_ai.presentation.models import (
    PresentationRequest,
    PresentationSpec,
    PresentationStatus,
)
from aegis_ai.presentation.object_store import PresentationObjectStore
from aegis_ai.presentation.planner import plan_presentation

logger = logging.getLogger("aegis_ai.presentation.manager")


class PresentationManager:
    """Centralised presentation lifecycle manager.

    Parameters
    ----------
    object_store:
        JSONL-backed persistence.
    device_router:
        Delivers specs to target surfaces.
    event_manager:
        Optional; publishes ``presentation.*`` events.
    audit_manager:
        Optional; logs presentation actions.
    notification_manager:
        Optional; used for short overlay fallback via existing notification infra.
    interruption_controller:
        Optional; consulted before delivering high-priority presentations.
    """

    def __init__(
        self,
        object_store: PresentationObjectStore | None = None,
        device_router: DeviceRouter | None = None,
        event_manager: Any = None,
        audit_manager: Any = None,
        notification_manager: Any = None,
        interruption_controller: Any = None,
        data_dir: str = "data",
    ) -> None:
        self._store = object_store or PresentationObjectStore(data_dir=data_dir)
        self._router = device_router or DeviceRouter()
        self._event_manager = event_manager
        self._audit_manager = audit_manager
        self._notification_manager = notification_manager
        self._interruption_controller = interruption_controller

    # ── Public API ───────────────────────────────────────────────

    def present(self, request: PresentationRequest | dict[str, Any]) -> dict[str, Any]:
        """Create, persist, and deliver a presentation.

        Returns the serialised PresentationSpec plus delivery results.
        """
        if isinstance(request, dict):
            request = PresentationRequest.from_dict(request)

        spec = plan_presentation(request)
        self._store.put(spec)

        # Emit event
        self._publish_event("presentation.created", spec)

        # Deliver
        delivery_result = self._router.deliver(spec)
        spec.updated_at_ms = int(time.time() * 1000)
        spec.status = PresentationStatus.DELIVERED if delivery_result.get("ok") else PresentationStatus.FAILED
        self._store.put(spec)

        self._publish_event("presentation.delivered", spec, extra={"delivery": delivery_result})
        self._audit("present", spec, delivery_result)

        return {
            "ok": delivery_result.get("ok", False),
            "presentation": spec.to_dict(),
            "delivery": delivery_result,
        }

    def dismiss(self, presentation_id: str) -> dict[str, Any]:
        """Dismiss a presentation by ID."""
        spec = self._store.get(presentation_id)
        if spec is None:
            return {"ok": False, "error": "Presentation not found", "code": "NOT_FOUND"}
        spec.status = PresentationStatus.DISMISSED
        spec.updated_at_ms = int(time.time() * 1000)
        self._store.put(spec)
        self._publish_event("presentation.dismissed", spec)
        self._audit("dismiss", spec)
        return {"ok": True, "presentation": spec.to_dict()}

    def list_active(self, limit: int = 100) -> list[dict[str, Any]]:
        """List active presentations."""
        return [s.to_dict() for s in self._store.list_active(limit=limit)]

    def list_all(self, limit: int = 200) -> list[dict[str, Any]]:
        """List all presentations."""
        return [s.to_dict() for s in self._store.list_all(limit=limit)]

    def get(self, presentation_id: str) -> dict[str, Any] | None:
        """Get a single presentation by ID."""
        spec = self._store.get(presentation_id)
        return spec.to_dict() if spec else None

    def user_action(self, presentation_id: str, action: dict[str, Any]) -> dict[str, Any]:
        """Record a user action on a presentation (e.g. button click)."""
        spec = self._store.get(presentation_id)
        if spec is None:
            return {"ok": False, "error": "Presentation not found", "code": "NOT_FOUND"}
        action_record = {
            "action": action,
            "timestamp_ms": int(time.time() * 1000),
        }
        spec.user_actions.append(action_record)
        spec.updated_at_ms = int(time.time() * 1000)
        self._store.put(spec)
        self._publish_event("presentation.user_action", spec, extra={"action": action_record})
        self._audit("user_action", spec, action_record)
        return {"ok": True, "presentation": spec.to_dict()}

    def update(self, presentation_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        """Update an existing presentation's content or metadata."""
        spec = self._store.get(presentation_id)
        if spec is None:
            return {"ok": False, "error": "Presentation not found", "code": "NOT_FOUND"}
        if "title" in patch:
            spec.title = patch["title"]
        if "summary" in patch:
            spec.summary = patch["summary"]
        if "content" in patch:
            spec.content = patch["content"]
        if "importance" in patch:
            try:
                spec.importance = __import__("aegis_ai.presentation.models", fromlist=["Importance"]).Importance(patch["importance"])
            except (ValueError, KeyError):
                pass
        spec.revision += 1
        spec.updated_at_ms = int(time.time() * 1000)
        self._store.put(spec)
        self._publish_event("presentation.updated", spec)
        return {"ok": True, "presentation": spec.to_dict()}

    def get_status(self) -> dict[str, Any]:
        """Return high-level manager status."""
        return {
            "total": self._store.count(),
            "active": len(self._store.list_active()),
        }

    # ── Internal helpers ─────────────────────────────────────────

    def _publish_event(self, event_type: str, spec: PresentationSpec, extra: dict[str, Any] | None = None) -> None:
        if self._event_manager is None:
            return
        try:
            payload: dict[str, Any] = {"presentation_id": spec.presentation_id, "title": spec.title, "status": spec.status.value}
            if extra:
                payload.update(extra)
            self._event_manager.publish_event(
                event_type=event_type,
                source="presentation_manager",
                payload=payload,
            )
        except Exception:
            logger.debug("Failed to publish event %s", event_type, exc_info=True)

    def _audit(self, action: str, spec: PresentationSpec, detail: Any = None) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.append(
                action=f"presentation.{action}",
                source="presentation_manager",
                detail={"presentation_id": spec.presentation_id, "title": spec.title, "detail": detail},
            )
        except Exception:
            logger.debug("Audit write failed for presentation.%s", action, exc_info=True)
