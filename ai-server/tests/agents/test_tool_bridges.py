"""Tool bridge tests (Phase 6 / Phase 9 DoD).

Validates:
- ToolBridge dataclass: registration, lookup, list, clear
- BridgeResult shape and to_dict()
- Native bridges (filesystem): in-process execution + workspace confinement
- Manifest risk/approval consistency for write-class dev-server capabilities
  (legacy manifests are tolerated, but the bridges themselves are gone)
- Import-boundary invariants (no direct openhands imports from bridges)
- No dev-server gRPC client references remain (Phase 9 deletion)
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _isolate_bridges():
    """Reset the bridge registry around every test so order does not matter."""
    from aegis_ai.tools.bridges import base as bridges_base

    bridges_base.clear_bridges()
    yield
    bridges_base.clear_bridges()


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Point AEGIS_REPO_PATH at an isolated temporary git repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setenv("AEGIS_REPO_PATH", str(repo))
    # Initialize a real git repo so `git status` works.
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=str(repo), check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=str(repo),
        check=True,
    )
    (repo / "README.md").write_text("hello\n")
    subprocess.run(["git", "add", "README.md"], cwd=str(repo), check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "init"],
        cwd=str(repo),
        check=True,
    )
    return repo


# ---------------------------------------------------------------------------
# Base / registry behavior
# ---------------------------------------------------------------------------


def test_bridge_registry_register_and_lookup():
    from aegis_ai.tools.bridges.base import (
        BridgeResult,
        ToolBridge,
        bridge_for_capability,
        list_bridges,
        register_bridge,
    )

    def _invoke(params, *, context):
        return BridgeResult(success=True, capability_id="x.demo")

    register_bridge(
        ToolBridge(
            capability_id="x.demo",
            kind="native",
            invoke=_invoke,
            description="Demo.",
        )
    )
    assert list_bridges() == ["x.demo"]
    bridge = bridge_for_capability("x.demo")
    assert bridge is not None
    assert bridge.kind == "native"
    assert bridge_for_capability("unknown") is None


def test_bridge_result_to_dict_shape():
    from aegis_ai.tools.bridges.base import BridgeResult

    result = BridgeResult(
        success=True,
        capability_id="x.demo",
        data={"foo": 1, "bar": "baz"},
    )
    out = result.to_dict()
    assert out["success"] is True
    assert out["capability_id"] == "x.demo"
    assert out["foo"] == 1
    assert out["bar"] == "baz"
    assert "error" not in out


def test_bridge_result_includes_error_when_present():
    from aegis_ai.tools.bridges.base import BridgeResult

    result = BridgeResult(
        success=False,
        capability_id="x.demo",
        error="boom",
    )
    out = result.to_dict()
    assert out["success"] is False
    assert out["error"] == "boom"


def test_tool_bridge_call_swallows_exceptions():
    from aegis_ai.tools.bridges.base import BridgeResult, ToolBridge

    def _bad(params, *, context):
        raise RuntimeError("nope")

    bridge = ToolBridge(
        capability_id="x.bad", kind="native", invoke=_bad
    )
    result = bridge({"a": 1})
    assert result.success is False
    assert "RuntimeError" in result.error
    assert result.capability_id == "x.bad"


def test_clear_bridges_removes_all():
    from aegis_ai.tools.bridges.base import (
        BridgeResult,
        ToolBridge,
        clear_bridges,
        list_bridges,
        register_bridge,
    )

    register_bridge(
        ToolBridge(
            capability_id="x.a", kind="native", invoke=lambda p, *, context: BridgeResult(True)
        )
    )
    register_bridge(
        ToolBridge(
            capability_id="x.b", kind="native", invoke=lambda p, *, context: BridgeResult(True)
        )
    )
    assert len(list_bridges()) == 2
    clear_bridges()
    assert list_bridges() == []


# ---------------------------------------------------------------------------
# Filesystem / native bridges
# ---------------------------------------------------------------------------


def test_filesystem_registers_three_native_bridges():
    from aegis_ai.tools.bridges.filesystem import register_default_bridges
    from aegis_ai.tools.bridges.base import bridge_for_capability

    register_default_bridges()
    expected = {
        "ai-server.workspace.repo_status",
        "ai-server.workspace.diff",
        "ai-server.workspace.test_results",
    }
    for cap in expected:
        bridge = bridge_for_capability(cap)
        assert bridge is not None, f"missing bridge for {cap}"
        assert bridge.kind == "native"


def test_repo_status_native_executes(workspace):
    from aegis_ai.tools.bridges.filesystem import register_default_bridges

    register_default_bridges()
    from aegis_ai.tools.bridges.base import bridge_for_capability

    bridge = bridge_for_capability("ai-server.workspace.repo_status")
    assert bridge is not None
    result = bridge({})
    assert result.success is True
    assert "branch_output" in result.data
    assert "master" in result.data["branch_output"] or "main" in result.data["branch_output"]


def test_diff_get_diff_returns_diff_text(workspace):
    from aegis_ai.tools.bridges.filesystem import register_default_bridges

    register_default_bridges()
    from aegis_ai.tools.bridges.base import bridge_for_capability

    (workspace / "README.md").write_text("hello\nworld\n")
    bridge = bridge_for_capability("ai-server.workspace.diff")
    assert bridge is not None
    result = bridge({})
    assert result.success is True
    assert "diff" in result.data
    assert "world" in result.data["diff"]


def test_test_get_results_empty_cache():
    from aegis_ai.tools.bridges.filesystem import register_default_bridges

    register_default_bridges()
    from aegis_ai.tools.bridges.base import bridge_for_capability

    bridge = bridge_for_capability("ai-server.workspace.test_results")
    assert bridge is not None
    result = bridge({})
    assert result.success is True
    assert result.data["cached"] is False
    assert result.data["result"] is None


def test_is_within_workspace_true_for_inner_path(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_REPO_PATH", str(tmp_path))
    from aegis_ai.tools.bridges.filesystem import (
        _is_within_workspace,
        _workspace_root,
    )

    inner = tmp_path / "sub" / "file.txt"
    inner.parent.mkdir()
    inner.write_text("ok")
    assert _is_within_workspace(inner, _workspace_root()) is True


def test_is_within_workspace_false_for_outside_path(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_REPO_PATH", str(tmp_path))
    from aegis_ai.tools.bridges.filesystem import (
        _is_within_workspace,
        _workspace_root,
    )

    outside = tmp_path.parent / "etc-passwd"
    assert _is_within_workspace(outside, _workspace_root()) is False


def test_repo_status_surfaces_error_when_not_git_repo(tmp_path, monkeypatch):
    """If `AEGIS_REPO_PATH` points at a non-git dir, status must surface the error."""
    bad_repo = tmp_path / "not_a_repo"
    bad_repo.mkdir()
    monkeypatch.setenv("AEGIS_REPO_PATH", str(bad_repo))
    from aegis_ai.tools.bridges.filesystem import register_default_bridges

    register_default_bridges()
    from aegis_ai.tools.bridges.base import bridge_for_capability

    bridge = bridge_for_capability("ai-server.workspace.repo_status")
    assert bridge is not None
    result = bridge({})
    # `git status` returns non-zero outside a git repo, so bridge must
    # surface a failure with a descriptive error message.
    assert result.success is False
    assert "not a git repository" in result.error or "git status failed" in result.error


# ---------------------------------------------------------------------------
# Import-boundary invariants (instruction.md §6, §35.4)
# ---------------------------------------------------------------------------


def test_bridges_do_not_import_openhands_directly():
    """Bridge layer must NOT import openhands-sdk directly.

    The OpenHands backend adapter is a different module
    (`aegis_ai/agents/backends/openhands/adapter.py`); bridges must only
    run in-process now that the dev-server is gone (Phase 9).
    """
    from aegis_ai.tools import bridges as _bridges_pkg

    pkg_path = Path(_bridges_pkg.__file__).resolve().parent
    assert pkg_path.exists()

    for py in pkg_path.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "import openhands" not in text, (
            f"{py.name} must not import openhands directly"
        )
        assert "from openhands" not in text, (
            f"{py.name} must not import openhands directly"
        )


def test_bridges_do_not_import_dev_server_pb2():
    """Bridges must not import the generated protobuf stubs directly."""
    from aegis_ai.tools import bridges as _bridges_pkg

    pkg_path = Path(_bridges_pkg.__file__).resolve().parent
    for py in pkg_path.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "dev_server_pb2" not in text, (
            f"{py.name} must not import dev_server_pb2 directly"
        )


def test_bridges_modules_are_importable():
    """All bridge modules must import cleanly under the canonical path."""
    for mod in [
        "aegis_ai.tools.bridges.base",
        "aegis_ai.tools.bridges.filesystem",
    ]:
        importlib.import_module(mod)


def test_git_and_github_bridges_removed():
    """Phase 9: git/github gRPC bridges are deleted. Their modules must
    no longer be importable."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("aegis_ai.tools.bridges.git")
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("aegis_ai.tools.bridges.github")


def test_bridges_do_not_reference_dev_server_grpc_client():
    """Phase 9: no bridge module may import DevServerGrpcClient.

    The dev-server gRPC client module is gone; bridges must not hold
    any reference to it (regression guard).
    """
    from aegis_ai.tools import bridges as _bridges_pkg

    pkg_path = Path(_bridges_pkg.__file__).resolve().parent
    for py in pkg_path.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "DevServerGrpcClient" not in text, (
            f"{py.name} must not reference DevServerGrpcClient"
        )
        assert "aegis_ai.integrations.dev" not in text, (
            f"{py.name} must not import aegis_ai.integrations.dev"
        )
