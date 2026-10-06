"""An audit that examined nothing must not report a clean verdict.

Three of the repo-root audits discover their population: capability coverage walks
``ai-server/capabilities/**/*.json``, the secret audit walks the tracked files plus the
static assets, and the mock inventory walks every text file. A discovered population can
legitimately be empty -- the manifest tree was moved or renamed, git is unavailable, the
suffix filter changed -- and an empty one audits nothing.

The defect is that an empty population and a clean one produced the *same* verdict
(measured 2026-10-06, before the fix):

    capability-coverage  128 manifests -> fail     0 manifests -> rc=0 "pass"
    secrets             1267 files     -> pass     0 files     -> rc=0 "pass"
    mocks               3901 files     -> fail     0 files     -> rc=0

That is the shape of a silent bypass: the audit reports success, so nobody looks. Each
audit now reports the denominator it read and refuses to call a zero population clean.

The control matters as much as the guard: a guard that simply fails everything would also
turn the three tests green, so ``test_capability_coverage_still_passes_over_a_read_population``
feeds a real (if minimal) manifest tree and requires the audit to still pass.
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


def _write_manifest(root: Path, relative: str, data: dict[str, Any]) -> None:
    path = root / "ai-server" / "capabilities" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_capability_coverage_refuses_to_pass_over_an_empty_manifest_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = _load("c80_empty_coverage", "audit-capability-coverage.py")
    monkeypatch.setattr(tool, "ROOT", tmp_path / "empty-repo")
    report = tmp_path / "reports"

    rc, out = _drive(tool, ["audit-capability-coverage.py", "--report-dir", str(report)], capsys)

    assert rc != 0, f"a manifest tree with nothing in it must not audit as clean, got:\n{out}"
    assert "no capability manifests found" in out, out
    payload = json.loads((report / "capability_coverage.json").read_text(encoding="utf-8"))
    assert payload["overall_status"] != "pass", payload["overall_status"]
    assert payload["summary"]["total"] == 0
    assert "no capability manifests found" in payload["error"]


def test_capability_coverage_still_passes_over_a_read_population(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The control: the guard must not be 'everything fails'."""
    tool = _load("c80_real_coverage", "audit-capability-coverage.py")
    root = tmp_path / "repo"
    _write_manifest(
        root,
        "builtin/pc-server/demo/ping.json",
        {
            "server_id": "pc-server",
            "app_id": "demo",
            "action": "ping",
            "capability_id": "pc-server.demo.ping",
            "side_effects": [],
        },
    )
    monkeypatch.setattr(tool, "ROOT", root)
    report = tmp_path / "reports"

    rc, out = _drive(tool, ["audit-capability-coverage.py", "--report-dir", str(report)], capsys)

    assert rc == 0, f"a read, clean manifest tree must still pass, got:\n{out}"
    assert "capabilities=1 failing=0" in out, out
    payload = json.loads((report / "capability_coverage.json").read_text(encoding="utf-8"))
    assert payload["overall_status"] == "pass"
    assert payload["error"] == ""


def test_secret_audit_refuses_to_pass_over_zero_scanned_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = _load("c80_empty_secrets", "audit-secrets.py")
    monkeypatch.setattr(tool, "_tracked_files", lambda: [])
    monkeypatch.setattr(tool, "_static_files", lambda: [])
    report = tmp_path / "reports"

    rc, out = _drive(tool, ["audit-secrets.py", "--report-dir", str(report)], capsys)

    assert rc != 0, f"'no secrets found' over zero files is not a clean secret audit, got:\n{out}"
    assert "files_scanned=0" in out, out
    assert "no files were scanned" in out, out
    payload = json.loads((report / "secret_inventory.json").read_text(encoding="utf-8"))
    assert payload["status"] != "pass"
    assert payload["files_scanned"] == 0


def test_mock_audit_refuses_to_pass_over_zero_scanned_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = _load("c80_empty_mocks", "audit-mocks.py")
    import audit_common

    monkeypatch.setattr(audit_common, "iter_text_files", lambda root=None: iter(()))
    report = tmp_path / "reports"

    rc, out = _drive(tool, ["audit-mocks.py", "--report-dir", str(report), "--json-only"], capsys)

    assert rc != 0, f"a mock inventory that walked no files must not exit clean, got:\n{out}"
    assert "files_scanned=0" in out, out
    assert "no files were walked" in out, out
    # Its consumer (`audit-v1-completion.py`) reads the population out of this report, so
    # the denominator has to travel with the blockers rather than only in the exit code.
    blockers_report = json.loads((report / "production_blockers.json").read_text(encoding="utf-8"))
    assert blockers_report["files_scanned"] == 0
    assert blockers_report["status"] != "pass"


def test_the_v1_completion_mock_check_requires_a_population(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The consumer has to read the denominator, or the guard stops at the report.

    ``audit-v1-completion.py`` turns a report with no blockers into a pass. That is also
    what a report says when it read nothing, so the check requires the denominator, with
    an in-test control: the same empty blocker list *with* a population still passes.

    The script reads its inputs from fixed paths under ``ROOT``, so the whole tree is
    redirected into ``tmp_path`` -- nothing in the repository is read or written.
    """
    tool = _load("c80_v1_completion", "audit-v1-completion.py")
    root = tmp_path / "repo"
    reports = root / "data" / "reports"
    reports.mkdir(parents=True)
    monkeypatch.setattr(tool, "ROOT", root)
    monkeypatch.setattr(tool, "CHECKLIST", root / "docs" / "v1-completion-checklist.md")
    monkeypatch.setattr(tool, "MOCK_REPORT", reports / "production_blockers.json")
    monkeypatch.setattr(tool, "UI_REPORT", reports / "ui_completeness.json")
    monkeypatch.setattr(tool, "CAPABILITY_REPORT", reports / "capability_coverage.json")
    monkeypatch.setattr(tool, "E2E_SUMMARY", reports / "e2e" / "latest" / "summary.json")
    out_dir = tmp_path / "out"

    def mock_check_status() -> dict[str, Any]:
        _drive(tool, ["audit-v1-completion.py", "--report-dir", str(out_dir)], capsys)
        payload = json.loads((out_dir / "v1_completion.json").read_text(encoding="utf-8"))
        return next(check for check in payload["checks"] if check["id"] == "production_blocker_mock_zero")

    tool.MOCK_REPORT.write_text(json.dumps({"blockers": [], "files_scanned": 0}), encoding="utf-8")
    check = mock_check_status()
    assert check["status"] == "fail", check
    assert "walked no files" in check["error"], check

    # A report from before the denominator existed cannot be called clean either: it does
    # not say what it read, so the only honest verdict is "regenerate it".
    tool.MOCK_REPORT.write_text(json.dumps({"blockers": []}), encoding="utf-8")
    check = mock_check_status()
    assert check["status"] == "fail", check
    assert "does not report files_scanned" in check["error"], check

    tool.MOCK_REPORT.write_text(json.dumps({"blockers": [], "files_scanned": 200}), encoding="utf-8")
    check = mock_check_status()
    assert check["status"] == "pass", check
    assert check["error"] == ""
