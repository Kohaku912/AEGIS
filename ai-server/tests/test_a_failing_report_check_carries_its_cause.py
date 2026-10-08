"""A failing report check must carry its cause -- and the cause may be one level down.

Measured 2026-10-08 (cycle 94) on the live tree. ``_report_pass`` recorded only
``f"Report status is {status}"`` when a report's status was not ``pass`` -- which repeats the
status the reader already had and names no cause. Of the four reports that fail, two carry a
top-level reason and two carry it one level down:

    mock_inventory.json      status=fail  error="production_blockers=2"        -> top level
    capability_coverage.json overall_status=fail  error="failing=1"            -> top level
    v1_completion.json       overall_status=fail  checks[0].error="open=5 ..." -> one level down
    ui_completeness.json     overall_status=fail  checks[0].missing=[...17...] -> one level down

``_report_cause(data, status)`` now reads the report's own ``error`` / ``reason``, else its
failing nested ``checks`` (naming each in ``error`` or ``missing``, bounded to five), else the
status alone. A ``pass`` never reaches it, so every passing report's record is unchanged.

Measured before/after on the live reports: **4 of the 6 call sites change, all in ``error``
only**; the two passing sites (``dead_code_report``, ``android_reconnect_metrics``) are
byte-identical and **no status changes**.

The nested shape is the defect cycles 92 and 93 closed for the E2E record and for a process
result -- here it is the report. It is deliberately a *separate* helper rather than a reuse of
``_result_cause``: the two read different record schemas (an E2E runner result names ``error``
on each nested check; a sub-audit report also uses ``missing``) and each names its own noun in
the fallback sentence.
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


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("c94_report_cause", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    sys.modules["c94_report_cause"] = module
    spec.loader.exec_module(module)
    return module


# --- _report_cause: the fallbacks, in order ----------------------------------------------


def test_a_top_level_error_wins() -> None:
    module = _load()

    cause = module._report_cause({"status": "fail", "error": "production_blockers=2"}, "fail")

    assert cause == "Report status is fail: production_blockers=2", cause


def test_a_top_level_reason_is_used_when_there_is_no_error() -> None:
    module = _load()

    cause = module._report_cause({"status": "fail", "reason": "the report's own reason"}, "fail")

    assert "the report's own reason" in cause, cause


def test_the_nested_checks_are_used_when_there_is_no_message() -> None:
    """The measured v1_completion shape: the reason sits on the nested check."""
    module = _load()
    data = {
        "overall_status": "fail",
        "checks": [
            {"id": "v1_checklist_closed", "status": "fail", "error": "open=5 partial=5 blocker=0"},
            {"id": "fine", "status": "pass", "error": ""},
        ],
    }

    cause = module._report_cause(data, "fail")

    assert "v1_checklist_closed: open=5 partial=5 blocker=0" in cause, cause
    assert "fine" not in cause, cause


def test_a_nested_missing_list_is_summarised_not_dumped() -> None:
    """The measured ui_completeness shape: 17 missing files must not flood the summary."""
    module = _load()
    data = {
        "overall_status": "fail",
        "checks": [{"id": "web-dashboard", "status": "fail", "missing": [f"file{i}.tsx" for i in range(17)]}],
    }

    cause = module._report_cause(data, "fail")

    assert "web-dashboard: [file0.tsx, file1.tsx, file2.tsx, (+14 more)]" in cause, cause
    assert "file9.tsx" not in cause, cause


def test_the_reason_list_is_bounded() -> None:
    module = _load()
    data = {"status": "fail", "checks": [{"id": f"c{i}", "status": "fail", "error": f"r{i}"} for i in range(8)]}

    cause = module._report_cause(data, "fail")

    assert "c0: r0" in cause and "c4: r4" in cause, cause
    assert "c5: r5" not in cause, cause
    assert "(+3 more)" in cause, cause


def test_a_fail_with_no_detail_still_names_the_status() -> None:
    """The last resort -- a non-pass report never returns an empty cause."""
    module = _load()

    cause = module._report_cause({"status": "fail"}, "fail")

    assert cause == "Report status is fail", cause


def test_an_empty_error_falls_through_to_the_checks() -> None:
    """A blank ``error`` is not a cause."""
    module = _load()
    data = {"status": "fail", "error": "   ", "checks": [{"id": "x", "status": "fail", "error": "real"}]}

    cause = module._report_cause(data, "fail")

    assert "x: real" in cause, cause


def test_a_nested_check_without_an_error_names_its_status() -> None:
    module = _load()
    data = {"status": "fail", "checks": [{"id": "y", "status": "fail"}]}

    cause = module._report_cause(data, "fail")

    assert "y: fail" in cause, cause


# --- _summarise ---------------------------------------------------------------------------


def test_summarise_leaves_a_short_list_intact() -> None:
    module = _load()

    assert module._summarise(["a", "b"]) == "[a, b]"


def test_summarise_collapses_a_long_list() -> None:
    module = _load()

    assert module._summarise(["a", "b", "c", "d", "e"]) == "[a, b, c, (+2 more)]"


def test_summarise_renders_a_scalar() -> None:
    module = _load()

    assert module._summarise(7) == "7"


# --- the control: a passing report is silent ----------------------------------------------


def test_a_passing_report_has_no_error(tmp_path: Path) -> None:
    module = _load()
    report = tmp_path / "r.json"
    report.write_text(json.dumps({"status": "pass", "files_scanned": 3}), encoding="utf-8")

    result = module._report_pass(report, "probe", "Probe", ["files_scanned"])

    assert result["status"] == "pass", result
    assert result["error"] == "", result


# --- the population: every call site main builds ------------------------------------------


def _path_literals(node: ast.AST) -> list[str]:
    """The string leaves of a ``report_dir / "a" / "b.json"`` chain, in order."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.BinOp):
        return _path_literals(node.left) + _path_literals(node.right)
    return []


