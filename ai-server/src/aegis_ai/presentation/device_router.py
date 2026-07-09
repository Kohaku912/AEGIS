"""Device Router — delivers presentations to target surfaces.

The router is intentionally thin: it resolves which adapter handles each
target and delegates.  Adapters are injected at construction time so the
router itself has no hard dependency on any specific server client.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from aegis_ai.presentation.models import Modality, PresentationSpec, PresentationStatus

logger = logging.getLogger("aegis_ai.presentation.device_router")


# ── Adapter protocol ─────────────────────────────────────────────


class PresentationAdapter(Protocol):
    """Minimal contract every output adapter must satisfy."""

    def deliver(self, spec: PresentationSpec) -> dict[str, Any]:
        """Attempt delivery; return ``{"ok": True, ...}`` or error dict."""
        ...


# ── Overlay broadcast adapter ────────────────────────────────────


class OverlayBroadcastAdapter:
    """Sends short text overlays via the existing
    ``ai-server.notification.broadcast_overlay`` capability.
    """

    def __init__(self, core_capability_client: Any = None) -> None:
        self._client = core_capability_client

    def deliver(self, spec: PresentationSpec) -> dict[str, Any]:
        if self._client is None:
            return {"ok": False, "error": "CoreCapabilityClient unavailable"}
        targets = spec.delivery.targets or ["pc", "android"]
        return self._client._broadcast_overlay({
            "message": spec.summary or spec.title,
            "title": spec.title,
            "targets": targets,
            "duration_ms": min(spec.delivery.ttl_ms, 15_000),
        })


# ── Dashboard adapter (placeholder — real rendering is in JS) ────


class DashboardAdapter:
    """Marks the spec as delivered for the dashboard renderer to pick up.

    The actual rendering happens client-side in the dashboard JS.
    This adapter just ensures the spec is stored and visible.
    """

    def deliver(self, spec: PresentationSpec) -> dict[str, Any]:
        return {"ok": True, "target": "dashboard", "stored": True}


# ── XR pending adapter ──────────────────────────────────────────


class XRPendingAdapter:
    """Stores XR-targeted presentations in a pending queue.

    When an XR client connects it can pull from this queue.
    """

    def __init__(self) -> None:
        self._pending: list[PresentationSpec] = []

    def deliver(self, spec: PresentationSpec) -> dict[str, Any]:
        self._pending.append(spec)
        return {"ok": True, "target": "xr_scene", "queued": True}

    def drain(self, limit: int = 50) -> list[dict[str, Any]]:
        items = self._pending[:limit]
        self._pending = self._pending[limit:]
        return [s.to_dict() for s in items]

    def count(self) -> int:
        return len(self._pending)


# ── Device Router ────────────────────────────────────────────────

_TARGET_MAP: dict[str, str] = {
    "dashboard": "dashboard",
    "pc_overlay": "overlay",
    "pc": "overlay",
    "android_overlay": "overlay",
    "android": "overlay",
    "xr_scene": "xr",
    "xr": "xr",
    "auto": "auto",
}


class DeviceRouter:
    """Resolves delivery targets and delegates to adapters."""

    def __init__(
        self,
        overlay_adapter: OverlayBroadcastAdapter | None = None,
        dashboard_adapter: DashboardAdapter | None = None,
        xr_adapter: XRPendingAdapter | None = None,
    ) -> None:
        self._overlay = overlay_adapter or OverlayBroadcastAdapter()
        self._dashboard = dashboard_adapter or DashboardAdapter()
        self._xr = xr_adapter or XRPendingAdapter()

    def deliver(self, spec: PresentationSpec) -> dict[str, Any]:
        """Route each target in the spec's delivery.targets list."""
        results: dict[str, Any] = {}
        delivered: list[str] = []
        failed: dict[str, str] = {}

        targets = spec.delivery.targets or ["dashboard"]

        for raw_target in targets:
            target = _TARGET_MAP.get(raw_target, raw_target)

            try:
                if target == "dashboard":
                    result = self._dashboard.deliver(spec)
                elif target == "overlay":
                    # Overlay only supports short text — downgrade if needed
                    if spec.modality not in (Modality.TEXT_CARD, Modality.OVERLAY_SHORT):
                        result = {"ok": True, "skipped": True, "reason": "modality not supported on overlay"}
                    else:
                        result = self._overlay.deliver(spec)
                elif target == "xr":
                    result = self._xr.deliver(spec)
                else:
                    result = {"ok": False, "error": f"Unknown target: {raw_target}"}
            except Exception as exc:
                logger.exception("Delivery failed for target %s", raw_target)
                result = {"ok": False, "error": str(exc)}

            results[raw_target] = result
            if result.get("ok"):
                delivered.append(raw_target)
            else:
                failed[raw_target] = result.get("error", "unknown error")

        spec.status = PresentationStatus.DELIVERED if delivered else PresentationStatus.FAILED
        return {
            "ok": bool(delivered),
            "delivered": delivered,
            "failed": failed,
            "results": results,
        }
