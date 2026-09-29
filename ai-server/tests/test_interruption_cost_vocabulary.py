"""`interruption_cost` is one name with three defaults, and one vacuous comparison.

Two separate defects live in the interruption-cost vocabulary. Both are measured here; neither
is fixed, because both need a call that is not a mechanical one.

**1. The two interruptibility maps disagree (B-11).** ``SituationModel.interruptibility`` is
mapped to "how interruptible is now" twice, for two different consumers:

* ``personal_ai/interruption.py::_RECEPTIVITY`` — P(the user welcomes an interruption now), the
  ``P(receptive)`` term of ``InterruptionController``'s expected-utility model (P1-6).
* ``autonomous/autonomous_loop.py::_current_interruption_cost`` — a cost axis for
  ``InitiativeEngine``, handed over as ``ActionCandidate(interruption_cost=...)``.

They are **not** copies of one another — different consumers, different axes — so unifying them
would be wrong. But both are monotone readings of one ladder, so they must agree on its *order*:
a level that is more receptive must not also be more costly. Exactly one pair violates that::

    batch_later vs important_only
      receptivity  0.20 vs 0.35  -> important_only is the MORE receptive of the two
      cost         0.40 vs 0.55  -> important_only is the MORE costly of the two

So ``InterruptionController`` speaks *more* readily when the user asked for important things only,
while ``InitiativeEngine`` is charged *more* to act — opposite conclusions from one input. The
cost map's middle two entries are transposed relative to the ladder
``interruptible > important_only > batch_later > suppress`` that ``_RECEPTIVITY`` follows and that
the level names themselves imply.

There is a structural half too. ``_RECEPTIVITY`` carries a discovery+equality guard on its key set
(``test_interruption_utility.py``), so a new ``interruptibility`` value cannot fall through to a
default. The cost map instead ends in a bare ``.get(kind, 0.2)``, so **a new level would silently
read as cheaper to interrupt than ``batch_later``** — the ghost-field pattern that
``_RECEPTIVITY``'s own docstring warns against, applied to one map and not its sibling.

**2. The routing comparison is constant in production (B-17).**
``PresentationRoutingPolicy.decide`` ends with::

    should_interrupt = important and not occupied and expected_usefulness >= interruption_cost

The third conjunct reads two fields that the autonomous loop fills from a task dict with the *same*
fallback — ``task.get(..., 0.5) or 0.5`` for both — and **nothing in the repository ever writes
either key into a task**. So the conjunct is ``0.5 >= 0.5``: always true. ``should_interrupt``
reduces to ``important and not occupied``, and the policy's own docstring calls these fields "facts
used to choose presentation surfaces". The field is live — lowering ``expected_usefulness`` does flip
the answer — but its default decides it. ``>=`` on two equal defaults also biases the boundary
toward interrupting.

The name carries **three** defaults across the subsystem: ``0.0`` on ``ActionCandidate``,
``0.2`` as the cost map's fallback, ``0.5`` on ``PresentationRoutingContext``. One name, three
answers to "what if we do not know".

**They are not three defaults on one quantity, and ③ "collapse them" was withdrawn (2026-09-29).**
Measured: ``0.0`` means *the caller passed nothing* (no ``src/`` site relies on it — both sites
construct ``ActionCandidate`` with an explicit ``interruption_cost=``, so only tests reach ``0.0``);
``0.2`` means *the reported level is not in the cost table*; ``0.5`` belongs to a **different
quantity** — the routing comparison's operand, compared against ``expected_usefulness`` rather than
summed into a score. Merging them would collapse three different unknowns into one, which is the
defect this module is about, not a repair of it.

**The cost function itself answers "we do not know" twice.** ``_current_interruption_cost`` returns
``0.15`` when there is no agent state or when the situation snapshot raises, and ``0.2`` when the
level is unnamed. The first version of this module recorded only ``0.2`` — i.e. the pin named after
"one name, N answers" under-counted the answers on its own axis. Both are recorded now, and the
scan classifies *every* ``Return`` of the function so a third answer cannot appear unnoticed.

Recorded as B-11 and B-17 in ``PROJECT_STATUS_REVIEW.md``. Fixing either moves behaviour the owner
owns (initiative cadence; what an autonomous result's usefulness is), so this module pins the state
so the divergence cannot widen unnoticed and the record cannot rot.
"""

from __future__ import annotations

import ast
import inspect
import itertools
from pathlib import Path
from typing import Any

