"""Research Approval E2E tests — Level 2/3 operations blocked in research pipeline."""

from __future__ import annotations

import pytest

from aegis_ai.tool_broker import InvokeStatus, ToolBroker
from aegis_ai.tool_registry import ToolRegistry
from aegis_schema.models import Capability, RiskLevel, ServerType
from policy_engine import create_default_policy_engine


def _make_cap(id: str, name: str = "Test", risk: RiskLevel = RiskLevel.READ_ONLY,
              server: ServerType = ServerType.BROWSER) -> Capability:
    return Capability(id=id, name=name, description=f"Capability {id}",
                      server_type=server, risk_level=risk)


class TestReadOnlyResearchNoApproval:
    """Read-only research capabilities auto-allow without approval."""

    def test_browser_extract_text_auto_allows(self):
        cap = _make_cap("browser.extract_page_text", risk=RiskLevel.READ_ONLY)
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry, create_default_policy_engine())
        result = broker.invoke_tool("browser.extract_page_text", {"max_length": 5000})
        assert result.success

    def test_browser_get_title_auto_allows(self):
        cap = _make_cap("browser.get_page_title", risk=RiskLevel.READ_ONLY)
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry, create_default_policy_engine())
        result = broker.invoke_tool("browser.get_page_title", {})
        assert result.success

    def test_browser_get_links_auto_allows(self):
        cap = _make_cap("browser.get_links", risk=RiskLevel.READ_ONLY)
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry, create_default_policy_engine())
        result = broker.invoke_tool("browser.get_links", {})
        assert result.success

    def test_browser_open_page_safe_action_auto_allows(self):
        cap = _make_cap("browser.open_page", risk=RiskLevel.SAFE_ACTION)
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry, create_default_policy_engine())
        result = broker.invoke_tool("browser.open_page", {"url": "https://example.com"})
        assert result.success


class TestDangerousOpsBlocked:
    """Level 2/3 operations require approval or are denied."""

    def test_download_file_requires_approval(self):
        cap = _make_cap("browser.download_file", risk=RiskLevel.APPROVAL_REQUIRED)
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry, create_default_policy_engine())
        result = broker.invoke_tool("browser.download_file",
                                   {"url": "https://example.com/file.pdf"})
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_fill_form_requires_approval(self):
        cap = _make_cap("browser.fill_form", "Fill Form", RiskLevel.SAFE_ACTION)
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry, create_default_policy_engine())
        result = broker.invoke_tool("browser.fill_form", {"form_selector": "#login"})
        # fill_form matches EXPLICIT_APPROVAL_PATTERNS
        assert result.status in (InvokeStatus.APPROVAL_NEEDED, InvokeStatus.DENIED)

    @pytest.mark.parametrize("bad_cap_id", [
        "browser.post_sns",
        "browser.purchase_item",
        "browser.captcha_bypass",
    ])
    def test_dangerous_caps_explicitly_denied(self, bad_cap_id):
        cap = _make_cap(bad_cap_id, risk=RiskLevel.READ_ONLY)  # Even if declared low
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry, create_default_policy_engine())
        result = broker.invoke_tool(bad_cap_id, {})
        assert result.status == InvokeStatus.DENIED, f"{bad_cap_id} should be DENIED"

    @pytest.mark.parametrize("approval_cap_id", [
        "browser.send_message",
        "browser.send_email",
        "browser.publish_post",
    ])
    def test_browser_send_requires_approval(self, approval_cap_id):
        cap = _make_cap(approval_cap_id, risk=RiskLevel.APPROVAL_REQUIRED)
        registry = ToolRegistry()
        registry.register_capability(cap)
        broker = ToolBroker(registry, create_default_policy_engine())
        result = broker.invoke_tool(approval_cap_id, {})
        assert result.status == InvokeStatus.APPROVAL_NEEDED, f"{approval_cap_id} should require approval"


class TestUnknownCapabilityBlocked:
    """Unregistered or malformed capabilities are denied."""

    def test_unknown_capability_returns_not_found(self):
        broker = ToolBroker(ToolRegistry(), create_default_policy_engine())
        result = broker.invoke_tool("nonexistent.research_cap", {})
        assert result.status == InvokeStatus.NOT_FOUND

    def test_unknown_capability_no_approval_request(self):
        engine = create_default_policy_engine()
        broker = ToolBroker(ToolRegistry(), engine)
        broker.invoke_tool("nonexistent.cap", {})
        assert len(engine.approval_store.get_pending()) == 0
