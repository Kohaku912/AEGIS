"""Tests for PC Server Windows Host integration.

These tests verify the connection between Docker AI Server
and Windows host PC Server.

Markers:
    real_pc_host — Requires running PC Server on Windows host
    e2e — Full end-to-end integration
"""

from __future__ import annotations

import json
import socket

import pytest

PC_HOST = "localhost"
PC_PORT = 50052


def _send_pc_command(command: str, host: str = PC_HOST, port: int = PC_PORT, timeout: float = 5.0) -> str | None:
    """Send a command to PC Server and return response."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.sendall(f"{command}\n".encode())
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if b"\n" in response:
                break
        sock.close()
        return response.decode().strip()
    except Exception:
        return None


def _pc_server_available() -> bool:
    """Check if PC Server is running."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((PC_HOST, PC_PORT))
        sock.close()
        return True
    except Exception:
        return False


# ── Skip if PC Server not running ──────────────────────────

requires_pc_server = pytest.mark.skipif(
    not _pc_server_available(),
    reason="PC Server not running on localhost:50052",
)


# ═══════════════════════════════════════════════════════════════
# 1. Health Check
# ═══════════════════════════════════════════════════════════════


@requires_pc_server
class TestPCServerHealth:
    """PC Server health endpoint tests."""

    def test_health_response(self):
        """Health endpoint returns valid JSON."""
        response = _send_pc_command("health")
        assert response is not None
        data = json.loads(response)
        assert data["status"] == "ok"

    def test_health_contains_version(self):
        """Health response contains version."""
        response = _send_pc_command("health")
        data = json.loads(response)
        assert "version" in data

    def test_health_contains_capabilities(self):
        """Health response contains capability count."""
        response = _send_pc_command("health")
        data = json.loads(response)
        assert "capabilities" in data
        assert data["capabilities"] > 0

    def test_health_contains_os_info(self):
        """Health response contains OS info."""
        response = _send_pc_command("health")
        data = json.loads(response)
        assert "os_name" in data


# ═══════════════════════════════════════════════════════════════
# 2. Observe Capabilities (Read-Only)
# ═══════════════════════════════════════════════════════════════


@requires_pc_server
class TestPCObserveCapabilities:
    """PC Server observe (read-only) capability tests."""

    def test_os_info(self):
        """OS info returns valid data."""
        response = _send_pc_command("os_info")
        assert response is not None
        data = json.loads(response)
        assert "os_name" in data
        assert "architecture" in data

    def test_screenshot(self):
        """Screenshot returns result."""
        response = _send_pc_command("screenshot")
        assert response is not None
        data = json.loads(response)
        assert "width" in data
        assert "height" in data

    def test_active_window(self):
        """Active window returns result."""
        response = _send_pc_command("active_window")
        assert response is not None
        data = json.loads(response)
        assert "title" in data
        assert "pid" in data

    def test_windows_list(self):
        """Window list returns result."""
        response = _send_pc_command("windows")
        assert response is not None
        data = json.loads(response)
        assert isinstance(data, list)


# ═══════════════════════════════════════════════════════════════
# 3. Integration E2E
# ═══════════════════════════════════════════════════════════════


@requires_pc_server
class TestPCIntegrationE2E:
    """End-to-end integration tests."""

    def test_health_then_screenshot(self):
        """Health check followed by screenshot."""
        health = _send_pc_command("health")
        assert health is not None

        screenshot = _send_pc_command("screenshot")
        assert screenshot is not None

    def test_multiple_commands_sequential(self):
        """Multiple commands work sequentially."""
        commands = ["health", "os_info", "active_window", "screenshot"]
        for cmd in commands:
            response = _send_pc_command(cmd)
            assert response is not None, f"Command '{cmd}' failed"
            data = json.loads(response)
            assert isinstance(data, dict)

    def test_unknown_command_returns_error(self):
        """Unknown command returns error."""
        response = _send_pc_command("nonexistent_command")
        assert response is not None
        # Server returns JSON error
        assert "error" in response.lower() or "ERR" in response
