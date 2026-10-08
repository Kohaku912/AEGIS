"""A failing sub-audit check must carry its cause -- and the reason is on *stdout*.

Measured 2026-10-08 (cycle 93) on the live tree. ``main`` spawns six sub-audits with
``run_command`` and recorded the exit-code check's cause as
``"error": <proc>["stderr"] if <proc>["status"] != "pass" else ""``. ``run_command``
captures ``stdout`` and ``stderr`` **separately**, and a failing audit writes its one-line
reason to ``stdout`` and exits nonzero, leaving ``stderr`` empty. Measured for all six:

    production_blocker_mock  rc=1  stdout="status=fail ... error=production_blockers=2"   stderr=""
    capability_coverage      rc=1  stdout="overall_status=fail ... error=failing=1"         stderr=""
    ui_completeness          rc=1  stdout="wrote ...\\ui_completeness.md"                   stderr=""
    v1_completion            rc=1  stdout="overall_status=fail open=5 partial=5 blockers=0" stderr=""
    dead_code                rc=0  (pass)                                                   stderr=""
    secret_inventory         rc=0  (pass)                                                   stderr=""

So the four failing checks reached ``readiness_summary.json`` as ``status: fail, error: ""``
-- the operator sees the check name and nothing else. That is the same defect cycle 92
closed for the E2E checks (``test_a_failing_e2e_check_carries_its_cause.py``).

``_process_cause(result)`` now reads ``stderr`` then ``stdout``: an unexpected traceback
still wins, and the audit's own reason is recorded when ``stderr`` is empty. A passing
result still returns ``""``, so every passing check's record is unchanged.

Correction to the earlier pin's rationale. That pin justified the silence by saying each of
the six has a ``*_report`` sibling "to carry the cause". The sibling does **not** carry the
*cause*: ``_report_pass`` returns ``f"Report status is {status}"``, which repeats the status
the exit-code check already gave. The report JSON holds the reason; neither check surfaced it.

``audit-ui-completeness.py`` is the exception that keeps the caveat honest: it prints only
its output path, so for it the recorded cause is a pointer at the report rather than a
reason -- more than silence, less than a diagnosis.
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

# The six reports the sub-audit exit-code checks point at -- an independent cross-check that
# the ``duration_ms`` tag below selects the intended population and nothing else.
_SUB_AUDIT_REPORTS = {
    "production_blockers.json",
    "capability_coverage.json",
    "dead_code_report.json",
    "secret_inventory.json",
    "ui_completeness.json",
    "v1_completion.json",
}

# ``run_command`` is the only source of a check's ``duration_ms``; tagging it lets the test
# *discover* the six sub-audit checks from ``main``'s own output instead of listing them.
_TAG = 4242


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("c93_readiness_cause", _AUDIT)
    assert spec is not None and spec.loader is not None, "cannot load the readiness audit"
    module = importlib.util.module_from_spec(spec)
    sys.modules["c93_readiness_cause"] = module
    spec.loader.exec_module(module)
    return module


# --- _process_cause: the fallbacks, in order ---------------------------------------------


def test_stderr_wins_when_it_is_populated() -> None:
    """An unexpected traceback lands on stderr -- it must not be replaced by the summary line."""
    module = _load()

    cause = module._process_cause({"status": "fail", "stderr": "Traceback (most recent call last)", "stdout": "noise"})

    assert cause == "Traceback (most recent call last)", cause


def test_stdout_is_used_when_stderr_is_empty() -> None:
    """The measured shape: stderr empty, the audit's own reason on stdout."""
    module = _load()

    cause = module._process_cause({"status": "fail", "stderr": "", "stdout": "error=production_blockers=2"})

    assert cause == "error=production_blockers=2", cause


def test_whitespace_only_stderr_falls_through_to_stdout() -> None:
    """A stream of spaces is not a cause."""
    module = _load()

    cause = module._process_cause({"status": "fail", "stderr": "  \n ", "stdout": "error=failing=1"})

    assert cause == "error=failing=1", cause


def test_the_cause_is_stripped() -> None:
    module = _load()

    cause = module._process_cause({"status": "fail", "stderr": "", "stdout": "  error=failing=1\n"})

    assert cause == "error=failing=1", cause


def test_a_fail_with_no_output_still_says_something() -> None:
    """The last resort -- a non-pass result never returns an empty cause."""
    module = _load()

    cause = module._process_cause({"status": "fail", "stderr": "", "stdout": ""})

    assert cause.strip(), cause


def test_missing_streams_do_not_raise() -> None:
    """A result shape without stdout/stderr keys is still a non-pass with a cause."""
    module = _load()

    cause = module._process_cause({"status": "fail"})

    assert cause.strip(), cause


