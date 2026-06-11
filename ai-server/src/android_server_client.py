"""Android Server Client — Python adapter for Android Server integration with AEGIS Core.

This module bridges the Kotlin Android Server with AEGIS Core's Python modules.
It provides:
- Capability registration with ToolRegistry (observe + action)
- Event push to EventBus (notifications, app state, device state, actions)
- Mock provider for CI testing
- Real provider for ADB-based local testing
- Retry/backoff when AEGIS Core is unavailable
- Graceful failure when Android device is unavailable
- Permission state tracking
- Notification redaction, allowlist, denylist

Architecture reference: docs/architecture.md §3.3, §4
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Protocol

from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    RiskLevel,
    ServerInfo,
    ServerStatus,
    ServerType,
)

logger = logging.getLogger("aegis.android_server_client")


# ═══════════════════════════════════════════════════════════════
# Notification Filter — redaction, allowlist, denylist
# ═══════════════════════════════════════════════════════════════

REDACTION_PATTERNS: list[tuple[str, str]] = [
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{1,7}\b", "[CARD_REDACTED]"),
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL_REDACTED]"),
    (r"\+\d{1,3}[\s-]?\d[\d\s-]{7,12}\d", "[PHONE_REDACTED]"),
    (r"(?i)(password|token|secret|key|api.?key)\s*[:=]\s*\S+", r"\1=[REDACTED]"),
    (r"(?<!\d)\d{4,8}(?!\d)", "[OTP_REDACTED]"),
]

DEFAULT_DENYLIST: set[str] = {
    "com.bank",
    "com.password.manager",
    "com.google.android.apps.authenticator",
    "com.azure.authenticator",
    "com.duosecurity.duomobile",
    "com.aegis.android",
    "android",
    "com.android.systemui",
}

DEFAULT_ALLOWLIST: set[str] = {
    "com.android.messaging",
    "com.google.android.gm",
    "com.slack",
    "com.discord",
    "jp.naver.line.android",
    "com.twitter.android",
    "com.whatsapp",
    "com.telegram.messenger",
}


class NotificationFilter:
    """Filters and redacts Android notifications before forwarding to AEGIS Core."""

    def __init__(
        self,
        denylist: set[str] | None = None,
        allowlist: set[str] | None = None,
        redaction_patterns: list[tuple[str, str]] | None = None,
    ) -> None:
        self._denylist = denylist if denylist is not None else set(DEFAULT_DENYLIST)
        self._allowlist = allowlist if allowlist is not None else set(DEFAULT_ALLOWLIST)
        self._patterns = redaction_patterns if redaction_patterns is not None else REDACTION_PATTERNS

    def is_blocked(self, package_name: str) -> bool:
        if package_name in self._allowlist:
            return False
        return package_name in self._denylist

    def is_sensitive(self, package_name: str) -> bool:
        sensitive_prefixes = ("com.bank", "com.password", "com.google.android.apps.authenticator")
        return any(package_name.startswith(p) for p in sensitive_prefixes) or package_name in {
            "com.azure.authenticator",
            "com.duosecurity.duomobile",
        }

    def redact(self, text: str) -> str:
        import re

        result = text
        for pattern, replacement in self._patterns:
            result = re.sub(pattern, replacement, result)
        return result

    def filter_notification(self, notification: dict[str, Any]) -> dict[str, Any] | None:
        pkg = notification.get("package_name", "")
        if self.is_blocked(pkg):
            return None
        filtered = dict(notification)
        filtered["title"] = self.redact(filtered.get("title", ""))
        filtered["text"] = self.redact(filtered.get("text", ""))
        filtered["redacted_only"] = self.is_sensitive(pkg)
        return filtered


# ═══════════════════════════════════════════════════════════════
# Permission State — tracks which Android permissions are granted
# ═══════════════════════════════════════════════════════════════


class PermissionState(Enum):
    """Android permission states."""

    GRANTED = auto()
    DENIED = auto()
    NOT_REQUESTED = auto()


@dataclass
class AndroidPermissions:
    """Tracks Android permission states."""

    notification_listener: PermissionState = PermissionState.NOT_REQUESTED
    media_projection: PermissionState = PermissionState.NOT_REQUESTED
    accessibility_service: PermissionState = PermissionState.NOT_REQUESTED
    overlay: PermissionState = PermissionState.NOT_REQUESTED

    def is_granted(self, permission: str) -> bool:
        """Check if a specific permission is granted."""
        state = getattr(self, permission, PermissionState.NOT_REQUESTED)
        return state == PermissionState.GRANTED

    def get_missing_permissions(self) -> list[str]:
        """Return list of permissions that are not granted."""
        missing = []
        for field_name in ["notification_listener", "media_projection", "accessibility_service", "overlay"]:
            if getattr(self, field_name) != PermissionState.GRANTED:
                missing.append(field_name)
        return missing


# ═══════════════════════════════════════════════════════════════
# UI Node — represents a node in the Android UI tree
# ═══════════════════════════════════════════════════════════════


@dataclass
class UINode:
    """A node in the Android UI tree (AccessibilityService)."""

    class_name: str = ""
    text: str = ""
    content_desc: str = ""
    resource_id: str = ""
    is_clickable: bool = False
    is_focusable: bool = False
    is_password: bool = False
    bounds: list[int] | None = None  # [left, top, right, bottom]
    children: list[UINode] | None = None


# ═══════════════════════════════════════════════════════════════
# Provider Protocol — abstracts real vs mock Android observation + action
# ═══════════════════════════════════════════════════════════════


class AndroidProvider(Protocol):
    """Protocol for Android observation providers."""

    def get_notifications(self, max_count: int = 0) -> list[dict[str, Any]]: ...

    def get_current_app(self) -> dict[str, Any]: ...

    def get_device_info(self) -> dict[str, Any]: ...

    def is_available(self) -> bool: ...


class AndroidActionProvider(Protocol):
    """Protocol for Android action providers.

    Real implementations use AccessibilityService / MediaProjection.
    Mock implementations return deterministic fake results for CI.
    """

    def get_screenshot(self, quality: int = 80) -> dict[str, Any]:
        """Capture screenshot via MediaProjection. Returns {success, image_base64, width, height}."""
        ...

    def get_ui_tree(self, include_invisible: bool = False) -> dict[str, Any]:
        """Get UI tree via AccessibilityService. Returns {success, root_node}."""
        ...

    def show_overlay(self, text: str, x: int = 100, y: int = 100, duration_ms: int = 5000) -> dict[str, Any]:
        """Show overlay notification. Returns {success, overlay_id}."""
        ...

    def hide_overlay(self, overlay_id: str = "") -> dict[str, Any]:
        """Hide overlay. Returns {success, overlay_id}."""
        ...

    def tap(self, x: int, y: int, duration_ms: int = 0) -> dict[str, Any]:
        """Tap at coordinates via AccessibilityService. Returns {success, x, y}."""
        ...

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 300) -> dict[str, Any]:
        """Swipe gesture via AccessibilityService. Returns {success}."""
        ...

    def type_text(self, text: str) -> dict[str, Any]:
        """Type text via AccessibilityService. Returns {success, characters_typed}."""
        ...

    def press_back(self) -> dict[str, Any]:
        """Press back button. Returns {success}."""
        ...

    def press_home(self) -> dict[str, Any]:
        """Press home button. Returns {success}."""
        ...

    def open_app(self, package_name: str, activity_name: str = "") -> dict[str, Any]:
        """Open an app by package name. Returns {success, package_name}."""
        ...


# ═══════════════════════════════════════════════════════════════
# Mock Provider — for CI testing (no real device calls)
# ═══════════════════════════════════════════════════════════════


class MockAndroidProvider:
    """Mock Android provider for CI testing. Returns deterministic fake data."""

    def __init__(self, available: bool = True) -> None:
        self._available = available
        self.call_log: list[tuple[str, dict[str, Any]]] = []
        self._overlay_visible = False

    # ── Observe ──

    def get_notifications(self, max_count: int = 0) -> list[dict[str, Any]]:
        self.call_log.append(("get_notifications", {"max_count": max_count}))
        notifications = [
            {
                "key": "mock_notif_001",
                "package_name": "com.android.messaging",
                "app_name": "Messages",
                "title": "Test Message",
                "text": "Hello from mock notification",
                "posted_ms": int(time.time() * 1000) - 60000,
                "is_ongoing": False,
                "is_clearable": True,
            },
            {
                "key": "mock_notif_002",
                "package_name": "com.google.android.gm",
                "app_name": "Gmail",
                "title": "New email",
                "text": "You have a new email from test@example.com",
                "posted_ms": int(time.time() * 1000) - 30000,
                "is_ongoing": False,
                "is_clearable": True,
            },
        ]
        return notifications[:max_count] if max_count > 0 else notifications

    def get_current_app(self) -> dict[str, Any]:
        self.call_log.append(("get_current_app", {}))
        return {
            "package_name": "com.google.android.apps.nexuslauncher",
            "activity_name": "com.google.android.apps.nexuslauncher.NexusLauncherActivity",
            "app_name": "Launcher",
        }

    def get_device_info(self) -> dict[str, Any]:
        self.call_log.append(("get_device_info", {}))
        return {
            "model": "Pixel 7",
            "manufacturer": "Google",
            "android_version": "14",
            "sdk_version": 34,
            "battery_level": 85,
            "battery_charging": False,
            "screen_on": True,
            "wifi_connected": True,
        }

    def is_available(self) -> bool:
        return self._available

    # ── Screenshot ──

    def get_screenshot(self, quality: int = 80) -> dict[str, Any]:
        self.call_log.append(("get_screenshot", {"quality": quality}))
        return {
            "success": True,
            "image_base64": "[MOCK_SCREENSHOT]",
            "width": 1080,
            "height": 2400,
            "format": "jpeg",
            "captured_ms": int(time.time() * 1000),
        }

    # ── UI Tree ──

    def get_ui_tree(self, include_invisible: bool = False) -> dict[str, Any]:
        self.call_log.append(("get_ui_tree", {"include_invisible": include_invisible}))
        return {
            "success": True,
            "root": {
                "class_name": "android.widget.FrameLayout",
                "resource_id": "android:id/content",
                "text": "",
                "content_desc": "",
                "is_clickable": False,
                "is_focusable": False,
                "is_password": False,
                "bounds": [0, 0, 1080, 2400],
                "children": [
                    {
                        "class_name": "android.widget.TextView",
                        "resource_id": "com.example:id/title",
                        "text": "Hello World",
                        "content_desc": "",
                        "is_clickable": False,
                        "is_focusable": False,
                        "is_password": False,
                        "bounds": [100, 200, 500, 250],
                        "children": [],
                    },
                    {
                        "class_name": "android.widget.Button",
                        "resource_id": "com.example:id/btn_submit",
                        "text": "Submit",
                        "content_desc": "Submit form",
                        "is_clickable": True,
                        "is_focusable": True,
                        "is_password": False,
                        "bounds": [100, 300, 400, 350],
                        "children": [],
                    },
                    {
                        "class_name": "android.widget.EditText",
                        "resource_id": "com.example:id/input_password",
                        "text": "",
                        "content_desc": "Password field",
                        "is_clickable": True,
                        "is_focusable": True,
                        "is_password": True,
                        "bounds": [100, 400, 500, 450],
                        "children": [],
                    },
                ],
            },
        }

    # ── Overlay ──

    def show_overlay(self, text: str, x: int = 100, y: int = 100, duration_ms: int = 5000) -> dict[str, Any]:
        self.call_log.append(("show_overlay", {"text": text[:50], "x": x, "y": y}))
        self._overlay_visible = True
        return {"success": True, "overlay_id": "mock_overlay_001"}

    def hide_overlay(self, overlay_id: str = "") -> dict[str, Any]:
        self.call_log.append(("hide_overlay", {"overlay_id": overlay_id}))
        self._overlay_visible = False
        return {"success": True, "overlay_id": overlay_id or "mock_overlay_001"}

    # ── Actions ──

    def tap(self, x: int, y: int, duration_ms: int = 0) -> dict[str, Any]:
        self.call_log.append(("tap", {"x": x, "y": y, "duration_ms": duration_ms}))
        return {"success": True, "x": x, "y": y}

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 300) -> dict[str, Any]:
        self.call_log.append(("swipe", {"start_x": start_x, "start_y": start_y, "end_x": end_x, "end_y": end_y}))
        return {"success": True}

    def type_text(self, text: str) -> dict[str, Any]:
        self.call_log.append(("type_text", {"text": text[:50]}))
        return {"success": True, "characters_typed": len(text)}

    def press_back(self) -> dict[str, Any]:
        self.call_log.append(("press_back", {}))
        return {"success": True}

    def press_home(self) -> dict[str, Any]:
        self.call_log.append(("press_home", {}))
        return {"success": True}

    def open_app(self, package_name: str, activity_name: str = "") -> dict[str, Any]:
        self.call_log.append(("open_app", {"package_name": package_name, "activity_name": activity_name}))
        return {"success": True, "package_name": package_name}


# ═══════════════════════════════════════════════════════════════
# ADB Provider — for local testing with real device via ADB
# ═══════════════════════════════════════════════════════════════


class ADBAndroidProvider:
    """ADB-based Android provider for local testing with a real device."""

    def __init__(self, device_serial: str | None = None) -> None:
        self._serial = device_serial
        self.call_log: list[tuple[str, dict[str, Any]]] = []

    def _adb(self, *args: str) -> str:
        cmd = ["adb"]
        if self._serial:
            cmd.extend(["-s", self._serial])
        cmd.extend(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                check=False,
            )
            return (result.stdout or "").strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error("ADB command failed: %s", e)
            return ""

    def get_notifications(self, max_count: int = 0) -> list[dict[str, Any]]:
        self.call_log.append(("get_notifications", {"max_count": max_count}))
        output = self._adb("shell", "dumpsys", "notification", "--noredact")
        notifications: list[dict[str, Any]] = []
        current_pkg, current_title, current_text = "", "", ""
        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("pkg="):
                current_pkg = line.split("=", 1)[1] if "=" in line else ""
            elif line.startswith("android.title="):
                current_title = line.split("=", 1)[1] if "=" in line else ""
            elif line.startswith("android.text="):
                current_text = line.split("=", 1)[1] if "=" in line else ""
                if current_pkg and current_title:
                    notifications.append(
                        {
                            "key": f"adb_notif_{len(notifications)}",
                            "package_name": current_pkg,
                            "app_name": current_pkg.split(".")[-1],
                            "title": current_title,
                            "text": current_text,
                            "posted_ms": int(time.time() * 1000),
                            "is_ongoing": False,
                            "is_clearable": True,
                        }
                    )
                    current_pkg, current_title, current_text = "", "", ""
        return notifications[:max_count] if max_count > 0 else notifications

    def get_current_app(self) -> dict[str, Any]:
        self.call_log.append(("get_current_app", {}))
        output = self._adb("shell", "dumpsys", "activity", "activities")
        package_name, activity_name = "", ""
        for line in output.split("\n"):
            if "mResumedActivity" in line or "topResumedActivity" in line:
                for part in line.split():
                    if "/" in part and "." in part:
                        components = part.split("/")
                        package_name = components[0].strip()
                        activity_name = components[1].strip() if len(components) > 1 else ""
                        break
                break
        return {
            "package_name": package_name or "unknown",
            "activity_name": activity_name or "unknown",
            "app_name": package_name.split(".")[-1] if package_name else "unknown",
        }

    def get_device_info(self) -> dict[str, Any]:
        self.call_log.append(("get_device_info", {}))
        model = self._adb("shell", "getprop", "ro.product.model")
        manufacturer = self._adb("shell", "getprop", "ro.product.manufacturer")
        android_version = self._adb("shell", "getprop", "ro.build.version.release")
        sdk_version_str = self._adb("shell", "getprop", "ro.build.version.sdk")
        battery_output = self._adb("shell", "dumpsys", "battery")
        battery_level, battery_charging = 0, False
        for line in battery_output.split("\n"):
            if "level:" in line:
                try:
                    battery_level = int(line.split(":")[1].strip())
                except ValueError:
                    pass
            if "status:" in line:
                battery_charging = "Charging" in line
        return {
            "model": model or "unknown",
            "manufacturer": manufacturer or "unknown",
            "android_version": android_version or "unknown",
            "sdk_version": int(sdk_version_str) if sdk_version_str.isdigit() else 0,
            "battery_level": battery_level,
            "battery_charging": battery_charging,
            "screen_on": True,
            "wifi_connected": True,
        }

    def is_available(self) -> bool:
        output = self._adb("devices")
        lines = output.strip().split("\n")
        for line in lines[1:]:
            if "\tdevice" in line:
                return True
        return False


# ═══════════════════════════════════════════════════════════════
# Connection State & Retry
# ═══════════════════════════════════════════════════════════════


class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    FAILED = auto()


@dataclass
class RetryConfig:
    max_retries: int = 5
    base_delay_ms: int = 100
    max_delay_ms: int = 30_000
    backoff_factor: float = 2.0


@dataclass
class ConnectionStats:
    state: ConnectionState = ConnectionState.DISCONNECTED
    retry_count: int = 0
    last_error: str = ""
    last_connected_at_ms: int = 0
    last_attempt_at_ms: int = 0
    total_registrations: int = 0
    total_events_pushed: int = 0


# ═══════════════════════════════════════════════════════════════
# Android Server Capabilities — Observe + Action
# ═══════════════════════════════════════════════════════════════

ANDROID_SERVER_ID = "android-server-main"

ANDROID_CAPABILITIES: list[Capability] = [
    # ── Observe (Level 0) ──
    Capability(
        id="android.get_notifications",
        name="Get Notifications",
        description="Retrieve current status bar notifications from the Android device.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.READ_ONLY,
        tags=["notification", "observe", "read_only"],
        timeout_ms=3000,
    ),
    Capability(
        id="android.get_current_app",
        name="Get Current App",
        description="Return the package name and activity of the foreground app.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.READ_ONLY,
        tags=["app", "observe", "read_only"],
        timeout_ms=1000,
    ),
    Capability(
        id="android.get_device_info",
        name="Get Device Info",
        description="Return device model, Android version, battery level, and connectivity.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.READ_ONLY,
        tags=["device", "system", "observe", "read_only"],
        timeout_ms=1000,
    ),
    Capability(
        id="android.get_screenshot",
        name="Get Screenshot",
        description="Capture screenshot via MediaProjection. Requires permission.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.READ_ONLY,
        tags=["screenshot", "observe", "read_only"],
        timeout_ms=5000,
    ),
    Capability(
        id="android.get_ui_tree",
        name="Get UI Tree",
        description="Get current UI tree via AccessibilityService. Requires permission.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.READ_ONLY,
        tags=["ui_tree", "observe", "read_only"],
        timeout_ms=3000,
    ),
    # ── Action Level 1 ──
    Capability(
        id="android.show_overlay",
        name="Show Overlay",
        description="Show an overlay notification on the Android device.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["overlay", "action"],
        timeout_ms=2000,
    ),
    Capability(
        id="android.hide_overlay",
        name="Hide Overlay",
        description="Hide the current overlay notification.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["overlay", "action"],
        timeout_ms=1000,
    ),
    Capability(
        id="android.open_app",
        name="Open App",
        description="Open an application by package name.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["app", "action"],
        timeout_ms=3000,
    ),
    Capability(
        id="android.press_home",
        name="Press Home",
        description="Press the home button.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["navigation", "action"],
        timeout_ms=1000,
    ),
    # ── Action Level 2 ──
    Capability(
        id="android.tap",
        name="Tap",
        description="Tap at screen coordinates via AccessibilityService. Requires approval.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["touch_input"],
        tags=["input", "action", "approval_required"],
        timeout_ms=2000,
    ),
    Capability(
        id="android.swipe",
        name="Swipe",
        description="Swipe gesture via AccessibilityService. Requires approval.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["touch_input"],
        tags=["input", "action", "approval_required"],
        timeout_ms=2000,
    ),
    Capability(
        id="android.type_text",
        name="Type Text",
        description="Type text via AccessibilityService. Requires approval. Denied for password fields.",
        server_type=ServerType.ANDROID,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["keyboard_input"],
        tags=["input", "action", "approval_required"],
        timeout_ms=5000,
    ),
]


def get_android_server_info() -> ServerInfo:
    """Create ServerInfo for the Android Server."""
    return ServerInfo(
        server_id=ANDROID_SERVER_ID,
        server_type=ServerType.ANDROID,
        version="0.2.0",
        status=ServerStatus.ONLINE,
        capability_ids=[cap.id for cap in ANDROID_CAPABILITIES],
        host="localhost",
        port=50053,
        started_at_ms=int(time.time() * 1000),
    )


# ═══════════════════════════════════════════════════════════════
# Password Field Detection — prevents typing into password fields
# ═══════════════════════════════════════════════════════════════


def contains_password_field(ui_tree: dict[str, Any]) -> bool:
    """Check if the UI tree contains a password field."""
    if ui_tree.get("is_password"):
        return True
    for child in ui_tree.get("children", []):
        if contains_password_field(child):
            return True
    return False


# ═══════════════════════════════════════════════════════════════
# Android Server Client — main integration point
# ═══════════════════════════════════════════════════════════════


class AndroidServerClient:
    """Python client that integrates Android Server with AEGIS Core.

    Responsibilities:
    1. Register Android capabilities with ToolRegistry
    2. Push Android events to EventBus
    3. Handle connection state and retry/backoff
    4. Graceful failure when Android device is unavailable
    5. Invoke capabilities through ToolBroker (with PolicyEngine enforcement)
    6. Push action result events to EventBus
    7. Track permission states
    """

    def __init__(
        self,
        event_bus: Any,
        registry: Any,
        provider: Any = None,
        retry_config: RetryConfig | None = None,
        notification_filter: NotificationFilter | None = None,
        permissions: AndroidPermissions | None = None,
        tool_broker: Any = None,
    ) -> None:
        self._event_bus = event_bus
        self._registry = registry
        self._provider = provider or MockAndroidProvider()
        self._retry = retry_config or RetryConfig()
        self._stats = ConnectionStats()
        self._registered = False
        self._notification_filter = notification_filter or NotificationFilter()
        self._permissions = permissions or AndroidPermissions()
        self._tool_broker = tool_broker

    @property
    def stats(self) -> ConnectionStats:
        return self._stats

    @property
    def is_registered(self) -> bool:
        return self._registered

    @property
    def notification_filter(self) -> NotificationFilter:
        return self._notification_filter

    @property
    def permissions(self) -> AndroidPermissions:
        return self._permissions

    @property
    def provider(self) -> Any:
        return self._provider

    # ── Registration ─────────────────────────────────────────

    def register(self) -> bool:
        """Register Android Server and its capabilities with AEGIS Core."""
        if not self._provider.is_available():
            self._stats.state = ConnectionState.FAILED
            self._stats.last_error = "Android device is not available"
            logger.warning("Android device not available — skipping registration")
            return False

        try:
            server_info = get_android_server_info()
            self._registry.register_server(server_info)
            for cap in ANDROID_CAPABILITIES:
                self._registry.register_capability(cap)

            self._registered = True
            self._stats.state = ConnectionState.CONNECTED
            self._stats.total_registrations = len(ANDROID_CAPABILITIES)
            self._stats.last_connected_at_ms = int(time.time() * 1000)
            logger.info("Android Server registered %d capabilities", len(ANDROID_CAPABILITIES))
            return True

        except Exception as e:
            self._stats.state = ConnectionState.FAILED
            self._stats.last_error = str(e)
            logger.error("Android Server registration failed: %s", e)
            return False

    def unregister(self) -> None:
        """Unregister Android Server from AEGIS Core."""
        self._registry.unregister_server(ANDROID_SERVER_ID)
        for cap in ANDROID_CAPABILITIES:
            self._registry.unregister_capability(cap.id)
        self._registered = False
        self._stats.state = ConnectionState.DISCONNECTED

    # ── Event Push ───────────────────────────────────────────

    def push_event(self, event: Event) -> bool:
        """Push an event to the EventBus."""
        if not self._registered:
            logger.warning("Cannot push event — Android Server not registered")
            return False
        try:
            result = self._event_bus.publish(event)
            if result:
                self._stats.total_events_pushed += 1
            return result
        except Exception as e:
            self._stats.last_error = str(e)
            logger.error("Failed to push event: %s", e)
            return False

    def push_notification_event(
        self,
        app_name: str,
        title: str,
        text: str,
        *,
        package_name: str = "",
        severity: int = 3,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Push an android.notification_received event with redaction."""
        raw = {"app_name": app_name, "title": title, "text": text, "package_name": package_name}
        filtered = self._notification_filter.filter_notification(raw)
        if filtered is None:
            return False
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="android.notification_received",
            source_server_type=ServerType.ANDROID,
            source_server_id=ANDROID_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=json.dumps(filtered),
            severity=severity,
            priority=priority,
            dedupe_key=f"android.notification:{package_name}:{title}",
        )
        return self.push_event(event)

    def push_app_changed_event(
        self,
        package_name: str,
        app_name: str,
        *,
        severity: int = 2,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Push an android.current_app_changed event."""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="android.current_app_changed",
            source_server_type=ServerType.ANDROID,
            source_server_id=ANDROID_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=json.dumps({"package_name": package_name, "app_name": app_name}),
            severity=severity,
            priority=priority,
            dedupe_key=f"android.current_app_changed:{package_name}",
        )
        return self.push_event(event)

    def push_device_state_event(
        self,
        battery_level: int,
        screen_on: bool,
        *,
        severity: int = 1,
        priority: EventPriority = EventPriority.BACKGROUND,
    ) -> bool:
        """Push an android.device_state event."""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="android.device_state",
            source_server_type=ServerType.ANDROID,
            source_server_id=ANDROID_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=json.dumps({"battery_level": battery_level, "screen_on": screen_on}),
            severity=severity,
            priority=priority,
            dedupe_key=f"android.device_state:{battery_level}:{screen_on}",
        )
        return self.push_event(event)

    def push_action_result_event(
        self,
        capability_id: str,
        success: bool,
        output: dict[str, Any] | None = None,
        error: str = "",
        *,
        severity: int = 2,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Push an android.action_completed or android.action_failed event."""
        event_type = "android.action_completed" if success else "android.action_failed"
        payload = json.dumps(
            {
                "capability_id": capability_id,
                "success": success,
                "output": output or {},
                "error": error,
                "timestamp_ms": int(time.time() * 1000),
            }
        )
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            source_server_type=ServerType.ANDROID,
            source_server_id=ANDROID_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=payload,
            severity=severity,
            priority=priority,
            dedupe_key=f"{event_type}:{capability_id}:{success}",
        )
        return self.push_event(event)

    def push_permission_missing_event(
        self,
        permission: str,
        *,
        severity: int = 7,
        priority: EventPriority = EventPriority.URGENT,
    ) -> bool:
        """Push an android.permission_missing event (wakes AI)."""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="android.permission_missing",
            source_server_type=ServerType.ANDROID,
            source_server_id=ANDROID_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=json.dumps({"permission": permission, "timestamp_ms": int(time.time() * 1000)}),
            severity=severity,
            priority=priority,
            dedupe_key=f"android.permission_missing:{permission}",
        )
        return self.push_event(event)

    # ── Capability Invocation ────────────────────────────────

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Invoke an Android capability via the provider (for testing)."""
        if not self._provider.is_available():
            return {"error": "Android device is not available", "capability_id": capability_id}

        params = params or {}
        try:
            # ── Observe ──
            if capability_id == "android.get_notifications":
                return {"notifications": self._provider.get_notifications(params.get("max_count", 0))}
            elif capability_id == "android.get_current_app":
                return self._provider.get_current_app()
            elif capability_id == "android.get_device_info":
                return self._provider.get_device_info()
            elif capability_id == "android.get_screenshot":
                return self._provider.get_screenshot(params.get("quality", 80))
            elif capability_id == "android.get_ui_tree":
                return self._provider.get_ui_tree(params.get("include_invisible", False))

            # ── Overlay ──
            elif capability_id == "android.show_overlay":
                return self._provider.show_overlay(
                    params["text"],
                    params.get("x", 100),
                    params.get("y", 100),
                    params.get("duration_ms", 5000),
                )
            elif capability_id == "android.hide_overlay":
                return self._provider.hide_overlay(params.get("overlay_id", ""))

            # ── Actions ──
            elif capability_id == "android.tap":
                return self._provider.tap(params["x"], params["y"], params.get("duration_ms", 0))
            elif capability_id == "android.swipe":
                return self._provider.swipe(
                    params["start_x"],
                    params["start_y"],
                    params["end_x"],
                    params["end_y"],
                    params.get("duration_ms", 300),
                )
            elif capability_id == "android.type_text":
                # Check for password field
                if params.get("is_password_field"):
                    return {"error": "Cannot type into password fields", "capability_id": capability_id}
                return self._provider.type_text(params["text"])
            elif capability_id == "android.press_back":
                return self._provider.press_back()
            elif capability_id == "android.press_home":
                return self._provider.press_home()
            elif capability_id == "android.open_app":
                return self._provider.open_app(params["package_name"], params.get("activity_name", ""))

            else:
                return {"error": f"Unknown capability: {capability_id}"}
        except KeyError as e:
            return {"error": f"Missing required parameter: {e}", "capability_id": capability_id}
        except Exception as e:
            return {"error": str(e), "capability_id": capability_id}

    # ── Retry / Backoff ──────────────────────────────────────

    def connect_with_retry(self) -> bool:
        """Attempt to connect to Android device with exponential backoff."""
        delay_ms = self._retry.base_delay_ms
        for attempt in range(self._retry.max_retries):
            self._stats.retry_count = attempt + 1
            self._stats.last_attempt_at_ms = int(time.time() * 1000)
            self._stats.state = ConnectionState.CONNECTING
            if self._provider.is_available():
                if self.register():
                    return True
            time.sleep(delay_ms / 1000.0)
            delay_ms = min(delay_ms * self._retry.backoff_factor, self._retry.max_delay_ms)
        self._stats.state = ConnectionState.FAILED
        self._stats.last_error = f"Failed to connect after {self._retry.max_retries} attempts"
        return False
