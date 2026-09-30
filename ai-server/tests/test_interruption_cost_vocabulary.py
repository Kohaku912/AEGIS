"""`interruption_cost` is one name with three defaults, and the vacuous comparison is now closed.

Two separate defects live in the interruption-cost vocabulary. **Both are now pinned against
regression rather than merely recorded** — and in each case the module used to assert the *defect*,
so both halves were re-pointed in the shape the `aegis-pin-a-dead-surface` skill describes: same
file, opposite claim, history kept deliberately. A reader who finds only the new claim cannot tell
whether the old one was resolved or quietly dropped.

**B-17's production half was FIXED on 2026-09-30** (register B-1 ②). Section 2 used to record that
``expected_usefulness >= interruption_cost`` was ``0.5 >= 0.5`` — always true — because
``_present_autonomous_result`` read *both* operands off the task dict with the same fallback and
nothing in ``src/`` ever wrote either key. The loop was also the **only** construction site of
``PresentationRoutingContext`` in ``src/``, so the vacuous comparison was the whole of production
behaviour, not one caller's mistake.

**1. The two interruptibility maps disagree (B-11) — order half FIXED 2026-09-30.** This module
used to *record* a disagreement; it now pins the agreement that replaced it. Same file, opposite
claim, which is the re-pointing shape the `aegis-pin-a-dead-surface` skill describes. The history is
kept deliberately: a reader who finds only the new claim cannot tell whether the old one was
resolved or quietly dropped.

``SituationModel.interruptibility`` is mapped to "how interruptible is now" twice, for two different
consumers:

* ``personal_ai/interruption.py::_RECEPTIVITY`` — P(the user welcomes an interruption now), the
  ``P(receptive)`` term of ``InterruptionController``'s expected-utility model (P1-6).
* ``autonomous/autonomous_loop.py::_current_interruption_cost`` — a cost axis for
  ``InitiativeEngine``, handed over as ``ActionCandidate(interruption_cost=...)``.

They are **not** copies of one another — different consumers, different axes — so unifying them
would be wrong. But both are monotone readings of one ladder, so they must agree on its *order*:
a level that is more receptive must not also be more costly. Exactly one pair violated that::

    batch_later vs important_only
      receptivity  0.20 vs 0.35  -> important_only is the MORE receptive of the two
      cost         0.40 vs 0.55  -> important_only is the MORE costly of the two

So ``InterruptionController`` spoke *more* readily when the user asked for important things only,
while ``InitiativeEngine`` was charged *more* to act — opposite conclusions from one input. The cost
map's middle two entries were transposed relative to the ladder
``interruptible > important_only > batch_later > suppress`` that ``_RECEPTIVITY`` follows and that
the level names themselves imply. **They were swapped on 2026-09-30** (register B-1 ①), so the cost
map now ascends the ladder ``_RECEPTIVITY`` descends. That swap moves the autonomous loop's
initiative cadence, which is why it is on the owner's review list (``DELEGATION.md`` §4).

There is a structural half too, and it is **still open**. ``_RECEPTIVITY`` carries a
discovery+equality guard on its key set (``test_interruption_utility.py``), so a new
``interruptibility`` value cannot fall through to a default. The cost map instead ends in a bare
``.get(kind, 0.2)``, so **a new level would silently read as cheaper to interrupt than
``batch_later``** — the ghost-field pattern that ``_RECEPTIVITY``'s own docstring warns against,
applied to one map and not its sibling.

**2. The routing comparison WAS constant in production (B-17) — FIXED 2026-09-30.**
``PresentationRoutingPolicy.decide`` ends with::

    should_interrupt = important and not occupied and expected_usefulness >= interruption_cost

The third conjunct used to read two fields that the autonomous loop filled from a task dict with the
*same* fallback — ``task.get(..., 0.5) or 0.5`` for both — and **nothing in the repository ever wrote
either key into a task**. So the conjunct was ``0.5 >= 0.5``: always true. ``should_interrupt``
reduced to ``important and not occupied``, and the policy's own docstring calls these fields "facts
used to choose presentation surfaces". The field was live — lowering ``expected_usefulness`` did flip
the answer — but its default decided it. ``>=`` on two equal defaults also biased the boundary
toward interrupting.

**What replaced it.** The loop now derives both operands from live signals, and neither is read off
the task dict:

* ``interruption_cost`` ← ``_current_interruption_cost()``, the real ladder (register B-1 ①), instead
  of ``task.get("interruption_cost", 0.5)``.
* ``expected_usefulness`` ← ``_expected_usefulness(task)``, the producing desire's pressure
  normalised with ``min(1.0, pressure / 10.0)`` — the same conversion this module's sibling already
  applies to pressure for an ``ActionCandidate``'s ``expected_benefit`` / ``urgency``. So the routing
  axis and the initiative axis agree on what a given pressure is worth, and no new vocabulary was
  introduced.

The pin below therefore no longer asserts "both operands share a fallback"; it asserts the opposite —
that neither operand is a task-dict lookup with a constant, and that the usefulness operand is
monotone in pressure with a *documented* neutral when the signal is unreadable.

**The context dataclass still defaults both to ``0.5``, and that is now a trap rather than a bug.**
The loop is the only ``src/`` caller, so production is fixed; but any *new* caller that omits the two
fields silently re-creates the vacuous comparison. The last pin in this section keeps demonstrating
that the field is live so the trap stays visible.

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

Recorded as B-11 and B-17 in ``PROJECT_STATUS_REVIEW.md``. Both were fixed on 2026-09-30 under the
owner's blanket go-ahead, and both moved behaviour the owner owns — the initiative cadence (the ①
swap) and what an autonomous result's usefulness is (②). Each fix therefore keeps a **named revert
detector**, so a regression reports which change it is undoing rather than "something moved":
``test_the_pair_that_used_to_be_transposed_is_now_ordered_correctly`` for ①, and
``test_the_presenter_no_longer_reads_either_operand_off_the_task`` for ②.
"""

