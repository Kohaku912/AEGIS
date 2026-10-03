"""The burden metric is judged by the judgment LLM and checked by the user — pinned.

§3.1 hole 3 was the last north-star hole: *"how much lighter did AEGIS make the user's
life"* had **no definition**, and a definition is a product call, not an implementation
choice. The owner supplied one on 2026-10-03 (``DELEGATION.md`` §4 item 8):

    the metric is **judged by the judgment LLM** and the user is **asked to confirm or
    correct it periodically**.

This file fixes that definition so it cannot drift, and fixes the two absences that keep
it from quietly becoming something else:

* it must **not** become a formula over the decision log — ``tests/test_burden_metric_has_no_instrument.py``
  still pins *why* a formula cannot work (2 of the 3 proposed sub-metrics are not
  computable), and the module must not import the audit package at all;
* it must **not** become a second approval surface — the ask is raised by the asker
  (``CoreCapabilities``, the only caller of ``ConfirmationStore.request``), so the module
  must not import ``aegis_ai.confirmation``.

The question fields are cross-checked against ``ConfirmationRequest``'s own dataclass: two
artefacts describing one thing are asserted to agree, rather than trusted to.
"""

from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path
from typing import Any

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "ai-server" / "src"
_METRIC = _SRC / "aegis_ai" / "burden" / "metric.py"
_INIT = _SRC / "aegis_ai" / "burden" / "__init__.py"
_LLM_YAML = _REPO / "ai-server" / "config" / "llm.yaml"

#: The judgment profile, named once. The module's constant must equal it, and
#: ``config/llm.yaml`` must declare it — a profile the config does not know would be
#: resolved by fallback, and the "judgment LLM" would silently be some other model.
_RECORDED_JUDGMENT_PROFILE = "decision"

#: The verdict vocabulary, pinned so a fourth state is a deliberate edit.
_RECORDED_VERDICTS = frozenset({"unasked", "confirmed", "corrected"})

#: Keys the ask carries. Every one must be a real ``ConfirmationRequest`` field, or the
#: asker's ``request(**fields)`` raises at the moment the user should have been asked.
_RECORDED_QUESTION_KEYS = frozenset(
    {"capability_id", "summary", "reason", "preview", "expected_effect", "side_effects"}
)


@lru_cache(maxsize=1)
def _tree() -> ast.Module:
    return ast.parse(_METRIC.read_text(encoding="utf-8"))


def _calls_named(name: str) -> list[ast.Call]:
    """Every call to ``name``, however it is reached (``x.generate`` or a bare ``generate``)."""
    out: list[ast.Call] = []
    for node in ast.walk(_tree()):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        called = (
            func.attr
            if isinstance(func, ast.Attribute)
            else (func.id if isinstance(func, ast.Name) else "")
        )
        if called == name:
            out.append(node)
    return out


def _kwarg(call: ast.Call, name: str) -> ast.expr | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _module_imports(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _imported_constants(module: Path) -> set[str]:
    """Names a module re-exports, read from its ``__init__`` import list."""
    tree = ast.parse(module.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            out.update(alias.name for alias in node.names)
    return out


def _resolved_field_reads() -> set[str]:
    """Response field names the module reads, however it reads them.

    ``getattr(response, "provider_used", "")`` is a real read. A mention inside a string
    literal is not an invocation — but a ``getattr`` *argument* is, so the two are told
    apart rather than lumped together, and the pin does not dictate the shape (a plain
    attribute access counts too).
    """
    fields = ("provider_used", "model_used")
    found: set[str] = set()
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Attribute) and node.attr in fields:
            found.add(node.attr)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value in fields
        ):
            found.add(node.args[1].value)
    return found


# ── the judgement goes to the judgment LLM ────────────────────────────────────


def test_the_metric_is_judged_by_the_judgment_profile() -> None:
    """The judgement is an LLM call carrying the judgment profile — not arithmetic."""
    calls = _calls_named("generate")
    assert calls, (
        f"no `generate(...)` call in {_METRIC.relative_to(_REPO)} — the metric is no longer "
        "judged by an LLM, so the owner's definition (§4 item 8) has been abandoned"
    )

    carrying = [call for call in calls if _kwarg(call, "profile") is not None]
    assert carrying, (
        "the LLM call no longer passes a `profile`, so it resolves to the router's default "
        "rather than the judgment LLM"
    )

    from aegis_ai.burden.metric import JUDGMENT_PROFILE

    assert JUDGMENT_PROFILE == _RECORDED_JUDGMENT_PROFILE, (
        f"the judgment profile is now {JUDGMENT_PROFILE!r}, recorded "
        f"{_RECORDED_JUDGMENT_PROFILE!r}. The burden metric is meant to be judged by the "
        "same profile the autonomous loop decides with."
    )


