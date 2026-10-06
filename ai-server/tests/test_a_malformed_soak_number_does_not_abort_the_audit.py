"""A malformed number in a readiness report must not abort the whole audit.

Measured 2026-10-07 (cycle 88), before the fix:

* ``scripts/audit-production-readiness.py::_display_soak_check`` did
  ``int(data.get("duration_seconds") or 0)`` on three report fields, and ``_e2e_check`` did
  ``int(match.get("duration_ms") or 0)`` on a fourth.
* A **truthy, non-numeric** value raised -- measured: ``"abc"`` -> ``ValueError``,
  ``[1, 2]`` -> ``TypeError``, ``{"a": 1}`` -> ``TypeError``, ``failure_count="x"`` ->
  ``ValueError``.
* ``main`` evaluates every check *before* it writes ``readiness_summary.json``, so an exception
  here leaves the **previous** report on disk -- the cycle-85 shape, reached through a *value*
  rather than a missing file.

The fix adds ``_as_int``, which reproduces ``int(value or 0)`` exactly for every input that did
**not** raise, and returns ``None`` exactly where it did. The three soak inputs treat ``None``
as a malformed measurement (a clean ``fail`` naming the field); ``duration_ms`` is metadata, so
it collapses to ``0`` and the verdict is unchanged. A differential pin keeps the pre-fix
formula as the oracle, so "no verdict changed for well-formed input" is measured, not asserted.
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

# Truthy and not a number: the old `int(value or 0)` raised on every one of these.
_MALFORMED = [
    ({"duration_seconds": "abc"}, "duration_seconds"),
    ({"duration_seconds": [1, 2]}, "duration_seconds"),
    ({"duration_seconds": {"a": 1}}, "duration_seconds"),
    ({"equivalent_duration_seconds": "x"}, "equivalent_duration_seconds"),
    ({"failure_count": "x"}, "failure_count"),
]

# Every input the old expression accepted -- `_as_int` must equal `int(value or 0)` for each.
_WELL_FORMED = [None, "", [], {}, 0, 0.0, 1234, 1.9, -5, True, "259200"]

# Truthy and not a number -- `_as_int` returns None (the only case that used to raise).
_NONE_CASES = ["abc", [1, 2], {"a": 1}, object()]


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _audit() -> Any:
    spec = importlib.util.spec_from_file_location("readiness_audit_soak_probe", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    sys.modules["readiness_audit_soak_probe"] = module
    spec.loader.exec_module(module)
    return module


def _write_soak(root: Path, payload: dict[str, object]) -> None:
    latest = root / "data" / "reports" / "e2e" / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    (latest / "display_soak_summary.json").write_text(json.dumps(payload), encoding="utf-8")


def _soak(root: Path, payload: dict[str, object]) -> dict[str, object]:
    module = _audit()
    _write_soak(root, payload)
    module.ROOT = root
    return module._display_soak_check()


# --- the malformed field is a clean fail, not an exception -----------------------------


@pytest.mark.parametrize("extra,field", _MALFORMED)
def test_a_malformed_soak_field_fails_and_names_it(tmp_path: Path, extra: dict, field: str) -> None:
    result = _soak(tmp_path, {"status": "pass", **extra})
    assert result["status"] == "fail", result
    assert field in str(result["error"]), result["error"]


def test_a_soak_report_that_would_have_passed_still_fails_when_a_field_is_malformed(tmp_path: Path) -> None:
    """The malformed guard fires even though status and duration are otherwise perfect."""
    result = _soak(
        tmp_path,
        {"status": "pass", "duration_seconds": 72 * 3600, "equivalent_duration_seconds": 0, "failure_count": "x"},
    )
    assert result["status"] == "fail"
    assert "failure_count" in str(result["error"])


# --- the coercion helper reproduces the old expression exactly -------------------------


@pytest.mark.parametrize("value", _WELL_FORMED)
def test_as_int_reproduces_int_value_or_zero(value: object) -> None:
    assert _audit()._as_int(value) == int(value or 0)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", _NONE_CASES)
def test_as_int_returns_none_where_the_old_expression_raised(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        int(value or 0)  # type: ignore[arg-type]  # the pre-fix behaviour
    assert _audit()._as_int(value) is None


# --- differential: no verdict changes for well-formed input ---------------------------


def _pre_fix_passed(data: dict[str, object]) -> bool:
    """The pre-fix formula, kept as the oracle."""
    if not data:
        return False
    duration = int(data.get("duration_seconds") or 0)
    equivalent = int(data.get("equivalent_duration_seconds") or 0)
    failures = int(data.get("failure_count") or 0)
    return (
        str(data.get("status") or "").lower() == "pass"
        and max(duration, equivalent) >= 72 * 60 * 60
        and failures == 0
    )


@pytest.mark.parametrize("value", [None, "", 0, 1234, 1.9, "259200"])
def test_the_soak_verdict_is_unchanged_for_well_formed_input(tmp_path: Path, value: object) -> None:
    payload: dict[str, object] = {"status": "pass", "duration_seconds": value, "failure_count": 0}
    expected = "pass" if _pre_fix_passed(payload) else "fail"
    assert _soak(tmp_path, payload)["status"] == expected


# --- the family is closed: no report number is coerced with a bare int -----------------


def test_no_report_number_is_coerced_with_a_bare_int() -> None:
    """Every ``int(...)`` in the audit that reads a mapping must go through ``_as_int``."""
    tree = ast.parse(_AUDIT.read_text(encoding="utf-8"))
    offenders = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "int"
        and any(isinstance(sub, ast.Attribute) and sub.attr == "get" for sub in ast.walk(node))
    ]
    assert offenders == [], f"report number coerced with a bare int() at line(s) {offenders}"


def test_the_coercion_helper_is_used_at_every_site() -> None:
    """`_as_int` is defined once and used four times (1 metadata + 3 soak inputs)."""
    text = _AUDIT.read_text(encoding="utf-8")
    assert text.count("def _as_int(") == 1
    assert text.count("_as_int(") == 5, "the helper should be defined once and called four times"


# --- the metadata path: malformed duration_ms must not raise, and must not flip a pass --


@pytest.mark.parametrize("value", ["abc", [1, 2], {"a": 1}])
def test_the_e2e_check_survives_a_malformed_duration_ms(tmp_path: Path, value: object) -> None:
    module = _audit()
    latest = tmp_path / "data" / "reports" / "e2e" / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    (latest / "summary.json").write_text(
        json.dumps({"checks": [{"id": "docker_core", "status": "pass", "duration_ms": value}]}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    result = module._e2e_check(tmp_path / "data" / "reports", "docker_core", "Docker core E2E")
    assert result["status"] == "pass"  # the verdict does not depend on metadata
    assert result["duration_ms"] == 0


def test_a_well_formed_duration_ms_is_kept(tmp_path: Path) -> None:
    module = _audit()
    latest = tmp_path / "data" / "reports" / "e2e" / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    (latest / "summary.json").write_text(
        json.dumps({"checks": [{"id": "docker_core", "status": "pass", "duration_ms": 1234}]}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    result = module._e2e_check(tmp_path / "data" / "reports", "docker_core", "Docker core E2E")
    assert result["duration_ms"] == 1234
