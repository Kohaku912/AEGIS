"""A blocker report that was never read must not read as "no blockers".

Cycle 81. `load_production_blocker_report` already had a loud branch for a report it
could not *parse*; the branch for a report it could not *find* returned the same shape
as a clean inventory (`{"blockers": []}`), so a caller could not tell "nothing is
blocked" from "the control never ran". The dashboard route, the readiness audit and the
runtime all read that value, and all of them turn "no blockers" into a pass.

Two sibling readers of the same file had the same asymmetry: `audit-production-readiness`
read it only `if blocker_path.exists()`, and `run-readiness-report.ps1` only
`if (Test-Path ...)` -- while each of them already synthesised a blocker for the
*unreadable* case in its own `except`/`catch`.

Every negative case below is paired with the control that must stay clean: a report that
*was* read, and holds no blockers, still counts zero.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

from aegis_ai.production_readiness import (
    blocker_capability_ids,
    load_production_blocker_report,
    production_blocker_count,
)

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"


def _load_script(module_name: str, filename: str) -> ModuleType:
    """Load a repo-root script by path.

    `scripts/*.py` are not a package (and one of them has a hyphen in its name), so
    `import` cannot reach them. Register the module in `sys.modules` **before**
    `exec_module`: the scripts use `from __future__ import annotations`, and dataclasses
    resolve those string annotations through `sys.modules`.
    """
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


@pytest.fixture(scope="module")
def readiness_audit() -> ModuleType:
    return _load_script("aegis_readiness_audit_under_test", "audit-production-readiness.py")


# -- the shared runtime loader -------------------------------------------------


def test_a_missing_report_is_not_a_clean_report(tmp_path: Path) -> None:
    missing = tmp_path / "production_blockers.json"

    report = load_production_blocker_report(missing)

    assert report["unreadable"] is True
    assert report["cause"] == "was not found"
    assert production_blocker_count(report) == 1
    assert str(missing) in report["blockers"][0]["reason"]
    # The diagnosis must reach the blocker an operator actually reads, not just sit in
    # a sibling key: "run the audit" and "the audit wrote garbage" are different actions.
    assert report["cause"] in report["blockers"][0]["reason"]


def test_a_report_that_is_not_a_json_object_is_not_a_clean_report(tmp_path: Path) -> None:
    """Valid JSON of the wrong shape used to fall through to the clean default."""
    path = tmp_path / "production_blockers.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")

    report = load_production_blocker_report(path)

    assert report["unreadable"] is True
    assert report["cause"] == "is not a JSON object"
    assert production_blocker_count(report) == 1


def test_an_unparseable_report_is_not_a_clean_report(tmp_path: Path) -> None:
    path = tmp_path / "production_blockers.json"
    path.write_text("{not json", encoding="utf-8")

    report = load_production_blocker_report(path)

    assert report["unreadable"] is True
    assert report["cause"] == "could not be read"
    assert production_blocker_count(report) == 1


def test_the_three_unreadable_causes_are_named_apart(tmp_path: Path) -> None:
    """A missing file and a malformed one are different failures.

    They must not share a wording: an operator reading `reason` has to be able to tell
    "run the audit" from "the audit wrote garbage".
    """
    missing = load_production_blocker_report(tmp_path / "nope.json")
    malformed_path = tmp_path / "malformed.json"
    malformed_path.write_text("{not json", encoding="utf-8")
    malformed = load_production_blocker_report(malformed_path)

    causes = {missing["cause"], malformed["cause"]}
    assert len(causes) == 2
    assert missing["blockers"][0]["reason"] != malformed["blockers"][0]["reason"]


def test_a_report_that_was_read_is_passed_through_unchanged(tmp_path: Path) -> None:
    """Control: the guard must not turn every report into a blocker."""
    path = tmp_path / "production_blockers.json"
    payload = {"status": "pass", "files_scanned": 3902, "blockers": []}
    path.write_text(json.dumps(payload), encoding="utf-8")

    report = load_production_blocker_report(path)

    assert report == payload
    assert "unreadable" not in report
    assert production_blocker_count(report) == 0


def test_a_read_report_that_names_a_blocker_still_counts_it(tmp_path: Path) -> None:
    path = tmp_path / "production_blockers.json"
    path.write_text(
        json.dumps(
            {
                "blockers": [
                    {"classification": "production_blocker", "capability_id": "pc-server.input.mouse_click"}
                ]
            }
        ),
        encoding="utf-8",
    )

    report = load_production_blocker_report(path)

    assert production_blocker_count(report) == 1
    assert blocker_capability_ids(report) == {"pc-server.input.mouse_click"}


def test_an_unreadable_report_names_no_capability(tmp_path: Path) -> None:
    """The limitation, pinned rather than left latent.

    The synthetic blocker has no `capability_id`, because inventing one would name a
    capability that is not blocked. So a capability-level consumer still sees an empty
    set -- the machine signal for this failure is the blocker *count* and its `reason`.
    """
    report = load_production_blocker_report(tmp_path / "production_blockers.json")

    assert production_blocker_count(report) == 1
    assert blocker_capability_ids(report) == set()


# -- the readiness audit's own reader -----------------------------------------


def test_the_readiness_audit_refuses_a_missing_blocker_report(
    readiness_audit: ModuleType, tmp_path: Path
) -> None:
    blockers = readiness_audit._load_blockers(tmp_path / "production_blockers.json")

    assert len(blockers) == 1
    assert blockers[0]["classification"] == "production_blocker"
    assert "was not found" in blockers[0]["reason"]


def test_the_readiness_audit_refuses_a_report_without_a_blockers_key(
    readiness_audit: ModuleType, tmp_path: Path
) -> None:
    """A renamed key used to read as zero blockers via `.get("blockers", [])`."""
    path = tmp_path / "production_blockers.json"
    path.write_text(json.dumps({"status": "pass", "files_scanned": 3902}), encoding="utf-8")

    blockers = readiness_audit._load_blockers(path)

    assert len(blockers) == 1
    assert "no blockers list" in blockers[0]["reason"]


def test_the_readiness_audit_refuses_a_report_that_is_not_an_object(
    readiness_audit: ModuleType, tmp_path: Path
) -> None:
    path = tmp_path / "production_blockers.json"
    path.write_text("[]", encoding="utf-8")

    blockers = readiness_audit._load_blockers(path)

    assert len(blockers) == 1
    assert "not a JSON object" in blockers[0]["reason"]


def test_the_readiness_audit_passes_a_read_blocker_list_through(
    readiness_audit: ModuleType, tmp_path: Path
) -> None:
    """Control: a real list -- empty or not -- is used as-is, not replaced."""
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"blockers": []}), encoding="utf-8")
    assert readiness_audit._load_blockers(empty) == []

    one = tmp_path / "one.json"
    one.write_text(
        json.dumps({"blockers": [{"classification": "production_blocker", "reason": "x"}]}), encoding="utf-8"
    )
    assert len(readiness_audit._load_blockers(one)) == 1


# -- the route an operator actually reads -------------------------------------


def test_the_dashboard_readiness_route_does_not_report_an_unread_report_as_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End to end: the consumer inherits the verdict.

    The loader's default path is *relative* (`data/reports/production_blockers.json`), and
    the dashboard fixture chdirs into `tmp_path`, so on a host that has never run the mock
    audit the route's report is genuinely absent. That is the production-relevant case: the
    dashboard used to answer "0 production blockers" for it.

    The view function is called through a request context rather than through
    `test_client()`. A real request runs the app's `before_request` auth middleware, which
    answers 401 without a passkey session; the middleware is not what this pin is about, and
    the route body is the closure registered here.
    """
    from test_documented_routes_are_registered import _app

    app = _app(tmp_path, monkeypatch)
    view = app.view_functions["api_production_readiness"]

    with app.test_request_context("/api/production/readiness"):
        payload = view().get_json()

    assert payload["runtime_mode"] == "production"
    assert payload["blockers"], "a report that was never read must not read as clean"
    assert payload["unreadable"] is True
    assert "was not found" in payload["blockers"][0]["reason"]