def test_a_pass_is_silent_even_with_output() -> None:
    """The control: a passing audit's chatter must not be recorded as an error."""
    module = _load()

    cause = module._process_cause({"status": "pass", "stderr": "warning: something", "stdout": "status=pass"})

    assert cause == "", cause


def test_a_missing_status_is_not_a_pass() -> None:
    """Absent status defaults to fail, as the old ``!= "pass"`` test did."""
    module = _load()

    cause = module._process_cause({"stderr": "", "stdout": "error=x"})

    assert cause == "error=x", cause


# --- the wiring: every sub-audit check main builds ---------------------------------------


def _stub(status: str, stdout: str = "", stderr: str = "") -> tuple[Any, list[list[str]]]:
    calls: list[list[str]] = []

    def run(command: list[str], cwd: Path | None = None, timeout: int = 120) -> dict[str, object]:
        calls.append(list(command))
        return {
            "command": list(command),
            "status": status,
            "exit_code": 0 if status == "pass" else 1,
            "duration_ms": _TAG,
            "stdout": stdout,
            "stderr": stderr,
        }

    return run, calls


def _run_main(
    module: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    status: str,
    stdout: str = "",
    stderr: str = "",
) -> tuple[list[dict[str, object]], list[list[str]]]:
    """Drive the real ``main`` with a stubbed ``run_command``; return the tagged checks."""
    run, calls = _stub(status, stdout, stderr)
    monkeypatch.setattr(module, "run_command", run)
    report_dir = tmp_path / "reports"
    monkeypatch.setattr(sys, "argv", ["audit-production-readiness.py", "--report-dir", str(report_dir)])

    module.main()

    payload = json.loads((report_dir / "readiness_summary.json").read_text(encoding="utf-8"))
    tagged = [c for c in payload["checks"] if c.get("duration_ms") == _TAG]
    return tagged, calls


def test_the_tag_selects_exactly_the_six_sub_audits(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Guard the discovery: if the tag stops selecting the six, the tests below are vacuous."""
    module = _load()

    tagged, calls = _run_main(module, monkeypatch, tmp_path, "fail", stdout="error=boom")

    assert len(calls) == 6, [c[1] for c in calls]
    assert len(tagged) == 6, [c["id"] for c in tagged]
    assert {Path(str(c["report_path"])).name for c in tagged} == _SUB_AUDIT_REPORTS, tagged


def test_every_sub_audit_check_carries_a_cause_when_not_passing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The property, over the discovered population -- stderr empty, reason on stdout."""
    module = _load()

    tagged, _ = _run_main(module, monkeypatch, tmp_path, "fail", stdout="overall_status=fail error=boom")

    assert tagged, "the tag selected nothing -- the wiring or the stub changed"
    for check in tagged:
        assert check["status"] == "fail", check
        assert str(check["error"]).strip(), f"{check['id']} fails with no cause: {check}"
        assert str(check["error"]) == "overall_status=fail error=boom", check


def test_a_passing_sub_audit_check_has_no_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The control: with the audits passing, all six records are silent and unchanged."""
    module = _load()

    tagged, _ = _run_main(module, monkeypatch, tmp_path, "pass", stdout="status=pass")

    assert len(tagged) == 6, [c["id"] for c in tagged]
    for check in tagged:
        assert check["status"] == "pass", check
        assert check["error"] == "", check


def test_a_traceback_on_stderr_is_not_lost(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The other half: a crashed audit's traceback reaches the summary, not its empty stdout."""
    module = _load()

    tagged, _ = _run_main(
        module, monkeypatch, tmp_path, "fail", stdout="", stderr="Traceback (most recent call last): ValueError"
    )

    assert len(tagged) == 6, [c["id"] for c in tagged]
    for check in tagged:
        assert "Traceback" in str(check["error"]), check


# --- the premise, measured live ----------------------------------------------------------


def test_the_live_capability_coverage_audit_names_its_reason_on_stdout() -> None:
    """The premise the fallback rests on: a real failing audit leaves stderr empty.

    If this ever changes -- the audit starts writing to stderr -- the fallback is no longer
    the thing being exercised and this test says so rather than passing by accident.
    """
    from audit_common import REPORT_DIR, run_command  # type: ignore[import-not-found]

    script = _SCRIPTS / "audit-capability-coverage.py"
    if not script.exists():
        pytest.skip("the capability-coverage audit is not present in this checkout")

    module = _load()
    result = run_command([sys.executable, str(script), "--report-dir", str(REPORT_DIR), "--json-only"])
    cause = module._process_cause(result)

    if result["status"] == "pass":
        assert cause == "", result
        return
    assert cause.strip(), f"a failing sub-audit carries no cause: {result}"
    assert not str(result["stderr"]).strip(), f"the premise changed -- stderr is no longer empty: {result}"
    assert cause == str(result["stdout"]).strip(), f"the cause must be the audit's own stdout line: {result}"
