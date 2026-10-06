"""The dead-code audit was the one audit outside every accounting.

Measured 2026-10-07, before the fix:

* ``scripts/audit-dead-code.py`` was the **only** ``scripts/audit-*.py`` that could not
  fail -- it ended ``return 0`` while its six siblings end
  ``return 0 if status == "pass" else 1`` -- and it printed ``dead_or_obsolete=0`` over a
  tree it never walked. That is the empty-population family cycle 80 pinned in three
  siblings, minus one member.
* its reference lookup collapsed **three** outcomes into one blank string. ``rg`` exits 1
  for "no match", which ``run_command`` reports as ``status="fail"`` -- the same status it
  uses when the binary could not be launched at all -- so a failed search and a real empty
  result both rendered as ``""``. The live report had **0 of 5** non-empty reference cells,
  and a blank cell reads as the strongest dead-code claim ("nothing references this file")
  when in fact nothing was searched. ``rg`` is not declared anywhere in the repository.
* ``scripts/audit-production-readiness.py`` **discarded** the result (a bare
  ``run_command(...)`` statement), so the audit's status was in neither ``checks`` nor
  ``summary.checks_total``: the live report had 30 checks and no dead-code id.

Each negative case is paired with a control that must stay clean, and the consumer pin is
structural (``ast``, not text): the defect *is* the discarded return value, so the pin is
that the call is assigned and that an entry is built from it.
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


def _load(name: str, filename: str) -> Any:
    """Load a repo-root audit by explicit path (its name has hyphens, so no `import`)."""
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / filename)
    assert spec is not None and spec.loader is not None, f"cannot load {filename}"
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolve string annotations through sys.modules, so register it first.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _drive(module: Any, argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    old_argv = sys.argv
    sys.argv = argv
    try:
        rc = module.main()
    finally:
        sys.argv = old_argv
    return rc, capsys.readouterr().out


def _launch_failure() -> dict[str, object]:
    """What ``run_command`` returns when the binary could not be started at all."""
    return {
        "command": ["rg"],
        "status": "fail",
        "exit_code": 1,
        "duration_ms": 1,
        "stdout": "",
        "stderr": "FileNotFoundError: [WinError 2] The system cannot find the file specified",
    }


# ---------------------------------------------------------------- the pure renderer


def test_a_failed_search_is_not_rendered_as_an_empty_string() -> None:
    tool = _load("c83_render_failed", "audit-dead-code.py")

    text, ran = tool.reference_lookup_text(_launch_failure())

    assert ran is False, "a search that never ran must not claim it did"
    assert text, "a failed search must not render as a blank reference cell"
    assert text.startswith("<reference search could not run:"), text
    assert "FileNotFoundError" in text, text


def test_a_real_empty_search_is_rendered_as_no_references() -> None:
    """``rg`` exits 1 for "no match"; that is a *result*, not a failure."""
    tool = _load("c83_render_nomatch", "audit-dead-code.py")

    text, ran = tool.reference_lookup_text(
        {"command": ["rg"], "status": "fail", "exit_code": 1, "stdout": "", "stderr": ""}
    )

    assert ran is True, "rg's documented no-match exit code is a completed search"
    assert text == "<no references found>", text
    # The control: the two situations must not share a rendering. This is the defect.
    assert text != tool.reference_lookup_text(_launch_failure())[0]


def test_a_successful_search_is_rendered_as_its_output() -> None:
    tool = _load("c83_render_hit", "audit-dead-code.py")

    text, ran = tool.reference_lookup_text(
        {"command": ["rg"], "status": "pass", "exit_code": 0, "stdout": "a.py:3:hit\n", "stderr": ""}
    )

    assert (text, ran) == ("a.py:3:hit", True)


def test_an_error_exit_is_not_mistaken_for_a_no_match() -> None:
    """Only exit 1 *with an empty stderr* is rg's no-match; anything else did not search."""
    tool = _load("c83_render_error", "audit-dead-code.py")

    text, ran = tool.reference_lookup_text(
        {"command": ["rg"], "status": "fail", "exit_code": 2, "stdout": "", "stderr": "unrecognized flag"}
    )

    assert ran is False, text
    assert text.startswith("<reference search could not run:"), text


