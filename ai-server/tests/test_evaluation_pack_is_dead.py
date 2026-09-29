"""The `aegis_ai/evaluation/` pack is dead, and the claims it still carries are false.

Measured 2026-09-29. Nothing outside `aegis_ai/evaluation/` imports `metrics`, `report`, `runner`,
`safety_tests`, `scenario` or `prompt_regression` — only `behavioral` is live. The dead members are
not merely unused, they *assert things that are no longer true*:

* ``ExpectedOutcome.APPROVAL_REQUIRED`` has no producer. The goal-change commit (``495105e``, Phase 2)
  deleted the only runner branch that could set it, and no ``InvokeStatus`` member is named
  ``APPROVAL_REQUIRED``. Two scenario steps still expect it, so they can never pass.
  ``DEFERRED`` and ``UNCERTAIN`` are likewise unreachable and expected by nobody.
* ``PromptRegressionRunner`` can never report a violation: it compares against ``"ALLOW"`` while every
  capability it builds is ``RiskLevel.APPROVAL_REQUIRED``, which ``DEFAULT_RISK_MAP`` maps to
  ``ALLOW_WITH_AUDIT``. All 15 cases pass while 10 of them declare ``DENY``.
* Every capability id those cases build is invented — all 19 are absent from the live catalog.

None of this is deleted here. The goal-change commit lists these among the *"stale approval-era
surfaces [that] still await an owner decision"*, so the delete-vs-wire call is the owner's. What this
module does is make the debt **visible and non-drifting**: each test discovers the surface from the
code and asserts the discovered set equals the recorded one, so the record cannot rot silently.

See ``docs/prompt-regression.md`` for the prose half of the same pin.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

_AI_SERVER = Path(__file__).resolve().parents[1]
_REPO = _AI_SERVER.parent
_SRC = _AI_SERVER / "src"
_TESTS = _AI_SERVER / "tests"
_PACKAGE = _SRC / "aegis_ai" / "evaluation"
_DOC = _REPO / "docs" / "prompt-regression.md"
_README = _REPO / "README.md"
_CASES_YAML = _REPO / "evaluation" / "prompt_regression" / "expected_behaviors.yaml"

# This file is the instrument, not a consumer: it imports the dead modules in order to measure them.
# Counting those imports as references would let the measurement erase what it measures, so the
# scan skips exactly this one file — and `test_the_live_modules_are_exactly_the_recorded_ones`
# fails if anything else starts referencing the package.
_SELF = Path(__file__).resolve()

# Modules in the package that something outside the package actually references.
_LIVE_MODULES = frozenset({"behavioral"})

# Modules in the package that nothing outside the package references. **Recorded debt, not an
# approval** — the delete-vs-wire call belongs to the owner.
_DEAD_MODULES = frozenset(
    {"metrics", "prompt_regression", "report", "runner", "safety_tests", "scenario"}
)

# `ExpectedOutcome` members that no branch of `EvaluationRunner` can produce.
_UNREACHABLE_OUTCOMES = frozenset({"APPROVAL_REQUIRED", "DEFERRED", "UNCERTAIN"})

# Steps that expect one of those, and therefore can never pass.
_STEPS_EXPECTING_AN_UNREACHABLE_OUTCOME = frozenset(
    {"safety_002/s2_invoke", "safety_level2_gate/invoke_level2"}
)

_SERVER_PREFIXES = (
    "pc-server.",
    "android-server.",
    "browser-server.",
    "room-server.",
    "ai-server.",
)


# ── Discovery helpers ───────────────────────────────────────────────────────

_IMPORT_RE = re.compile(r"aegis_ai\.evaluation\.([A-Za-z_][A-Za-z0-9_]*)")


def _modules_present() -> set[str]:
    """Every module in the package, discovered from the filesystem."""
    return {path.stem for path in _PACKAGE.glob("*.py")} - {"__init__"}


def _modules_referenced_outside_the_package() -> set[str]:
    """Every package module named by a file outside the package — excluding this instrument."""
    found: set[str] = set()
    for root in (_SRC, _TESTS):
        for path in root.rglob("*.py"):
            if _PACKAGE in path.parents or path.resolve() == _SELF:
                continue
            found.update(_IMPORT_RE.findall(path.read_text(encoding="utf-8")))
    return found


class _InvokeResult:
    """The shape `_handle_invoke_tool` reads: `.success` and `.status.name`."""

    def __init__(self, success: bool, status: Any) -> None:
        self.success = success
        self.status = status


class _Broker:
    """A broker that always answers the same way."""

    def __init__(self, result: _InvokeResult) -> None:
        self._result = result

    def invoke_tool(self, capability_id: str, params: dict[str, Any]) -> _InvokeResult:
        return self._result


def _outcomes_the_runner_can_produce() -> set[str]:
    """Drive the runner over every reachable branch and collect `actual_outcome`.

    This is a *producer* count, not a reading of the enum: the runner is the only thing that writes
    `actual_outcome`, so the set it can write is the set of outcomes a scenario can expect and still
    pass.
    """
    from aegis_ai.evaluation.runner import EvaluationRunner
    from aegis_ai.evaluation.safety_tests import SAFETY_BENCHMARK
    from aegis_ai.evaluation.scenario import ALL_SCENARIOS, ScenarioStep
    from tool_broker import InvokeStatus

    produced: set[str] = set()
    idle = EvaluationRunner()

    # 1. every action the shipped scenarios dispatch, plus one no scenario names
    actions = {step.action for scenario in ALL_SCENARIOS + SAFETY_BENCHMARK for step in scenario.steps}
    actions.add("__no_such_action__")
    for action in sorted(actions):
        produced.add(idle._run_step(ScenarioStep(step_id="probe", action=action)).actual_outcome)

    # 2. every broker status the invoke_tool branch can echo back
    for status in InvokeStatus:
        for success in (True, False):
            runner = EvaluationRunner(tool_broker=_Broker(_InvokeResult(success, status)))
            produced.add(
                runner._run_step(
                    ScenarioStep(
                        step_id="probe",
                        action="invoke_tool",
                        params={"capability_id": "pc-server.screenshot.get_screenshot"},
                    )
                ).actual_outcome
            )

    # 3. the same branch with no broker at all
    produced.add(idle._run_step(ScenarioStep(step_id="probe", action="invoke_tool")).actual_outcome)
    return produced


def _capability_ids_the_regression_cases_build() -> set[str]:
    """Reproduce the id construction in `PromptRegressionRunner.run_case`."""
    from aegis_ai.evaluation.prompt_regression import ALL_REGRESSION_CASES

    built: set[str] = set()
    for case in ALL_REGRESSION_CASES:
        for action in case.forbidden_actions:
            built.add(action if action.startswith(_SERVER_PREFIXES) else f"pc-server.{action}")
    return built


# ── The package is dead ─────────────────────────────────────────────────────

def test_the_dead_modules_are_exactly_the_ones_nothing_outside_the_package_references() -> None:
    present = _modules_present()
    referenced = _modules_referenced_outside_the_package()

    assert len(present) >= 7, f"package discovery found only {sorted(present)}"
    assert referenced == _LIVE_MODULES, (
        "the set of package modules referenced from outside changed: "
        f"{sorted(referenced)} — update docs/prompt-regression.md if the pack was wired up"
    )
    assert present - referenced == _DEAD_MODULES


# ── `ExpectedOutcome` has members no branch can produce ─────────────────────

def test_the_expected_outcomes_the_runner_cannot_produce_are_the_recorded_ones() -> None:
    from aegis_ai.evaluation.scenario import ExpectedOutcome

    declared = {member.name for member in ExpectedOutcome}
    produced = _outcomes_the_runner_can_produce()

    assert declared & produced == {"SUCCESS", "DENIED"}, (
        "the runner now produces an expected outcome it did not before: "
        f"{sorted(declared & produced)}"
    )
    assert declared - produced == _UNREACHABLE_OUTCOMES


def test_the_steps_expecting_an_unreachable_outcome_are_the_recorded_ones() -> None:
    from aegis_ai.evaluation.safety_tests import SAFETY_BENCHMARK
    from aegis_ai.evaluation.scenario import ALL_SCENARIOS, ExpectedOutcome

    unreachable = {member.name for member in ExpectedOutcome} - _outcomes_the_runner_can_produce()
    scenarios = ALL_SCENARIOS + SAFETY_BENCHMARK
    observed = {
        f"{scenario.scenario_id}/{step.step_id}"
        for scenario in scenarios
        for step in scenario.steps
        if step.expected_outcome.name in unreachable
    }

    assert len(scenarios) >= 12, f"scenario discovery found only {len(scenarios)}"
    assert observed == _STEPS_EXPECTING_AN_UNREACHABLE_OUTCOME


# ── The regression pack cannot fail ─────────────────────────────────────────

def test_no_regression_case_names_a_capability_that_exists(tmp_path) -> None:
    from aegis_ai.capability_catalog import CapabilityCatalog

    catalog = CapabilityCatalog("capabilities", "apps", data_dir=str(tmp_path))
    real = {entry["id"] for entry in catalog.list_for_llm()}
    built = _capability_ids_the_regression_cases_build()

    assert len(real) >= 120, f"catalog discovery found only {len(real)} ids"
    assert len(built) >= 19, f"case discovery found only {len(built)} ids"
    assert built & real == set(), (
        "a case now names a real capability — the record in docs/prompt-regression.md needs updating"
    )


def test_the_regression_runner_passes_the_cases_it_was_written_to_catch(tmp_path) -> None:
    from aegis_ai.evaluation.prompt_regression import ALL_REGRESSION_CASES, PromptRegressionRunner
    from policy_engine import PolicyEngine

    engine = PolicyEngine(data_dir=str(tmp_path))
    results = PromptRegressionRunner(policy_engine=engine).run_all()

    deny_cases = [case for case in ALL_REGRESSION_CASES if case.expected_policy_decision == "DENY"]
    assert len(deny_cases) >= 10, (
        f"the recorded vacuity assumes at least 10 DENY cases, found {len(deny_cases)}"
    )
    assert all(result.passed for result in results), (
        "the runner reported a violation — its comparison may have been fixed; "
        "docs/prompt-regression.md says the check cannot fire"
    )


def test_the_two_copies_of_the_case_list_disagree() -> None:
    from aegis_ai.evaluation.prompt_regression import ALL_REGRESSION_CASES

    assert _CASES_YAML.is_file(), f"{_CASES_YAML} is gone, but docs/prompt-regression.md points at it"
    yaml_cases = yaml.safe_load(_CASES_YAML.read_text(encoding="utf-8"))["cases"]

    python_ids = {case.case_id for case in ALL_REGRESSION_CASES}
    yaml_ids = {case["id"] for case in yaml_cases}

    assert len(python_ids) >= 15 and len(yaml_ids) >= 17
    assert python_ids - yaml_ids, "the YAML now covers every Python case"
    assert yaml_ids - python_ids, "the Python list now covers every YAML case"

    python_actions = {case.case_id: set(case.forbidden_actions) for case in ALL_REGRESSION_CASES}
    yaml_actions = {case["id"]: set(case["forbidden_actions"]) for case in yaml_cases}
    disagreeing = sorted(
        case_id
        for case_id in python_ids & yaml_ids
        if python_actions[case_id] != yaml_actions[case_id]
    )
    assert disagreeing, (
        "docs/prompt-regression.md says the copies disagree on a shared case id; none does"
    )


# ── The prose half of the pin ───────────────────────────────────────────────

def test_the_doc_stops_claiming_the_pack_is_implemented() -> None:
    text = _DOC.read_text(encoding="utf-8")

    assert "**Status**: Implemented" not in text
    assert "not wired" in text, "the doc must state that nothing runs the pack"


def test_the_doc_stops_offering_a_test_command_that_does_not_exist() -> None:
    text = _DOC.read_text(encoding="utf-8")

    assert "pytest tests/test_prompt_regression.py" not in text
    assert not (_TESTS / "test_prompt_regression.py").exists(), (
        "the test file now exists — the doc must stop calling the pack unwired"
    )
    assert "A failing test means a safety regression was introduced" not in text


def test_the_doc_only_points_at_paths_that_exist() -> None:
    text = _DOC.read_text(encoding="utf-8")
    targets = re.findall(r"\]\(([^)#]+)\)", text)
    local = [t for t in targets if not t.startswith(("http://", "https://", "mailto:"))]

    assert len(local) >= 4, f"doc link discovery found only {local}"
    missing = sorted(t for t in local if not (_DOC.parent / t).resolve().exists())
    assert missing == [], f"docs/prompt-regression.md links to files that do not exist: {missing}"


def test_the_readme_does_not_advertise_the_pack_as_working_tests() -> None:
    rows = [line for line in _README.read_text(encoding="utf-8").splitlines() if "docs/prompt-regression.md" in line]

    assert len(rows) == 1, f"expected one README row for the pack, found {len(rows)}"
    assert "Injection defense tests" not in rows[0]
    assert "not wired" in rows[0]
