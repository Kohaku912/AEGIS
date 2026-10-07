"""Every sibling audit must honour ``--report-dir`` -- for reads *and* writes.

Measured 2026-10-07 (cycle 91), before the fix. The readiness audit (cycle 90) routed its
own report paths through ``--report-dir``, but two siblings it *runs* still did not:

* ``audit-ui-completeness.py`` called no ``argparse`` at all -- ``parse_args`` / ``args.``
  appear zero times -- so ``--report-dir`` was ignored outright. Driven with a custom dir
  it wrote ``ROOT/data/reports/ui_completeness.{json,md}`` and never created the custom
  dir; ``ROOT``'s report mtime moved. The readiness audit then read
  ``<custom>/ui_completeness.json`` and found nothing.
* ``audit-v1-completion.py`` wrote into the custom dir, but its four report **reads** were
  module-level ``ROOT`` constants (``E2E_SUMMARY`` / ``UI_REPORT`` / ``MOCK_REPORT`` /
  ``CAPABILITY_REPORT``), so its evidence named the ``ROOT`` tree
  (``data/reports/ui_completeness.json``, ...) even when pointed at an empty directory. A
  sandbox run reported on the operator's real reports.

The fix routes every report path through ``report_dir``. ``_display_path`` keeps the
default's evidence strings byte-identical (posix, relative to ``ROOT`` when inside it) and
never raises ``ValueError`` for a report dir outside ``ROOT``.

The default ``--report-dir`` is ``ROOT/data/reports``, so every routed path is
**byte-identical** to the old hard-coded one -- proved here by re-running both audits with
the default: ``ui_completeness.json`` / ``.md`` and ``v1_completion.md`` are byte-identical
and ``v1_completion.json`` is identical once ``generated_at`` / ``duration_ms`` are dropped.
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
_UI = _SCRIPTS / "audit-ui-completeness.py"
_V1 = _SCRIPTS / "audit-v1-completion.py"

# The four report reads cycle 91 routed through report_dir.
_REROUTED_CHECKS = {"ui_completeness", "capability_coverage", "production_blocker_mock_zero", "required_real_e2e"}


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _drive(module: Any, argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    old_argv = sys.argv
    sys.argv = argv
    try:
        rc = module.main()
    finally:
        sys.argv = old_argv
    return rc, capsys.readouterr().out


def _div_chain(node: ast.AST) -> tuple[str | None, list[str]]:
    """Flatten ``a / "x" / "y"`` into ``(base_name, ["x", "y"])``.

    ``base_name`` is ``None`` when the leftmost operand is not a bare name, and the
    segment list is empty when any ``/`` operand is not a string constant -- so a chain
    like ``ROOT / path`` (a variable) is not reported as a literal report path.
    """
    segments: list[str] = []
    cur = node
    while isinstance(cur, ast.BinOp) and isinstance(cur.op, ast.Div):
        right = cur.right
        if isinstance(right, ast.Constant) and isinstance(right.value, str):
            segments.append(right.value)
        else:
            return None, []
        cur = cur.left
    base = cur.id if isinstance(cur, ast.Name) else None
    return base, list(reversed(segments))


def _root_data_paths(path: Path) -> list[int]:
    """Line numbers of ``ROOT / "data" / ...`` expressions -- a report path that ignores ``--report-dir``."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            base, segments = _div_chain(node)
            if base == "ROOT" and segments and segments[0] == "data":
                hits.append(node.lineno)
    return hits


# --- the family is closed: no report path is rooted at ROOT ------------------------------


@pytest.mark.parametrize("script", [_UI, _V1], ids=["ui-completeness", "v1-completion"])
def test_no_report_path_is_rooted_at_root(script: Path) -> None:
    hits = _root_data_paths(script)
    assert hits == [], (
        f"{script.name} still builds a report path as ROOT/...data... at line(s) {hits}; "
        "that read or write ignores --report-dir"
    )


@pytest.mark.parametrize("script", [_UI, _V1], ids=["ui-completeness", "v1-completion"])
def test_both_siblings_use_the_shared_argument_parser(script: Path) -> None:
    tree = ast.parse(script.read_text(encoding="utf-8"))
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "parse_args" in called, f"{script.name} must accept --report-dir via the shared parser"


# --- the default is unchanged: the routed path equals the old hard-coded one -------------


