"""The two L1 routes partition the event space: disjoint, and exhaustive off the exclusions.

L1 is reached through two subscriptions with two filters (``runtime.py``):

* ``_should_route_to_l1_immediate`` -- membership in ``_L1_IMMEDIATE_EVENT_TYPES`` (16 types).
* ``_should_route_to_l1_background`` -- everything else, minus ``_L1_EXCLUDED_EVENT_TYPES``
  (``{""}``) and anything starting with ``_L1_EXCLUDED_EVENT_PREFIXES``
  (``("l1.", "l2.", "l3.", "presentation.")``).

The exclusions are a **feedback guard**, not tidiness: ``l1.*`` is L1's *own* output
(``l1.observation`` / ``l1.decision`` / ``l1.escalation`` / ``l1.capability.*``) and
``l2.*`` / ``l3.*`` / ``presentation.*`` are the layers downstream. If any of them reached
L1, an event would trigger the pipeline that publishes it -- a loop. So "neither route takes
an excluded event" is a safety invariant, and the two filters must not both take one event.

``tests/test_runtime_singleton.py`` (``test_l1_routing_helpers_...``) pins the filters by
**example**: seven immediate types and five background cases. Measured 2026-10-09 (cycle 124),
that leaves two of the four declared prefixes -- ``l2.`` and ``l3.`` -- exercised by **no**
test, and neither disjointness nor exhaustiveness is asserted anywhere. This file enumerates
the module's own declarations instead of sampling, so adding a prefix extends the pin.

What this file does NOT claim: that the *set* of excluded prefixes is complete (a missing
prefix is invisible to any test that enumerates the declared tuple -- the same gap item 45
records for the immediate types), nor that L1's output is otherwise loop-free.
"""

from __future__ import annotations

from typing import Any

import aegis_ai.runtime as runtime_module

# The three declarations this file enumerates. Read through a helper so a *rename* turns
# the read red instead of silently making every assertion below vacuous.
_IMMEDIATE = "_L1_IMMEDIATE_EVENT_TYPES"
_PREFIXES = "_L1_EXCLUDED_EVENT_PREFIXES"
_EXCLUDED_TYPES = "_L1_EXCLUDED_EVENT_TYPES"


def _declared(name: str) -> Any:
    try:
        return getattr(runtime_module, name)
    except AttributeError as exc:  # pragma: no cover - control path
        raise AssertionError(
            f"{name} is gone from runtime.py -- the L1 routing declaration was renamed or "
            "moved; update this file (and DELEGATION.md section 4 item 48/85 if the routes moved)"
        ) from exc


def _immediate(event_type: str) -> bool:
    return runtime_module._should_route_to_l1_immediate(event_type)


def _background(event_type: str) -> bool:
    return runtime_module._should_route_to_l1_background(event_type)


def _excluded(event_type: str) -> bool:
    return event_type in _declared(_EXCLUDED_TYPES) or event_type.startswith(
        tuple(_declared(_PREFIXES))
    )


def _space() -> set[str]:
    """Every declared member, every declared prefix, plus representatives and near-misses.

    Not a sample of the (infinite) string space -- the invariant is structural. The point is
    that the space is *generated from the declarations*, so a new declared prefix or type is
    covered without editing this function.
    """
    space: set[str] = set(_declared(_IMMEDIATE))
    space |= set(_declared(_EXCLUDED_TYPES))
    for prefix in _declared(_PREFIXES):
        space.add(prefix)
        space.add(prefix + "x")
        space.add(prefix + "observation")
    space |= {
        # ordinary types: one that the immediate set names, one that it does not
        "pc.user_activity.snapshot",
        "android.user_activity.changed",
        "self_call",
        "memory.written",
        "notification.sent",
        # near-misses: the exclusion is a *prefix*, so these must NOT be excluded
        "l1",
        "l2",
        "l3",
        "presentation",
        "l1x",
        "x.l1.observation",
        # case-sensitivity: the prefixes are lower-case
        "L1.observation",
    }
    return space


# ── controls ──────────────────────────────────────────────────────────────────────────


def test_the_declared_populations_are_non_empty() -> None:
    """Control: an empty declaration would make every enumeration below vacuous."""
    assert _declared(_IMMEDIATE), f"{_IMMEDIATE} is empty -- the enumeration proves nothing"
    assert _declared(_PREFIXES), f"{_PREFIXES} is empty -- the exclusion loop proves nothing"


