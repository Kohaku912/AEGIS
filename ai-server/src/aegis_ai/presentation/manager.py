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
import threading
import time
from typing import Any

from aegis_ai.presentation.device_router import DeviceRouter
from aegis_ai.presentation.models import (
    Importance,
    PresentationRequest,
    PresentationSpec,
    PresentationStatus,
)
from aegis_ai.presentation.object_store import PresentationObjectStore
from aegis_ai.presentation.planner import plan_presentation, plan_presentation_v2
from aegis_ai.presentation.preferences import PresentationPreferences

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
        self._preferences = PresentationPreferences(data_dir=data_dir)
        self._sweeper_stop = threading.Event()
        self._sweeper_thread: threading.Thread | None = None
        self._sweeper_lock = threading.Lock()

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

        if (
            self._interruption_controller is not None
            and spec.importance != Importance.CRITICAL
        ):
            notification = {
                "category": "presentation",
                "severity": spec.importance.value,
                "title": spec.title,
            }
            decision = self._interruption_controller.decide(notification)
            if decision["decision"] in {"suppress", "batch_later"}:
                spec.metadata.setdefault("interruption", {})
                spec.metadata["interruption"].update(
                    {
                        "decision": decision["decision"],
                        "reason": decision["reason"],
                    }
                )
                spec.updated_at_ms = int(time.time() * 1000)
                spec.status = PresentationStatus.QUEUED
                self._store.put(spec)
                self._publish_event(
                    "presentation.queued",
                    spec,
                    extra={"interruption": decision},
                )
                self._audit("queue", spec, {"interruption": decision})
                return {
                    "ok": True,
                    "presentation": spec.to_dict(),
                    "delivery": {
                        "ok": False,
                        "suppressed": True,
                        "reason": decision["reason"],
                    },
                }

        # Deliver
        delivery_result = self._router.deliver(spec)
        spec.delivery_state = delivery_result.get("delivery_state", spec.delivery_state)
        spec.updated_at_ms = int(time.time() * 1000)
        spec.status = PresentationStatus.DELIVERED if delivery_result.get("ok") else PresentationStatus.FAILED
        self._store.put(spec)

        if (
            delivery_result.get("ok")
            and self._notification_manager is not None
            and spec.importance in (Importance.HIGH, Importance.CRITICAL)
        ):
            try:
                severity = "warning" if spec.importance == Importance.HIGH else "critical"
                notification = self._notification_manager.create_notification(
                    title=spec.title,
                    body=spec.summary,
                    severity=severity,
                    category="presentation",
                    channels=list(spec.delivery.targets),
                )
                notification_id = notification.get("notification_id")
                if notification_id:
                    spec.metadata["notification_id"] = notification_id
                    spec.updated_at_ms = int(time.time() * 1000)
                    self._store.put(spec)
            except Exception:
                logger.debug("Failed to create presentation notification", exc_info=True)

        self._publish_event("presentation.delivered", spec, extra={"delivery": delivery_result})
        self._audit("present", spec, delivery_result)

        return {
            "ok": delivery_result.get("ok", False),
            "presentation": spec.to_dict(),
            "delivery": delivery_result,
        }

    async def present_async(
        self,
        request: PresentationRequest | dict[str, Any],
        llm_router: Any = None,
    ) -> dict[str, Any]:
        """Async variant of present() with optional LLM-assisted planning."""
        if isinstance(request, dict):
            request = PresentationRequest.from_dict(request)

        spec = await plan_presentation_v2(request, llm_router)
        self._store.put(spec)

        self._publish_event("presentation.created", spec)

        if (
            self._interruption_controller is not None
            and spec.importance != Importance.CRITICAL
        ):
            notification = {
                "category": "presentation",
                "severity": spec.importance.value,
                "title": spec.title,
            }
            decision = self._interruption_controller.decide(notification)
            if decision.get("decision") in {"suppress", "batch_later"}:
                spec.metadata.setdefault("interruption", {})
                spec.metadata["interruption"].update(
                    {
                        "decision": decision.get("decision"),
                        "reason": decision.get("reason"),
                    }
                )
                spec.updated_at_ms = int(time.time() * 1000)
                spec.status = PresentationStatus.QUEUED
                self._store.put(spec)
                self._publish_event(
                    "presentation.queued",
                    spec,
                    extra={"interruption": decision},
                )
                self._audit("queue", spec, {"interruption": decision})
                return {
                    "ok": True,
                    "presentation": spec.to_dict(),
                    "delivery": {
                        "ok": False,
                        "suppressed": True,
                        "reason": decision.get("reason"),
                    },
                }

        delivery_result = self._router.deliver(spec)
        spec.delivery_state = delivery_result.get("delivery_state", spec.delivery_state)
        spec.updated_at_ms = int(time.time() * 1000)
        spec.status = PresentationStatus.DELIVERED if delivery_result.get("ok") else PresentationStatus.FAILED
        self._store.put(spec)

        if (
            delivery_result.get("ok")
            and self._notification_manager is not None
            and spec.importance in (Importance.HIGH, Importance.CRITICAL)
        ):
            try:
                severity = "warning" if spec.importance == Importance.HIGH else "critical"
                notification = self._notification_manager.create_notification(
                    title=spec.title,
                    body=spec.summary,
                    severity=severity,
                    category="presentation",
                    channels=list(spec.delivery.targets),
                )
                notification_id = notification.get("notification_id")
                if notification_id:
                    spec.metadata["notification_id"] = notification_id
                    spec.updated_at_ms = int(time.time() * 1000)
                    self._store.put(spec)
            except Exception:
                logger.debug("Failed to create presentation notification", exc_info=True)

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
        notification_id = spec.metadata.get("notification_id")
        if notification_id and self._notification_manager is not None:
            try:
                dismiss_notification = getattr(self._notification_manager, "dismiss_notification", None)
                if dismiss_notification is None:
                    dismiss_notification = getattr(self._notification_manager, "dismiss", None)
                if dismiss_notification is not None:
                    dismiss_notification(notification_id)
            except Exception:
                logger.debug("Failed to dismiss presentation notification", exc_info=True)
        self._publish_event("presentation.dismissed", spec)
        self._audit("dismiss", spec)
        return {"ok": True, "presentation": spec.to_dict()}

    def list_active(self, limit: int = 100) -> list[dict[str, Any]]:
        """List active presentations."""
        return [s.to_dict() for s in self._store.list_active(limit=limit)]

    def list_all(self, limit: int = 200) -> list[dict[str, Any]]:
        """List all presentations."""
        return [s.to_dict() for s in self._store.list_all(limit=limit)]

    def start_sweeper(self, interval_seconds: int = 300) -> None:
        """Start the background expiry sweeper."""
        with self._sweeper_lock:
            if self._sweeper_thread is not None and self._sweeper_thread.is_alive():
                return
            self._sweeper_stop = threading.Event()
            self._sweeper_thread = threading.Thread(
                target=self._sweep_loop,
                args=(interval_seconds,),
                name="presentation-sweeper",
                daemon=True,
            )
            self._sweeper_thread.start()

    def stop_sweeper(self) -> None:
        """Stop the background expiry sweeper."""
        self._sweeper_stop.set()

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
        self._preferences.record_interaction(spec.modality.value, spec.placement.zone, action.get("type", "unknown"))
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
                importance_cls = __import__(
                    "aegis_ai.presentation.models",
                    fromlist=["Importance"],
                ).Importance
                spec.importance = importance_cls(patch["importance"])
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

    def get_preferences(self) -> dict[str, Any]:
        """Return current presentation preference scores."""
        return self._preferences.get_scores()

    # ── Internal helpers ─────────────────────────────────────────

    def _publish_event(self, event_type: str, spec: PresentationSpec, extra: dict[str, Any] | None = None) -> None:
        if self._event_manager is None:
            return
        try:
            payload: dict[str, Any] = {
                "presentation_id": spec.presentation_id,
                "title": spec.title,
                "status": spec.status.value,
            }
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

    def _sweep_once(self) -> None:
        """Expire any presentations whose TTL has elapsed."""
        expired = self._store.list_expired()
        if not expired:
            return

        now_ms = int(time.time() * 1000)
        for spec in expired:
            spec.status = PresentationStatus.EXPIRED
            spec.updated_at_ms = now_ms
            self._store.put(spec)
            self._publish_event("presentation.expired", spec)
            self._audit("expire", spec, {"reason": "ttl_expired"})

    def _sweep_loop(self, interval_seconds: int) -> None:
        """Run expiry sweeps until stopped."""
        while not self._sweeper_stop.is_set():
            self._sweep_once()
            if self._sweeper_stop.wait(interval_seconds):
                break