@pytest.mark.parametrize("script", [_UI, _V1], ids=["ui-completeness", "v1-completion"])
def test_default_report_dir_is_the_old_hard_coded_tree(script: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from audit_common import REPORT_DIR, parse_args  # type: ignore[import-not-found]

    assert REPORT_DIR == _REPO_ROOT / "data" / "reports"
    monkeypatch.setattr(sys, "argv", [script.name])
    assert Path(parse_args("probe").report_dir) == REPORT_DIR


# --- ui-completeness writes where it was told -------------------------------------------


def test_ui_completeness_writes_into_the_custom_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load("c91_ui", _UI)
    root = tmp_path / "repo"
    real = root / "data" / "reports"
    real.mkdir(parents=True)
    monkeypatch.setattr(module, "ROOT", root)
    # A sentinel the run must not touch: a ROOT-rooted write would rewrite it.
    sentinel = real / "ui_completeness.json"
    sentinel.write_text("untouched", encoding="utf-8")
    before = sentinel.read_bytes()

    custom = tmp_path / "custom"
    rc, out = _drive(module, [str(_UI), "--report-dir", str(custom)], capsys)

    assert (custom / "ui_completeness.json").exists(), out
    assert (custom / "ui_completeness.md").exists(), out
    assert str(custom) in out, out
    assert sentinel.read_bytes() == before, "the ROOT report must not be rewritten"
    assert rc == 1  # the UI ledger is still partial; the point is *where* it wrote


# --- v1-completion reads its reports from where it was told ------------------------------


def test_v1_completion_reads_its_reports_from_the_custom_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Pointed at an empty dir, the four report checks must fail *there*, not pass on ROOT's tree."""
    module = _load("c91_v1", _V1)
    custom = tmp_path / "custom"
    custom.mkdir()

    rc, _ = _drive(module, [str(_V1), "--report-dir", str(custom)], capsys)
    payload = json.loads((custom / "v1_completion.json").read_text(encoding="utf-8"))
    checks = {check["id"]: check for check in payload["checks"]}

    assert rc == 1
    for check_id in _REROUTED_CHECKS:
        check = checks[check_id]
        assert check["status"] == "fail", check
        evidence = check["evidence"][0]
        assert str(custom) in evidence, (check_id, evidence)
        assert "data/reports" not in evidence, (check_id, evidence)


def test_v1_completion_never_reads_the_root_tree_for_a_custom_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A *populated* ROOT tree must not leak into a run pointed at an empty dir.

    The four report checks fail for the custom dir even though the real reports exist --
    the run must not read them. The wording differs per check (``_report_status`` says
    "Missing or unreadable", the blocker check says "does not report files_scanned"), so
    the property pinned is the *path*: each check names the custom dir somewhere in its
    evidence or error, and never the ``ROOT`` report tree.
    """
    module = _load("c91_v1_leak", _V1)
    custom = tmp_path / "custom"
    custom.mkdir()

    _, _ = _drive(module, [str(_V1), "--report-dir", str(custom)], capsys)
    payload = json.loads((custom / "v1_completion.json").read_text(encoding="utf-8"))
    checks = {check["id"]: check for check in payload["checks"]}

    # The real ROOT reports exist (this repository is the one being audited), so a leak
    # would show up as a non-"missing" error or a pass.
    assert (module.ROOT / "data" / "reports" / "ui_completeness.json").exists()
    for check_id in _REROUTED_CHECKS:
        check = checks[check_id]
        blob = " ".join(str(item) for item in [*check["evidence"], check["error"]])
        assert check["status"] == "fail", check
        assert str(custom) in blob, (check_id, blob)
        assert "data/reports" not in blob, (check_id, blob)
        assert str(module.ROOT) not in blob, (check_id, blob)


# --- _display_path: posix-relative inside ROOT, absolute outside, never raising ----------


def test_v1_display_path_is_relative_inside_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load("c91_v1_display", _V1)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    assert module._display_path(tmp_path / "data" / "reports" / "x.json") == "data/reports/x.json"


def test_v1_display_path_is_absolute_outside_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load("c91_v1_display_out", _V1)
    monkeypatch.setattr(module, "ROOT", tmp_path / "repo")
    outside = tmp_path / "elsewhere" / "x.json"
    assert module._display_path(outside) == str(outside)


def test_v1_display_path_never_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load("c91_v1_display_never", _V1)
    monkeypatch.setattr(module, "ROOT", tmp_path / "repo")
    for path in (tmp_path / "a", tmp_path / "repo" / "b", Path("relative") / "c"):
        assert isinstance(module._display_path(path), str)
