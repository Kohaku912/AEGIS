"""PC Server Client — Python adapter for PC Server integration with AEGIS Core.

This module bridges the Rust PC Server with AEGIS Core's Python modules.
It provides:
- Capability registration with ToolRegistry (observe + action)
- Event push to EventBus
- Mock provider for CI testing
- Real provider stub for local development
- Retry/backoff when AEGIS Core is unavailable
- Graceful failure when PC Server is down
- File allowlist/denylist for safe file operations
- Action result event push

Architecture reference: docs/architecture.md §3.2, §4
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
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

logger = logging.getLogger("aegis.pc_server_client")


# ═══════════════════════════════════════════════════════════════
# File Safety — allowlist / denylist for file operations
# ═══════════════════════════════════════════════════════════════

# Directories that are NEVER accessible
DENYLIST_DIRS: set[str] = {
    ".ssh",
    ".gnupg",
    ".aws",
    ".gcloud",
    ".azure",
    "/etc/ssl",
    "/etc/ssh",
    "/etc/shadow",
    "/etc/passwd",
    "node_modules",
    ".git",
}

# File patterns that are NEVER accessible
DENYLIST_FILE_PATTERNS: set[str] = {
    ".pem",
    ".key",
    ".crt",
    ".p12",
    ".pfx",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    ".env",
    "credentials.json",
    "credentials.xml",
    "token",
    "secret",
    "password",
}

# Directories that are always accessible (read and write)
ALLOWLIST_DIRS: set[str] = {
    "workspace",
    "projects",
    "documents",
    "downloads",
    "desktop",
    "tmp",
    "temp",
}


def is_path_denied(path: str) -> bool:
    """Check if a file path is denied by safety rules."""
    p = Path(path)
    parts = set(p.parts)

    # Check directory denylist
    if parts & DENYLIST_DIRS:
        return True

    # Check if any parent directory is denied
    for parent in p.parents:
        if parent.name in DENYLIST_DIRS:
            return True

    # Check file pattern denylist
    name_lower = p.name.lower()
    for pattern in DENYLIST_FILE_PATTERNS:
        if pattern in name_lower:
            return True

    return False


def is_path_allowed(path: str) -> bool:
    """Check if a file path is in the allowlist."""
    p = Path(path)
    parts = set(p.parts)
    return bool(parts & ALLOWLIST_DIRS)


# ═══════════════════════════════════════════════════════════════
# Provider Protocol — abstracts real vs mock PC observation + action
# ═══════════════════════════════════════════════════════════════


class PCProvider(Protocol):
    """Protocol for PC observation providers."""

    def get_screenshot(self, display_id: int = 0) -> dict[str, Any]:
        """Capture screenshot. Returns dict with width, height, image_base64, format."""
        ...

    def get_active_window(self) -> dict[str, Any]:
        """Get active window info. Returns dict with title, process_name, pid, etc."""
        ...

    def list_windows(self) -> list[dict[str, Any]]:
        """List all visible windows."""
        ...

    def get_clipboard(self) -> str:
        """Get clipboard text content."""
        ...

    def get_os_info(self) -> dict[str, Any]:
        """Get OS information."""
        ...

    def is_available(self) -> bool:
        """Check if the PC Server / provider is reachable."""
        ...


class PCActionProvider(Protocol):
    """Protocol for PC action providers.

    Real implementations use Rust OS-native APIs (Windows SendInput).
    Mock implementations return deterministic fake results for CI.
    """

    # ── Mouse ──
    def mouse_move(self, x: int, y: int) -> dict[str, Any]:
        """Move mouse to absolute coordinates. Returns {success, x, y}."""
        ...

    def mouse_click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict[str, Any]:
        """Click at coordinates. Returns {success, x, y, button, clicks}."""
        ...

    # ── Keyboard ──
    def keyboard_type(self, text: str, interval_ms: int = 0) -> dict[str, Any]:
        """Type text. Returns {success, characters_typed}."""
        ...

    def press_hotkey(self, keys: list[str]) -> dict[str, Any]:
        """Press hotkey combination. Returns {success, keys}."""
        ...

    # ── App Control ──
    def launch_app(self, app_path: str, args: list[str] | None = None) -> dict[str, Any]:
        """Launch an application. Returns {success, pid, app_path}."""
        ...

    def close_window(self, window_id: int | None = None, process_name: str = "") -> dict[str, Any]:
        """Close a window. Returns {success, window_id}."""
        ...

    def focus_window(self, window_id: int | None = None, process_name: str = "") -> dict[str, Any]:
        """Bring window to focus. Returns {success, window_id}."""
        ...

    def move_window(self, window_id: int, x: int, y: int) -> dict[str, Any]:
        """Move window to coordinates. Returns {success, window_id, x, y}."""
        ...

    def resize_window(self, window_id: int, width: int, height: int) -> dict[str, Any]:
        """Resize window. Returns {success, window_id, width, height}."""
        ...

    # ── Overlay ──
    def show_overlay(self, text: str, x: int = 100, y: int = 100, duration_ms: int = 5000) -> dict[str, Any]:
        """Show an overlay notification. Returns {success, overlay_id}."""
        ...

    def hide_overlay(self, overlay_id: str = "") -> dict[str, Any]:
        """Hide overlay. Returns {success, overlay_id}."""
        ...

    # ── Clipboard ──
    def write_clipboard(self, text: str) -> dict[str, Any]:
        """Write to clipboard. Returns {success, characters_written}."""
        ...

    # ── File ──
    def read_file(self, path: str, max_bytes: int = 1_000_000) -> dict[str, Any]:
        """Read file contents. Returns {success, content, size_bytes, path}."""
        ...

    def write_file(self, path: str, content: str, create_dirs: bool = False) -> dict[str, Any]:
        """Write content to file. Returns {success, path, bytes_written}."""
        ...


# ═══════════════════════════════════════════════════════════════
# Mock Provider — for CI testing (no real OS calls)
# ═══════════════════════════════════════════════════════════════


class MockPCProvider:
    """Mock PC provider for CI testing. Returns deterministic fake data."""

    def __init__(self, available: bool = True) -> None:
        self._available = available
        self.call_log: list[tuple[str, dict[str, Any]]] = []
        self._clipboard: str = "[MOCK_CLIPBOARD]"
        self._overlay_visible: bool = False
        self._files: dict[str, str] = {}  # Mock filesystem

    # ── Observe ──

    def get_screenshot(self, display_id: int = 0) -> dict[str, Any]:
        self.call_log.append(("get_screenshot", {"display_id": display_id}))
        return {
            "width": 1920,
            "height": 1080,
            "image_base64": "[MOCK_SCREENSHOT]",
            "format": "png",
            "captured_at_ms": int(time.time() * 1000),
        }

    def get_active_window(self) -> dict[str, Any]:
        self.call_log.append(("get_active_window", {}))
        return {
            "title": "Mock Window — VS Code",
            "process_name": "code.exe",
            "pid": 12345,
            "x": 0,
            "y": 0,
            "width": 1920,
            "height": 1080,
        }

    def list_windows(self) -> list[dict[str, Any]]:
        self.call_log.append(("list_windows", {}))
        return [self.get_active_window()]

    def get_clipboard(self) -> str:
        self.call_log.append(("get_clipboard", {}))
        return self._clipboard

    def get_os_info(self) -> dict[str, Any]:
        self.call_log.append(("get_os_info", {}))
        return {
            "os_name": "Windows",
            "os_version": "11",
            "hostname": "DESKTOP-MOCK",
            "username": "testuser",
            "architecture": "x86_64",
        }

    def is_available(self) -> bool:
        return self._available

    # ── Mouse ──

    def mouse_move(self, x: int, y: int) -> dict[str, Any]:
        self.call_log.append(("mouse_move", {"x": x, "y": y}))
        return {"success": True, "x": x, "y": y}

    def mouse_click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict[str, Any]:
        self.call_log.append(("mouse_click", {"x": x, "y": y, "button": button, "clicks": clicks}))
        return {"success": True, "x": x, "y": y, "button": button, "clicks": clicks}

    # ── Keyboard ──

    def keyboard_type(self, text: str, interval_ms: int = 0) -> dict[str, Any]:
        self.call_log.append(("keyboard_type", {"text": text[:50], "interval_ms": interval_ms}))
        return {"success": True, "characters_typed": len(text)}

    def press_hotkey(self, keys: list[str]) -> dict[str, Any]:
        self.call_log.append(("press_hotkey", {"keys": keys}))
        return {"success": True, "keys": keys}

    # ── App Control ──

    def launch_app(self, app_path: str, args: list[str] | None = None) -> dict[str, Any]:
        self.call_log.append(("launch_app", {"app_path": app_path, "args": args}))
        return {"success": True, "pid": 99999, "app_path": app_path}

    def close_window(self, window_id: int | None = None, process_name: str = "") -> dict[str, Any]:
        self.call_log.append(("close_window", {"window_id": window_id, "process_name": process_name}))
        return {"success": True, "window_id": window_id}

    def focus_window(self, window_id: int | None = None, process_name: str = "") -> dict[str, Any]:
        self.call_log.append(("focus_window", {"window_id": window_id, "process_name": process_name}))
        return {"success": True, "window_id": window_id}

    def move_window(self, window_id: int, x: int, y: int) -> dict[str, Any]:
        self.call_log.append(("move_window", {"window_id": window_id, "x": x, "y": y}))
        return {"success": True, "window_id": window_id, "x": x, "y": y}

    def resize_window(self, window_id: int, width: int, height: int) -> dict[str, Any]:
        self.call_log.append(("resize_window", {"window_id": window_id, "width": width, "height": height}))
        return {"success": True, "window_id": window_id, "width": width, "height": height}

    # ── Overlay ──

    def show_overlay(self, text: str, x: int = 100, y: int = 100, duration_ms: int = 5000) -> dict[str, Any]:
        self.call_log.append(("show_overlay", {"text": text[:50], "x": x, "y": y}))
        self._overlay_visible = True
        return {"success": True, "overlay_id": "mock_overlay_001"}

    def hide_overlay(self, overlay_id: str = "") -> dict[str, Any]:
        self.call_log.append(("hide_overlay", {"overlay_id": overlay_id}))
        self._overlay_visible = False
        return {"success": True, "overlay_id": overlay_id or "mock_overlay_001"}

    # ── Clipboard ──

    def write_clipboard(self, text: str) -> dict[str, Any]:
        self.call_log.append(("write_clipboard", {"text": text[:50]}))
        self._clipboard = text
        return {"success": True, "characters_written": len(text)}

    # ── File ──

    def read_file(self, path: str, max_bytes: int = 1_000_000) -> dict[str, Any]:
        self.call_log.append(("read_file", {"path": path, "max_bytes": max_bytes}))
        content = self._files.get(path, f"[MOCK_FILE_CONTENT:{path}]")
        return {"success": True, "content": content[:max_bytes], "size_bytes": len(content), "path": path}

    def write_file(self, path: str, content: str, create_dirs: bool = False) -> dict[str, Any]:
        self.call_log.append(("write_file", {"path": path, "content_len": len(content)}))
        self._files[path] = content
        return {"success": True, "path": path, "bytes_written": len(content)}


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
    total_actions_executed: int = 0
    total_actions_denied: int = 0


# ═══════════════════════════════════════════════════════════════
# PC Server Capabilities — Observe + Action
# ═══════════════════════════════════════════════════════════════

PC_SERVER_ID = "pc-server-main"

PC_CAPABILITIES: list[Capability] = [
    # ── Observe (Level 0) ──
    Capability(
        id="pc.get_screenshot",
        name="Screenshot Capture",
        description="Capture the current display as a PNG image.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.READ_ONLY,
        tags=["screenshot", "observe", "read_only"],
        timeout_ms=5000,
    ),
    Capability(
        id="pc.get_active_window",
        name="Get Active Window",
        description="Return the title, process, and position of the foreground window.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.READ_ONLY,
        tags=["window", "observe", "read_only"],
        timeout_ms=1000,
    ),
    Capability(
        id="pc.list_windows",
        name="List Windows",
        description="List all visible windows with title and process info.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.READ_ONLY,
        tags=["window", "observe", "read_only"],
        timeout_ms=2000,
    ),
    Capability(
        id="pc.get_clipboard",
        name="Get Clipboard",
        description="Read the current clipboard text (secrets are redacted).",
        server_type=ServerType.PC,
        risk_level=RiskLevel.READ_ONLY,
        tags=["clipboard", "observe", "read_only"],
        timeout_ms=500,
    ),
    Capability(
        id="pc.get_os_info",
        name="Get OS Info",
        description="Return OS name, version, hostname, username, and architecture.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.READ_ONLY,
        tags=["os", "system", "observe"],
        timeout_ms=1000,
    ),
    Capability(
        id="pc.list_directory",
        name="List Directory",
        description="List files in a directory (sensitive dirs restricted).",
        server_type=ServerType.PC,
        risk_level=RiskLevel.READ_ONLY,
        tags=["files", "observe"],
        timeout_ms=3000,
    ),
    # ── Mouse (Level 1–2) ──
    Capability(
        id="pc.mouse_move",
        name="Mouse Move",
        description="Move mouse cursor to absolute screen coordinates.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["mouse", "action"],
        timeout_ms=1000,
    ),
    Capability(
        id="pc.mouse_click",
        name="Mouse Click",
        description="Click at screen coordinates. Requires approval.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["mouse_click"],
        tags=["mouse", "action", "approval_required"],
        timeout_ms=2000,
    ),
    # ── Keyboard (Level 2) ──
    Capability(
        id="pc.keyboard_type",
        name="Keyboard Type",
        description="Type text at current cursor position. Requires approval.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["keyboard_input"],
        tags=["keyboard", "action", "approval_required"],
        timeout_ms=5000,
    ),
    Capability(
        id="pc.press_hotkey",
        name="Press Hotkey",
        description="Press a hotkey combination (e.g. Ctrl+C). Requires approval.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["keyboard_input"],
        tags=["keyboard", "action", "approval_required"],
        timeout_ms=1000,
    ),
    # ── App Control (Level 1–2) ──
    Capability(
        id="pc.launch_app",
        name="Launch Application",
        description="Launch an application by path. Auto-allowed for safe apps.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["app", "action"],
        timeout_ms=5000,
    ),
    Capability(
        id="pc.close_window",
        name="Close Window",
        description="Close a window by ID or process name. Requires approval.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["window_close"],
        tags=["window", "action", "approval_required"],
        timeout_ms=2000,
    ),
    Capability(
        id="pc.focus_window",
        name="Focus Window",
        description="Bring a window to the foreground.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["window", "action"],
        timeout_ms=1000,
    ),
    Capability(
        id="pc.move_window",
        name="Move Window",
        description="Move a window to specified screen coordinates.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["window", "action"],
        timeout_ms=1000,
    ),
    Capability(
        id="pc.resize_window",
        name="Resize Window",
        description="Resize a window to specified dimensions.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["window", "action"],
        timeout_ms=1000,
    ),
    # ── Overlay (Level 1) ──
    Capability(
        id="pc.show_overlay",
        name="Show Overlay",
        description="Display an overlay notification on screen.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["overlay", "action"],
        timeout_ms=2000,
    ),
    Capability(
        id="pc.hide_overlay",
        name="Hide Overlay",
        description="Hide the current overlay notification.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["overlay", "action"],
        timeout_ms=1000,
    ),
    # ── Clipboard (Level 2) ──
    Capability(
        id="pc.write_clipboard",
        name="Write Clipboard",
        description="Write text to the system clipboard. Requires approval.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["clipboard_write"],
        tags=["clipboard", "action", "approval_required"],
        timeout_ms=1000,
    ),
    # ── File (Level 0 / Level 2) ──
    Capability(
        id="pc.read_file",
        name="Read File",
        description="Read file contents. Denied for sensitive paths.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.READ_ONLY,
        tags=["file", "observe", "read_only"],
        timeout_ms=3000,
    ),
    Capability(
        id="pc.write_file",
        name="Write File",
        description="Write content to a file. Requires approval. Denied for sensitive paths.",
        server_type=ServerType.PC,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["file_write"],
        tags=["file", "action", "approval_required"],
        timeout_ms=5000,
    ),
]


def get_pc_server_info() -> ServerInfo:
    """Create ServerInfo for the PC Server."""
    return ServerInfo(
        server_id=PC_SERVER_ID,
        server_type=ServerType.PC,
        version="0.2.0",
        status=ServerStatus.ONLINE,
        capability_ids=[cap.id for cap in PC_CAPABILITIES],
        host="localhost",
        port=50052,
        started_at_ms=int(time.time() * 1000),
    )


# ═══════════════════════════════════════════════════════════════
# PC Server Client — main integration point
# ═══════════════════════════════════════════════════════════════


class PCServerClient:
    """Python client that integrates PC Server with AEGIS Core.

    Responsibilities:
    1. Register PC capabilities with ToolRegistry
    2. Push PC events to EventBus
    3. Handle connection state and retry/backoff
    4. Graceful failure when PC Server is down
    5. Invoke capabilities through ToolBroker (with PolicyEngine enforcement)
    6. Push action result events to EventBus
    """

    def __init__(
        self,
        event_bus: Any,
        registry: Any,
        provider: Any = None,
        retry_config: RetryConfig | None = None,
        tool_broker: Any = None,
    ) -> None:
        self._event_bus = event_bus
        self._registry = registry
        self._provider = provider or MockPCProvider()
        self._retry = retry_config or RetryConfig()
        self._stats = ConnectionStats()
        self._registered = False
        self._tool_broker = tool_broker

    @property
    def stats(self) -> ConnectionStats:
        return self._stats

    @property
    def is_registered(self) -> bool:
        return self._registered

    @property
    def provider(self) -> Any:
        return self._provider

    # ── Registration ─────────────────────────────────────────

    def register(self) -> bool:
        """Register PC Server and its capabilities with AEGIS Core."""
        if not self._provider.is_available():
            self._stats.state = ConnectionState.FAILED
            self._stats.last_error = "PC Server is not available"
            logger.warning("PC Server not available — skipping registration")
            return False

        try:
            server_info = get_pc_server_info()
            self._registry.register_server(server_info)
            for cap in PC_CAPABILITIES:
                self._registry.register_capability(cap)

            self._registered = True
            self._stats.state = ConnectionState.CONNECTED
            self._stats.total_registrations = len(PC_CAPABILITIES)
            self._stats.last_connected_at_ms = int(time.time() * 1000)
            logger.info("PC Server registered %d capabilities", len(PC_CAPABILITIES))
            return True

        except Exception as e:
            self._stats.state = ConnectionState.FAILED
            self._stats.last_error = str(e)
            logger.error("PC Server registration failed: %s", e)
            return False

    def unregister(self) -> None:
        """Unregister PC Server from AEGIS Core."""
        self._registry.unregister_server(PC_SERVER_ID)
        for cap in PC_CAPABILITIES:
            self._registry.unregister_capability(cap.id)
        self._registered = False
        self._stats.state = ConnectionState.DISCONNECTED

    # ── Event Push ───────────────────────────────────────────

    def push_event(self, event: Event) -> bool:
        """Push an event to the EventBus."""
        if not self._registered:
            logger.warning("Cannot push event — PC Server not registered")
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
        """Push a pc.action_result event."""
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
            event_type="pc.action_result",
            source_server_type=ServerType.PC,
            source_server_id=PC_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=payload,
            severity=severity,
            priority=priority,
            dedupe_key=f"pc.action_result:{capability_id}:{success}",
        )
        return self.push_event(event)

    def push_window_changed_event(
        self,
        window_title: str,
        process_name: str,
        pid: int,
        *,
        severity: int = 3,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Push a pc.window_changed event."""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="pc.window_changed",
            source_server_type=ServerType.PC,
            source_server_id=PC_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=f'{{"title":"{window_title}","process":"{process_name}","pid":{pid}}}',
            severity=severity,
            priority=priority,
            dedupe_key=f"pc.window_changed:{process_name}",
        )
        return self.push_event(event)

    def push_screen_changed_event(
        self,
        *,
        severity: int = 2,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Push a pc.screen_changed event."""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="pc.screen_changed",
            source_server_type=ServerType.PC,
            source_server_id=PC_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json='{"change":"screen_updated"}',
            severity=severity,
            priority=priority,
            dedupe_key="pc.screen_changed",
        )
        return self.push_event(event)

    # ── Capability Invocation ────────────────────────────────

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Invoke a PC capability via the provider (for testing).

        In production, ToolBroker → PolicyEngine handles this.
        """
        if not self._provider.is_available():
            return {"error": "PC Server is not available", "capability_id": capability_id}

        params = params or {}
        try:
            # ── Observe ──
            if capability_id == "pc.get_screenshot":
                return self._provider.get_screenshot(params.get("display_id", 0))
            elif capability_id == "pc.get_active_window":
                return self._provider.get_active_window()
            elif capability_id == "pc.list_windows":
                return {"windows": self._provider.list_windows()}
            elif capability_id == "pc.get_clipboard":
                return {"text": self._provider.get_clipboard()}
            elif capability_id == "pc.get_os_info":
                return self._provider.get_os_info()

            # ── Mouse ──
            elif capability_id == "pc.mouse_move":
                return self._provider.mouse_move(params["x"], params["y"])
            elif capability_id == "pc.mouse_click":
                return self._provider.mouse_click(
                    params["x"],
                    params["y"],
                    params.get("button", "left"),
                    params.get("clicks", 1),
                )

            # ── Keyboard ──
            elif capability_id == "pc.keyboard_type":
                return self._provider.keyboard_type(params["text"], params.get("interval_ms", 0))
            elif capability_id == "pc.press_hotkey":
                return self._provider.press_hotkey(params["keys"])

            # ── App Control ──
            elif capability_id == "pc.launch_app":
                return self._provider.launch_app(params["app_path"], params.get("args"))
            elif capability_id == "pc.close_window":
                return self._provider.close_window(params.get("window_id"), params.get("process_name", ""))
            elif capability_id == "pc.focus_window":
                return self._provider.focus_window(params.get("window_id"), params.get("process_name", ""))
            elif capability_id == "pc.move_window":
                return self._provider.move_window(params["window_id"], params["x"], params["y"])
            elif capability_id == "pc.resize_window":
                return self._provider.resize_window(params["window_id"], params["width"], params["height"])

            # ── Overlay ──
            elif capability_id == "pc.show_overlay":
                return self._provider.show_overlay(
                    params["text"],
                    params.get("x", 100),
                    params.get("y", 100),
                    params.get("duration_ms", 5000),
                )
            elif capability_id == "pc.hide_overlay":
                return self._provider.hide_overlay(params.get("overlay_id", ""))

            # ── Clipboard ──
            elif capability_id == "pc.write_clipboard":
                return self._provider.write_clipboard(params["text"])

            # ── File ──
            elif capability_id == "pc.read_file":
                # Check denylist
                if is_path_denied(params["path"]):
                    return {"error": "Path is denied by safety rules", "path": params["path"]}
                return self._provider.read_file(params["path"], params.get("max_bytes", 1_000_000))
            elif capability_id == "pc.write_file":
                # Check denylist
                if is_path_denied(params["path"]):
                    return {"error": "Path is denied by safety rules", "path": params["path"]}
                return self._provider.write_file(params["path"], params["content"], params.get("create_dirs", False))

            else:
                return {"error": f"Unknown capability: {capability_id}"}
        except KeyError as e:
            return {"error": f"Missing required parameter: {e}", "capability_id": capability_id}
        except Exception as e:
            return {"error": str(e), "capability_id": capability_id}

    # ── Retry / Backoff ──────────────────────────────────────

    def connect_with_retry(self) -> bool:
        """Attempt to connect to PC Server with exponential backoff."""
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