from aegis_ai.personal_ai.interruption import _RECEPTIVITY, InterruptionController
from aegis_ai.presentation.routing_policy import PresentationRoutingContext, PresentationRoutingPolicy

_SRC = Path(__file__).resolve().parents[1] / "src" / "aegis_ai"
_LOOP_SRC = _SRC / "autonomous" / "autonomous_loop.py"

#: The ladder the level names imply, most interruptible first. `_RECEPTIVITY` follows it.
_LADDER = ("interruptible", "important_only", "batch_later", "suppress")

#: The one pair whose order the two maps disagree on. **Recorded debt, not an approval** —
#: fixing it changes when the autonomous loop raises an initiative.
_DISAGREEING_PAIR = frozenset({"batch_later", "important_only"})

#: The cost map's fallback for a level it does not name.
_RECORDED_COST_DEFAULT = 0.2

#: The levels the cost fallback sits *below* — i.e. what an unrecognised level is charged less than.
_RECORDED_LEVELS_ABOVE_THE_FALLBACK = ["batch_later", "important_only", "suppress"]

#: Every value ``_current_interruption_cost`` returns when it does not know, keyed by value with
#: the condition that produces it. ``0.15`` = no agent state, or the situation snapshot raised;
#: ``0.2`` = the level is not in the cost table. **Recorded debt, not an approval** — ``0.15`` was
#: absent from the first version of this pin, so the pin named after "one name, N answers" was
#: itself under-counting. Two answers to one question on one axis is the defect, not the fix.
_RECORDED_UNKNOWN_ANSWERS = {
    0.15: "no agent state, or the situation snapshot raised",
    0.2: "the reported level is not in the cost table",
}

#: The two fields `PresentationRoutingPolicy`'s last comparison reads.
_ROUTING_COMPARISON_FIELDS = frozenset({"expected_usefulness", "interruption_cost"})

#: Where those keys are written as dict literals anywhere in `src/`, by enclosing function.
#: Both are the *echo* into the presentation payload — not task construction, which is the
#: direction the comparison reads from. Recorded so a new writer (or a real one) fails loudly.
_RECORDED_KEY_WRITERS = frozenset(
    {("autonomous/autonomous_loop.py", "_present_autonomous_result")}
)


# ── Discovery ───────────────────────────────────────────────────────────────

def _cost_function() -> ast.FunctionDef:
    """``_current_interruption_cost``'s AST node, or a failure naming what to revisit."""
    tree = ast.parse(_LOOP_SRC.read_text(encoding="utf-8"))
    function = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_current_interruption_cost"
        ),
        None,
    )
    assert function is not None, (
        "autonomous_loop.py no longer defines _current_interruption_cost — the record in "
        "PROJECT_STATUS_REVIEW.md (B-11) needs revisiting"
    )
    return function


def _cost_map_and_default() -> tuple[dict[str, float], Any]:
    """Discover ``_current_interruption_cost``'s table and fallback from its source.

    Read from the AST rather than re-typed here: a second copy of the numbers would be the very
    defect this module is about. The table is identified as **the receiver of the fallback
    ``.get(..., default)``**, which ties the two together structurally — the method also contains
    an unrelated empty ``{}``.
    """
    fallbacks = [
        node
        for node in ast.walk(_cost_function())
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and len(node.args) == 2
        and isinstance(node.args[1], ast.Constant)
    ]
    assert len(fallbacks) == 1, f"expected one fallback default, found {len(fallbacks)}"
    table = fallbacks[0].func.value
    assert isinstance(table, ast.Dict), (
        "_current_interruption_cost no longer falls back from a literal table"
    )
    return ast.literal_eval(table), fallbacks[0].args[1].value


def _unknown_answers_in_the_cost_function() -> dict[float, list[int]]:
    """Every value ``_current_interruption_cost`` returns when it does not know, by line number.

    Two shapes count as an answer: a bare ``return <number>``, and ``return <table>.get(key,
    <number>)``. Any other ``Return`` shape is an **unclassified path** and raises rather than
    being skipped — an anchor that does not match is a SKIP, not a pass, and a SKIP here would
    silently shrink the recorded set. The table's *named* levels are deliberately not collected:
    they answer "we know", which is a different vocabulary from the one this module is about.
    """
    answers: dict[float, list[int]] = {}
    for node in ast.walk(_cost_function()):
        if not isinstance(node, ast.Return) or node.value is None:
            continue
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, (int, float)):
            answer = float(value.value)
        elif (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and value.func.attr == "get"
            and len(value.args) == 2
            and isinstance(value.args[1], ast.Constant)
            and isinstance(value.args[1].value, (int, float))
        ):
            answer = float(value.args[1].value)
        else:
            raise AssertionError(
                "_current_interruption_cost grew a return shape this scan cannot classify "
                f"(line {node.lineno}): {ast.dump(value)[:80]} — the unknown-answer set may now "
                "be incomplete, so the record in PROJECT_STATUS_REVIEW.md (B-11) needs revisiting"
            )
        answers.setdefault(answer, []).append(node.lineno)
    return answers