def _literal_list(node: ast.AST) -> list[str]:
    if isinstance(node, ast.List):
        return [e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
    return []


def _report_pass_sites() -> list[dict[str, object]]:
    """Every ``_report_pass(...)`` call site in the audit, discovered from its source.

    Never a hand-written list: a new call site is covered without editing this test.
    """
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    sites: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Name) and func.id == "_report_pass"):
            continue
        rel = "/".join(_path_literals(node.args[0]))
        assert rel, f"could not read the report path of a _report_pass call: {ast.dump(node)[:200]}"
        present: list[str] = []
        for kw in node.keywords:
            if kw.arg == "present_fields":
                present = _literal_list(kw.value)
        sites.append(
            {
                "rel": rel,
                "check_id": node.args[1].value,  # type: ignore[attr-defined]
                "name": node.args[2].value,  # type: ignore[attr-defined]
                "required": _literal_list(node.args[3]),
                "present": present,
            }
        )
    return sites


def test_the_discovery_finds_the_call_sites() -> None:
    """Guard the discovery: an empty or single-site result would make the test below vacuous."""
    sites = _report_pass_sites()

    assert len(sites) == 6, [s["check_id"] for s in sites]
    assert {s["rel"] for s in sites} == {
        "mock_inventory.json",
        "capability_coverage.json",
        "ui_completeness.json",
        "v1_completion.json",
        "dead_code_report.json",
        "e2e/latest/android-real.json",
    }, sites


@pytest.mark.parametrize("index", range(6))
def test_every_report_pass_site_carries_the_reports_reason(index: int, tmp_path: Path) -> None:
    """Drive each real call site with a report that names its reason on the top level."""
    module = _load()
    sites = _report_pass_sites()
    site = sites[index]
    report = tmp_path / str(site["rel"])
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"overall_status": "fail", "error": "the reason"}), encoding="utf-8")

    result = module._report_pass(
        report,
        str(site["check_id"]),
        str(site["name"]),
        list(site["required"]),  # type: ignore[arg-type]
        present_fields=list(site["present"]),  # type: ignore[arg-type]
    )

    assert result["status"] == "fail", result
    assert "the reason" in str(result["error"]), f"{site['check_id']} fails without its cause: {result}"


# --- the live reports ---------------------------------------------------------------------


def test_the_live_failing_reports_carry_a_cause() -> None:
    """The measured symptom: each live failing report now names its own reason."""
    from audit_common import REPORT_DIR  # type: ignore[import-not-found]

    module = _load()
    sites = _report_pass_sites()
    checked = 0
    for site in sites:
        path = REPORT_DIR / str(site["rel"])
        if not path.exists():
            continue
        result = module._report_pass(
            path,
            str(site["check_id"]),
            str(site["name"]),
            list(site["required"]),  # type: ignore[arg-type]
            present_fields=list(site["present"]),  # type: ignore[arg-type]
        )
        if result["status"] == "pass":
            assert result["error"] == "", result
            continue
        checked += 1
        cause = str(result["error"])
        assert cause.strip(), f"{site['check_id']} fails with no cause: {result}"
        # The live reports that fail all carry a reason somewhere, so the bare status is not enough.
        assert cause != "Report status is fail", f"{site['check_id']} records the bare status: {result}"
    assert checked, "no live failing report was checked -- the reports may have moved"