def test_the_declared_exclusions_are_exactly_these() -> None:
    """A budget, not a sample -- an enumeration cannot see the declaration *shrink*.

    Measured 2026-10-09 (cycle 124): the tests below enumerate ``_L1_EXCLUDED_EVENT_PREFIXES``,
    so deleting ``"l2."`` or ``"l3."`` from the tuple simply removed them from the loop and the
    pin stayed green (mutation M1/M2 survived). The feedback guard is exactly these four
    prefixes; widening or narrowing it has to be a deliberate edit to this line too.
    """
    assert set(_declared(_PREFIXES)) == {"l1.", "l2.", "l3.", "presentation."}, (
        f"the excluded-prefix set changed to {sorted(_declared(_PREFIXES))} -- the feedback "
        "guard is exactly these four; update this pin and the runtime comment together"
    )
    assert set(_declared(_EXCLUDED_TYPES)) == {""}, (
        f"the excluded-type set changed to {sorted(_declared(_EXCLUDED_TYPES))} -- the empty "
        "event type is the only one; a real type here would be silently dropped"
    )


def test_a_representative_type_reaches_each_route() -> None:
    """Non-vacuity floor: both filters must accept something, or 'disjoint' is trivial."""
    assert _immediate("pc.user_activity.snapshot"), (
        "no immediate type was accepted -- the immediate filter is dead"
    )
    assert _background("memory.written"), (
        "no background type was accepted -- the background filter is dead"
    )


# ── the enumerated exclusions (the feedback guard) ────────────────────────────────────


def test_every_declared_excluded_prefix_is_rejected_by_both_routes() -> None:
    """Enumerate the declared prefixes -- `l2.` and `l3.` are covered by no other test."""
    failures: list[str] = []
    for prefix in _declared(_PREFIXES):
        for member in (prefix + "x", prefix + "observation", prefix + "capability.invoked"):
            if _immediate(member):
                failures.append(f"{member!r} reached the *immediate* route")
            if _background(member):
                failures.append(f"{member!r} reached the *background* route")
    assert not failures, (
        "an excluded prefix is not a feedback guard any more (an L1/L2/L3/presentation event "
        "would re-enter the pipeline that publishes it):\n  " + "\n  ".join(failures)
    )


def test_every_declared_excluded_type_is_rejected_by_both_routes() -> None:
    failures: list[str] = []
    for event_type in _declared(_EXCLUDED_TYPES):
        if _immediate(event_type):
            failures.append(f"{event_type!r} reached the immediate route")
        if _background(event_type):
            failures.append(f"{event_type!r} reached the background route")
    assert not failures, "\n  ".join(failures)


def test_no_immediate_type_is_also_excluded() -> None:
    """Consistency: a type declared immediate must not sit under an excluded prefix.

    If it did, the two declarations would contradict: the immediate filter would take it and
    the background filter's exclusion would claim it belongs to the internal-noise family.
    """
    overlap = sorted(t for t in _declared(_IMMEDIATE) if _excluded(t))
    assert not overlap, (
        f"{overlap} are declared immediate *and* excluded -- the declarations contradict"
    )


# ── the partition itself ──────────────────────────────────────────────────────────────


def test_the_two_routes_are_disjoint() -> None:
    """No event may reach both routes (it would run the L1 pipeline twice)."""
    both = sorted(t for t in _space() if _immediate(t) and _background(t))
    assert not both, (
        f"{both} reach *both* L1 routes -- the partition is broken and those events would be "
        "processed twice (once inline, once on the immediate worker)"
    )


def test_every_non_excluded_type_reaches_a_route() -> None:
    """Exhaustive off the exclusions: a normal event must not fall through both filters.

    A gap here is silent: the event is published, no subscriber matches, and nothing records
    that L1 never saw it.
    """
    gap = sorted(t for t in _space() if not _excluded(t) and not _immediate(t) and not _background(t))
    assert not gap, (
        f"{gap} are not excluded and reach neither route -- they are dropped silently"
    )


def test_the_excluded_family_is_recognised_by_prefix_not_by_containment() -> None:
    """Pin the *rule*: the exclusion is `startswith`, so a mid-string `l1.` is not excluded.

    ``x.l1.observation`` and ``l1x`` contain / resemble the prefix but do not start with it;
    they are ordinary events. This distinguishes the guard from a substring filter, which
    would also swallow unrelated types.
    """
    for member in ("x.l1.observation", "l1x", "L1.observation"):
        assert not _excluded(member), f"{member!r} must not be treated as internal noise"
        assert _background(member), (
            f"{member!r} does not start with an excluded prefix, so the background route takes it"
        )
