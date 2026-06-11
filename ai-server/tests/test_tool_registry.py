"""Tests for ToolRegistry — capability and server registration, search, filtering."""

from __future__ import annotations

import pytest

from aegis_schema.models import (
    Capability,
    RiskLevel,
    ServerInfo,
    ServerStatus,
    ServerType,
)
from tool_registry import ToolRegistry

# ── Helpers ───────────────────────────────────────────────────

_ID_TO_SERVER: dict[str, ServerType] = {
    "pc": ServerType.PC,
    "android": ServerType.ANDROID,
    "browser": ServerType.BROWSER,
    "room": ServerType.ROOM,
    "dev": ServerType.DEV,
    "ai": ServerType.AI,
}


def _make_cap(
    id: str = "pc.test",
    name: str = "Test",
    description: str = "A test capability",
    server_type: ServerType | None = None,
    risk_level: RiskLevel = RiskLevel.SAFE_ACTION,
    tags: list[str] | None = None,
) -> Capability:
    if server_type is None:
        prefix = id.split(".")[0]
        server_type = _ID_TO_SERVER.get(prefix, ServerType.PC)
    return Capability(
        id=id,
        name=name,
        description=description,
        server_type=server_type,
        risk_level=risk_level,
        tags=tags or [],
    )


def _make_server(
    server_id: str = "pc-main",
    server_type: ServerType = ServerType.PC,
    capability_ids: list[str] | None = None,
) -> ServerInfo:
    return ServerInfo(
        server_id=server_id,
        server_type=server_type,
        capability_ids=capability_ids or [],
    )


# ═══════════════════════════════════════════════════════════════
# Server Registration Tests
# ═══════════════════════════════════════════════════════════════

class TestServerRegistration:
    def test_register_server(self):
        reg = ToolRegistry()
        reg.register_server(_make_server("pc-main"))
        assert reg.get_server("pc-main") is not None
        assert reg.get_server("pc-main").server_type == ServerType.PC

    def test_register_server_empty_id_raises(self):
        """Pydantic catches empty server_id before ToolRegistry does."""
        reg = ToolRegistry()
        with pytest.raises(ValueError):
            reg.register_server(ServerInfo(server_id="", server_type=ServerType.PC))

    def test_unregister_server(self):
        reg = ToolRegistry()
        reg.register_server(_make_server("pc-main"))
        reg.unregister_server("pc-main")
        assert reg.get_server("pc-main") is None

    def test_list_servers(self):
        reg = ToolRegistry()
        reg.register_server(_make_server("pc-1", ServerType.PC))
        reg.register_server(_make_server("pc-2", ServerType.PC))
        reg.register_server(_make_server("android-1", ServerType.ANDROID))
        assert len(reg.list_servers()) == 3
        assert len(reg.list_servers(server_type=ServerType.PC)) == 2

    def test_list_servers_by_status(self):
        reg = ToolRegistry()
        online = ServerInfo(server_id="s1", server_type=ServerType.PC, status=ServerStatus.ONLINE)
        offline = ServerInfo(server_id="s2", server_type=ServerType.PC, status=ServerStatus.OFFLINE)
        reg.register_server(online)
        reg.register_server(offline)
        assert len(reg.list_servers(status=ServerStatus.ONLINE)) == 1

    def test_register_server_syncs_capability_ids(self):
        reg = ToolRegistry()
        cap = _make_cap("pc.test")
        reg.register_capability(cap)
        reg.register_server(_make_server("pc-main", capability_ids=["pc.test"]))
        caps = reg.get_capabilities_for_server("pc-main")
        assert len(caps) == 1
        assert caps[0].id == "pc.test"


# ═══════════════════════════════════════════════════════════════
# Capability Registration Tests
# ═══════════════════════════════════════════════════════════════

