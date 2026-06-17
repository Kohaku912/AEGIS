"""Architecture guard tests — verify that architecture violations have been fixed.

These tests ensure that:
1. No socket/urllib in dashboard routes
2. No plan.has_approval_required_steps() in router
3. No direct capability_catalog access in dashboard routes
4. No direct memory backend constructors in dashboard routes
5. No read_all() in backup/export.py and grpc_server.py
6. All execution paths go through TaskManager
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest


# Paths to check
DASHBOARD_ROUTES = Path(__file__).parent.parent / "src" / "aegis_ai" / "web" / "dashboard_routes.py"
ROUTER = Path(__file__).parent.parent / "src" / "aegis_ai" / "interaction" / "router.py"
EXPORT = Path(__file__).parent.parent / "src" / "aegis_ai" / "backup" / "export.py"
GRPC_SERVER = Path(__file__).parent.parent / "src" / "aegis_ai" / "grpc_server.py"


def _read_file(path: Path) -> str:
    """Read file content."""
    return path.read_text(encoding="utf-8")


class TestDashboardRoutesGuards:
    """Tests for dashboard_routes.py architecture guards."""

    def test_no_socket_import(self):
        """Verify no socket import in dashboard routes."""
        content = _read_file(DASHBOARD_ROUTES)
        assert "import socket" not in content, "socket import found in dashboard_routes.py"

    def test_no_urllib_import(self):
        """Verify no urllib import in dashboard routes."""
        content = _read_file(DASHBOARD_ROUTES)
        assert "import urllib" not in content, "urllib import found in dashboard_routes.py"

    def test_no_check_port_function(self):
        """Verify _check_port function is removed."""
        content = _read_file(DASHBOARD_ROUTES)
        assert "def _check_port" not in content, "_check_port function found in dashboard_routes.py"

    def test_no_http_json_function(self):
        """Verify _http_json function is removed."""
        content = _read_file(DASHBOARD_ROUTES)
        assert "def _http_json" not in content, "_http_json function found in dashboard_routes.py"

    def test_no_socket_connect(self):
        """Verify no socket.connect in dashboard routes."""
        content = _read_file(DASHBOARD_ROUTES)
        assert "socket.connect" not in content, "socket.connect found in dashboard_routes.py"

    def test_no_urllib_request(self):
        """Verify no urllib.request in dashboard routes."""
        content = _read_file(DASHBOARD_ROUTES)
        assert "urllib.request" not in content, "urllib.request found in dashboard_routes.py"

    def test_no_direct_capability_catalog_access(self):
        """Verify no direct capability_catalog access in dashboard routes."""
        content = _read_file(DASHBOARD_ROUTES)
        # Check for direct access patterns
        patterns = [
            r"self\._runtime\.capability_catalog\.",
            r"runtime\.capability_catalog\.",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content)
            assert len(matches) == 0, f"Direct capability_catalog access found: {matches}"

    def test_no_direct_memory_backend_constructors(self):
        """Verify no direct memory backend constructors in dashboard routes."""
        content = _read_file(DASHBOARD_ROUTES)
        # Check for direct constructor patterns (allow fallback in _get_mem_backend)
        patterns = [
            r"AdvancedMemory\(",
            r"EpisodicMemory\(",
            r"SemanticMemory\(",
            r"SkillMemory\(",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content)
            assert len(matches) == 0, f"Direct memory backend constructor found: {pattern}"

        # ActionTraceMemory is allowed as fallback when MemoryManager doesn't have it
        action_trace_matches = re.findall(r"ActionTraceMemory\(", content)
        # Should only appear in fallback pattern (if atm is None)
        assert len(action_trace_matches) <= 3, f"Too many ActionTraceMemory constructors: {len(action_trace_matches)}"


class TestRouterGuards:
    """Tests for interaction/router.py architecture guards."""

    def test_no_plan_based_approval_check(self):
        """Verify no plan.has_approval_required_steps() in router control flow."""
        content = _read_file(ROUTER)
        # Check for the short-circuit pattern
        assert "has_approval_required_steps" not in content, "has_approval_required_steps found in router.py"


class TestExportGuards:
    """Tests for backup/export.py architecture guards."""

    def test_no_read_all_in_export(self):
        """Verify no read_all() in export.py."""
        content = _read_file(EXPORT)
        # Check for read_all() calls (not method definitions)
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if ".read_all()" in line and "def " not in line:
                pytest.fail(f"read_all() found in export.py at line {i}: {line.strip()}")


class TestGrpcServerGuards:
    """Tests for grpc_server.py architecture guards."""

    def test_no_read_all_in_grpc(self):
        """Verify no read_all() in grpc_server.py."""
        content = _read_file(GRPC_SERVER)
        # Check for read_all() calls (not method definitions)
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if ".read_all()" in line and "def " not in line:
                pytest.fail(f"read_all() found in grpc_server.py at line {i}: {line.strip()}")


class TestTaskManagerIntegration:
    """Tests for TaskManager integration."""

    def test_chat_send_uses_task_manager(self):
        """Verify chat_send uses TaskManager."""
        content = _read_file(DASHBOARD_ROUTES)
        assert "task_manager.create_task" in content, "TaskManager.create_task not found in chat_send"

    def test_router_uses_task_manager(self):
        """Verify router uses TaskManager."""
        content = _read_file(ROUTER)
        assert "task_manager" in content, "task_manager not found in router.py"


class TestSleepManagerIntegration:
    """Tests for SleepManager integration."""

    def test_sleep_manager_has_consolidation_system(self):
        """Verify SleepManager has consolidation_system parameter."""
        sleep_path = Path(__file__).parent.parent / "src" / "aegis_ai" / "memory" / "sleep.py"
        content = _read_file(sleep_path)
        assert "consolidation_system" in content, "consolidation_system not found in sleep.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
