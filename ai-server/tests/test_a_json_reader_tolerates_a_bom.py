"""A JSON reader in the audit toolchain must tolerate a BOM.

Measured 2026-10-08 (cycle 95). ``utf-8-sig`` strips a leading BOM if present and is otherwise
identical to ``utf-8`` -- but reading a BOM'd file as ``utf-8`` raises ``JSONDecodeError``, and
every one of these readers hides that behind a broad ``except Exception`` that returns a
*default* (``{}``, or a blocker). The defaults are not neutral:

    readiness._load_blockers(BOM'd clean report)  ->  [{"classification": "production_blocker",
                                                        "reason": "Could not read ..."}]
    v1._report_status(BOM'd report that says pass) ->  ("fail", "Missing or unreadable ...")
    audit_common.read_overrides(BOM'd overrides)   ->  {}          (every override dropped)
    ui.read_json(BOM'd artifact)                   ->  {}

A fabricated production blocker, a pass turned into a fail, and silently ignored override
classifications. And a BOM is not exotic here: **48 of 68** JSON reports under ``data/reports``
carry one, so the tree routinely produces them.

The declared population is every ``json.loads(<file>.read_text(...))`` site in the audit
toolchain -- ``scripts/audit*.py`` plus ``scripts/audit_common.py``. Six of the seven read
``utf-8``; the readiness audit's own ``_load_json`` already read ``utf-8-sig``. All seven do now.

The census is discovered by ``ast``, so a *new* JSON reader that reads ``utf-8`` reddens it --
and a guard asserts the discovery is not empty, so the check cannot pass vacuously.
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


@pytest.fixture(autouse=True)
def _scripts_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(_SCRIPTS))


def _load(rel: str, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / rel)
    assert spec is not None and spec.loader is not None, f"cannot load {rel}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, data: object, *, bom: bool) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8-sig" if bom else "utf-8")
    if bom:
        assert path.read_bytes().startswith(b"\xef\xbb\xbf"), "the fixture did not write a BOM"
    return path


# --- the readers --------------------------------------------------------------------------


def test_the_readiness_reader_reads_a_bomd_report(tmp_path: Path) -> None:
    """The control: this one already read ``utf-8-sig`` before the fix."""
    module = _load("audit-production-readiness.py", "c95_readiness_control")
    report = _write(tmp_path / "r.json", {"status": "pass", "files_scanned": 3}, bom=True)

    assert module._load_json(report) == {"status": "pass", "files_scanned": 3}


def test_load_blockers_does_not_fabricate_a_blocker_from_a_bom(tmp_path: Path) -> None:
    """The measured defect: a BOM'd *clean* report read as a production blocker."""
    module = _load("audit-production-readiness.py", "c95_readiness_blockers")
    report = _write(tmp_path / "production_blockers.json", {"status": "pass", "files_scanned": 9, "blockers": []}, bom=True)

    assert module._load_blockers(report) == []


def test_load_blockers_still_reads_a_real_blocker_from_a_bomd_report(tmp_path: Path) -> None:
    """The other direction: the report's own blockers must come through, not a read error."""
    module = _load("audit-production-readiness.py", "c95_readiness_blockers2")
    blocker = {"classification": "production_blocker", "reason": "the real reason"}
    report = _write(tmp_path / "production_blockers.json", {"status": "fail", "blockers": [blocker]}, bom=True)

    assert module._load_blockers(report) == [blocker]


def test_the_v1_reader_reads_a_bomd_report(tmp_path: Path) -> None:
    module = _load("audit-v1-completion.py", "c95_v1_reader")
    report = _write(tmp_path / "ui_completeness.json", {"overall_status": "pass"}, bom=True)

    assert module._load_json(report) == {"overall_status": "pass"}


def test_a_bomd_passing_report_is_not_reported_missing(tmp_path: Path) -> None:
    """The measured defect: a pass became ``fail`` with the cause "Missing or unreadable"."""
    module = _load("audit-v1-completion.py", "c95_v1_status")
    report = _write(tmp_path / "ui_completeness.json", {"overall_status": "pass"}, bom=True)

    assert module._report_status(report) == ("pass", "")


def test_a_bomd_failing_report_names_its_real_status(tmp_path: Path) -> None:
    module = _load("audit-v1-completion.py", "c95_v1_status2")
    report = _write(tmp_path / "ui_completeness.json", {"overall_status": "fail"}, bom=True)

    status, error = module._report_status(report)

    assert status == "fail", (status, error)
    assert "Missing or unreadable" not in error, error
    assert "fail" in error, error


