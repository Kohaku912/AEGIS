"""Every readiness report-pass must name the population the report measured.

Cycle 80 closed the empty-population family in the **generators** ("an empty scan is not a
clean inventory"): `audit-mocks.py`, `audit-capability-coverage.py` and friends refuse to
report `pass` over zero rows. But the readiness audit is the **consumer** that turns those
reports into the verdict, and its `_report_pass` accepted a report whose status was `pass`
while the report measured nothing at all.

Measured 2026-10-07, before the fix -- a `{"status": "pass", "overall_status": "pass"}`
report with **no** population field, at each of the six call sites:

  mock_inventory.json       mock_inventory_report       required_fields=None  -> pass (vacuous)
  capability_coverage.json  capability_coverage_report  required_fields=None  -> pass (vacuous)
  ui_completeness.json      ui_completeness_report      required_fields=None  -> pass (vacuous)
  v1_completion.json        v1_completion_report        required_fields=None  -> pass (vacuous)
  dead_code_report.json     dead_code_report            ["files_walked"]      -> fail
  .../android-real.json     android_reconnect_metrics   ["reconnect_count", "heartbeat_failure_count"] -> fail

Cycle 83 gave exactly one of these (`dead_code_report`) a denominator; the other four were
left behind. The argument is now **required** -- not defaulted to `None` -- so a new call
site cannot omit it, and the population is discovered from the source rather than listed.
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
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


def _load_readiness_audit() -> Any:
    """Load the repo-root audit by path (its name has hyphens, so no `import`)."""
    spec = importlib.util.spec_from_file_location("readiness_report_pass_probe", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    sys.modules["readiness_report_pass_probe"] = module
    spec.loader.exec_module(module)
    return module


def _report_pass_calls() -> list[tuple[str, str, list[str] | None]]:
    """Every `_report_pass(...)` call site: (relative path, check id, required fields).

    Discovered from the source, so a new call site is covered without editing this file.
    """
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    calls: list[tuple[str, str, list[str] | None]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_report_pass"):
            continue
        args = node.args
        parts = [s.value for s in ast.walk(args[0]) if isinstance(s, ast.Constant) and isinstance(s.value, str)]
        rel = "/".join(parts)
        check_id = args[1].value if isinstance(args[1], ast.Constant) else "?"
        required = None
        if len(args) >= 4 and isinstance(args[3], ast.List):
            required = [e.value for e in args[3].elts if isinstance(e, ast.Constant)]
        calls.append((rel, check_id, required))
    return calls


def _live_path(rel: str) -> Path:
    return _REPO_ROOT / rel if rel.startswith("data/") else _REPO_ROOT / "data" / "reports" / rel


def test_the_report_pass_family_is_enumerated() -> None:
    """Discovery must not be vacuous: all six call sites are found."""
    calls = _report_pass_calls()
    assert len(calls) == 6, calls
    assert all(rel and cid for rel, cid, _ in calls), calls


def test_every_report_pass_call_site_names_a_population() -> None:
    """The family invariant: no call site may accept a report that measured nothing."""
    missing = [rel for rel, _cid, required in _report_pass_calls() if not required]
    assert missing == [], f"these call sites accept a report that measured nothing: {missing}"


def test_the_population_argument_has_no_default() -> None:
    """Make the hole unrepresentable: a default of `None` re-opens it at any new call site."""
    module = _load_readiness_audit()
    param = inspect.signature(module._report_pass).parameters["required_fields"]
    assert param.default is inspect.Parameter.empty, "a default for `required_fields` re-opens the hole"


def test_a_report_that_measured_nothing_fails_every_check(tmp_path: Path) -> None:
    """Behavioural pin: `pass` with no population is not clean, at *every* call site."""
    module = _load_readiness_audit()
    for rel, check_id, required in _report_pass_calls():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"status": "pass", "overall_status": "pass"}), encoding="utf-8")
        result = module._report_pass(path, check_id, "X", required or [])
        assert result["status"] == "fail", f"{rel} ({check_id}) read a report that measured nothing as clean"


def test_a_report_with_its_population_still_passes(tmp_path: Path) -> None:
    """Control: a `pass` report that *did* measure something still passes."""
    module = _load_readiness_audit()
    for rel, check_id, required in _report_pass_calls():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {"status": "pass"}
        for field in required or []:
            payload[field] = "measured"  # `_report_pass` only requires non-empty
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = module._report_pass(path, check_id, "X", required or [])
        assert result["status"] == "pass", (rel, result["error"])


def test_a_failing_report_still_fails(tmp_path: Path) -> None:
    """Control on the status branch: a measured report that says `fail` is not clean."""
    module = _load_readiness_audit()
    for rel, check_id, required in _report_pass_calls():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {"status": "fail"}
        for field in required or []:
            payload[field] = "measured"
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = module._report_pass(path, check_id, "X", required or [])
        assert result["status"] == "fail", (rel, result["status"])


def test_the_population_requirement_does_not_change_the_live_verdict() -> None:
    """The fix must not change the live verdict: the shipped reports all name their population.

    The live `mock_inventory.json` is `fail` (two production blockers) -- that is the point:
    the invariant is not "every report passes", it is "requiring the population changes
    nothing", because every shipped report carries it.
    """
    module = _load_readiness_audit()
    checked = 0
    for rel, check_id, required in _report_pass_calls():
        path = _live_path(rel)
        if not path.exists():
            continue
        checked += 1
        with_population = module._report_pass(path, check_id, "X", required or [])
        status_only = module._report_pass(path, check_id, "X", [])
        assert with_population["status"] == status_only["status"], (
            rel,
            with_population["error"],
            status_only["error"],
        )
    if checked == 0:
        pytest.skip("no data/reports in this checkout (gitignored)")
