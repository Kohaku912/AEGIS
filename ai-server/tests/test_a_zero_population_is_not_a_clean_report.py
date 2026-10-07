"""A zero population must not read as a clean report -- and a zero *metric* must.

Measured 2026-10-07 (cycle 89), before the fix:

* ``_report_pass`` tested emptiness with ``data.get(field) in (None, "", [])``. That tuple
  matches ``None``, ``""`` and ``[]`` -- but **not** ``0``, ``False`` or ``{}``. So
  ``{"status": "pass", "files_scanned": 0}`` read as **clean**, and so did ``capabilities: 0``,
  ``checks: 0`` and ``files_walked: 0`` -- a report that measured *nothing*, passing the very
  check the empty-population family (cycles 80/83/86) exists to catch.
* The obvious tightening -- treat ``0`` as empty for every field -- is **wrong**, and the live
  tree says so: ``data/reports/e2e/latest/android-real.json`` carries
  ``heartbeat_failure_count: 0``, which is the *good* outcome. Folding it into the population
  list would flip a correct ``pass`` to ``fail``.

So the two kinds of field are now separate arguments:

* ``required_fields`` (positional, required) -- the measured **population**. Empty means falsy
  (``0``, ``False``, ``{}``, ``[]``, ``""``, ``None``, absent).
* ``present_fields`` (keyword-only, default empty) -- fields the report must merely **carry**,
  where ``0`` is a legitimate measurement.

The family invariant is discovered from the source, so a new call site is covered without
editing this file.
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
_LIVE_ANDROID = _REPO_ROOT / "data" / "reports" / "e2e" / "latest" / "android-real.json"

_POPULATION_FIELDS = ["files_scanned", "capabilities", "checks", "files_walked"]
_FALSY = [0, False, {}, [], "", None]


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _module() -> Any:
    spec = importlib.util.spec_from_file_location("readiness_audit_zero_probe", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    sys.modules["readiness_audit_zero_probe"] = module
    spec.loader.exec_module(module)
    return module


def _drive(tmp: Path, payload: dict, required: list[str], present: list[str] | None = None) -> dict[str, object]:
    path = tmp / "report.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    kwargs = {"present_fields": present} if present is not None else {}
    return _module()._report_pass(path, "chk", "Check", required, **kwargs)


def _report_pass_calls() -> list[tuple[str, str, list[str], list[str]]]:
    """(relative path, check id, required fields, present fields) for every call site."""
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    calls: list[tuple[str, str, list[str], list[str]]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_report_pass"):
            continue
        args = node.args
        parts = [s.value for s in ast.walk(args[0]) if isinstance(s, ast.Constant) and isinstance(s.value, str)]
        rel = "/".join(parts)
        check_id = args[1].value if isinstance(args[1], ast.Constant) else "?"
        required = (
            [e.value for e in args[3].elts if isinstance(e, ast.Constant)]
            if len(args) >= 4 and isinstance(args[3], ast.List)
            else []
        )
        present: list[str] = []
        for kw in node.keywords:
            if kw.arg == "present_fields" and isinstance(kw.value, ast.List):
                present = [e.value for e in kw.value.elts if isinstance(e, ast.Constant)]
        calls.append((rel, check_id, required, present))
    return calls


def _live_path(rel: str) -> Path:
    return _REPO_ROOT / rel if rel.startswith("data/") else _REPO_ROOT / "data" / "reports" / rel


# --- the zero hole ---------------------------------------------------------------------


@pytest.mark.parametrize("field", _POPULATION_FIELDS)
@pytest.mark.parametrize("value", _FALSY)
def test_a_falsy_population_field_fails(tmp_path: Path, field: str, value: object) -> None:
    result = _drive(tmp_path, {"status": "pass", field: value}, [field])
    assert result["status"] == "fail", (field, value, result)
    assert field in str(result["error"])


@pytest.mark.parametrize("field", _POPULATION_FIELDS)
def test_a_nonzero_population_still_passes(tmp_path: Path, field: str) -> None:
    assert _drive(tmp_path, {"status": "pass", field: 5}, [field])["status"] == "pass"
    assert _drive(tmp_path, {"status": "pass", field: [{"a": 1}]}, [field])["status"] == "pass"


def test_every_call_site_rejects_a_zero_population(tmp_path: Path) -> None:
    """The family invariant: no call site may accept a zero population as clean."""
    calls = _report_pass_calls()
    assert len(calls) == 6, calls
    for rel, check_id, required, _present in calls:
        for field in required:
            result = _drive(tmp_path, {"status": "pass", field: 0}, required)
            assert result["status"] == "fail", f"{rel} ({check_id}) accepted a zero `{field}`"


# --- the metric kind: zero is legitimate ----------------------------------------------


@pytest.mark.parametrize("value", [0, 0.0, False, 3260])
def test_a_zero_metric_is_not_an_empty_population(tmp_path: Path, value: object) -> None:
    result = _drive(tmp_path, {"status": "pass", "checks": [1], "n": value}, ["checks"], ["n"])
    assert result["status"] == "pass", (value, result)


@pytest.mark.parametrize("value", [None, ""])
def test_a_metric_that_is_absent_or_empty_still_fails(tmp_path: Path, value: object) -> None:
    result = _drive(tmp_path, {"status": "pass", "checks": [1], "n": value}, ["checks"], ["n"])
    assert result["status"] == "fail"
    assert "n" in str(result["error"])


def test_the_live_android_report_still_passes() -> None:
    """The live differential: `heartbeat_failure_count: 0` must stay a `pass`."""
    if not _LIVE_ANDROID.exists():
        pytest.skip("live android report not present")
    live = json.loads(_LIVE_ANDROID.read_text(encoding="utf-8-sig"))
    assert live.get("heartbeat_failure_count") == 0, "the live fixture no longer exercises the zero metric"
    result = _module()._report_pass(
        _LIVE_ANDROID,
        "android_reconnect_metrics",
        "Android reconnect metrics",
        ["checks"],
        present_fields=["reconnect_count", "heartbeat_failure_count"],
    )
    assert result["status"] == "pass", result


# --- the two kinds are structurally separate -------------------------------------------


def test_present_fields_is_keyword_only_with_no_default() -> None:
    param = inspect.signature(_module()._report_pass).parameters["present_fields"]
    assert param.kind is inspect.Parameter.KEYWORD_ONLY, "present_fields must not be positional"
    assert param.default == (), "an empty default keeps it an *additional* constraint"


def test_the_android_metrics_are_present_fields_not_population_fields() -> None:
    android = [c for c in _report_pass_calls() if c[1] == "android_reconnect_metrics"]
    assert len(android) == 1, android
    _rel, _cid, required, present = android[0]
    assert set(present) == {"reconnect_count", "heartbeat_failure_count"}, present
    assert "reconnect_count" not in required and "heartbeat_failure_count" not in required, required
    assert required, "the android call site must still name a population"


def test_every_call_site_names_a_population_or_a_present_set() -> None:
    unconstrained = [rel for rel, _cid, required, present in _report_pass_calls() if not required and not present]
    assert unconstrained == [], f"these call sites constrain nothing: {unconstrained}"
