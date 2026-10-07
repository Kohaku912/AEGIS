"""A failing E2E check must carry its cause -- and the cause may be one level down.

Measured 2026-10-07 (cycle 92) on the live tree. ``_e2e_check`` recorded only the matched
record's top-level ``error``:

    _e2e_check(REPORT_DIR, "manager_e2e", ...) -> {"status": "fail", "error": ""}

but the record it matched (``data/reports/e2e/latest/manager-e2e.json``, readable because
``_load_json`` uses ``utf-8-sig``) carried **ten failing nested ``checks``** naming the
reason -- seven ``リモート サーバーに接続できません。`` and three
``ai-server container is not running``. So the readiness summary recorded a ``fail`` with
no cause: the operator sees the check name and nothing else.

The fix adds ``_result_cause(match, status)``: the top-level message when present, else the
failing nested checks (bounded), else the status itself -- a non-pass result never returns
``""``. Passing results still return ``""``, so every passing check's record is unchanged.

The E2E checks are the ones with no report-reading sibling to carry the cause: the six
sub-audits each have a ``*_report`` check beside them (``ui_completeness`` /
``ui_completeness_report``), so their exit-code check can stay silent without losing
information. ``manager_e2e`` has no such sibling.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
_AUDIT = _SCRIPTS / "audit-production-readiness.py"

# Every id main passes to _e2e_check.
_E2E_IDS = ("docker_core", "docker_persistence", "backup_restore", "manager_e2e", "browser_real", "dev_real")


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("c92_readiness_cause", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    sys.modules["c92_readiness_cause"] = module
    spec.loader.exec_module(module)
    return module


def _report_dir(tmp_path: Path, *entries: dict[str, object]) -> Path:
    """A report dir whose ``e2e/latest/summary.json`` carries the given check entries."""
    report_dir = tmp_path / "reports"
    latest = report_dir / "e2e" / "latest"
    latest.mkdir(parents=True)
    (latest / "summary.json").write_text(json.dumps({"checks": list(entries)}), encoding="utf-8")
    return report_dir


# --- the fallbacks, in order -------------------------------------------------------------


def test_a_non_pass_result_without_a_message_names_its_status(tmp_path: Path) -> None:
    """The last resort: no message and no nested checks still must not say nothing."""
    module = _load()
    report_dir = _report_dir(tmp_path, {"id": "probe_check", "status": "fail"})

    result = module._e2e_check(report_dir, "probe_check", "Probe")

    assert result["status"] == "fail", result
    assert result["error"], f"a fail with no cause is the defect: {result}"
    assert "fail" in str(result["error"]), result


def test_a_non_pass_result_uses_its_nested_checks(tmp_path: Path) -> None:
    module = _load()
    report_dir = _report_dir(
        tmp_path,
        {
            "id": "manager_e2e",
            "status": "fail",
            "error": "",
            "checks": [
                {"id": "runtime_health", "status": "fail", "error": "cannot reach the remote server"},
                {"id": "servers", "status": "fail", "error": "ai-server container is not running"},
                {"id": "tasks", "status": "pass", "error": ""},
            ],
        },
    )

    result = module._e2e_check(report_dir, "manager_e2e", "Stateful Manager E2E")

    assert result["status"] == "fail", result
    cause = str(result["error"])
    assert "runtime_health: cannot reach the remote server" in cause, cause
    assert "servers: ai-server container is not running" in cause, cause
    # The passing nested check contributes nothing.
    assert "tasks" not in cause, cause


def test_the_top_level_message_wins(tmp_path: Path) -> None:
    """The nested checks are a fallback -- an explicit message is never overridden."""
    module = _load()
    report_dir = _report_dir(
        tmp_path,
        {
            "id": "manager_e2e",
            "status": "fail",
            "error": "the explicit reason",
            "checks": [{"id": "runtime_health", "status": "fail", "error": "the nested reason"}],
        },
    )

    result = module._e2e_check(report_dir, "manager_e2e", "Stateful Manager E2E")

    assert str(result["error"]) == "the explicit reason", result


def test_nested_passes_only_falls_back_to_the_status(tmp_path: Path) -> None:
    module = _load()
    report_dir = _report_dir(
        tmp_path,
        {
            "id": "manager_e2e",
            "status": "fail",
            "error": "",
            "checks": [{"id": "runtime_health", "status": "pass", "error": ""}],
        },
    )

    result = module._e2e_check(report_dir, "manager_e2e", "Stateful Manager E2E")

    assert result["status"] == "fail", result
    assert result["error"], result
    assert "fail" in str(result["error"]), result


def test_the_cause_is_bounded(tmp_path: Path) -> None:
    """A pathological report cannot flood the summary: five reasons, then a count."""
    module = _load()
    nested = [{"id": f"c{i}", "status": "fail", "error": f"reason {i}"} for i in range(8)]
    report_dir = _report_dir(tmp_path, {"id": "manager_e2e", "status": "fail", "error": "", "checks": nested})

    result = module._e2e_check(report_dir, "manager_e2e", "Stateful Manager E2E")

    cause = str(result["error"])
    assert "c0: reason 0" in cause and "c4: reason 4" in cause, cause
    assert "c5: reason 5" not in cause, cause
    assert "(+3 more)" in cause, cause


# --- the control: passing checks are untouched -------------------------------------------


def test_a_pass_result_has_no_error(tmp_path: Path) -> None:
    module = _load()
    report_dir = _report_dir(tmp_path, {"id": "docker_core", "status": "pass"})

    result = module._e2e_check(report_dir, "docker_core", "Docker core E2E")

    assert result["status"] == "pass", result
    assert result["error"] == "", result


def test_a_pass_result_ignores_stray_nested_failures(tmp_path: Path) -> None:
    """The status decides: a pass is a pass even if a nested check disagrees."""
    module = _load()
    report_dir = _report_dir(
        tmp_path,
        {"id": "docker_core", "status": "pass", "checks": [{"id": "x", "status": "fail", "error": "noise"}]},
    )

    result = module._e2e_check(report_dir, "docker_core", "Docker core E2E")

    assert result["status"] == "pass", result
    assert result["error"] == "", result


# --- the property, over the declared population ------------------------------------------


@pytest.mark.parametrize("check_id", _E2E_IDS)
def test_every_e2e_check_carries_a_cause_when_not_passing(check_id: str, tmp_path: Path) -> None:
    """Enumerate the ids main passes to _e2e_check -- never sample them."""
    module = _load()
    report_dir = _report_dir(tmp_path, {"id": check_id, "status": "fail"})

    result = module._e2e_check(report_dir, check_id, check_id)

    assert result["status"] == "fail", result
    assert str(result["error"]).strip(), f"{check_id} fails with no cause: {result}"


def test_the_live_manager_e2e_check_carries_its_cause() -> None:
    """The measured symptom: the live manager_e2e fail now names its reason."""
    from audit_common import REPORT_DIR  # type: ignore[import-not-found]

    standalone = REPORT_DIR / "e2e" / "latest" / "manager-e2e.json"
    if not standalone.exists():
        pytest.skip("the live manager-e2e report is not present in this checkout")

    module = _load()
    result = module._e2e_check(REPORT_DIR, "manager_e2e", "Stateful Manager E2E")

    if result["status"] == "pass":
        assert result["error"] == "", result
        return
    cause = str(result["error"])
    assert cause.strip(), f"the live manager_e2e fail carries no cause: {result}"
    # The live record's reason is one level down; the cause must reach it.
    assert ":" in cause, cause