def test_the_ui_reader_reads_a_bomd_artifact(tmp_path: Path) -> None:
    module = _load("audit-ui-completeness.py", "c95_ui_reader")
    artifact = _write(tmp_path / "contrast-report.json", {"ok": True}, bom=True)

    assert module.read_json(artifact) == {"ok": True}


def test_read_overrides_reads_a_bomd_overrides_file(tmp_path: Path) -> None:
    """The measured defect: every override silently dropped."""
    module = _load("audit_common.py", "c95_overrides")
    _write(tmp_path / "audit_overrides.json", {"src/a.py": "allow_with_audit"}, bom=True)

    assert module.read_overrides(tmp_path) == {"src/a.py": "allow_with_audit"}


def test_infer_capability_id_reads_a_bomd_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load("audit_common.py", "c95_infer")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    rel = "ai-server/capabilities/pc/files/read.json"
    _write(tmp_path / rel, {"capability_id": "pc.files.read"}, bom=True)

    assert module.infer_capability_id(rel, "") == "pc.files.read"


def test_the_capability_coverage_audit_reads_a_bomd_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The manifest reader lives inside ``main`` -- drive it with a patched ``ROOT``."""
    module = _load("audit-capability-coverage.py", "c95_capability")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    manifest = tmp_path / "ai-server" / "capabilities" / "pc" / "files" / "read.json"
    _write(manifest, {"server_id": "pc", "app_id": "files", "action": "read", "capability_id": "pc.files.read"}, bom=True)
    report_dir = tmp_path / "reports"
    monkeypatch.setattr(sys, "argv", ["audit-capability-coverage.py", "--report-dir", str(report_dir)])

    module.main()

    payload = json.loads((report_dir / "capability_coverage.json").read_text(encoding="utf-8-sig"))
    rows = payload["summary"]
    assert rows["total"] == 1, payload
    # A BOM read as utf-8 would have produced a row whose error names the decode failure.
    for row in payload.get("capabilities", []):
        assert "BOM" not in str(row.get("error") or ""), row


# --- the control: genuinely broken JSON is still a default, not a crash -------------------


def test_malformed_json_still_reads_as_empty(tmp_path: Path) -> None:
    """Widening the encoding must not widen the handler: a broken file is still ``{}``."""
    module = _load("audit-v1-completion.py", "c95_malformed")
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")

    assert module._load_json(broken) == {}


def test_a_bomd_file_that_is_not_json_still_reads_as_empty(tmp_path: Path) -> None:
    module = _load("audit-v1-completion.py", "c95_bom_broken")
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8-sig")

    assert module._load_json(broken) == {}


# --- the census: every JSON reader in the audit toolchain ---------------------------------


def _json_read_sites() -> list[dict[str, object]]:
    """Every ``json.loads(<file>.read_text(...))`` site in the audit toolchain.

    Discovered by ``ast`` from a *glob-defined* population (``scripts/audit*.py`` plus
    ``scripts/audit_common.py``), never a hand-written list: a new reader is covered without
    editing this test.
    """
    sites: list[dict[str, object]] = []
    for path in sorted(_SCRIPTS.glob("audit*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "loads"):
                continue
            if not (isinstance(node.func.value, ast.Name) and node.func.value.id == "json"):
                continue
            reads = [
                sub
                for sub in ast.walk(node)
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr == "read_text"
            ]
            if not reads:
                continue
            encoding: object = None
            for kw in reads[0].keywords:
                if kw.arg == "encoding" and isinstance(kw.value, ast.Constant):
                    encoding = kw.value.value
            sites.append({"file": path.name, "line": node.lineno, "encoding": encoding})
    return sites


def test_the_census_finds_the_population() -> None:
    """Guard the discovery: an empty or short result would make the test below vacuous."""
    sites = _json_read_sites()

    assert len(sites) >= 7, sites
    assert {s["file"] for s in sites} >= {
        "audit-capability-coverage.py",
        "audit-production-readiness.py",
        "audit-ui-completeness.py",
        "audit-v1-completion.py",
        "audit_common.py",
    }, sites


def test_every_json_reader_in_the_audit_toolchain_reads_utf8_sig() -> None:
    sites = _json_read_sites()

    bad = [s for s in sites if s["encoding"] != "utf-8-sig"]
    assert not bad, f"these JSON readers would read a BOM'd file as a default: {bad}"
