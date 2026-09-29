"""Filesystem bridge — read-only inspection of the AEGIS workspace.

Phase 6 (instruction.md §36) read 3 個の代替: `ai-server.workspace.repo_status` /
`ai-server.workspace.diff` / `ai-server.workspace.test_results` は
OpenHands 標準ツール (`filesystem.read`, `terminal.execute`) で
代用可能なので、bridge 実装は **policy-enforced な in-process
inspection** としてここで行う.

`AEGIS_REPO_PATH` 環境変数 (Docker: ``/workspace``) をルートとし、
その外のアクセスは `PolicyEngine` 規約に従い deny する.
"""
from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from aegis_ai.tools.bridges.base import (
    BridgeResult,
    ToolBridge,
    register_bridge,
)

logger = logging.getLogger("aegis_ai.tools.bridges.filesystem")

_DEFAULT_REPO_PATH = os.environ.get("AEGIS_REPO_PATH", ".")
_MAX_DIFF_BYTES = 200_000


def _workspace_root() -> Path:
    """Resolve the workspace root. Always absolute."""
    raw = os.environ.get("AEGIS_REPO_PATH", ".") or "."
    return Path(raw).resolve()


def _is_within_workspace(path: Path, root: Path) -> bool:
    """True when ``path`` is inside ``root`` (after symlink-resolve)."""
    try:
        path_resolved = path.resolve(strict=False)
        root_resolved = root.resolve(strict=False)
    except OSError:
        return False
    try:
        path_resolved.relative_to(root_resolved)
        return True
    except ValueError:
        return False


def _enforce_workspace(path: Path) -> BridgeResult | None:
    """Return an error result if ``path`` is outside the workspace; else None."""
    root = _workspace_root()
    if not _is_within_workspace(path, root):
        return BridgeResult(
            success=False,
            error=(
                f"path {path!s} is outside AEGIS_REPO_PATH ({root!s}); "
                "PolicyEngine denies access"
            ),
        )
    return None


def _run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run a git command and return (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", "git executable not found"
    except subprocess.TimeoutExpired:
        return 124, "", "git command timed out"
    return proc.returncode, proc.stdout, proc.stderr


# ---------------------------------------------------------------------------
# repo.status — read-only
# ---------------------------------------------------------------------------


def _repo_status(params: dict[str, Any], *, context: dict[str, Any]) -> BridgeResult:
    """``ai-server.workspace.repo_status`` — current branch / commit / clean state."""
    workspace = _workspace_root()
    rc, out, err = _run_git(
        [
            "status",
            "--porcelain=v1",
            "--branch",
        ],
        workspace,
    )
    if rc != 0:
        return BridgeResult(
            success=False,
            error=f"git status failed: {err.strip() or 'unknown'}",
            capability_id="ai-server.workspace.repo_status",
        )
    return BridgeResult(
        success=True,
        capability_id="ai-server.workspace.repo_status",
        data={
            "branch_output": out,
            "workspace": str(workspace),
        },
    )


# ---------------------------------------------------------------------------
# diff.get_diff — read-only
# ---------------------------------------------------------------------------


def _diff_get(params: dict[str, Any], *, context: dict[str, Any]) -> BridgeResult:
    """``ai-server.workspace.diff`` — diff for pathspec."""
    workspace = _workspace_root()
    pathspec = params.get("path") or params.get("pathspec") or "."
    if isinstance(pathspec, str):
        pathspecs = [pathspec]
    elif isinstance(pathspec, list):
        pathspecs = [str(p) for p in pathspec]
    else:
        pathspecs = ["."]

    rc, out, err = _run_git(
        [
            "--no-pager",
            "diff",
            "--no-color",
            "--",
            *pathspecs,
        ],
        workspace,
    )
    if rc != 0:
        return BridgeResult(
            success=False,
            error=f"git diff failed: {err.strip() or 'unknown'}",
            capability_id="ai-server.workspace.diff",
        )
    if len(out) > _MAX_DIFF_BYTES:
        out = out[:_MAX_DIFF_BYTES] + "\n[truncated]\n"
    return BridgeResult(
        success=True,
        capability_id="ai-server.workspace.diff",
        data={"diff": out, "truncated": len(out) >= _MAX_DIFF_BYTES},
    )


# ---------------------------------------------------------------------------
# test.get_results — read-only
# ---------------------------------------------------------------------------


_TEST_RESULTS_CACHE: dict[str, dict[str, Any]] = {}


def _test_get_results(
    params: dict[str, Any], *, context: dict[str, Any]
) -> BridgeResult:
    """``ai-server.workspace.test_results`` — last cached test run results.

    The actual test execution is `ai-server.test.run_pytest` (write
    class). This read function only returns the
    last cached result. Tests may pass ``run_id`` to look up a
    specific run.
    """
    run_id = str(params.get("run_id", "latest") or "latest")
    cached = _TEST_RESULTS_CACHE.get(run_id) or _TEST_RESULTS_CACHE.get("latest")
    if cached is None:
        return BridgeResult(
            success=True,
            capability_id="ai-server.workspace.test_results",
            data={"cached": False, "result": None, "run_id": run_id},
        )
    return BridgeResult(
        success=True,
        capability_id="ai-server.workspace.test_results",
        data={"cached": True, "result": cached, "run_id": run_id},
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_default_bridges() -> None:
    """Register the read-only filesystem bridges. Idempotent."""
    register_bridge(
        ToolBridge(
            capability_id="ai-server.workspace.repo_status",
            kind="native",
            invoke=_repo_status,
            description="In-process git status for the AEGIS workspace.",
        )
    )
    register_bridge(
        ToolBridge(
            capability_id="ai-server.workspace.diff",
            kind="native",
            invoke=_diff_get,
            description="In-process git diff with workspace confinement.",
        )
    )
    register_bridge(
        ToolBridge(
            capability_id="ai-server.workspace.test_results",
            kind="native",
            invoke=_test_get_results,
            description="Read last cached test run results.",
        )
    )


__all__ = [
    "register_default_bridges",
    "_is_within_workspace",
    "_enforce_workspace",
    "_workspace_root",
]