from __future__ import annotations

import ast
import inspect
import itertools
from pathlib import Path
from typing import Any

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.personal_ai.interruption import _RECEPTIVITY, InterruptionController
from aegis_ai.presentation.routing_policy import PresentationRoutingContext, PresentationRoutingPolicy

_SRC = Path(__file__).resolve().parents[1] / "src" / "aegis_ai"
_LOOP_SRC = _SRC / "autonomous" / "autonomous_loop.py"

#: The ladder the level names imply, most interruptible first. `_RECEPTIVITY` follows it.
_LADDER = ("interruptible", "important_only", "batch_later", "suppress")

#: The pair whose order the two maps **used to** disagree on (B-11). Transposed until 2026-09-30,
#: when the two values were swapped (register B-1 ①), so `_disagreeing_pairs()` is now empty.
#: Kept as a name so the regression detector below can point at *this* pair rather than at
#: "some pair somewhere" — and because a swap is exactly the kind of change that gets reverted.
_THE_TRANSPOSED_PAIR = frozenset({"batch_later", "important_only"})

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


def _presenter_function() -> ast.FunctionDef:
    """``_present_autonomous_result``'s AST node, or a failure naming what to revisit."""
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
    return function


def _usefulness_function() -> ast.FunctionDef:
    """``_expected_usefulness``'s AST node — the derivation that replaced the constant."""
    tree = ast.parse(_LOOP_SRC.read_text(encoding="utf-8"))
    function = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_expected_usefulness"
        ),
        None,
    )
    assert function is not None, (
        "autonomous_loop.py no longer defines _expected_usefulness — if the presenter reads "
        "expected_usefulness off a task again, B-17 has been reverted"
    )
    return function


def _routing_context_keywords() -> dict[str, ast.AST]:
    """The values the presenter hands to ``PresentationRoutingContext``, by keyword name."""
    calls = [
        node
        for node in ast.walk(_presenter_function())
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "PresentationRoutingContext"
    ]
    assert len(calls) == 1, (
        f"expected the presenter to build exactly one routing context, found {len(calls)}"
    )
    return {keyword.arg: keyword.value for keyword in calls[0].keywords if keyword.arg}


def _task_lookups_of_the_routing_fields() -> list[int]:
    """Line numbers of every ``<obj>.get("<routing field>")`` left in the presenter.

    **This is the revert detector for B-1 ②.** Both operands used to be read here — with a shared
    ``0.5`` fallback — which made ``expected_usefulness >= interruption_cost`` always true. The fix
    requires this to be empty. The receiver is deliberately not constrained: *any* lookup of these
    two keys in this function is the shape being reverted, whatever it is called on.
    """
    found: list[int] = []
    for node in ast.walk(_presenter_function()):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value in _ROUTING_COMPARISON_FIELDS
        ):
            found.append(node.lineno)
    return found


def _called_name(expression: ast.AST) -> str:
    """The attribute name of a ``self.<name>(...)`` call, else ``"<not a self-call>"``."""
    if (
        isinstance(expression, ast.Call)
        and isinstance(expression.func, ast.Attribute)
        and isinstance(expression.func.value, ast.Name)
        and expression.func.value.id == "self"
    ):
        return expression.func.attr
    return "<not a self-call>"