class TestCapabilityRegistration:
    def test_register_capability(self):
        reg = ToolRegistry()
        cap = _make_cap("pc.screenshot", risk_level=RiskLevel.READ_ONLY)
        reg.register_capability(cap)
        assert "pc.screenshot" in reg
        assert reg.get_capability("pc.screenshot") == cap

    def test_register_duplicate_overwrites(self):
        reg = ToolRegistry()
        cap1 = _make_cap("pc.test", name="First")
        cap2 = _make_cap("pc.test", name="Second")
        reg.register_capability(cap1)
        reg.register_capability(cap2)
        assert reg.get_capability("pc.test").name == "Second"

    def test_register_unspecified_risk_raises(self):
        """Pydantic model_validator rejects UNSPECIFIED before ToolRegistry sees it."""
        with pytest.raises(ValueError, match="UNSPECIFIED"):
            _make_cap("pc.test", risk_level=RiskLevel.UNSPECIFIED)

    def test_register_forbidden_risk_raises(self):
        """Pydantic model_validator rejects FORBIDDEN before ToolRegistry sees it."""
        with pytest.raises(ValueError, match="FORBIDDEN"):
            _make_cap("pc.test", risk_level=RiskLevel.FORBIDDEN)

    def test_unregister_capability(self):
        reg = ToolRegistry()
        reg.register_capability(_make_cap("pc.test"))
        reg.unregister_capability("pc.test")
        assert reg.get_capability("pc.test") is None

    def test_find_nonexistent_returns_none(self):
        reg = ToolRegistry()
        assert reg.find_capability("nonexistent") is None


# ═══════════════════════════════════════════════════════════════
# Filtering Tests
# ═══════════════════════════════════════════════════════════════

class TestFiltering:
    @pytest.fixture
    def populated_registry(self) -> ToolRegistry:
        reg = ToolRegistry()
        reg.register_capability(_make_cap("pc.read", "Read", risk_level=RiskLevel.READ_ONLY, server_type=ServerType.PC, tags=["observe"]))
        reg.register_capability(_make_cap("pc.action", "Action", risk_level=RiskLevel.SAFE_ACTION, server_type=ServerType.PC, tags=["action"]))
        reg.register_capability(_make_cap("pc.approval", "Approval", risk_level=RiskLevel.APPROVAL_REQUIRED, server_type=ServerType.PC, tags=["dangerous"]))
        reg.register_capability(_make_cap("android.read", "Android Read", risk_level=RiskLevel.READ_ONLY, server_type=ServerType.ANDROID, tags=["observe"]))
        reg.register_capability(_make_cap("browser.action", "Browser Action", risk_level=RiskLevel.SAFE_ACTION, server_type=ServerType.BROWSER, tags=["web"]))
        return reg

    def test_filter_by_server_type(self, populated_registry):
        pc_caps = populated_registry.list_capabilities(server_type=ServerType.PC)
        assert len(pc_caps) == 3
        android_caps = populated_registry.list_capabilities(server_type=ServerType.ANDROID)
        assert len(android_caps) == 1

    def test_filter_by_max_risk(self, populated_registry):
        safe = populated_registry.list_capabilities(max_risk_level=RiskLevel.SAFE_ACTION)
        assert len(safe) == 4  # 2 READ_ONLY + 2 SAFE_ACTION
        for cap in safe:
            assert cap.risk_level <= RiskLevel.SAFE_ACTION

    def test_filter_by_tags(self, populated_registry):
        observe_caps = populated_registry.list_capabilities(tags=["observe"])
        assert len(observe_caps) == 2  # pc.read + android.read

    def test_filter_combined(self, populated_registry):
        result = populated_registry.list_capabilities(
            server_type=ServerType.PC,
            max_risk_level=RiskLevel.READ_ONLY,
        )
        assert len(result) == 1
        assert result[0].id == "pc.read"

    def test_get_safe_capabilities(self, populated_registry):
        safe = populated_registry.get_safe_capabilities()
        for cap in safe:
            assert cap.risk_level <= RiskLevel.SAFE_ACTION

    def test_get_approval_capabilities(self, populated_registry):
        approval = populated_registry.get_approval_capabilities()
        assert len(approval) == 1
        assert approval[0].id == "pc.approval"

    def test_get_capabilities_by_server_type(self, populated_registry):
        browser_caps = populated_registry.get_capabilities_by_server_type(ServerType.BROWSER)
        assert len(browser_caps) == 1
        assert browser_caps[0].id == "browser.action"


# ═══════════════════════════════════════════════════════════════
# Search Tests
# ═══════════════════════════════════════════════════════════════