# ------------------------------------------------- the report never has a blank cell


def test_the_report_never_has_a_blank_reference_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = _load("c83_blank_cell", "audit-dead-code.py")
    root = tmp_path / "repo"
    root.mkdir()
    (root / "debug_out.txt").write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(tool, "ROOT", root)
    monkeypatch.setattr(tool, "run_command", lambda *a, **k: _launch_failure())
    report = tmp_path / "reports"

    rc, out = _drive(tool, ["audit-dead-code.py", "--report-dir", str(report), "--json-only"], capsys)

    payload = json.loads((report / "dead_code_report.json").read_text(encoding="utf-8"))
    assert payload["findings"], "the fixture tree must produce a finding"
    blanks = [f["file"] for f in payload["findings"] if not str(f["text"]).strip()]
    assert blanks == [], f"a failed search still renders blank for: {blanks}"
    assert all(f["text"].startswith("<reference search could not run:") for f in payload["findings"])
    assert payload["reference_search_failures"] == len(payload["findings"]), payload["reference_search_failures"]
    assert rc == 0, out  # a degraded *reference column* is not, by itself, a failed audit


def test_a_real_match_still_becomes_the_reference_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The control: the guard must not be "every reference becomes could-not-run"."""
    tool = _load("c83_real_cell", "audit-dead-code.py")
    root = tmp_path / "repo"
    root.mkdir()
    (root / "debug_out.txt").write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(tool, "ROOT", root)
    monkeypatch.setattr(
        tool,
        "run_command",
        lambda *a, **k: {
            "command": ["rg"],
            "status": "pass",
            "exit_code": 0,
            "stdout": "src/other.py:9:debug_out.txt\n",
            "stderr": "",
        },
    )
    report = tmp_path / "reports"

    _drive(tool, ["audit-dead-code.py", "--report-dir", str(report), "--json-only"], capsys)

    payload = json.loads((report / "dead_code_report.json").read_text(encoding="utf-8"))
    assert payload["reference_search_failures"] == 0
    assert payload["findings"][0]["text"] == "src/other.py:9:debug_out.txt"


# --------------------------------------------------------- the population denominator


def test_the_dead_code_audit_refuses_to_pass_over_an_empty_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = _load("c83_empty_tree", "audit-dead-code.py")
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(tool, "ROOT", empty)
    report = tmp_path / "reports"

    rc, out = _drive(tool, ["audit-dead-code.py", "--report-dir", str(report), "--json-only"], capsys)

    assert rc != 0, f"a tree with nothing in it must not audit as clean, got:\n{out}"
    assert "files_walked=0" in out, out
    assert "no files were walked" in out, out
    payload = json.loads((report / "dead_code_report.json").read_text(encoding="utf-8"))
    assert payload["status"] != "pass", payload["status"]
    assert payload["files_walked"] == 0


def test_the_dead_code_audit_still_passes_over_a_read_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The control: the guard must not be "everything fails"."""
    tool = _load("c83_read_tree", "audit-dead-code.py")
    root = tmp_path / "repo"
    root.mkdir()
    (root / "keep.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(tool, "ROOT", root)
    monkeypatch.setattr(tool, "run_command", lambda *a, **k: {"status": "pass", "exit_code": 0, "stdout": "", "stderr": ""})
    report = tmp_path / "reports"

    rc, out = _drive(tool, ["audit-dead-code.py", "--report-dir", str(report), "--json-only"], capsys)

    assert rc == 0, f"a walked, clean tree must still pass, got:\n{out}"
    assert "files_walked=1" in out, out
    payload = json.loads((report / "dead_code_report.json").read_text(encoding="utf-8"))
    assert payload["status"] == "pass"
    assert payload["files_walked"] == 1
    assert payload["findings"] == []


# ------------------------------------------------------------- the consumer reads it


def test_the_readiness_report_check_requires_the_population(tmp_path: Path) -> None:
    """A report that does not say what it walked cannot be called clean."""
    readiness = _load("c83_readiness_report_pass", "audit-production-readiness.py")

    stale = tmp_path / "dead_code_report.json"
    stale.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
    check = readiness._report_pass(stale, "dead_code_report", "Dead code report", ["files_walked"])
    assert check["status"] == "fail", check
    assert "files_walked" in str(check["error"]), check

    fresh = tmp_path / "dead_code_report.json"
    fresh.write_text(json.dumps({"status": "pass", "files_walked": 10}), encoding="utf-8")
    check = readiness._report_pass(fresh, "dead_code_report", "Dead code report", ["files_walked"])
    assert check["status"] == "pass", check
    assert check["error"] == ""

    # The function *can* require a field; only this pins that the call site *does*. Without
    # it the guard is a capability nothing uses, and the denominator travels unread.
    source = (_SCRIPTS / "audit-production-readiness.py").read_text(encoding="utf-8")
    call = next((use for use in _report_pass_uses(source) if use[1] == "dead_code_report"), None)
    assert call is not None, "the readiness audit does not read the dead-code report"
    assert "files_walked" in call[2], f"the consumer does not require the population: {call}"


# ------------------------------------------------- the result is captured, not dropped


def _dead_code_run_command_uses(tree: ast.AST) -> tuple[list[int], list[int]]:
    """Return (line numbers of bare-statement calls, line numbers of assigned calls)."""
    bare: list[int] = []
    assigned: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Name) and call.func.id == "run_command" and _names_dead_code(call):
                bare.append(node.lineno)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Name) and call.func.id == "run_command" and _names_dead_code(call):
                assigned.append(node.lineno)
    return bare, assigned