def _disagreeing_pairs() -> set[frozenset[str]]:
    """Pairs whose order differs between the two maps."""
    cost, _ = _cost_map_and_default()
    shared = sorted(set(_RECEPTIVITY) & set(cost))
    return {
        frozenset({a, b})
        for a, b in itertools.combinations(shared, 2)
        if (_RECEPTIVITY[a] - _RECEPTIVITY[b]) * (cost[a] - cost[b]) > 0
    }


def _dict_literal_writers(keys: frozenset[str]) -> set[tuple[str, str]]:
    """Every ``{key: ...}`` literal in ``src/`` naming one of ``keys``, as (file, function)."""

    def enclosing(path: Path) -> set[tuple[str, str]]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found: set[tuple[str, str]] = set()

        def visit(node: ast.AST, function: str) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit(child, child.name)
                    continue
                if isinstance(child, ast.Dict):
                    for key in child.keys:
                        if isinstance(key, ast.Constant) and key.value in keys:
                            found.add((path.relative_to(_SRC).as_posix(), function))
                visit(child, function)

        visit(tree, "<module>")
        return found

    writers: set[tuple[str, str]] = set()
    for path in sorted(_SRC.rglob("*.py")):
        writers |= enclosing(path)
    return writers


def _task_fallbacks_in_the_presenter() -> list[Any]:
    """The fallback values the presenter uses when it reads the two routing fields off a task."""
    tree = ast.parse(_LOOP_SRC.read_text(encoding="utf-8"))
    function = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_present_autonomous_result"
        ),
        None,
    )
    assert function is not None, "autonomous_loop.py no longer defines _present_autonomous_result"

    fallbacks: list[Any] = []
    for node in ast.walk(function):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float"):
            continue
        for inner in ast.walk(node):
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr == "get"
                and len(inner.args) == 2
                and isinstance(inner.args[0], ast.Constant)
                and inner.args[0].value in _ROUTING_COMPARISON_FIELDS
            ):
                fallbacks.append(inner.args[1].value)
    return fallbacks


# ── 1. The two maps describe one ladder ─────────────────────────────────────

def test_the_cost_map_names_every_level_the_receptivity_map_names_except_unknown() -> None:
    """A level the cost map omits falls through to a default instead of being weighed."""
    cost, _ = _cost_map_and_default()
    expected = set(_RECEPTIVITY) - {"unknown"}

    assert len(expected) >= 4, f"receptivity discovery found only {sorted(_RECEPTIVITY)}"
    assert set(cost) == expected, (
        "the cost map and _RECEPTIVITY no longer cover the same levels.\n"
        f"  named by receptivity but not cost: {sorted(expected - set(cost))}\n"
        f"  named by cost but not receptivity: {sorted(set(cost) - expected)}"
    )


def test_the_cost_map_falls_back_to_the_recorded_default() -> None:
    """The fallback is unguarded, so pin its value *and* what it reads as permission over.

    ``_RECEPTIVITY``'s docstring states the principle — "the honest value has to be its own entry
    rather than a fallback that happens to read as permission" — and its key set is asserted equal
    to ``situation.py``'s vocabulary. The cost map has no such guard.
    """
    cost, default = _cost_map_and_default()

    assert default == _RECORDED_COST_DEFAULT
    above = sorted(level for level, value in cost.items() if value > default)
    assert above == _RECORDED_LEVELS_ABOVE_THE_FALLBACK, (
        "the cost fallback no longer sits below exactly those levels: "
        f"{above} — an unrecognised interruptibility is now charged differently"
    )