class TestSearch:
    @pytest.fixture
    def reg(self) -> ToolRegistry:
        r = ToolRegistry()
        r.register_capability(_make_cap("pc.screenshot", "Screenshot Capture", "Take a screenshot of the display", ServerType.PC, RiskLevel.READ_ONLY, ["screenshot", "observe"]))
        r.register_capability(_make_cap("pc.launch_app", "Launch App", "Launch application", ServerType.PC, RiskLevel.SAFE_ACTION, ["app", "action"]))
        r.register_capability(_make_cap("browser.open_page", "Open Web Page", "Navigate to a URL", ServerType.BROWSER, RiskLevel.SAFE_ACTION, ["browser", "web"]))
        r.register_capability(_make_cap("browser.extract_text", "Extract Text", "Extract page content", ServerType.BROWSER, RiskLevel.READ_ONLY, ["text", "observe"]))
        return r

    def test_search_by_name(self, reg):
        results = reg.search("screenshot")
        assert len(results) == 1
        assert results[0].id == "pc.screenshot"

    def test_search_by_description(self, reg):
        results = reg.search("application")
        assert len(results) == 1
        assert results[0].id == "pc.launch_app"

    def test_search_by_tag(self, reg):
        results = reg.search("observe")
        assert len(results) == 2  # pc.screenshot + browser.extract_text

    def test_search_case_insensitive(self, reg):
        results = reg.search("SCREENSHOT")
        assert len(results) == 1

    def test_search_no_results(self, reg):
        results = reg.search("nonexistentxyz")
        assert len(results) == 0

    def test_search_with_server_filter(self, reg):
        results = reg.search("open", server_type=ServerType.BROWSER)
        assert len(results) == 1
        assert results[0].id == "browser.open_page"

    def test_search_with_risk_filter(self, reg):
        results = reg.search("browser", max_risk_level=RiskLevel.READ_ONLY)
        assert len(results) == 1
        assert results[0].id == "browser.extract_text"


# ═══════════════════════════════════════════════════════════════
# Stats Tests
# ═══════════════════════════════════════════════════════════════

class TestStats:
    def test_empty_registry(self):
        reg = ToolRegistry()
        stats = reg.stats()
        assert stats.total_capabilities == 0
        assert stats.total_servers == 0

    def test_populated_registry(self):
        reg = ToolRegistry()
        reg.register_capability(_make_cap("pc.cap_one", server_type=ServerType.PC))
        reg.register_capability(_make_cap("pc.cap_two", server_type=ServerType.PC))
        reg.register_capability(_make_cap("android.cap_one", server_type=ServerType.ANDROID))
        stats = reg.stats()
        assert stats.total_capabilities == 3
        assert "PC" in stats.capabilities_by_server
        assert stats.capabilities_by_server["PC"] == 2
        assert stats.capabilities_by_server["ANDROID"] == 1

    def test_stats_online_count(self):
        reg = ToolRegistry()
        reg.register_server(ServerInfo(server_id="s1", server_type=ServerType.PC, status=ServerStatus.ONLINE))
        reg.register_server(ServerInfo(server_id="s2", server_type=ServerType.PC, status=ServerStatus.OFFLINE))
        reg.register_server(ServerInfo(server_id="s3", server_type=ServerType.PC, status=ServerStatus.ONLINE))
        assert reg.stats().online_servers == 2


# ═══════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_empty_search_returns_all(self):
        reg = ToolRegistry()
        reg.register_capability(_make_cap("pc.cap_a"))
        reg.register_capability(_make_cap("pc.cap_b"))
        results = reg.search("")
        assert len(results) == 2  # empty string matches everything

    def test_len(self):
        reg = ToolRegistry()
        assert len(reg) == 0
        reg.register_capability(_make_cap("pc.cap_a"))
        assert len(reg) == 1

    def test_contains(self):
        reg = ToolRegistry()
        assert "pc.cap_a" not in reg
        reg.register_capability(_make_cap("pc.cap_a"))
        assert "pc.cap_a" in reg

    def test_unregister_server_does_not_delete_capabilities(self):
        reg = ToolRegistry()
        cap = _make_cap("pc.test")
        reg.register_capability(cap)
        reg.register_server(_make_server("pc-main", capability_ids=["pc.test"]))
        reg.unregister_server("pc-main")
        # Capability definition should still exist
        assert reg.get_capability("pc.test") is not None

    def test_get_capabilities_for_unknown_server(self):
        reg = ToolRegistry()
        caps = reg.get_capabilities_for_server("nonexistent")
        assert caps == []
