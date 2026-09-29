"""The interruption decision is an expected utility, not a ladder.

``InterruptionController.decide`` used to be a chain of ``if`` statements: sleeping
batches, gaming batches, ``important_only`` batches, and everything else sent. The
chain was not wrong so much as *unaccountable* — there was no way to see why one
notification was deferred and another delivered, and no way to change the balance
without adding another branch.

It now computes ``net = benefit × P(receptive) − cost`` and speaks when ``net > 0``
(proposal P1-14, after Horvitz). This module guards the two things that make that a
real model rather than a ladder wearing a utility costume:

1. **The reported numbers determine the decision.** Every model decision carries its
   own terms, and ``test_the_decision_is_the_sign_of_the_reported_utility`` recomputes
   the sign from them. If someone reintroduces a special case that returns without
   consulting the arithmetic, that test fails.
2. **The parameters cover the vocabulary they claim to.** Receptivity keys are
   discovered from ``SituationModel``'s source rather than hand-listed, so a new
   interruptibility value cannot fall through to a default that reads as permission.

Hard gates — emergency stop, exception categories, critical severity, quiet hours, the
user's proactive preference — are asserted to short-circuit *without* the model being
consulted. Those are declared rules, not trade-offs, and a test that only checked the
decision string would not notice if the model started overriding them.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aegis_ai.personal_ai.interruption import (
    _DEFAULT_OCCUPANCY,
    _OCCUPANCY,
    _RECEPTIVITY,
    _SEVERITY_VALUE,
    InterruptionController,
)

_SITUATION_SRC = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "personal_ai" / "situation.py"


class _Situation:
    """Minimal stand-in for ``SituationModel`` — the controller only calls get_state()."""

    def __init__(self, **state):
        self._state = state

    def get_state(self):
        return dict(self._state)


class _UserModel:
    def __init__(self, quiet=False, allows=True):
        self._quiet = quiet
        self._allows = allows

    def is_quiet_now(self, hour):
        return self._quiet

    def allows_proactive(self, category):
        return self._allows


class _UserModelStore:
    def __init__(self, model):
        self._model = model

    def get(self):
        return self._model


def _controller(tmp_path, situation=None, model=None):
    return InterruptionController(
        data_dir=str(tmp_path),
        situation_model=situation,
        user_model_store=_UserModelStore(model) if model is not None else None,
    )


#: Situations chosen to exercise every receptivity value plus the occupancy extremes.
_SITUATIONS = {
    "interruptible": _Situation(interruptibility="interruptible", state="working", activity={"label": "working"}),
    "important_only": _Situation(interruptibility="important_only", state="focused", activity={"label": "focused"}),
    "batch_later": _Situation(interruptibility="batch_later", state="away", activity={"label": "away"}),
    "suppress": _Situation(interruptibility="suppress", state="sleeping", activity={"label": "sleeping"}),
    "unknown": _Situation(),
    "occupied": _Situation(
        interruptibility="interruptible",
        state="chatting",
        activity={"label": "chatting"},
        attention={"label": "screen_active"},
    ),
}

_SEVERITIES = ("info", "warning")


# ── The load-bearing property ─────────────────────────────────────────────────


@pytest.mark.parametrize("situation_name", sorted(_SITUATIONS))
@pytest.mark.parametrize("severity", _SEVERITIES)
def test_the_decision_is_the_sign_of_the_reported_utility(tmp_path, situation_name, severity):
    """Recompute the decision from the numbers the decision itself reports.

    This is the assertion that distinguishes a model from a ladder. Any branch that
    returns a verdict the arithmetic does not support fails here.
    """
    controller = _controller(tmp_path, situation=_SITUATIONS[situation_name])
    decision = controller.decide({"notification_id": "n", "category": "general", "severity": severity})

    assert "utility" in decision, f"{situation_name}/{severity} did not report a utility breakdown"
    utility = decision["utility"]

    recomputed = utility["benefit"] * utility["p_receptive"] - utility["cost"]
    assert recomputed == pytest.approx(utility["net"], abs=1e-12), (
        "the reported net is not the product/difference of the reported terms"
    )
    assert (decision["decision"] == "send_now") == (utility["net"] > 0), (
        f"{situation_name}/{severity}: decision {decision['decision']!r} does not match "
        f"the sign of net={utility['net']!r}"
    )


def test_higher_severity_is_never_less_likely_to_interrupt(tmp_path):
    """Monotonicity: benefit only ever rises with severity, so the verdict cannot fall."""
    for situation_name in sorted(_SITUATIONS):
        controller = _controller(tmp_path, situation=_SITUATIONS[situation_name])
        nets = [
            controller.decide({"notification_id": "n", "category": "general", "severity": s})["utility"]["net"]
            for s in _SEVERITIES
        ]
        assert nets == sorted(nets), f"{situation_name}: net utility fell as severity rose ({nets})"


def test_utility_breakdown_is_complete_for_model_decisions(tmp_path):
    """A partial breakdown is worse than none — the reader cannot recompute it."""
    controller = _controller(tmp_path, situation=_SITUATIONS["interruptible"])
    utility = controller.decide({"severity": "info"})["utility"]
    for key in ("benefit", "p_receptive", "cost", "net", "interruptibility", "activity", "attention", "occupancy"):
        assert key in utility, f"the breakdown is missing {key!r}"


def test_decide_is_deterministic(tmp_path):
    """No hidden clock or global: the same input must give the same verdict."""
    notification = {"notification_id": "n", "category": "general", "severity": "info"}
    first = _controller(tmp_path, situation=_SITUATIONS["unknown"]).decide(notification)
    second = _controller(tmp_path, situation=_SITUATIONS["unknown"]).decide(notification)
    assert first == second


# ── Hard gates are not trade-offs ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "case,expected",
    [
        ("emergency_stop", "emergency_stop"),
        ("exception_category", "send_now"),
        ("critical_severity", "send_now"),
        ("quiet_hours", "batch_later"),
        ("proactive_disallowed", "suppress"),
    ],
)
def test_hard_gates_short_circuit_without_consulting_the_model(tmp_path, case, expected):
    """Each declared rule must decide *before* the utility model runs.

    The ``utility`` key is absent exactly when the model was never consulted, so
    asserting its absence is how this test distinguishes "the gate won" from "the gate
    agreed with the arithmetic this time".
    """
    situation = _SITUATIONS["interruptible"]
    model = None
    controller = _controller(tmp_path, situation=situation)

    if case == "emergency_stop":
        controller.set_emergency_stop(True)
        notification = {"severity": "info"}
    elif case == "exception_category":
        notification = {"category": "safety_warning", "severity": "info"}
    elif case == "critical_severity":
        notification = {"category": "general", "severity": "critical"}
    elif case == "quiet_hours":
        model = _UserModel(quiet=True)
        controller = _controller(tmp_path, situation=situation, model=model)
        notification = {"category": "general", "severity": "info"}
    else:
        model = _UserModel(allows=False)
        controller = _controller(tmp_path, situation=situation, model=model)
        notification = {"category": "general", "severity": "info"}

    decision = controller.decide(notification)
    assert decision["decision"] == expected
    assert "utility" not in decision, (
        f"{case} was decided by the utility model — a declared rule must short-circuit it"
    )


def test_the_bypass_makes_the_top_severities_unreachable(tmp_path):
    """Record the coupling that makes two ``_SEVERITY_VALUE`` entries unreachable.

    ``error`` and ``critical`` never reach the model because the hard bypass returns
    first. The entries are kept so the table stays complete if that bypass moves — this
    test is what stops them from being silently dead weight.
    """
    controller = _controller(tmp_path, situation=_SITUATIONS["suppress"])
    for severity in ("error", "critical"):
        decision = controller.decide({"category": "general", "severity": severity})
        assert decision["decision"] == "send_now"
        assert "utility" not in decision, f"{severity} reached the model; the bypass moved"
        assert severity in _SEVERITY_VALUE, "keep the table complete even though this entry is unreachable"


# ── Parameters cover the vocabulary they claim to ─────────────────────────────


def _vocabulary(variable: str) -> set[str]:
    """Every string literal ``situation.py`` assigns to ``variable``.

    Discovered from the source rather than hand-listed: a hand-maintained list is the
    defect this is meant to catch. Covers dict values (``{"interruptibility": "x"}``),
    plain assignments, and tuple assignments (``a, x, c = "p", "v", 0.8``).
    """
    tree = ast.parse(_SITUATION_SRC.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == variable and isinstance(value, ast.Constant) and isinstance(value.value, str):
                    found.add(value.value)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    found.add(node.value.value)
                if isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple):
                    names = [e.id for e in target.elts if isinstance(e, ast.Name)]
                    if variable in names:
                        index = names.index(variable)
                        elements = node.value.elts
                        if index < len(elements) and isinstance(elements[index], ast.Constant) and isinstance(elements[index].value, str):
                            found.add(elements[index].value)
    return found


def test_receptivity_covers_every_interruptibility_the_situation_model_emits():
    """A missing key would fall through to a default, which is a silent wrong answer."""
    emitted = _vocabulary("interruptibility")
    assert emitted, "discovery found no interruptibility values — the scan has drifted"
    assert set(_RECEPTIVITY) == emitted, (
        "SituationModel's interruptibility vocabulary and _RECEPTIVITY have drifted.\n"
        f"  emitted but unmapped: {sorted(emitted - set(_RECEPTIVITY))}\n"
        f"  mapped but unreachable: {sorted(set(_RECEPTIVITY) - emitted)}"
    )


def test_every_situation_state_label_is_mapped_or_explicitly_defaulted():
    """Every label the situation model can name is either weighted or routed to the default.

    ``unknown`` is allowed to be absent: it resolves through ``_DEFAULT_OCCUPANCY``, and
    that routing is deliberate. Anything *else* missing would be a label silently
    getting the neutral value because nobody wrote it down.
    """
    labels = _vocabulary("state")
    assert labels, "discovery found no state labels — the scan has drifted"
    unmapped = labels - set(_OCCUPANCY) - {"unknown"}
    assert not unmapped, f"state labels with no occupancy weight: {sorted(unmapped)}"
    assert 0.0 < _DEFAULT_OCCUPANCY < 1.0


def test_occupancy_is_bounded_and_ordered(tmp_path):
    """Weights are probabilities of being busy: in range, and sleeping ≥ working."""
    assert all(0.0 <= v <= 1.0 for v in _OCCUPANCY.values())
    assert all(0.0 <= v <= 1.0 for v in _RECEPTIVITY.values())
    assert _OCCUPANCY["sleeping"] > _OCCUPANCY["working"]
    assert _RECEPTIVITY["interruptible"] > _RECEPTIVITY["suppress"]


# ── Behaviour that must not move ──────────────────────────────────────────────


def test_an_unknown_situation_keeps_delivering_info(tmp_path):
    """The documented calibration point.

    With no situation model the controller knows nothing, and the honest reading of
    ``unknown`` is a coin flip — which nets positive for an ``info`` notification. That
    keeps a deployment without observations behaving as it did before the model existed.
    A parameter change that flips this should fail here and force the trade-off to be
    made explicitly rather than by drift.
    """
    decision = _controller(tmp_path).decide({"notification_id": "n", "category": "general", "severity": "info"})
    assert decision["decision"] == "send_now"
    assert decision["utility"]["net"] > 0
    assert decision["utility"]["interruptibility"] == "unknown"


def test_a_focused_user_defers_a_low_severity_notification(tmp_path):
    """The case the old ladder encoded, now arrived at arithmetically."""
    decision = _controller(tmp_path, situation=_SITUATIONS["important_only"]).decide(
        {"notification_id": "n", "category": "general", "severity": "info"}
    )
    assert decision["decision"] == "batch_later"
    assert decision["utility"]["net"] <= 0


def test_a_sleeping_user_defers_even_a_warning(tmp_path):
    """``suppress`` receptivity is the floor, and occupancy is at its maximum."""
    decision = _controller(tmp_path, situation=_SITUATIONS["suppress"]).decide(
        {"notification_id": "n", "category": "general", "severity": "warning"}
    )
    assert decision["decision"] == "batch_later"


def test_active_attention_lowers_receptivity(tmp_path):
    """The attention signal must move the number, not just decorate the reason."""
    calm = _Situation(interruptibility="interruptible", state="chatting", activity={"label": "chatting"})
    busy = _Situation(
        interruptibility="interruptible",
        state="chatting",
        activity={"label": "chatting"},
        attention={"label": "screen_active"},
    )
    quiet_net = _controller(tmp_path, situation=calm).decide({"severity": "info"})["utility"]["net"]
    busy_net = _controller(tmp_path, situation=busy).decide({"severity": "info"})["utility"]["net"]
    assert busy_net < quiet_net


def test_deferred_notifications_are_batched_and_flushable(tmp_path):
    """Deferral must still queue the notification — the model changes the verdict, not the plumbing."""
    controller = _controller(tmp_path, situation=_SITUATIONS["suppress"])
    controller.before_send({"notification_id": "n1", "category": "general", "severity": "info"})
    assert controller.get_status()["batched_count"] == 1

    flushed = controller.flush_batch()
    assert len(flushed) == 1
    assert controller.get_status()["batched_count"] == 0


def test_the_audit_record_carries_the_utility(tmp_path):
    """The decision log is the point of the change — it must include the terms."""
    records: list[dict] = []

    class _Audit:
        def log_decision(self, **kwargs):
            records.append(kwargs)

    controller = InterruptionController(
        data_dir=str(tmp_path), situation_model=_SITUATIONS["important_only"], audit_manager=_Audit()
    )
    controller.before_send({"notification_id": "n", "category": "general", "severity": "info"})

    assert records, "no audit record was written"
    assert "utility" in records[-1]["detail"], "the audit record dropped the utility breakdown"
