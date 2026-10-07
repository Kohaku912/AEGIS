"""A source-reading readiness check must fail, not abort the audit.

Measured 2026-10-07, before the fix:

* ``scripts/audit-production-readiness.py`` evaluates every check in ``main`` *before* it
  writes ``readiness_summary.json``. Three of its six source-reading checks called
  ``(ROOT / rel).read_text(...)`` with **no** existence guard -- ``_dashboard_auth_check``,
  ``_capability_override_persistence_check`` and ``_mock_provider_reject_check`` -- while
  the other three guarded with ``.exists()``.
* Driven with a ``ROOT`` that lacks the file, the three unguarded ones raised
  ``FileNotFoundError``: out of ``main``, before any write. So a single moved source file
  would abort the whole audit and leave the **previous** report on disk -- a stale report
  that every downstream reader (the dashboard route's ``load_production_blocker_report``
  and ``_load_blockers``) then reads as fresh.
* ``_dashboard_auth_check`` also returned ``evidence=[]`` on **every** branch: the live
  readiness summary had it as the only check naming nothing it measured.

The population is **discovered** from the module's AST (functions whose body reads a file
and whose only parameter is ``report_dir``), not hand-listed, so a new source-reading check
cannot be added unguarded without these pins noticing; a declared set documents the intent
and reddens on drift. Cycle 90 gave ``_capability_override_persistence_check`` a
``report_dir`` parameter, so the discovery admits that shape too.
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
_AUDIT = _SCRIPTS / "audit-production-readiness.py"

# The declared population. `_source_reading_checks` discovers it; a mismatch reddens both
# this and the family drive, so a new member cannot slip in unguarded.
_EXPECTED_SOURCE_READERS = {
    "_dashboard_auth_check",
    "_capability_override_persistence_check",
    "_mock_provider_reject_check",
    "_docker_bind_check",
    "_room_production_scope_check",
    "_volume_persistence_check",
}


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _load_readiness_audit() -> Any:
    """Load the repo-root audit by path (its name has hyphens, so no `import`)."""
    spec = importlib.util.spec_from_file_location("readiness_audit_probe", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolve string annotations through sys.modules, so register it first.
    sys.modules["readiness_audit_probe"] = module
    spec.loader.exec_module(module)
    return module


def _source_reading_checks() -> set[str]:
    """Zero-argument functions in the audit whose body reads a file -- discovered, not listed.

    Two shapes count: an inline ``X.read_text(...)`` (the guarded siblings) and a call to
    the ``_source_text`` helper (the three checks the fix moved onto it). Keying on
    ``read_text`` alone would silently drop the very members the fix introduced -- the same
    trap cycle 83 hit when the dead-code script name lived inside a list literal.
    """

    def _reads(node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False
        if isinstance(node.func, ast.Attribute) and node.func.attr == "read_text":
            return True
        return isinstance(node.func, ast.Name) and node.func.id == "_source_text"

    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        args = node.args
        params = [a.arg for a in (*args.posonlyargs, *args.args)]
        if args.vararg or args.kwarg or args.kwonlyargs:
            continue
        if [p for p in params if p != "report_dir"]:
            continue
        if any(_reads(inner) for inner in ast.walk(node)):
            names.add(node.name)
    return names


def _drive(module: Any, name: str, report_dir: Path) -> dict[str, object]:
    """Call a member, passing ``report_dir`` only when it declares one."""
    fn = getattr(module, name)
    return fn(report_dir) if "report_dir" in inspect.signature(fn).parameters else fn()


def test_the_source_reading_family_is_enumerated() -> None:
    """Discovery must equal the declared set: neither an omission nor a new unguarded member."""
    assert _source_reading_checks() == _EXPECTED_SOURCE_READERS


def test_no_source_reading_check_aborts_the_audit_when_its_file_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The family drive: with an empty ROOT every member returns a verdict, none raises.

    This is the behavioural pin. Before the fix it raised ``FileNotFoundError`` for the
    three unguarded members, which is exactly the abort that skips the report write.
    """
    module = _load_readiness_audit()
    monkeypatch.setattr(module, "ROOT", tmp_path)  # empty dir: every source file is absent
    for name in sorted(_source_reading_checks()):
        result = _drive(module, name, tmp_path)  # must not raise
        assert result["status"] in {"pass", "fail", "warn"}, name
        assert result["evidence"], f"{name} returned a verdict naming nothing it read"


def test_the_missing_file_is_named_in_the_verdict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing file must be a *named* failure, not a traceback."""
    module = _load_readiness_audit()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    expected = {
        "_dashboard_auth_check": "ai-server/src/aegis_ai/docker_entrypoint.py",
        "_capability_override_persistence_check": "ai-server/src/aegis_ai/capability_catalog.py",
        "_mock_provider_reject_check": "ai-server/src/aegis_ai/production_readiness.py",
    }
    for name, rel in expected.items():
        result = _drive(module, name, tmp_path)
        assert result["status"] == "fail", name
        assert rel in result["evidence"], (name, result["evidence"])
        assert rel in result["error"], (name, result["error"])


def test_the_guarded_siblings_still_return_a_clean_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Control: the three checks that were *already* guarded keep their old shape."""
    module = _load_readiness_audit()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    for name in ("_docker_bind_check", "_room_production_scope_check", "_volume_persistence_check"):
        result = getattr(module, name)()
        assert result["status"] == "fail", name
        assert result["evidence"], name


def test_every_source_reading_check_names_what_it_read() -> None:
    """The denominator pin: against the *real* tree, no member returns an empty evidence list.

    Before the fix ``_dashboard_auth_check`` returned ``evidence=[]`` on every branch -- the
    only check in the live readiness summary that named nothing it measured.
    """
    module = _load_readiness_audit()  # real ROOT
    for name in sorted(_source_reading_checks()):
        result = _drive(module, name, _REPO_ROOT / "data" / "reports")
        assert result["evidence"], f"{name} returned a verdict naming nothing it read"


def test_no_check_reads_a_path_it_did_not_bind_and_guard() -> None:
    """Structural invariant: a `read_text` receiver is a *name*, never an inline `ROOT / rel`.

    The guarded siblings bind ``compose = ROOT / "..."`` then test ``compose.exists()``; the
    two loaders and ``_source_text`` bind the path too. An inline ``(ROOT / rel).read_text()``
    is therefore the defect shape, and this pin makes it a build failure rather than a crash
    that only shows up once a file is moved.
    """
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr != "read_text":
            continue
        receiver = node.func.value
        if isinstance(receiver, ast.BinOp) and isinstance(receiver.op, ast.Div):
            offenders.append(ast.unparse(receiver))
    assert offenders == [], f"unguarded inline path reads: {offenders}"
