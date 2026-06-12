"""Tests for Operations Dashboard — observability views and Flask routes."""

from __future__ import annotations

import json
import time

from aegis_ai.audit import AuditLog
from aegis_ai.observability.audit_view import AuditView
from aegis_ai.observability.capability_health import CapabilityHealthView
from aegis_ai.observability.event_view import EventView
from aegis_ai.observability.memory_view import MemoryView
from aegis_ai.observability.server_health import ServerHealthView
from aegis_ai.settings.store import SettingsStore
from aegis_ai.web.dashboard_routes import DashboardApp
from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    RiskLevel,
    ServerInfo,
    ServerStatus,
    ServerType,
)
from approval import ApprovalStore
from event_bus import EventBus
from tool_registry import ToolRegistry

# ── Helpers ──────────────────────────────────────────────────


def _make_event(event_type: str = "test.event", severity: int = 3) -> Event:
    return Event(
        event_id=f"evt_{int(time.time() * 1000)}",
        event_type=event_type,
        source_server_type=ServerType.PC,
        source_server_id="test-server",
        timestamp_ms=int(time.time() * 1000),
        payload_json="{}",
        severity=severity,
        priority=EventPriority.NORMAL,
    )


def _setup_dashboard() -> tuple[DashboardApp, EventBus, ToolRegistry, AuditLog, ApprovalStore]:
    bus = EventBus()
    registry = ToolRegistry()
    audit = AuditLog(path="data/test_dashboard_audit.jsonl")
    approval_store = ApprovalStore()
    settings_store = SettingsStore(
        path="data/test_dashboard_settings.json",
        audit_path="data/test_dashboard_settings_audit.jsonl",
    )

    # Register a test server and capability
    registry.register_server(ServerInfo(
        server_id="test-server", server_type=ServerType.PC,
        version="0.1.0", status=ServerStatus.ONLINE,
    ))
    registry.register_capability(Capability(
        id="pc.screenshot", name="Screenshot",
        description="Take screenshot",
        server_type=ServerType.PC, risk_level=RiskLevel.READ_ONLY,
    ))

    app = DashboardApp()

    return app, bus, registry, audit, approval_store


# ═══════════════════════════════════════════════════════════════
# 1. Server Health
# ═══════════════════════════════════════════════════════════════


class TestServerHealth:
    """Server health view shows connected servers."""

    def test_get_all_servers(self):
        """Returns registered servers."""
        _, _, registry, _, _ = _setup_dashboard()
        view = ServerHealthView(tool_registry=registry)
        servers = view.get_all_servers()
        assert len(servers) >= 1
        assert servers[0]["server_id"] == "test-server"

    def test_get_summary(self):
        """Returns server summary."""
        _, _, registry, _, _ = _setup_dashboard()
        view = ServerHealthView(tool_registry=registry)
        summary = view.get_summary()
        assert summary["total_servers"] >= 1
        assert summary["online_servers"] >= 1


# ═══════════════════════════════════════════════════════════════
# 2. Capability Health
# ═══════════════════════════════════════════════════════════════


class TestCapabilityHealth:
    """Capability health view shows capability stats."""

    def test_get_all_capabilities(self):
        """Returns registered capabilities."""
        _, _, registry, _, _ = _setup_dashboard()
        view = CapabilityHealthView(tool_registry=registry)
        caps = view.get_all_capabilities()
        assert len(caps) >= 1

    def test_record_invocation(self):
        """Invocation recording works."""
        view = CapabilityHealthView()
        view.record_invocation("test.cap", True, 10.0)
        health = view.get_capability_health("test.cap")
        assert health["total_invocations"] == 1
        assert health["success_count"] == 1


# ═══════════════════════════════════════════════════════════════
# 3. Event View
# ═══════════════════════════════════════════════════════════════


class TestEventView:
    """Event view shows EventBus data."""

    def test_get_recent_events(self):
        """Returns recent events."""
        app, bus, _, _, _ = _setup_dashboard()
        bus.publish(_make_event("test.event"))
        view = EventView(event_bus=bus)
        events = view.get_recent_events(10)
        assert len(events) >= 1

    def test_get_stats(self):
        """Returns event stats."""
        bus = EventBus()
        bus.publish(_make_event())
        view = EventView(event_bus=bus)
        stats = view.get_stats()
        assert stats["total_published"] >= 1


# ═══════════════════════════════════════════════════════════════
# 4. Audit View
# ═══════════════════════════════════════════════════════════════


class TestAuditView:
    """Audit view shows masked audit entries."""

    def test_get_recent_entries(self):
        """Returns recent audit entries."""
        audit = AuditLog(path="data/test_dashboard_audit_view.jsonl")
        audit.log_decision("test", "cap", "ALLOW", reason="test")
        view = AuditView(audit_log=audit)
        entries = view.get_recent_entries(10)
        assert len(entries) >= 1

    def test_mask_secrets(self):
        """Secrets are masked in audit entries."""
        view = AuditView()
        masked = view._mask_text('password="secret123"')
        assert "secret123" not in masked
        assert "REDACTED" in masked


# ═══════════════════════════════════════════════════════════════
# 5. Memory View
# ═══════════════════════════════════════════════════════════════


class TestMemoryView:
    """Memory view shows memory summary."""

    def test_get_summary(self):
        """Returns memory summary."""
        view = MemoryView()
        summary = view.get_summary()
        assert "episodic_count" in summary


# ═══════════════════════════════════════════════════════════════
# 6. Dashboard Flask Routes
# ═══════════════════════════════════════════════════════════════


class TestDashboardRoutes:
    """Dashboard Flask routes return valid responses."""

    def test_home_route(self):
        """Home route returns 200."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/")
            assert resp.status_code == 200

    def test_servers_route(self):
        """Servers route returns 200."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/dashboard/servers")
            assert resp.status_code == 200

    def test_capabilities_route(self):
        """Capabilities route returns 200."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/dashboard/capabilities")
            assert resp.status_code == 200

    def test_events_route(self):
        """Events route returns 200."""
        app, bus, _, _, _ = _setup_dashboard()
        bus.publish(_make_event("test.event"))
        with app.app.test_client() as client:
            resp = client.get("/dashboard/events")
            assert resp.status_code == 200

    def test_tasks_route(self):
        """Tasks route returns 200."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/dashboard/tasks")
            assert resp.status_code == 200

    def test_memory_route(self):
        """Memory route returns 200."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/dashboard/memory")
            assert resp.status_code == 200

    def test_audit_route(self):
        """Audit route returns 200."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/dashboard/audit")
            assert resp.status_code == 200

    def test_errors_route(self):
        """Errors route returns 200."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/dashboard/errors")
            assert resp.status_code == 200

    def test_health_route(self):
        """Health route returns ok."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/health")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert data["status"] == "ok"

    def test_api_overview(self):
        """API overview returns JSON."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/api/dashboard/overview")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert "servers" in data
            assert "events" in data

    def test_api_events(self):
        """API events returns JSON."""
        app, bus, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/api/dashboard/events")
            assert resp.status_code == 200

    def test_api_capabilities(self):
        """API capabilities returns JSON."""
        app, _, _, _, _ = _setup_dashboard()
        with app.app.test_client() as client:
            resp = client.get("/api/dashboard/capabilities")
            assert resp.status_code == 200