def _strings_in(node: ast.AST) -> list[str]:
    """Every string literal under ``node`` -- the script name lives inside a list, not an arg."""
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _names_dead_code(call: ast.Call) -> bool:
    return any("audit-dead-code" in text for text in _strings_in(call))


def _check_ids(source: str) -> list[str]:
    """The ``"id"`` of every ``{"id": ...}`` check literal (the ``checks.append`` entries)."""
    ids: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "id" and isinstance(value, ast.Constant):
                    ids.append(str(value.value))
    return ids


def _report_pass_uses(source: str) -> list[tuple[str, str, list[str]]]:
    """``(report path, check id, required fields)`` for every ``_report_pass(...)`` call.

    ``_report_pass`` takes its check id **positionally**, so it is not visible to a
    ``{"id": ...}`` scan -- the pin has to follow the call, not one syntax. The required
    fields matter too: a test that calls ``_report_pass`` with the field itself only proves
    the function *can* require it, not that this call site *does*.
    """
    uses: list[tuple[str, str, list[str]]] = []
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_report_pass"):
            continue
        path = " ".join(_strings_in(node.args[0])) if node.args else ""
        check_id = str(node.args[1].value) if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) else ""
        required = _strings_in(node.args[3]) if len(node.args) >= 4 else []
        uses.append((path, check_id, required))
    return uses


def test_the_readiness_audit_captures_the_dead_code_result() -> None:
    """The defect *is* the discarded value, so pin the binding, not a message."""
    source = (_SCRIPTS / "audit-production-readiness.py").read_text(encoding="utf-8")
    bare, assigned = _dead_code_run_command_uses(ast.parse(source))

    assert bare == [], f"the dead-code result is discarded again at line(s) {bare}"
    assert len(assigned) == 1, f"expected exactly one captured dead-code run, got lines {assigned}"


def test_the_readiness_audit_counts_the_dead_code_check() -> None:
    source = (_SCRIPTS / "audit-production-readiness.py").read_text(encoding="utf-8")

    assert "dead_code" in _check_ids(source), "the captured result never becomes a check entry"
    uses = _report_pass_uses(source)
    assert any("dead_code_report.json" in path and check_id == "dead_code_report" for path, check_id, _ in uses), (
        f"the dead-code report is not read by the consumer: {uses}"
    )