def test_the_cost_function_has_only_the_recorded_unknown_answers() -> None:
    """The function answers "we do not know" twice; both answers are recorded, not just the table's.

    The first version of this pin recorded only the ``.get(kind, 0.2)`` fallback, so ``0.15`` —
    returned when there is no agent state or when the situation snapshot raises — was invisible to
    the very detector that exists to count this kind of divergence. A pin named after "one name, N
    answers" has to scan for *all* the answers, not for the shape it was first written against.
    """
    answers = _unknown_answers_in_the_cost_function()

    assert sum(len(lines) for lines in answers.values()) >= 3, (
        f"the scan classified only {answers} — it is no longer finding the function's returns, "
        "so the equality below would pass vacuously"
    )
    assert set(answers) == set(_RECORDED_UNKNOWN_ANSWERS), (
        "the cost function's 'we do not know' answers changed.\n"
        f"  unrecorded: {sorted(set(answers) - set(_RECORDED_UNKNOWN_ANSWERS))}\n"
        f"  recorded but gone: {sorted(set(_RECORDED_UNKNOWN_ANSWERS) - set(answers))}\n"
        "  — a new answer is a new vocabulary entry, not a detail: record it in "
        "_RECORDED_UNKNOWN_ANSWERS and in PROJECT_STATUS_REVIEW.md (B-11)"
    )


def test_the_receptivity_map_follows_the_ladder_the_level_names_imply() -> None:
    """Establishes which of the two maps is the outlier, rather than leaving it open."""
    assert _LADDER[0] == "interruptible" and _LADDER[-1] == "suppress"
    values = [_RECEPTIVITY[level] for level in _LADDER]
    assert values == sorted(values, reverse=True), (
        f"_RECEPTIVITY no longer descends {_LADDER}: {values}"
    )


def test_the_two_maps_disagree_on_exactly_the_recorded_pair() -> None:
    assert _disagreeing_pairs() == {_DISAGREEING_PAIR}


def test_the_cost_value_reaches_the_initiative_engine_and_not_the_controller() -> None:
    """Pins *why* the two maps are not duplicates — so a future "unify them" refactor is noticed."""
    parameters = set(inspect.signature(InterruptionController.decide).parameters)
    assert parameters == {"self", "notification"}, (
        f"InterruptionController.decide now accepts {sorted(parameters)} — if it grew an "
        "interruption_cost parameter, the two maps may finally be redundant"
    )

    tree = ast.parse(_LOOP_SRC.read_text(encoding="utf-8"))
    handovers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and any(keyword.arg == "interruption_cost" for keyword in node.keywords)
    ]
    assert len(handovers) >= 2, (
        "expected interruption_cost to be handed to the initiative engine, found "
        f"{len(handovers)} sites"
    )
    supplied = 0
    for node in handovers:
        value = next(kw.value for kw in node.keywords if kw.arg == "interruption_cost")
        supplied += sum(
            1
            for inner in ast.walk(value)
            if isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Attribute)
            and inner.func.attr == "_current_interruption_cost"
        )
    assert supplied >= 2, (
        "fewer than two interruption_cost handovers come from _current_interruption_cost() — "
        "the cost axis is being sourced elsewhere"
    )


# ── 2. The routing comparison is constant in production ─────────────────────

def test_the_presenter_gives_both_routing_fields_the_same_fallback() -> None:
    """``expected_usefulness >= interruption_cost`` is ``0.5 >= 0.5`` whenever neither is set."""
    fallbacks = _task_fallbacks_in_the_presenter()

    assert len(fallbacks) == 2, (
        f"expected the presenter to default both routing fields, found {fallbacks}"
    )
    assert fallbacks[0] == fallbacks[1], (
        f"the two operands of the routing comparison now default differently: {fallbacks} — "
        "the comparison may no longer be constant"
    )


def test_nothing_in_src_writes_the_two_fields_into_a_task() -> None:
    """The only writers are the echoes into the presentation payload, not task construction."""
    writers = _dict_literal_writers(_ROUTING_COMPARISON_FIELDS)

    assert writers, "discovery found no writers at all — the scan has drifted"
    assert writers == _RECORDED_KEY_WRITERS, (
        "a new place now writes expected_usefulness/interruption_cost as a dict key: "
        f"{sorted(writers)} — if it feeds a task, B-17 may be closed"
    )


def test_the_routing_comparison_is_decided_by_its_defaults() -> None:
    """The field is live — its *default* is what makes the guard vacuous, so both halves are pinned."""
    policy = PresentationRoutingPolicy()
    base: dict[str, Any] = {"importance": "high", "user_attention": "idle"}

    at_default = policy.decide(PresentationRoutingContext(**base))
    assert at_default.interrupt is True, (
        "the routing policy no longer interrupts at the defaults — the comparison's outcome changed"
    )

    lowered = policy.decide(PresentationRoutingContext(expected_usefulness=0.4, **base))
    assert lowered.interrupt is False, (
        "expected_usefulness is no longer consulted, so the comparison is dead rather than vacuous"
    )
