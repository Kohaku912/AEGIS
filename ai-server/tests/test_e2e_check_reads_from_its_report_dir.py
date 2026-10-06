"""``_e2e_check`` must read the E2E tree from the report dir its caller passes.

Measured 2026-10-07 (cycle 87), before the fix:

* ``scripts/audit-production-readiness.py``'s ``_e2e_check`` took ``report_dir`` as its
  first argument and all six call sites passed it -- but the body **never used it**. It
  hard-coded ``ROOT / "data" / "reports" / "e2e" / "latest"`` instead.
* With the default ``--report-dir`` (``data/reports``) the two agree, so the audit looked
  fine. With a custom ``--report-dir`` they do not: driving the check with a ``report_dir``
  that holds a valid ``summary.json`` while ``ROOT`` holds none returned
  ``"Missing E2E result for docker_core"`` -- the argument was ignored, disagreeing with
  ``_report_pass``, which honours it.
* The function also overrides the ``summary.json`` entry with a per-check file
  (``docker-core.json``) whenever the file's ``id`` matches, with **no freshness guard**:
  a summary ``fail`` plus a standalone ``pass`` returned ``pass``. That precedence is
  pinned here as-is (changing it is an owner decision), not silently altered.

The fix routes every read through ``report_dir / "e2e" / "latest"`` -- byte-identical to
the old path for the default, and correct for a custom one. ``report_dir`` is a Name in the
body again, and ``ROOT`` is not (checked through the AST, so the explanatory comment that
*names* ``ROOT`` cannot satisfy it -- a mention is not a reader).
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
_AUDIT = _SCRIPTS / "audit-production-readiness.py"

# The six call sites, discovered from the AST below; declared here so a seventh reddens.
_EXPECTED_E2E_CHECKS = 6


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _load_readiness_audit() -> Any:
    """Load the repo-root audit by path (its name has hyphens, so no `import`)."""
    spec = importlib.util.spec_from_file_location("readiness_audit_e2e_probe", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    sys.modules["readiness_audit_e2e_probe"] = module
    spec.loader.exec_module(module)
    return module


def _e2e_check_fn() -> ast.FunctionDef:
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_e2e_check":
            return node
    raise AssertionError("_e2e_check not found in the readiness audit")


def _names_in(fn: ast.FunctionDef) -> set[str]:
    return {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}


def _e2e_call_first_args() -> list[str]:
    """The first positional argument source of every ``_e2e_check(...)`` call."""
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    args: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_e2e_check":
            assert node.args, "every _e2e_check call must pass a report_dir"
            first = node.args[0]
            args.append(first.id if isinstance(first, ast.Name) else ast.dump(first))
    return args


def _drive(report_dir: Path, check_id: str = "docker_core") -> dict[str, object]:
    return _load_readiness_audit()._e2e_check(report_dir, check_id, "Docker core E2E")


def _write_e2e(tmp: Path, files: dict[str, object]) -> Path:
    report_dir = tmp / "data" / "reports"
    latest = report_dir / "e2e" / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    for name, obj in files.items():
        (latest / name).write_text(json.dumps(obj), encoding="utf-8")
    return report_dir


# --- the dead-parameter regression, read through the AST ------------------------------


def test_e2e_check_references_its_report_dir_argument() -> None:
    """The parameter must be *used*; it was accepted and passed but never read."""
    assert "report_dir" in _names_in(_e2e_check_fn()), (
        "_e2e_check accepts report_dir but never reads it -- the hard-coded path is back"
    )


def test_e2e_check_does_not_hardcode_root() -> None:
    """No ``ROOT`` in the body: the path must come from ``report_dir`` (comments do not count)."""
    assert "ROOT" not in _names_in(_e2e_check_fn()), (
        "_e2e_check hard-codes ROOT again instead of using report_dir"
    )


def test_every_call_site_passes_the_report_dir() -> None:
    args = _e2e_call_first_args()
    assert len(args) == _EXPECTED_E2E_CHECKS, f"expected {_EXPECTED_E2E_CHECKS} call sites, found {len(args)}"
    assert set(args) == {"report_dir"}, f"a call site passes something other than report_dir: {sorted(set(args))}"


# --- behaviour: the argument is honoured ----------------------------------------------


def test_a_custom_report_dir_is_honoured(tmp_path: Path) -> None:
    """Data under ``report_dir`` is read even when ``ROOT`` knows nothing about it."""
    report_dir = _write_e2e(tmp_path, {"summary.json": {"checks": [{"id": "docker_core", "status": "pass"}]}})
    result = _drive(report_dir)
    assert result["status"] == "pass", f"report_dir was ignored: {result}"
    assert result["error"] == ""


def test_a_report_dir_without_data_yields_missing_e2e_result(tmp_path: Path) -> None:
    """Control: an empty report_dir is a clean ``fail`` naming the summary, not a crash."""
    report_dir = tmp_path / "data" / "reports"
    (report_dir / "e2e" / "latest").mkdir(parents=True)
    result = _drive(report_dir)
    assert result["status"] == "fail"
    assert "Missing E2E result" in str(result["error"])


def test_the_default_report_dir_is_the_live_e2e_tree() -> None:
    """The fix is a no-op for the default ``--report-dir`` (``data/reports``)."""
    from audit_common import REPORT_DIR  # type: ignore[import-not-found]

    assert REPORT_DIR / "e2e" / "latest" / "summary.json" == (
        _REPO_ROOT / "data" / "reports" / "e2e" / "latest" / "summary.json"
    )


# --- precedence: a standalone file overrides the summary entry (pinned, not changed) ---


def test_a_standalone_file_overrides_the_summary_entry(tmp_path: Path) -> None:
    """Documented precedence: the per-check file wins over the summary, in both directions."""
    report_dir = _write_e2e(
        tmp_path,
        {
            "summary.json": {"checks": [{"id": "docker_core", "status": "fail"}]},
            "docker-core.json": {"id": "docker_core", "status": "pass"},
        },
    )
    assert _drive(report_dir)["status"] == "pass"


def test_a_standalone_file_with_a_foreign_id_does_not_override(tmp_path: Path) -> None:
    """Control: the file only wins when its ``id`` matches the check."""
    report_dir = _write_e2e(
        tmp_path,
        {
            "summary.json": {"checks": [{"id": "docker_core", "status": "fail"}]},
            "docker-core.json": {"id": "someone_else", "status": "pass"},
        },
    )
    assert _drive(report_dir)["status"] == "fail"


def test_the_six_live_ids_still_resolve_from_the_default_tree() -> None:
    """If the live E2E tree is present, the default report_dir resolves it (no live edit)."""
    from audit_common import REPORT_DIR  # type: ignore[import-not-found]

    latest = REPORT_DIR / "e2e" / "latest"
    if not latest.is_dir():
        pytest.skip("live E2E tree not present")
    for check_id in ("docker_core", "docker_persistence", "backup_restore", "manager_e2e", "browser_real", "dev_real"):
        result = _drive(REPORT_DIR, check_id)
        assert result["status"] in {"pass", "fail"}, result