def test_the_judgment_profile_is_declared_in_the_llm_config() -> None:
    """A profile the config does not declare would be resolved by fallback, silently."""
    text = _LLM_YAML.read_text(encoding="utf-8")
    assert f"\n  {_RECORDED_JUDGMENT_PROFILE}:\n" in text, (
        f"config/llm.yaml no longer declares a `{_RECORDED_JUDGMENT_PROFILE}` profile. The "
        "judgment LLM would then be whichever profile the resolver falls back to."
    )


def test_the_assessment_records_the_resolved_provider_not_just_the_request() -> None:
    """A label names the request; the resolved provider is what actually judged.

    This is the trap the shipped allowlist sets: `decision` names DeepSeek, the allowlist
    permits only `api.typesafe.ai`, so the call is denied and degrades to Mock — and a
    Mock judgement says nothing about the user's life. Recording the *resolved* pair is
    how that stops being invisible.
    """
    fields = {
        node.target.id
        for node in ast.walk(_tree())
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    for required in ("judged_by_provider", "judged_by_model"):
        assert required in fields, (
            f"`BurdenAssessment` no longer declares `{required}`, so an assessment cannot "
            "say which provider actually produced it"
        )

    reads = _resolved_field_reads()
    assert reads == {"provider_used", "model_used"}, (
        "`assess()` no longer reads the provider's resolved `provider_used` / `model_used`; "
        f"observed {sorted(reads)}"
    )


# ── the two absences that keep it from becoming something else ────────────────


def test_the_metric_never_reads_the_audit_log() -> None:
    """The refuted premise, pinned as an absence: it is a judgement, not a derivation."""
    imports = _module_imports(_tree())
    offenders = {name for name in imports if name.startswith("aegis_ai.audit")}
    assert not offenders, (
        f"{_METRIC.relative_to(_REPO)} imports {sorted(offenders)}. The burden metric is a "
        "judgement — deriving it from the decision log is the premise "
        "`test_burden_metric_has_no_instrument.py` measured and refuted for 2 of 3 "
        "sub-metrics."
    )
    identifiers = {node.id for node in ast.walk(_tree()) if isinstance(node, ast.Name)}
    assert "AuditEntry" not in identifiers, (
        "the metric now names `AuditEntry`; it is reading the decision log rather than "
        "judging the period"
    )


def test_the_metric_cannot_raise_a_confirmation_itself() -> None:
    """The ask belongs to the asker. A second asker is a second approval surface."""
    imports = _module_imports(_tree())
    offenders = {name for name in imports if name.startswith("aegis_ai.confirmation")}
    assert not offenders, (
        f"{_METRIC.relative_to(_REPO)} imports {sorted(offenders)}. Raising the ask here "
        "would make this module a second `ConfirmationStore.request` caller — the asker "
        "(`CoreCapabilities`) is the only one, on purpose."
    )
    called = {node.attr for node in ast.walk(_tree()) if isinstance(node, ast.Attribute)}
    assert "request" not in called, (
        "the metric calls `.request(...)`; the ask must be raised by the asker"
    )


# ── the question agrees with the model it is handed to ────────────────────────


def test_the_question_keys_are_real_confirmation_fields() -> None:
    """Two artefacts describing one thing are asserted to agree, not trusted to."""
    from aegis_ai.burden.metric import BurdenAssessment, BurdenMetric
    from aegis_ai.confirmation.models import ConfirmationRequest

    question = BurdenMetric.build_user_question(BurdenAssessment(window_start_ms=0, window_end_ms=1))

    assert set(question) == _RECORDED_QUESTION_KEYS, (
        "the ask's field set changed.\n"
        f"  recorded: {sorted(_RECORDED_QUESTION_KEYS)}\n"
        f"  observed: {sorted(question)}"
    )

    declared = set(ConfirmationRequest.__dataclass_fields__)
    unknown = set(question) - declared
    assert not unknown, (
        f"the ask carries {sorted(unknown)}, which `ConfirmationRequest` does not declare — "
        "the asker's `request(**fields)` would raise exactly when the user should be asked"
    )


# ── the cadence, and the verdict vocabulary ───────────────────────────────────


def test_the_check_is_periodic_and_a_first_run_is_not_due() -> None:
    """A cadence, not a one-shot — and never before a judgement exists to ask about."""
    from aegis_ai.burden.metric import DEFAULT_ASK_INTERVAL_MS, BurdenMetric

    assert DEFAULT_ASK_INTERVAL_MS > 0, "a non-positive interval would ask on every cycle"

    metric = BurdenMetric(llm=None)
    assert metric.ask_interval_ms == DEFAULT_ASK_INTERVAL_MS, (
        "the default interval is no longer the shipped one"
    )

    now = 1_000_000_000_000
    assert not metric.due_for_user_check(last_ask_ms=None, now_ms=now), (
        "a first run reports 'due' — the user would be asked about a judgement that does "
        "not exist yet"
    )
    assert not metric.due_for_user_check(last_ask_ms=now - 1, now_ms=now), (
        "the check is due immediately after the previous one"
    )
    assert metric.due_for_user_check(last_ask_ms=now - DEFAULT_ASK_INTERVAL_MS, now_ms=now), (
        "the check is never due — the user is never asked"
    )


def test_the_verdict_vocabulary_is_the_recorded_one() -> None:
    from aegis_ai.burden import metric as module

    observed = {
        value
        for name, value in vars(module).items()
        if name.startswith("VERDICT_") and isinstance(value, str)
    }
    assert observed == _RECORDED_VERDICTS, (
        f"the verdict vocabulary changed.\n  recorded: {sorted(_RECORDED_VERDICTS)}\n"
        f"  observed: {sorted(observed)}"
    )


# ── behaviour, driven through a fake provider ─────────────────────────────────


class _Response:
    def __init__(self, content: str, *, provider: str, model: str, success: bool = True, error: str = ""):
        self.content = content
        self.provider_used = provider
        self.model_used = model
        self.success = success
        self.error = error


class _FakeLLM:
    """Records how it was called, so the profile is asserted behaviourally too."""

    def __init__(self, response: _Response) -> None:
        self._response = response
        self.calls: list[dict[str, Any]] = []

    def generate(self, **kwargs: Any) -> _Response:
        self.calls.append(kwargs)
        return self._response


def _assess(response: _Response):
    from aegis_ai.burden.metric import BurdenMetric

    llm = _FakeLLM(response)
    metric = BurdenMetric(llm)
    return metric, metric.assess(window_start_ms=0, window_end_ms=1, activity=["booked a table"])


def test_a_real_judgement_is_parsed_and_the_profile_is_passed_through() -> None:
    payload = '{"score": 0.7, "summary": "Saved an errand.", "evidence": ["booked a table"]}'
    metric, assessment = _assess(_Response(payload, provider="typesafe", model="jev-latest"))

    assert metric._llm.calls[0]["profile"] == _RECORDED_JUDGMENT_PROFILE, (
        "the behavioural call did not carry the judgment profile"
    )
    assert assessment.score == pytest.approx(0.7)
    assert assessment.evidence == ["booked a table"]
    assert (assessment.judged_by_provider, assessment.judged_by_model) == ("typesafe", "jev-latest")
    assert assessment.is_trustworthy


def test_a_mock_judgement_is_marked_untrustworthy() -> None:
    """The allowlist trap: a denied call degrades to Mock, and that must be visible."""
    payload = '{"score": 0.9, "summary": "Looks good!", "evidence": []}'
    _, assessment = _assess(_Response(payload, provider="mock", model="mock"))

    assert assessment.score == pytest.approx(0.9), "the parse still happened"
    assert not assessment.is_trustworthy, (
        "a Mock judgement reports as trustworthy — the asker would then ask the user to "
        "confirm a number no model produced"
    )


def test_a_failed_judgement_is_recorded_rather_than_raised() -> None:
    _, assessment = _assess(
        _Response("", provider="typesafe", model="jev-latest", success=False, error="401")
    )
    assert assessment.score is None
    assert assessment.error
    assert not assessment.is_trustworthy


def test_a_non_json_judgement_is_recorded_rather_than_raised() -> None:
    _, assessment = _assess(
        _Response("I think it was fine.", provider="typesafe", model="jev-latest")
    )
    assert assessment.score is None
    assert "JSON" in assessment.error


def test_the_user_verdict_never_overwrites_the_judgement() -> None:
    """The gap between the LLM's number and the user's answer is the signal."""
    from aegis_ai.burden.metric import VERDICT_CORRECTED, BurdenMetric

    payload = '{"score": 0.9, "summary": "Big week.", "evidence": []}'
    _, assessment = _assess(_Response(payload, provider="typesafe", model="jev-latest"))

    BurdenMetric.apply_user_verdict(assessment, verdict=VERDICT_CORRECTED, note="barely helped")

    assert assessment.score == pytest.approx(0.9), "the LLM's score was overwritten"
    assert assessment.user_verdict == VERDICT_CORRECTED
    assert assessment.user_note == "barely helped"


def test_an_unknown_verdict_is_rejected() -> None:
    from aegis_ai.burden.metric import BurdenAssessment, BurdenMetric

    with pytest.raises(ValueError):
        BurdenMetric.apply_user_verdict(
            BurdenAssessment(window_start_ms=0, window_end_ms=1), verdict="maybe"
        )


def test_the_package_re_exports_the_public_surface() -> None:
    """A package that hides its own constants makes the pins above unreachable."""
    exported = _imported_constants(_INIT)
    for name in (
        "BurdenMetric",
        "BurdenAssessment",
        "JUDGMENT_PROFILE",
        "DEFAULT_ASK_INTERVAL_MS",
        "BURDEN_CHECK_CAPABILITY_ID",
    ):
        assert name in exported, f"aegis_ai.burden no longer re-exports `{name}`"