def _pressure_divisor() -> float:
    """The constant ``_expected_usefulness`` divides pressure by, read from its source.

    Read from the AST rather than re-typed, so the check that it still equals the engine's maximum
    is a real comparison rather than a literal compared with itself.
    """
    divisors = [
        node.right.value
        for node in ast.walk(_usefulness_function())
        if isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Div)
        and isinstance(node.right, ast.Constant)
        and isinstance(node.right.value, (int, float))
    ]
    assert len(divisors) == 1, (
        f"expected _expected_usefulness to divide by exactly one constant, found {divisors} — "
        "the pressure normalisation was rewritten, so the divisor check below is stale"
    )
    return float(divisors[0])


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


def test_the_two_maps_agree_on_the_ladder_order() -> None:
    """B-11's order half: the cost map ascends the ladder `_RECEPTIVITY` descends.

    Non-vacuous by construction. An empty disagreement set over two maps that share nothing proves
    nothing, so both *inputs* are asserted before the agreement is — and the receptivity map is
    checked to still descend, or the agreement would be measured against a map that is itself out
    of order.
    """
    cost, _ = _cost_map_and_default()
    shared = sorted(set(_RECEPTIVITY) & set(cost))
    assert len(shared) >= 4, f"the two maps no longer share the ladder: {shared}"

    receptivity = [_RECEPTIVITY[level] for level in _LADDER]
    assert receptivity == sorted(receptivity, reverse=True), (
        f"_RECEPTIVITY no longer descends {_LADDER}: {receptivity} — the agreement below would "
        "be measured against a map that is itself out of order"
    )
    costs = [cost[level] for level in _LADDER]
    assert costs == sorted(costs), (
        f"the cost map no longer ascends {_LADDER}: {costs} — a level that is more receptive "
        "must not also be more costly (PROJECT_STATUS_REVIEW.md B-11)"
    )
    assert _disagreeing_pairs() == set(), (
        f"the two maps disagree again: {sorted(sorted(pair) for pair in _disagreeing_pairs())}"
    )


def test_the_pair_that_used_to_be_transposed_is_now_ordered_correctly() -> None:
    """The revert detector for the 2026-09-30 swap — named, so a regression says which pair.

    The ladder-order test above would also catch a revert, but it reports "the cost map no longer
    ascends" and leaves the reader to find the pair. This one names it.
    """
    cost, _ = _cost_map_and_default()
    a, b = sorted(_THE_TRANSPOSED_PAIR)
    assert (_RECEPTIVITY[a] - _RECEPTIVITY[b]) * (cost[a] - cost[b]) < 0, (
        f"{a} and {b} are transposed again: receptivity {_RECEPTIVITY[a]} vs {_RECEPTIVITY[b]}, "
        f"cost {cost[a]} vs {cost[b]} — this is the B-1 ① swap being reverted"
    )


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


# ── 2. The routing comparison: constant until 2026-09-30 ────────────────────

def test_the_presenter_no_longer_reads_either_operand_off_the_task() -> None:
    """**The named revert detector for B-1 ②.**

    ``expected_usefulness=float(task.get("expected_usefulness", 0.5) or 0.5)`` and the same for
    ``interruption_cost`` made the policy's last conjunct ``0.5 >= 0.5``. Restoring either line turns
    this red, and the failure says which line.
    """
    lookups = _task_lookups_of_the_routing_fields()
    assert lookups == [], (
        "the presenter reads expected_usefulness/interruption_cost off the task dict again at "
        f"line(s) {lookups} — that is the B-1 ② constant being reverted: with both operands "
        "defaulted to the same value the routing comparison is always true"
    )

    keywords = _routing_context_keywords()
    for field in sorted(_ROUTING_COMPARISON_FIELDS):
        assert field in keywords, (
            f"the presenter no longer passes {field} to PresentationRoutingContext, so it falls "
            "back to the dataclass default of 0.5 — the vacuous comparison this test guards"
        )


def test_the_two_operands_come_from_the_live_signals() -> None:
    """Which signals, exactly — so a swap or a third source fails loudly rather than silently."""
    keywords = _routing_context_keywords()

    assert _called_name(keywords["interruption_cost"]) == "_current_interruption_cost", (
        "interruption_cost no longer comes from the real cost ladder: "
        f"{ast.dump(keywords['interruption_cost'])[:120]}"
    )
    assert _called_name(keywords["expected_usefulness"]) == "_expected_usefulness", (
        "expected_usefulness no longer comes from the pressure derivation: "
        f"{ast.dump(keywords['expected_usefulness'])[:120]}"
    )


def test_the_pressure_divisor_still_matches_the_engine_maximum() -> None:
    """The normalisation is a *second* copy of the pressure range, so it is checked, not trusted.

    ``min(1.0, pressure / 10.0)`` mirrors what the loop already does for an ``ActionCandidate``'s
    ``expected_benefit`` / ``urgency``, and what ``intrinsic_task_generator`` does for task priority.
    Three copies of one fact is a divergence waiting to happen, so the divisor is compared with the
    engine's own constant instead of being assumed to agree with it.
    """
    from aegis_ai.desire.pressure import _MAX_PRESSURE

    assert _pressure_divisor() == _MAX_PRESSURE, (
        f"_expected_usefulness divides pressure by {_pressure_divisor()} but the engine's maximum is "
        f"{_MAX_PRESSURE} — the routing axis would no longer mean what the initiative axis means"
    )


