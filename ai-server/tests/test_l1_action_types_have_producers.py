"""Every ``L1ActionType`` the router can produce -- and the one it declares but never does.

``L1ActionType`` (``intake/l1_models.py``) has five members: ``ESCALATE``, ``CAPABILITY``,
``OBSERVE``, ``IGNORE``, ``NOOP``. ``L1Router.decide`` produces **four** of them; ``NOOP`` is
declared, documented in the class docstring ("NOOP: 何もしない"), and constructed **nowhere**
in ``src/`` -- measured 2026-10-09 (cycle 124): the token ``L1ActionType.NOOP`` appears **0**
times under ``src/`` while each of the other four appears once (all in ``l1_router.py``).

This is deliberately *not* symmetric with L2. ``L2ActionType.NOOP`` is a **live** surface:
``autonomous/l2_mind.py`` constructs it on four fallback paths (disabled, gateway error, JSON
parse failure, non-dict output) and consumes it (``if decision.action.type == L2ActionType.NOOP``).
So "L1 has a NOOP too" is a natural assumption that happens to be false.

On the L1 path ``"noop"`` is only ever a **string default**, never the enum: ``runtime.py``
writes ``... or "noop"`` / ``getattr(..., "noop")`` in four places, so a reader can find the
*sentinel* without ever finding the *member*.

Recorded as ``DELEGATION.md`` section 4 item 86 (a declared surface with no producer is an
open decision: produce it, or retire it). The pins below fix the census so a new producer --
or a quiet deletion -- has to be a deliberate edit to the record and to this file.
"""

from __future__ import annotations

import ast
from pathlib import Path

from aegis_ai.intake.l1_models import L1ActionType

_SERVER = Path(__file__).resolve().parents[1]
_ROUTER = _SERVER / "src" / "aegis_ai" / "intake" / "l1_router.py"
_SRC = _SERVER / "src"

#: Measured 2026-10-09 (cycle 124): the router's producer is ``decide`` alone.
_PRODUCER = "decide"

#: The four the router constructs. A budget, not a sample: an enumeration of the *source*
#: cannot see a construction disappear unless the expected set is stated.
_PRODUCED = {"ESCALATE", "CAPABILITY", "IGNORE", "OBSERVE"}

#: The member that is declared and never constructed (section 4 item 86).
_UNPRODUCED = "NOOP"


def _router_tree() -> ast.Module:
    return ast.parse(_ROUTER.read_text(encoding="utf-8"), filename=str(_ROUTER))


def _function(name: str) -> ast.FunctionDef:
    for node in ast.walk(_router_tree()):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(
        f"{name} is gone from l1_router.py -- the L1 decision producer moved; update "
        "DELEGATION.md section 4 item 86 and this file"
    )


def _constructed_in(name: str) -> set[str]:
    """The ``L1ActionType.<X>`` attribute names built anywhere inside ``name``."""
    found: set[str] = set()
    for node in ast.walk(_function(name)):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "L1ActionType"
        ):
            found.add(node.attr)
    return found


def _src_token_count(token: str) -> int:
    return sum(
        p.read_text(encoding="utf-8", errors="replace").count(token)
        for p in _SRC.rglob("*.py")
    )


# ── controls ──────────────────────────────────────────────────────────────────────────


def test_the_declared_members_are_exactly_these() -> None:
    """Budget: the enum's membership is a recorded fact, so a rename/addition shows up here."""
    declared = {m.name for m in L1ActionType}
    assert declared == {"ESCALATE", "CAPABILITY", "OBSERVE", "IGNORE", "NOOP"}, (
        f"L1ActionType changed to {sorted(declared)} -- update section 4 item 86 and this file"
    )


def test_the_router_constructs_exactly_four_of_them() -> None:
    """The producer census: which members ``decide`` actually builds."""
    produced = _constructed_in(_PRODUCER)
    assert produced == _PRODUCED, (
        f"{_PRODUCER} now constructs {sorted(produced)} (expected {sorted(_PRODUCED)}) -- if "
        f"{_UNPRODUCED!r} gained or lost a producer, section 4 item 86 is stale"
    )


# ── the finding ───────────────────────────────────────────────────────────────────────


def test_noop_is_declared_but_never_constructed() -> None:
    """``NOOP`` is in the enum and in its docstring, and no code builds it.

    Kept as a pin rather than a one-off measurement because the *record* (section 4 item 86)
    would otherwise rot: a new ``L1ActionType.NOOP`` producer, or a quiet deletion of the
    member, would leave the record asserting something false with nothing to notice.
    """
    assert _UNPRODUCED in {m.name for m in L1ActionType}, (
        f"{_UNPRODUCED} was removed from the enum -- item 86 is resolved (the member is gone); "
        "delete this pin and close the item"
    )
    assert _UNPRODUCED not in _constructed_in(_PRODUCER), (
        f"{_PRODUCER} now constructs {_UNPRODUCED} -- the member is live; update section 4 "
        "item 86 (its premise was 'declared but never constructed') and this file"
    )


def test_the_token_scan_is_not_vacuous_and_finds_no_live_noop() -> None:
    """Control + finding: the scan must find the four live members, and no ``NOOP``.

    Without the first assertion, ``NOOP not in src`` could mean "the scan read nothing".
    """
    for member in sorted(_PRODUCED):
        assert _src_token_count(f"L1ActionType.{member}") >= 1, (
            f"the scan did not find `L1ActionType.{member}` under src/ -- the scan is broken, "
            "so the NOOP assertion below is vacuous"
        )
    assert _src_token_count(f"L1ActionType.{_UNPRODUCED}") == 0, (
        f"`L1ActionType.{_UNPRODUCED}` is now referenced under src/ -- section 4 item 86 "
        "described it as unconstructed; re-measure and update the record"
    )
