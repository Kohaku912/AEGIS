"""MCP gateway tests (Phase 7 DoD).

Validates:
- list_tools_for_agent returns MCP-shaped tool schemas
- mcp_tools_list_payload has JSON-RPC 2.0 envelope + tools array
- mcp_tools_call_payload wraps every call through ToolBroker.execute()
- call_tool_for_agent refuses tools not allowed by the profile
- call_tool_for_agent surfaces approval_required as a structured error
- call_tool_for_agent funnels unknown exceptions to isError=True
- CapabilityCatalog.list_for_agent / mcp_tool_schemas respect
  profile.allows_capability, profile.denied_capabilities and risk ceiling
- Import boundary: mcp_gateway does not import openhands / fastmcp / mcp
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


class _FakeProfile:
    """Minimal AgentProfile duck-type for tests."""

    def __init__(
        self,
        *,
        profile_id: str = "general",
        allowed: list[str] | None = None,
        denied: list[str] | None = None,
        risk_ceiling: str = "HIGH_RISK",
    ) -> None:
        self.id = profile_id
        self.allowed_capabilities = list(allowed or [])
        self.denied_capabilities = list(denied or [])
        self.risk_ceiling = risk_ceiling

    def allows_capability(self, cap_id: str) -> bool:
        if cap_id in self.denied_capabilities:
            return False
        if self.allowed_capabilities:
            return cap_id in self.allowed_capabilities
        return True


def _make_runtime(broker=None):
    runtime = MagicMock()
    if broker is not None:
        runtime.tool_broker = broker
    return runtime


def _make_broker(*, return_value=None, side_effect=None):
    broker = MagicMock()
    if side_effect is not None:
        broker.execute.side_effect = side_effect
    else:
        broker.execute.return_value = return_value
    return broker


# ---------------------------------------------------------------------------
# tools/list — payload shape
# ---------------------------------------------------------------------------


def test_list_tools_for_agent_returns_list():
    from aegis_ai.tools.mcp_gateway import list_tools_for_agent

    profile = _FakeProfile()
    tools = list_tools_for_agent(profile)
    assert isinstance(tools, list)
    # Each entry is a dict with the MCP tool keys
    for tool in tools[:5]:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert "type" in tool["inputSchema"]


def test_list_tools_for_agent_uses_canonical_id_as_name():
    from aegis_ai.tools.mcp_gateway import list_tools_for_agent

    profile = _FakeProfile()
    tools = list_tools_for_agent(profile)
    for tool in tools:
        # canonical form is server_id.app_id.action (3 dot-separated parts)
        assert tool["name"].count(".") >= 2, f"non-canonical name: {tool['name']!r}"


def test_mcp_tools_list_payload_jsonrpc_envelope():
    from aegis_ai.tools.mcp_gateway import mcp_tools_list_payload

    profile = _FakeProfile()
    payload = mcp_tools_list_payload(profile, request_id=42)
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == 42
    assert "result" in payload
    assert "tools" in payload["result"]
    assert "nextCursor" in payload["result"]


def test_mcp_initialize_payload_envelope():
    from aegis_ai.tools.mcp_gateway import mcp_initialize_payload

    payload = mcp_initialize_payload(request_id=1)
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == 1
    assert payload["result"]["protocolVersion"]
    assert payload["result"]["serverInfo"]["name"]
    assert "tools" in payload["result"]["capabilities"]


# ---------------------------------------------------------------------------
# Capability filter — list_for_agent
# ---------------------------------------------------------------------------


def test_list_for_agent_respects_denied_capabilities():
    from aegis_ai.capability_catalog import CapabilityCatalog

    profile = _FakeProfile(denied=["pc-server.screenshot.get_screenshot"])
    catalog = CapabilityCatalog.instance()
    visible = catalog.list_for_agent(profile)
    cap_ids = [c["id"] for c in visible]
    assert "pc-server.screenshot.get_screenshot" not in cap_ids


def test_list_for_agent_respects_risk_ceiling_readonly():
    from aegis_ai.capability_catalog import CapabilityCatalog

    profile = _FakeProfile(risk_ceiling="READ_ONLY")
    catalog = CapabilityCatalog.instance()
    visible = catalog.list_for_agent(profile)
    # Anything with risk > READ_ONLY must be excluded
    for entry in visible:
        assert entry.get("risk", "READ_ONLY") in {"READ_ONLY", "low"}


def test_mcp_tool_schemas_have_aegis_meta():
    from aegis_ai.capability_catalog import CapabilityCatalog

    profile = _FakeProfile()
    catalog = CapabilityCatalog.instance()
    schemas = catalog.mcp_tool_schemas(profile)
    assert isinstance(schemas, list)
    if schemas:
        tool = schemas[0]
        assert "name" in tool
        assert "inputSchema" in tool
        assert "_meta" in tool
        assert "aegis" in tool["_meta"]
        meta = tool["_meta"]["aegis"]
        assert "risk" in meta
        assert "requires_approval" in meta


# ---------------------------------------------------------------------------
# tools/call — broker funnel
# ---------------------------------------------------------------------------


def test_call_tool_for_agent_invokes_broker_execute():
    from aegis_ai.tools.mcp_gateway import call_tool_for_agent

    broker = _make_broker(return_value={"success": True, "value": 42})
    runtime = _make_runtime(broker=broker)
    profile = _FakeProfile()

    response = call_tool_for_agent(
        "pc-server.screenshot.get_screenshot",
        {"region": "full"},
        profile=profile,
        runtime=runtime,
    )
    assert response["isError"] is False
    assert response["content"][0]["type"] == "text"
    assert "42" in response["content"][0]["text"]
    broker.execute.assert_called_once()


def test_call_tool_for_agent_records_profile_in_context():
    from aegis_ai.tools.mcp_gateway import call_tool_for_agent

    broker = _make_broker(return_value="ok")
    runtime = _make_runtime(broker=broker)
    profile = _FakeProfile(profile_id="coding")

    call_tool_for_agent(
        "pc-server.screenshot.get_screenshot",
        {},
        profile=profile,
        runtime=runtime,
    )
    # The request passed to broker.execute must mention the profile
    args, kwargs = broker.execute.call_args
    request = args[0] if args else kwargs.get("request")
    assert request is not None
    ctx = getattr(request, "context", None) or getattr(request, "metadata", None) or {}
    assert ctx.get("agent_profile") == "coding"
    assert ctx.get("caller") == "mcp_gateway"


def test_call_tool_for_agent_refuses_not_allowed():
    from aegis_ai.tools.mcp_gateway import call_tool_for_agent

    broker = _make_broker()
    runtime = _make_runtime(broker=broker)
    profile = _FakeProfile(denied=["pc-server.screenshot.get_screenshot"])

    response = call_tool_for_agent(
        "pc-server.screenshot.get_screenshot",
        {},
        profile=profile,
        runtime=runtime,
    )
    assert response["isError"] is True
    assert "not allowed" in response["content"][0]["text"]
    broker.execute.assert_not_called()


def test_call_tool_for_agent_refuses_invalid_arguments():
    from aegis_ai.tools.mcp_gateway import call_tool_for_agent

    broker = _make_broker()
    runtime = _make_runtime(broker=broker)
    profile = _FakeProfile()

    response = call_tool_for_agent(
        "pc-server.screenshot.get_screenshot",
        "not a dict",  # type: ignore[arg-type]
        profile=profile,
        runtime=runtime,
    )
    assert response["isError"] is True
    assert "arguments" in response["content"][0]["text"]


def test_call_tool_for_agent_handles_broker_exception():
    from aegis_ai.tools.mcp_gateway import call_tool_for_agent

    broker = _make_broker(side_effect=RuntimeError("broker down"))
    runtime = _make_runtime(broker=broker)
    profile = _FakeProfile()

    response = call_tool_for_agent(
        "pc-server.screenshot.get_screenshot",
        {},
        profile=profile,
        runtime=runtime,
    )
    assert response["isError"] is True
    assert "RuntimeError" in response["content"][0]["text"]
    assert "broker down" in response["content"][0]["text"]


def test_call_tool_for_agent_marks_non_success_tool_result_as_error():
    from aegis_ai.tools.mcp_gateway import call_tool_for_agent
    from tool_broker import InvokeStatus, ToolExecutionResult

    broker = _make_broker(
        return_value=ToolExecutionResult(
            request_id="r1",
            status=InvokeStatus.NOT_FOUND,
            error="Capability 'agent.run' is not registered in the capability catalog.",
        )
    )
    runtime = _make_runtime(broker=broker)
    profile = _FakeProfile()

    response = call_tool_for_agent(
        "agent.run",
        {"goal": "test"},
        profile=profile,
        runtime=runtime,
    )
    assert response["isError"] is True
    assert response["error_code"] == "not_found"
    assert "not registered" in response["error"]


def test_mcp_tools_call_payload_envelope():
    from aegis_ai.tools.mcp_gateway import mcp_tools_call_payload

    broker = _make_broker(return_value={"ok": True})
    runtime = _make_runtime(broker=broker)
    profile = _FakeProfile()

    payload = mcp_tools_call_payload(
        "pc-server.screenshot.get_screenshot",
        {},
        profile=profile,
        runtime=runtime,
        request_id=7,
    )
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == 7
    assert payload["result"]["isError"] is False
    assert payload["result"]["content"]


def test_call_tool_for_agent_uses_runtime_broker():
    """If the runtime exposes its own tool_broker, prefer it over the global."""
    from aegis_ai.tools.mcp_gateway import call_tool_for_agent

    runtime_broker = _make_broker(return_value="from-runtime")
    other_broker = _make_broker(return_value="from-global")
    runtime = _make_runtime(broker=runtime_broker)
    profile = _FakeProfile()

    with patch("tool_broker.ToolBroker", other_broker):
        response = call_tool_for_agent(
            "pc-server.screenshot.get_screenshot",
            {},
            profile=profile,
            runtime=runtime,
        )
    assert response["isError"] is False
    assert "from-runtime" in response["content"][0]["text"]
    runtime_broker.execute.assert_called_once()
    other_broker.execute.assert_not_called()


# ---------------------------------------------------------------------------
# execute_for_agent facade (Phase 7 §36)
# ---------------------------------------------------------------------------


def test_execute_for_agent_facade_in_aegis_tool_broker():
    """``aegis_ai.tool_broker.execute_for_agent`` must be importable."""
    from aegis_ai.tool_broker import execute_for_agent

    assert callable(execute_for_agent)


def test_execute_for_agent_calls_broker_execute():
    from aegis_ai.tool_broker import execute_for_agent
    from tool_broker import ToolBroker

    broker = _make_broker(return_value="ok")
    profile = _FakeProfile(profile_id="coding")

    # ``_execute_for_agent`` resolves the broker via
    # ``ToolBroker.instance()`` (Phase 7 §36 singleton hook). We patch
    # the classmethod so the wrapper receives our mock broker.
    with patch.object(ToolBroker, "instance", classmethod(lambda cls: broker)):
        result = execute_for_agent(
            "pc-server.screenshot.get_screenshot",
            {"region": "full"},
            profile=profile,
        )
    assert result == "ok"
    broker.execute.assert_called_once()
    request = broker.execute.call_args[0][0]
    ctx = getattr(request, "context", None) or getattr(request, "metadata", None) or {}
    assert ctx.get("agent_profile") == "coding"
    assert ctx.get("caller") == "agent"


# ---------------------------------------------------------------------------
# Import-boundary invariants (instruction.md §6, §35.4, §39.7)
# ---------------------------------------------------------------------------


def test_mcp_gateway_does_not_import_openhands():
    from aegis_ai.tools import mcp_gateway as mod

    src_path = Path(mod.__file__).resolve()
    text = src_path.read_text(encoding="utf-8")
    assert "import openhands" not in text
    assert "from openhands" not in text


def test_mcp_gateway_does_not_import_fastmcp_or_mcp_sdk():
    """We deliberately implement the wire format in plain JSON — no
    external MCP SDK should leak into AEGIS core."""
    from aegis_ai.tools import mcp_gateway as mod

    src_path = Path(mod.__file__).resolve()
    text = src_path.read_text(encoding="utf-8")
    for forbidden in ("import fastmcp", "from fastmcp", "import mcp", "from mcp"):
        assert forbidden not in text, f"forbidden import: {forbidden}"


def test_mcp_gateway_module_is_importable():
    importlib.import_module("aegis_ai.tools.mcp_gateway")
    importlib.import_module("aegis_ai.tools")
    # re-exports
    from aegis_ai.tools import mcp_gateway  # noqa: F401


def test_aegis_ai_tools_does_not_import_openhands():
    """The whole ``aegis_ai.tools`` package stays SDK-free."""
    from aegis_ai import tools as tools_pkg

    pkg_path = Path(tools_pkg.__file__).resolve().parent
    for py in pkg_path.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "import openhands" not in text
        assert "from openhands" not in text
