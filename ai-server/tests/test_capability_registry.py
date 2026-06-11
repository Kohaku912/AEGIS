"""Tests for CapabilityRegistry — Phase 1.x server/capability registration."""

from __future__ import annotations

import pytest

from aegis_ai.capability_registry import CapabilityRegistry
from aegis_schema.models import Capability, RiskLevel, ServerInfo, ServerType


def _make_cap(id: str, name: str = "Test", server: ServerType = ServerType.PC,
              risk: RiskLevel = RiskLevel.SAFE_ACTION,
              tags: list[str] | None = None) -> Capability:
    return Capability(id=id, name=name, description=f"Capability {id}",
                      server_type=server, risk_level=risk, tags=tags or [])


def _make_server(server_id: str = "srv-1", stype: ServerType = ServerType.PC,
                 caps: list[str] | None = None) -> ServerInfo:
    return ServerInfo(server_id=server_id, server_type=stype, capability_ids=caps or [])


class TestServerRegistration:
    def test_register_server(self):
        reg = CapabilityRegistry()
        reg.register_server(_make_server("pc-main"))
        assert reg.get_server("pc-main") is not None
        assert reg.get_server("pc-main").server_type == ServerType.PC

    def test_unregister_server(self):
        reg = CapabilityRegistry()
        reg.register_server(_make_server("pc-main"))
        reg.unregister_server("pc-main")
        assert reg.get_server("pc-main") is None

    def test_list_servers_filtered(self):
        reg = CapabilityRegistry()
        reg.register_server(_make_server("pc-1", ServerType.PC))
        reg.register_server(_make_server("android-1", ServerType.ANDROID))
        assert len(reg.list_servers(server_type=ServerType.PC)) == 1
        assert len(reg.list_servers(server_type=ServerType.ANDROID)) == 1


class TestCapabilityRegistration:
    def test_register_capability(self):
        reg = CapabilityRegistry()
        cap = _make_cap("pc.screenshot", risk=RiskLevel.READ_ONLY, tags=["observe"])
        reg.register_capability(cap)
        assert reg.get_capability("pc.screenshot") == cap

    def test_duplicate_capability_detected(self):
        """Duplicate capability IDs should overwrite (last write wins)."""
        reg = CapabilityRegistry()
        cap1 = _make_cap("pc.test", name="First")
        cap2 = _make_cap("pc.test", name="Second")
        reg.register_capability(cap1)
        reg.register_capability(cap2)
        # Second registration overwrites
        assert reg.get_capability("pc.test").name == "Second"

    def test_unregister_capability(self):
        reg = CapabilityRegistry()
        reg.register_capability(_make_cap("pc.test"))
        reg.unregister_capability("pc.test")
        assert reg.get_capability("pc.test") is None

    def test_unspecified_risk_raises(self):
        reg = CapabilityRegistry()
        with pytest.raises(ValueError, match="UNSPECIFIED"):
            reg.register_capability(_make_cap("pc.bad", risk=RiskLevel.UNSPECIFIED))

    def test_forbidden_risk_raises(self):
        reg = CapabilityRegistry()
        with pytest.raises(ValueError, match="FORBIDDEN"):
            reg.register_capability(_make_cap("pc.bad", risk=RiskLevel.FORBIDDEN))


class TestCapabilitySearch:
    @pytest.fixture
    def populated(self) -> CapabilityRegistry:
        reg = CapabilityRegistry()
        reg.register_capability(_make_cap(
            "pc.screenshot", "Screenshot", ServerType.PC, RiskLevel.READ_ONLY, ["observe"]))
        reg.register_capability(_make_cap(
            "pc.click", "Mouse Click", ServerType.PC, RiskLevel.SAFE_ACTION, ["input"]))
        reg.register_capability(_make_cap(
            "android.screenshot", "Android Screen", ServerType.ANDROID, RiskLevel.READ_ONLY, ["observe"]))
        reg.register_capability(_make_cap(
            "browser.open", "Open Page", ServerType.BROWSER, RiskLevel.SAFE_ACTION, ["web"]))
        return reg

    def test_find_capabilities_by_query(self, populated):
        results = populated.search("screenshot")
        assert len(results) == 2  # pc.screenshot + android.screenshot

    def test_find_capabilities_by_tags(self, populated):
        results = populated.list_capabilities(tags=["observe"])
        assert len(results) == 2

    def test_find_capabilities_by_server_type(self, populated):
        results = populated.list_capabilities(server_type=ServerType.PC)
        assert len(results) == 2

    def test_find_capabilities_by_safety_level(self, populated):
        results = populated.list_capabilities(max_risk_level=RiskLevel.READ_ONLY)
        assert len(results) == 2  # pc.screenshot + android.screenshot
        for cap in results:
            assert cap.risk_level <= RiskLevel.READ_ONLY

    def test_find_nonexistent_returns_none(self, populated):
        assert populated.find_capability("nonexistent.cap") is None


class TestToolBrokerIntegration:
    """Verify ToolBroker uses CapabilityRegistry correctly."""

    def test_registry_and_broker_together(self):
        from aegis_ai.policy_engine import PolicyEngine
        from aegis_ai.tool_broker import ToolBroker

        reg = CapabilityRegistry()
        reg.register_capability(_make_cap("pc.screenshot", risk=RiskLevel.READ_ONLY))
        broker = ToolBroker(reg, PolicyEngine())

        result = broker.invoke_tool("pc.screenshot", {})
        assert result.success
        assert result.status.value == 1  # SUCCESS

    def test_registry_stores_metadata_does_not_execute(self):
        """CapabilityRegistry stores data; ToolBroker executes."""
        reg = CapabilityRegistry()
        reg.register_capability(_make_cap("pc.test", risk=RiskLevel.READ_ONLY))
        cap = reg.get_capability("pc.test")
        assert cap is not None
        assert isinstance(cap, Capability)
        # Registry does NOT have execute/invoke methods
        assert not hasattr(reg, "execute")
        assert not hasattr(reg, "invoke")
