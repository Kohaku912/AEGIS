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
        "dashboard": (_env_host("DASHBOARD_HOST"), _env_port("DASHBOARD_PORT", 8090)),
    }


def _server_env_prefix(server_id: str) -> str:
    return server_id.upper().replace("-", "_")


def _disabled_servers() -> set[str]:
    raw = os.getenv("AEGIS_DISABLED_SERVERS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def _server_enabled(server_id: str) -> bool:
    return _server_configuration_state(server_id) == ServerStatus.ONLINE


def _server_configuration_state(server_id: str) -> ServerStatus:
    """Return the configured lifecycle state before network health is checked."""
    if server_id in _disabled_servers():
        return ServerStatus.DISABLED
    key = f"{_server_env_prefix(server_id)}_ENABLED"
    raw = os.getenv(key)
    if raw is None and server_id == "room-server":
        raw = os.getenv("ROOM_SERVER_ENABLED")
    if raw is None:
        if server_id == "room-server":
            return ServerStatus.UNCONFIGURED
        return ServerStatus.ONLINE
    normalized = raw.strip().lower()
    if normalized in {"0", "false", "no", "off", "disabled"}:
        return ServerStatus.DISABLED
    if normalized in {"", "unconfigured"}:
        return ServerStatus.UNCONFIGURED
    return ServerStatus.ONLINE


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
        # Wakes the background loop out of its inter-check sleep. Without it, ``stop``
        # can only wait out the full interval (60s by default) and then gives up.
        self._stop_event = threading.Event()

        for server_id, (host, port) in self._servers.items():
            configured = _server_configuration_state(server_id)
            enabled = configured == ServerStatus.ONLINE
            self._status[server_id] = {
                "server_id": server_id,
                "status": ServerStatus.DEGRADED.value if enabled else configured.value,
                "host": host,
                "port": port,
                "last_check_ms": 0,
                "last_change_ms": 0,
                "error": "Awaiting first health check" if enabled else f"Server is {configured.value} by environment",
                "mode": "checking" if enabled else configured.value,
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
                if self._status[server_id]["status"] in {
                    ServerStatus.UNKNOWN.value,
                    ServerStatus.DEGRADED.value,
                } and _server_enabled(server_id):
                    self._status[server_id]["status"] = ServerStatus.ONLINE.value

    def register_server(self, server_id: str, host: str, port: int) -> None:
        """Register a server for health checking."""
        with self._lock:
            configured = _server_configuration_state(server_id)
            enabled = configured == ServerStatus.ONLINE
            self._servers[server_id] = (host, port)
            self._status[server_id] = {
                "server_id": server_id,
                "status": ServerStatus.DEGRADED.value if enabled else configured.value,
                "host": host,
                "port": port,
                "last_check_ms": 0,
                "last_change_ms": 0,
                "error": "Awaiting first health check" if enabled else f"Server is {configured.value} by environment",
                "mode": "checking" if enabled else configured.value,
            }

    # ── Background checks ─────────────────────────────────────

    def start_background_checks(self) -> None:
        """Start background health check thread."""
        if self._running:
            return
        self._running = True
        self._stop_event.clear()
        self._check_thread = threading.Thread(
            target=self._background_loop, daemon=True, name="status-check"
        )
        self._check_thread.start()
        logger.info("StatusManager background checks started (interval=%ss)", self._check_interval)

    def stop_background_checks(self) -> None:
        """Stop background health check thread, promptly.

        Setting ``_running = False`` alone is not enough: the loop spends almost all of
        its life waiting out ``self._check_interval`` (60s by default), so a bare
        ``join(timeout=5)`` returns with the thread still alive — and it then keeps
        running, and keeps probing the LAN, until the interval happens to expire.
        Setting the stop event interrupts that wait so ``join`` actually joins.
        """
        self._running = False
        self._stop_event.set()

        thread = self._check_thread
        if thread is not None:
            thread.join(timeout=5)
            if thread.is_alive():
                logger.warning(
                    "StatusManager background check thread did not stop within 5s; it will "
                    "exit on its next wake-up"
                )
            else:
                self._check_thread = None

    def check_now(self) -> dict[str, dict[str, Any]]:
        """Run health checks immediately and return snapshot."""
        self._run_checks()
        return self.get_snapshot()

    # ── Internal ──────────────────────────────────────────────

    def _background_loop(self) -> None:
        while self._running:
            try:
                self._run_checks(abort=self._stop_event)
            except Exception:
                logger.debug("Status check failed", exc_info=True)
            if self._stop_event.wait(self._check_interval):
                break

    def _run_checks(self, *, abort: threading.Event | None = None) -> None:
        """Run one health-check sweep.

        ``abort`` is supplied by the background loop, so that ``stop()`` takes effect at
        a server boundary instead of after the whole sweep. A sweep touches the network,
        so finishing one can take many seconds — long enough for the thread to outlive
        the runtime that started it, and long enough that the join in
        ``stop_background_checks`` gives up and reports a thread that never stopped.

        ``check_now()`` passes nothing: an explicit synchronous request should always run
        to completion, even on a manager whose background checks were never started (for
        which ``_running`` is ``False`` but nothing has been stopped either).
        """
        with self._lock:
            servers = dict(self._servers)

        # Collect status changes and publish them only AFTER releasing the lock.
        # Publishing while holding ``self._lock`` deadlocks: event subscribers
        # (e.g. the L1 pipeline via ``_compact_world_state_for_l1``) call back
        # into ``get_snapshot()``, which needs the same non-reentrant lock.
        pending_changes: list[tuple[str, str, str]] = []

        for server_id, (host, port) in servers.items():
            if abort is not None and abort.is_set():
                return

            configured = _server_configuration_state(server_id)
            if configured != ServerStatus.ONLINE:
                with self._lock:
                    old_status = self._status.get(server_id, {}).get(
                        "status", ServerStatus.UNKNOWN.value
                    )
                    self._status[server_id]["last_check_ms"] = int(time.time() * 1000)
                    self._status[server_id]["status"] = configured.value
                    self._status[server_id]["mode"] = configured.value
                    self._status[server_id]["error"] = f"Server is {configured.value} by environment"
                    if old_status != configured.value:
                        self._status[server_id]["last_change_ms"] = int(time.time() * 1000)
                        pending_changes.append((server_id, old_status, configured.value))
                continue

            if server_id == "android-server":
                with self._lock:
                    self._status[server_id]["last_check_ms"] = int(time.time() * 1000)
                continue

            details: dict[str, Any] = {}
            resolved_host = host
            if server_id in {"pc-server", "room-server"}:
                resolved = self._resolve_endpoint(server_id, host, port)
                if resolved:
                    resolved_host, port = resolved
                    with self._lock:
                        self._servers[server_id] = (resolved_host, port)
                        self._status[server_id]["host"] = resolved_host
                        self._status[server_id]["port"] = port

            if server_id == "browser-server":
                new_status, details = self._check_browser_health(resolved_host, port)
                is_up = new_status in {ServerStatus.ONLINE.value, ServerStatus.DEGRADED.value}
            else:
                is_up = self._check_port(resolved_host, port)
                new_status = ServerStatus.ONLINE.value if is_up else ServerStatus.OFFLINE.value
                if not is_up and server_id in {"pc-server", "room-server"}:
                    details = {"error": f"Port {port} unreachable (host={resolved_host}; candidates/LAN scan failed)"}

            with self._lock:
                old_status = self._status.get(server_id, {}).get(
                    "status", ServerStatus.UNKNOWN.value
                )
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
                    pending_changes.append((server_id, old_status, new_status))

        for server_id, old_status, new_status in pending_changes:
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

    def _resolve_endpoint(self, server_id: str, host: str, port: int) -> tuple[str, int] | None:
        """Re-resolve pc/room hosts when DHCP assigns a new LAN IP."""
        try:
            from aegis_ai.net.endpoint_resolver import resolve_tcp_endpoint

            # ``allow_lan_scan`` is deliberately left unset so the documented
            # ``AEGIS_LAN_SCAN_ENABLED`` switch decides. Passing ``True`` here used to
            # override it, which meant an operator (or a test run) could not turn LAN
            # discovery off - the switch was documented and had no effect on this path.
            return resolve_tcp_endpoint(
                server_id,
                port=port,
                timeout=min(self._timeout, 0.5),
            )
        except Exception:
            logger.debug("Endpoint resolve failed for %s", server_id, exc_info=True)
            if self._check_port(host, port):
                return host, port
            return None

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
        change: tuple[str, str, str] | None = None
        with self._lock:
            if server_id not in self._status:
                return
            configured = _server_configuration_state(server_id)
            if configured != ServerStatus.ONLINE:
                status = configured
                error = f"Server is {configured.value} by environment"
            old = self._status[server_id]["status"]
            self._status[server_id]["status"] = status.value
            self._status[server_id]["last_change_ms"] = int(time.time() * 1000)
            self._status[server_id]["error"] = error or None
            if old != status.value:
                change = (server_id, old, status.value)
        # Publish outside the lock (see _run_checks for why).
        if change is not None:
            self._publish_change(*change)

    def _publish_change(self, server_id: str, old_status: str, new_status: str) -> None:
        if self._event_manager is None:
            return
        try:
            from aegis_ai.event.helpers import build_event
            event = build_event(
                "status.changed",
                source_server_id="status_manager",
                payload={
                    "server_id": server_id,
                    "old_status": old_status,
                    "new_status": new_status,
                },
            )
            self._event_manager.publish(event)
        except Exception:
            logger.debug("Failed to publish status.change event", exc_info=True)