class _StubDesireSystem:
    """Just the one accessor ``_expected_usefulness`` is allowed to use."""

    def __init__(self, state: Any, *, raises: bool = False) -> None:
        self._state = state
        self._raises = raises

    def get_pressure_state(self) -> Any:
        if self._raises:
            raise RuntimeError("situation snapshot failed")
        return self._state


class _StubLoop:
    """Enough of ``AutonomousLoop`` to call the method — the real loop is never constructed."""

    def __init__(self, state: Any = None, *, raises: bool = False, has_desire: bool = True) -> None:
        if has_desire:
            self._desire = _StubDesireSystem(state, raises=raises)


def _usefulness(state: Any = None, task: Any = None, **loop_kwargs: Any) -> float:
    return AutonomousLoop._expected_usefulness(_StubLoop(state, **loop_kwargs), task or {})


def test_expected_usefulness_is_monotone_in_pressure() -> None:
    """A more pressuring desire is a more useful result — the axis the comparison now reads."""
    readings = [
        _usefulness({"growth": {"pressure": p}}, {"desire": "growth"})
        for p in (0.0, 2.5, 5.0, 7.5, 10.0)
    ]

    assert readings == [0.0, 0.25, 0.5, 0.75, 1.0], (
        f"the pressure ladder is no longer the documented min(1.0, pressure / 10.0): {readings}"
    )
    assert readings[0] != readings[-1], (
        "the derivation is constant again — the whole point of B-1 ② is that this operand moves"
    )


def test_expected_usefulness_clamps_to_the_unit_interval() -> None:
    """The routing axis is 0–1, so a pressure outside the engine's range must not escape it."""
    assert _usefulness({"growth": {"pressure": 99.0}}, {"desire": "growth"}) == 1.0
    assert _usefulness({"growth": {"pressure": -3.0}}, {"desire": "growth"}) == 0.0


def test_expected_usefulness_reads_as_unknown_when_the_signal_is_unreadable() -> None:
    """Every unreadable path must read as the *documented* neutral — not as confident, not as zero.

    ``0.5`` is pressure 5.0: the module's own unknown default (``low_desires[...].get("pressure",
    5.0)``), not an invented midpoint. A silent zero here would read as "never worth interrupting
    for", which is a claim the loop cannot support.
    """
    neutral = 0.5
    assert _usefulness(None, {"desire": "growth"}) == neutral, "an empty pressure state"
    assert _usefulness({"growth": {"pressure": 3.0}}, {}) == neutral, "no desire on the task"
    assert _usefulness({"growth": {"pressure": 3.0}}, {"desire": ""}) == neutral, "a blank desire"
    assert _usefulness({"growth": {"pressure": 3.0}}, {"desire": "social"}) == neutral, "unknown desire"
    assert _usefulness(None, {"desire": "growth"}, has_desire=False) == neutral, "no desire system"
    assert _usefulness(None, {"desire": "growth"}, raises=True) == neutral, "the accessor raises"
    assert _usefulness({"growth": {}}, {"desire": "growth"}) == neutral, "an entry with no pressure"
    assert _usefulness({"growth": {"pressure": "abc"}}, {"desire": "growth"}) == neutral, "non-numeric"


def test_nothing_in_src_writes_the_two_fields_into_a_task() -> None:
    """Now a guard against a *new* writer rather than evidence of the defect.

    The loop used to read both keys off a task while nothing wrote them — the mismatch that made the
    comparison constant. The read is gone; this keeps the write side honest, because a new dict
    literal carrying these names is how a future task-feeding path would announce itself.
    """
    writers = _dict_literal_writers(_ROUTING_COMPARISON_FIELDS)

    assert writers, "discovery found no writers at all — the scan has drifted"
    assert writers == _RECORDED_KEY_WRITERS, (
        "a new place now writes expected_usefulness/interruption_cost as a dict key: "
        f"{sorted(writers)} — if it feeds a task, the presenter's operand sourcing is in question"
    )


def test_the_context_defaults_still_make_the_comparison_vacuous_for_a_direct_caller() -> None:
    """The trap that survives the fix, pinned so a new caller cannot walk into it silently.

    The loop is the only ``src/`` construction site and now supplies both operands, so production is
    fixed. But ``PresentationRoutingContext`` still defaults both to ``0.5``, so a caller that omits
    them re-creates ``0.5 >= 0.5``. This keeps demonstrating that the field is *live* — the guard is
    vacuous because of the default, not because the comparison is dead.
    """
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
