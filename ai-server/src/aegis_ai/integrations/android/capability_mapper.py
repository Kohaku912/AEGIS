"""Fixed Android capability dispatch map.

Android devices are fixed gRPC terminals. They do not receive arbitrary code,
dynamic plugins, or free-form command execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AndroidCapabilityRoute:
    """A static route from canonical capability ID to Android gRPC method."""

    capability_id: str
    method: str
    request_type: str
    required_permissions: tuple[str, ...] = field(default_factory=tuple)
    implemented: bool = True


class AndroidCapabilityMapper:
    """Maps canonical AEGIS capability IDs to AndroidServer RPCs."""

    _ROUTES: dict[str, AndroidCapabilityRoute] = {
        "android-server.device.get_status": AndroidCapabilityRoute(
            "android-server.device.get_status",
            "GetDeviceStatus",
            "AndroidGetDeviceStatusRequest",
        ),
        "android-server.permissions.get_status": AndroidCapabilityRoute(
            "android-server.permissions.get_status",
            "GetPermissionStatus",
            "GetPermissionStatusRequest",
        ),
        "android-server.accessibility.get_status": AndroidCapabilityRoute(
            "android-server.accessibility.get_status",
            "GetAccessibilityStatus",
            "GetAccessibilityStatusRequest",
        ),
        "android-server.overlay.show": AndroidCapabilityRoute(
            "android-server.overlay.show",
            "ShowOverlay",
            "AndroidShowOverlayRequest",
            ("overlay",),
        ),
        "android-server.approval.request": AndroidCapabilityRoute(
            "android-server.approval.request",
            "RequestApproval",
            "AndroidApprovalRequest",
            ("overlay",),
        ),
        "android-server.notification.get_notifications": AndroidCapabilityRoute(
            "android-server.notification.get_notifications",
            "GetNotifications",
            "GetNotificationsRequest",
            ("notification_listener",),
        ),
        "android-server.screen.get_current_app": AndroidCapabilityRoute(
            "android-server.screen.get_current_app",
            "GetCurrentApp",
            "GetCurrentAppRequest",
            ("accessibility",),
        ),
        "android-server.screen.get_ui_tree": AndroidCapabilityRoute(
            "android-server.screen.get_ui_tree",
            "GetUiTree",
            "GetUiTreeRequest",
            ("accessibility",),
        ),
        "android-server.screen.get_screenshot": AndroidCapabilityRoute(
            "android-server.screen.get_screenshot",
            "GetScreenshot",
            "GetAndroidScreenshotRequest",
            ("media_projection",),
        ),
        "android-server.ui.tap": AndroidCapabilityRoute(
            "android-server.ui.tap",
            "Tap",
            "TapRequest",
            ("accessibility",),
        ),
        "android-server.ui.swipe": AndroidCapabilityRoute(
            "android-server.ui.swipe",
            "Swipe",
            "SwipeRequest",
            ("accessibility",),
        ),
        "android-server.ui.type_text": AndroidCapabilityRoute(
            "android-server.ui.type_text",
            "TypeText",
            "AndroidTypeTextRequest",
            ("accessibility",),
        ),
        "android-server.ui.back": AndroidCapabilityRoute(
            "android-server.ui.back",
            "PressBack",
            "PressBackRequest",
            ("accessibility",),
        ),
        "android-server.ui.home": AndroidCapabilityRoute(
            "android-server.ui.home",
            "PressHome",
            "PressHomeRequest",
            ("accessibility",),
        ),
        "android-server.app.open": AndroidCapabilityRoute(
            "android-server.app.open",
            "OpenApp",
            "OpenAppRequest",
        ),
        "android-server.location.get_current": AndroidCapabilityRoute(
            "android-server.location.get_current",
            "GetLocation",
            "GetLocationRequest",
            ("location",),
        ),
        "android-server.safety.emergency_stop": AndroidCapabilityRoute(
            "android-server.safety.emergency_stop",
            "EmergencyStop",
            "AndroidEmergencyStopRequest",
        ),
    }

    def get_route(self, capability_id: str) -> AndroidCapabilityRoute | None:
        """Return the fixed route for a canonical Android capability."""
        return self._ROUTES.get(capability_id)

    def list_capabilities(self) -> list[str]:
        """Return all fixed Android capability IDs."""
        return sorted(self._ROUTES)

    def availability(self, permissions: dict[str, bool] | None = None) -> dict[str, dict[str, Any]]:
        """Return per-capability availability and missing permissions."""
        permissions = permissions or {}
        items: dict[str, dict[str, Any]] = {}
        for cap_id, route in self._ROUTES.items():
            missing = [p for p in route.required_permissions if permissions.get(p) is False]
            items[cap_id] = {
                "implemented": route.implemented,
                "method": route.method,
                "required_permissions": list(route.required_permissions),
                "available": route.implemented and not missing,
                "missing_permissions": missing,
            }
        return items
