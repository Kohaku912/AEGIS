"""Every report read and write must honour ``--report-dir``.

Measured 2026-10-07 (cycle 90), before the fix. ``main`` runs its sub-audits with
``--report-dir <report_dir>`` and ``_e2e_check`` (cycle 87) reads ``<report_dir>/e2e/latest``
-- but seven sites still hard-coded the report tree to ``ROOT``:

* ``main``: the ``pc_real`` and ``android_real`` reads (two call sites) and the
  ``summary.json`` / ``summary.md`` **write**;
* ``_secrets_check``: ``secret_inventory.json`` -- although ``main`` had just told
  ``audit-secrets.py --report-dir <report_dir>`` to write it *there*;
* ``_capability_override_persistence_check``: ``manager-risk-override.json``;
* ``_display_soak_check``: ``display_soak_summary.json``.

Driven with a custom ``--report-dir`` (measured): the three checks' ``evidence`` named the
``ROOT`` tree, ``<custom>/e2e/latest/summary.json`` was never written, and ``ROOT``'s
``summary.json`` / ``summary.md`` were **rewritten** -- a sandbox run clobbered the
operator's real E2E summary while the sandbox got none.

The fix routes every one of the seven through ``report_dir``. The three zero-argument
checks gain a ``report_dir`` parameter; ``_display_path`` keeps the default's evidence
strings byte-identical (relative to ``ROOT`` when inside it) and never raises
``ValueError`` for a report dir outside ``ROOT``.

The default ``--report-dir`` is ``ROOT/data/reports``, so every routed path is
**byte-identical** to the old one -- proved here by re-running the audit end-to-end: all
32 check statuses and the E2E summary are unchanged (one evidence string differs only by
separator style).
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
_AUDIT = _SCRIPTS / "audit-production-readiness.py"

# The three checks cycle 90 gave a report_dir parameter.
_REROUTED_CHECKS = {"_secrets_check", "_capability_override_persistence_check", "_display_soak_check"}


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("readiness_audit_reportdir_probe", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    sys.modules["readiness_audit_reportdir_probe"] = module
    spec.loader.exec_module(module)
    return module


def _report_dir() -> Path:
    from audit_common import REPORT_DIR  # type: ignore[import-not-found]

    return REPORT_DIR


def _main_fn() -> ast.FunctionDef:
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return node
    raise AssertionError("main() not found in the readiness audit")


# --- the hard-coded report path is gone (AST) ------------------------------------------


def _rooted_report_paths() -> list[str]:
    """Every ``ROOT / ... "data" ...`` expression in the module -- the defect shape."""
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        parts: list[object] = []
        cur: ast.AST = node
        while isinstance(cur, ast.BinOp) and isinstance(cur.op, ast.Div):
            if isinstance(cur.right, ast.Constant):
                parts.append(cur.right.value)
            cur = cur.left
        parts.reverse()
        if isinstance(cur, ast.Name) and cur.id == "ROOT" and any(isinstance(p, str) and "data" in p for p in parts):
            offenders.append(ast.unparse(node))
    return offenders


def test_no_report_path_is_hardcoded_to_root() -> None:
    """The family closed: no report path is rooted at ``ROOT`` any more."""
    assert _rooted_report_paths() == []


def test_the_hardcoded_path_was_a_real_shape() -> None:
    """Control: the detector fires on the shape it is meant to catch."""
    sample = ast.parse('x = ROOT / "data" / "reports" / "e2e" / "latest"\n').body[0]
    node = sample.value  # type: ignore[attr-defined]
    assert isinstance(node, ast.BinOp)


def test_the_three_rerouted_checks_take_a_report_dir() -> None:
    """Each gained the parameter; a regression to zero-argument reddens here."""
    module = _load()
    import inspect

    for name in sorted(_REROUTED_CHECKS):
        assert "report_dir" in inspect.signature(getattr(module, name)).parameters, name


# --- every call site passes the report dir ---------------------------------------------


def _reader_calls() -> list[ast.Call]:
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _REROUTED_CHECKS
    ]


def test_every_reader_call_site_passes_the_report_dir() -> None:
    calls = _reader_calls()
    assert len(calls) == len(_REROUTED_CHECKS), f"expected {len(_REROUTED_CHECKS)} call sites, found {len(calls)}"
    for call in calls:
        assert call.args, f"{call.func.id} called without report_dir"  # type: ignore[attr-defined]
        first = call.args[0]
        assert isinstance(first, ast.Name) and first.id == "report_dir", ast.unparse(first)


def test_the_e2e_summary_write_is_rooted_at_report_dir() -> None:
    """The write must land in the same tree the E2E checks read."""
    assigns = [
        node
        for node in ast.walk(_main_fn())
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "latest"
    ]
    assert len(assigns) == 1, f"expected exactly one `latest = ...` in main(), found {len(assigns)}"
    names = {x.id for x in ast.walk(assigns[0].value) if isinstance(x, ast.Name)}
    assert "report_dir" in names, "the E2E summary write does not use report_dir"
    assert "ROOT" not in names, "the E2E summary write is rooted at ROOT again"


def test_the_e2e_reads_are_rooted_at_report_dir() -> None:
    """No ``_real_device_report_check`` / android ``_report_pass`` call roots its path at ROOT."""
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        if node.func.id not in {"_real_device_report_check", "_report_pass"}:
            continue
        first = node.args[0] if node.args else None
        if first is None:
            continue
        names = {x.id for x in ast.walk(first) if isinstance(x, ast.Name)}
        if "ROOT" in names:
            raise AssertionError(f"{node.func.id} call roots its path at ROOT: {ast.unparse(first)}")


# --- behaviour: a custom report dir is honoured ----------------------------------------


def _write(report_dir: Path, rel: str, payload: object) -> None:
    path = report_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(payload), encoding="utf-8")


def test_secrets_check_reads_the_passed_report_dir(tmp_path: Path) -> None:
    """A report written only under the custom dir is the one the check reads."""
    _write(tmp_path, "secret_inventory.json", {"status": "pass", "findings": []})
    result = _load()._secrets_check(tmp_path)
    assert result["status"] == "pass", result


def test_secrets_check_names_the_passed_report_dir(tmp_path: Path) -> None:
    result = _load()._secrets_check(tmp_path)
    assert result["status"] == "fail"
    assert any(str(tmp_path) in str(e) for e in result["evidence"]), result["evidence"]


def test_secrets_check_ignores_the_default_tree(tmp_path: Path) -> None:
    """Control: an empty custom dir fails even though the default tree has a report."""
    result = _load()._secrets_check(tmp_path / "nothing-here")
    assert result["status"] == "fail"
    assert "missing" in str(result["error"]).lower(), result["error"]


def test_display_soak_reads_the_passed_report_dir(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "e2e/latest/display_soak_summary.json",
        {"status": "pass", "duration_seconds": 72 * 3600, "equivalent_duration_seconds": 0, "failure_count": 0},
    )
    result = _load()._display_soak_check(tmp_path)
    assert result["status"] == "pass", result


def test_display_soak_names_the_passed_report_dir(tmp_path: Path) -> None:
    result = _load()._display_soak_check(tmp_path)
    assert result["status"] == "fail"
    assert any(str(tmp_path) in str(e) for e in result["evidence"]), result["evidence"]


def test_capability_override_reads_the_passed_report_dir(tmp_path: Path) -> None:
    """The E2E evidence is read from the custom dir; the *source* still comes from ROOT."""
    _write(tmp_path, "e2e/latest/manager-risk-override.json", {"status": "pass"})
    result = _load()._capability_override_persistence_check(tmp_path)
    assert result["status"] == "pass", result


def test_capability_override_ignores_the_default_tree(tmp_path: Path) -> None:
    """Control: the live default tree has the evidence; a custom dir without it fails."""
    result = _load()._capability_override_persistence_check(tmp_path)
    assert result["status"] == "fail"
    assert "E2E evidence" in str(result["error"]), result["error"]


def test_capability_override_names_the_passed_report_dir(tmp_path: Path) -> None:
    result = _load()._capability_override_persistence_check(tmp_path)
    assert any(str(tmp_path) in str(e) for e in result["evidence"]), result["evidence"]


# --- _display_path: relative inside ROOT, absolute outside, never raising --------------


def test_display_path_is_relative_inside_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    assert module._display_path(tmp_path / "data" / "reports" / "x.json") == str(Path("data/reports/x.json"))


def test_display_path_is_absolute_outside_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load()
    monkeypatch.setattr(module, "ROOT", tmp_path / "inside")
    outside = tmp_path / "outside" / "x.json"
    assert module._display_path(outside) == str(outside)


def test_display_path_never_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load()
    monkeypatch.setattr(module, "ROOT", tmp_path / "inside")
    for path in (tmp_path / "outside", tmp_path / "inside" / "x", Path("relative")):
        assert isinstance(module._display_path(path), str)


def test_display_path_is_used_by_the_relative_evidence_sites() -> None:
    """The two sites that used ``relative_to(ROOT)`` now route through the guarded helper."""
    src = _AUDIT.read_text(encoding="utf-8")
    assert "str(report.relative_to(ROOT))" not in src, "an unguarded relative_to(ROOT) is back"
    assert "str(e2e_path.relative_to(ROOT))" not in src, "an unguarded relative_to(ROOT) is back"


# --- the default is unchanged ----------------------------------------------------------


def test_the_default_report_dir_is_the_live_e2e_tree() -> None:
    """A no-op for the default: ``REPORT_DIR/e2e/latest`` *is* the old hard-coded path."""
    assert _report_dir() / "e2e" / "latest" == _REPO_ROOT / "data" / "reports" / "e2e" / "latest"


def test_the_live_secrets_report_resolves_from_the_default() -> None:
    result = _load()._secrets_check(_report_dir())
    assert result["status"] in {"pass", "fail"}, result
    assert result["evidence"], "the live secrets check names nothing it read"


def test_the_live_display_soak_resolves_from_the_default() -> None:
    result = _load()._display_soak_check(_report_dir())
    assert result["status"] in {"pass", "fail"}, result
    assert result["evidence"], "the live soak check names nothing it read"


def test_the_live_secrets_evidence_stays_relative_to_root() -> None:
    """The default's evidence must keep its historical shape (a ROOT-relative string)."""
    result = _load()._secrets_check(_report_dir())
    assert not Path(str(result["evidence"][0])).is_absolute(), result["evidence"]


def test_the_live_capability_override_evidence_stays_relative_to_root() -> None:
    result = _load()._capability_override_persistence_check(_report_dir())
    assert not Path(str(result["evidence"][0])).is_absolute(), result["evidence"]
