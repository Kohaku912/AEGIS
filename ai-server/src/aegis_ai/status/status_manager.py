"""Status Manager — centralized server health monitoring.

Replaces direct _check_port() calls in dashboard routes.
Background health checks with cached snapshots for non-blocking reads.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import threading
import time
import urllib.request
from enum import Enum
from typing import Any

logger = logging.getLogger("aegis_ai.status.status_manager")


class ServerStatus(Enum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    DISABLED = "disabled"
    UNCONFIGURED = "unconfigured"


def _env_host(name: str, default: str = "localhost") -> str:
    return os.getenv(name, default)


def _env_port(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _default_servers() -> dict[str, tuple[str, int]]:
    return {
        "ai-server": (_env_host("AI_SERVER_HOST"), _env_port("AEGIS_GRPC_PORT", 50051)),
        "pc-server": (_env_host("PC_SERVER_HOST"), _env_port("PC_SERVER_PORT", 50052)),
        "browser-server": (_env_host("BROWSER_SERVER_HOST"), _env_port("BROWSER_SERVER_PORT", 50053)),
        "android-server": (_env_host("ANDROID_SERVER_HOST"), _env_port("ANDROID_SERVER_PORT", 50054)),
        "room-server": (_env_host("ROOM_SERVER_HOST"), _env_port("ROOM_SERVER_PORT", 50055)),
        "dev-server": (_env_host("DEV_SERVER_HOST"), _env_port("DEV_SERVER_PORT", 50056)),
        "dashboard": (_env_host("DASHBOARD_HOST"), _env_port("DASHBOARD_PORT", 8090)),
    }


def _server_env_prefix(server_id: str) -> str:
    return server_id.upper().replace("-", "_")


def _disabled_servers() -> set[str]:
    raw = os.getenv("AEGIS_DISABLED_SERVERS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def _server_enabled(server_id: str) -> bool:
    if server_id in _disabled_servers():
        return False
    key = f"{_server_env_prefix(server_id)}_ENABLED"
    raw = os.getenv(key)
    if raw is None and server_id == "room-server":
        raw = os.getenv("ROOM_SERVER_ENABLED")
    if raw is None and server_id == "dev-server":
        raw = os.getenv("DEV_SERVER_ENABLED")
    if raw is None:
        return True
    return raw.strip().lower() not in {"0", "false", "no", "off", "disabled", "unconfigured"}


class StatusManager:
    """Centralized server status monitoring with background checks.

    Provides cached snapshots for non-blocking dashboard reads.
    Publishes status.change events when server state changes.

    Parameters
    ----------
    event_manager:
        Optional EventManager for publishing status.change events.
    check_interval:
        Background check interval in seconds (default: 60).
    timeout:
        Per-server check timeout in seconds (default: 3).
    """

    def __init__(
        self,
        event_manager: Any = None,
        check_interval: float = 60.0,
        timeout: float = 3.0,
    ) -> None:
        self._event_manager = event_manager
        self._check_interval = check_interval
        self._timeout = timeout

        self._servers: dict[str, tuple[str, int]] = _default_servers()
        self._status: dict[str, dict[str, Any]] = {}
        self._previous_status: dict[str, str] = {}
        self._lock = threading.Lock()
        self._check_thread: threading.Thread | None = None
        self._running = False

        for server_id, (host, port) in self._servers.items():
            enabled = _server_enabled(server_id)
            self._status[server_id] = {
                "server_id": server_id,
                "status": ServerStatus.UNKNOWN.value if enabled else ServerStatus.UNCONFIGURED.value,
                "host": host,
                "port": port,
                "last_check_ms": 0,
                "last_change_ms": 0,
                "error": None if enabled else "Server disabled or unconfigured by environment",
                "mode": "enabled" if enabled else "unconfigured",
            }

    # ── Public API ────────────────────────────────────────────

    def get_snapshot(self) -> dict[str, dict[str, Any]]:
        """Return cached status snapshot for all servers. Non-blocking."""
        with self._lock:
            return dict(self._status)

    def get_server_status(self, server_id: str) -> dict[str, Any] | None:
        """Return cached status for a single server. Non-blocking."""
        with self._lock:
            return self._status.get(server_id)

    def mark_online(self, server_id: str) -> None:
        """Manually mark a server as online."""
        self._update_status(server_id, ServerStatus.ONLINE)

    def mark_offline(self, server_id: str, error: str = "") -> None:
        """Manually mark a server as offline."""
        self._update_status(server_id, ServerStatus.OFFLINE, error=error)

    def mark_degraded(self, server_id: str, error: str = "") -> None:
        """Manually mark a server as degraded."""
        self._update_status(server_id, ServerStatus.DEGRADED, error=error)

    def update_heartbeat(self, server_id: str) -> None:
        """Update heartbeat timestamp for a server."""
        with self._lock:
            if server_id in self._status:
                self._status[server_id]["last_check_ms"] = int(time.time() * 1000)
                if self._status[server_id]["status"] == ServerStatus.UNKNOWN.value:
                    self._status[server_id]["status"] = ServerStatus.ONLINE.value

    def register_server(self, server_id: str, host: str, port: int) -> None:
        """Register a server for health checking."""
        with self._lock:
            enabled = _server_enabled(server_id)
            self._servers[server_id] = (host, port)
            self._status[server_id] = {
                "server_id": server_id,
                "status": ServerStatus.UNKNOWN.value if enabled else ServerStatus.UNCONFIGURED.value,
                "host": host,
                "port": port,
                "last_check_ms": 0,
                "last_change_ms": 0,
                "error": None if enabled else "Server disabled or unconfigured by environment",
                "mode": "enabled" if enabled else "unconfigured",
            }

    # ── Background checks ─────────────────────────────────────

    def start_background_checks(self) -> None:
        """Start background health check thread."""
        if self._running:
            return
        self._running = True
        self._check_thread = threading.Thread(
            target=self._background_loop, daemon=True, name="status-check"
        )
        self._check_thread.start()
        logger.info("StatusManager background checks started (interval=%ss)", self._check_interval)

    def stop_background_checks(self) -> None:
        """Stop background health check thread."""
        self._running = False
        if self._check_thread is not None:
            self._check_thread.join(timeout=5)
            self._check_thread = None

    def check_now(self) -> dict[str, dict[str, Any]]:
        """Run health checks immediately and return snapshot."""
        self._run_checks()
        return self.get_snapshot()

    # ── Internal ──────────────────────────────────────────────

    def _background_loop(self) -> None:
        while self._running:
            try:
                self._run_checks()
            except Exception:
                logger.debug("Status check failed", exc_info=True)
            time.sleep(self._check_interval)

    def _run_checks(self) -> None:
        with self._lock:
            servers = dict(self._servers)

        for server_id, (host, port) in servers.items():
            if not _server_enabled(server_id):
                old_status = self._status.get(server_id, {}).get("status", ServerStatus.UNKNOWN.value)
                with self._lock:
                    self._status[server_id]["last_check_ms"] = int(time.time() * 1000)
                    self._status[server_id]["status"] = ServerStatus.UNCONFIGURED.value
                    self._status[server_id]["mode"] = "unconfigured"
                    self._status[server_id]["error"] = "Server disabled or unconfigured by environment"
                    if old_status != ServerStatus.UNCONFIGURED.value:
                        self._status[server_id]["last_change_ms"] = int(time.time() * 1000)
                        self._publish_change(server_id, old_status, ServerStatus.UNCONFIGURED.value)
                continue

            if server_id == "android-server":
                with self._lock:
                    self._status[server_id]["last_check_ms"] = int(time.time() * 1000)
                continue

            old_status = self._status.get(server_id, {}).get("status", ServerStatus.UNKNOWN.value)
            details: dict[str, Any] = {}
            if server_id == "browser-server":
                new_status, details = self._check_browser_health(host, port)
                is_up = new_status in {ServerStatus.ONLINE.value, ServerStatus.DEGRADED.value}
            else:
                is_up = self._check_port(host, port)
                new_status = ServerStatus.ONLINE.value if is_up else ServerStatus.OFFLINE.value

            with self._lock:
                self._status[server_id]["last_check_ms"] = int(time.time() * 1000)
                self._status[server_id]["mode"] = str(details.get("mode") or "enabled")
                self._status[server_id].update(details)
                self._status[server_id]["error"] = (
                    str(details.get("degraded_reason") or "") or None
                    if is_up
                    else str(details.get("error") or f"Port {port} unreachable")
                )
                if self._status[server_id]["status"] != new_status:
                    self._status[server_id]["status"] = new_status
                    self._status[server_id]["last_change_ms"] = int(time.time() * 1000)
                    self._publish_change(server_id, old_status, new_status)

    def _check_port(self, host: str, port: int) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self._timeout)
            s.connect((host, port))
            s.close()
            return True
        except Exception:
            return False

    def _check_browser_health(self, host: str, port: int) -> tuple[str, dict[str, Any]]:
        """Read Browser Server's structured health instead of inferring health from an open port."""
        try:
            with urllib.request.urlopen(f"http://{host}:{port}/health", timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            health = str(payload.get("status") or "").lower()
            status = ServerStatus.DEGRADED.value if health == "degraded" else ServerStatus.ONLINE.value
            return status, {
                "capabilities": int(payload.get("capabilities", 0) or 0),
                "version": str(payload.get("version") or ""),
                "mode": str(payload.get("mode") or "enabled"),
                "browser_use_available": bool(payload.get("browser_use_available", False)),
                "playwright_available": bool(payload.get("playwright_available", False)),
                "profile_root": str(payload.get("profile_root") or ""),
                "profile_name": str(payload.get("profile_name") or ""),
                "headless": bool(payload.get("headless", True)),
                "resources": dict(payload.get("resources") or {}),
                "degraded_reason": str(payload.get("degraded_reason") or ""),
                "recovery_hint": str(payload.get("recovery_hint") or ""),
            }
        except Exception as exc:
            if self._check_port(host, port):
                return ServerStatus.DEGRADED.value, {
                    "degraded_reason": f"Browser health endpoint failed: {exc}",
                    "recovery_hint": "Inspect Browser Server health and logs.",
                }
            return ServerStatus.OFFLINE.value, {"error": f"Port {port} unreachable"}

    def _update_status(self, server_id: str, status: ServerStatus, error: str = "") -> None:
        with self._lock:
            if server_id not in self._status:
                return
            old = self._status[server_id]["status"]
            self._status[server_id]["status"] = status.value
            self._status[server_id]["last_change_ms"] = int(time.time() * 1000)
            self._status[server_id]["error"] = error or None
            if old != status.value:
                self._publish_change(server_id, old, status.value)

    def _publish_change(self, server_id: str, old_status: str, new_status: str) -> None:
        if self._event_manager is None:
            return
        try:
            from aegis_schema.models import Event, EventPriority
            event = Event(
                event_type="status.changed",
                source="status_manager",
                priority=EventPriority.NORMAL,
                payload={
                    "server_id": server_id,
                    "old_status": old_status,
                    "new_status": new_status,
                },
            )
            self._event_manager.publish(event)
        except Exception:
            logger.debug("Failed to publish status.change event", exc_info=True)
