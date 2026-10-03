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
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "ai-server" / "src"
_METRIC = _SRC / "aegis_ai" / "burden" / "metric.py"
_INIT = _SRC / "aegis_ai" / "burden" / "__init__.py"
_LLM_YAML = _REPO / "ai-server" / "config" / "llm.yaml"
_SETTINGS_JSON = _REPO / "ai-server" / "config" / "settings.json"
#: The capability the ask travels as. Its ``input_schema`` is a second artefact describing
#: the same question, so the two are asserted to agree rather than trusted to.
_ASK_MANIFEST = (
    _REPO / "ai-server" / "capabilities" / "builtin" / "ai-server" / "confirmation" / "request.json"
)

#: The judgment profile, named once. The module's constant must equal it, and
#: ``config/llm.yaml`` must declare it — a profile the config does not know would be
#: resolved by fallback, and the "judgment LLM" would silently be some other model.
#:
#: ``jev_decision``, not ``decision``: the first cut used ``decision``, which resolves to
#: ``api.deepseek.com`` — a host the shipped allowlist denies, so the judgement degraded to
#: Mock and a correctly-wired caller could never ask. See
#: :func:`test_the_judgment_profile_resolves_to_a_permitted_destination`, which is the
#: half that catches it. *Declared* and *resolves* are two different claims.
_RECORDED_JUDGMENT_PROFILE = "jev_decision"

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
    """A profile the config does not declare would be resolved by fallback, silently.

    This is only *half* the claim, and on its own it passed while the feature was inert:
    see :func:`test_the_judgment_profile_resolves_to_a_permitted_destination` for the other
    half. A profile can be declared, resolve, and still be denied by the gate.
    """
    text = _LLM_YAML.read_text(encoding="utf-8")
    assert f"\n  {_RECORDED_JUDGMENT_PROFILE}:\n" in text, (
        f"config/llm.yaml no longer declares a `{_RECORDED_JUDGMENT_PROFILE}` profile. The "
        "judgment LLM would then be whichever profile the resolver falls back to."
    )


def test_the_judgment_profile_resolves_to_a_permitted_destination(tmp_path: Path) -> None:
    """*Declared* is not *resolves*. Drive the real resolver and the real gate.

    The defect this closes, measured: the profile was ``decision``, ``llm.yaml`` declared
    it, and the test above passed — while ``decision`` resolved to ``api.deepseek.com``,
    which the shipped allowlist denies. The judgement then degraded to Mock,
    ``is_trustworthy`` was False, and a correctly-wired asker would **never ask**. Two
    halves each green while composing into "the metric can never ask".

    The negative control matters as much as the assertion: ``decision`` is still denied, so
    this is measuring the allowlist rather than a gate that happens to allow everything.
    """
    from aegis_ai.burden.metric import JUDGMENT_PROFILE
    from aegis_ai.egress import EgressDecision, EgressGate, EgressRequest
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver
    from aegis_ai.settings.store import SettingsStore

    store = SettingsStore(
        path=str(_SETTINGS_JSON),
        audit_path=str(tmp_path / "settings_audit.jsonl"),
    )
    resolver = LLMSettingsResolver(str(_LLM_YAML))
    # Constructed directly rather than through `configure_egress_gate`: the real class and
    # the real settings, without mutating a process global that other tests share.
    gate = EgressGate(settings_store=store)

    def _decide(profile: str) -> tuple[Any, Any]:
        settings = resolver.resolve(profile_id=profile)
        decision = gate.check(
            EgressRequest(
                destination=settings.base_url,
                purpose="llm.chat",
                component="llm.factory",
            )
        )
        return settings, decision

    settings, decision = _decide(JUDGMENT_PROFILE)
    assert decision is EgressDecision.ALLOW, (
        f"the judgment profile `{JUDGMENT_PROFILE}` resolves to {settings.base_url!r}, which "
        f"the shipped egress allowlist {sorted(gate.allowed_hosts)} denies. The judgement "
        "would degrade to Mock, `is_trustworthy` would be False, and the user would never "
        "be asked — the check would be wired and inert."
    )
    assert settings.provider == "typesafe", (
        f"`{JUDGMENT_PROFILE}` no longer resolves to the TypeSafe provider "
        f"(observed {settings.provider!r})"
    )

    # Negative control: the allowlist really is a filter, not a rubber stamp.
    denied_settings, denied = _decide("decision")
    assert denied is EgressDecision.DENY, (
        f"the control profile `decision` ({denied_settings.base_url!r}) is now permitted, so "
        "the assertion above proves nothing about the allowlist"
    )


def test_the_ask_satisfies_the_capabilitys_own_input_schema() -> None:
    """The ask travels as the capability's arguments, so it must pass the capability's schema.

    Measured defect: ``side_effects`` was a list here and the manifest declares a string, so
    ``jsonschema.validate`` rejected it and the broker denied the ask with
    ``VALIDATION_DENY`` — the question never reached the user. A key-name check against
    ``ConfirmationRequest`` cannot see that (the dataclass types the field ``Any``), which
    is why the question is now validated against the manifest itself.
    """
    from jsonschema import ValidationError, validate

    from aegis_ai.burden.metric import BurdenAssessment, BurdenMetric

    manifest = json.loads(_ASK_MANIFEST.read_text(encoding="utf-8"))
    schema = manifest["input_schema"]
    question = BurdenMetric.build_user_question(
        BurdenAssessment(window_start_ms=0, window_end_ms=1, summary="Saved an errand.")
    )

    validate(instance=question, schema=schema)

    # Negative control: the shape this replaced must still be rejected, or the schema is
    # not actually constraining the field the defect was in.
    with pytest.raises(ValidationError):
        validate(instance={**question, "side_effects": []}, schema=schema)


def test_the_ask_is_recorded_by_the_real_capability(tmp_path: Path) -> None:
    """Driven through the real client and a real store: the question becomes askable.

    The schema test above proves the *shape* is accepted; this proves the handler that
    receives it records it. Both are needed — a schema the handler then drops would pass the
    first and fail the user.
    """
    from aegis_ai.burden.metric import (
        BURDEN_CHECK_CAPABILITY_ID,
        BurdenAssessment,
        BurdenMetric,
    )
    from aegis_ai.confirmation import ConfirmationStore
    from aegis_ai.core_capabilities import AegisCoreCapabilityClient

    store = ConfirmationStore(str(tmp_path / "confirmations"))
    client = AegisCoreCapabilityClient(
        data_dir=str(tmp_path / "core"),
        server_executor=None,
        personal_managers={"confirmation_store": store},
    )

    question = BurdenMetric.build_user_question(
        BurdenAssessment(window_start_ms=0, window_end_ms=1, summary="Saved an errand.")
    )
    result = client.invoke_capability("ai-server.confirmation.request", dict(question))

    assert result.get("ok") is True, f"the real capability refused the ask: {result}"
    recorded = store.all(limit=5)
    assert len(recorded) == 1, (
        "the ask was accepted by the capability but nothing reached the store, so the user "
        "would never see the question"
    )
    assert recorded[0].capability_id == BURDEN_CHECK_CAPABILITY_ID, (
        "the ask is not filed under the burden-check id, so the dashboard cannot group it "
        "apart from action confirmations"
    )
    assert recorded[0].status == "pending"


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
