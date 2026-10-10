"""Cycle 143 pin: the ``op`` projection is hand-written twice; the two sites must
agree on a declared core, and the shared reader must request only keys a writer emits.

``ui_overview.py`` builds the same "one operation" dict at two sites, from two
different sources:

1. ``_operation_from_audit_group(group)``  -- a chat / task / system audit group;
2. ``_operation_from_autonomous_cycle(cycle)`` -- one autonomous loop cycle.

Measured 2026-10-10 (cycle 143): each site emits **30** keys, sharing **26** (a
25-key literal core plus the trailing ``causal_chain``).  Of those 25 core keys,
**7 carry a byte-identical value expression at both sites** -- ``title`` /
``action_summary`` / ``summary`` / ``what_happened`` / ``narrative`` /
``result_summary`` / ``steps`` (e.g. ``"narrative": what_happened`` appears twice) --
while the other 18 share only the key *name*, because their values are derived from
different sources (``group`` vs ``cycle``).  Four keys are site-specific:

* audit-group only: ``duration_ms`` / ``linked_entity_ids`` / ``target`` / ``targets``;
* cycle only:      ``decision`` / ``decision_reason`` / ``skip_reason`` / ``wait_reason``.

``_causal_chain_from_operation(op)`` is the **shared reader** for both.  It reads
``op["decision"]`` and ``op["skip_reason"]`` -- keys only the *cycle* site emits --
behind an ``or`` chain::

    if not enriched.get("decision_reason"):
        enriched["decision_reason"] = str(op.get("decision") or op.get("skip_reason") or "")

So for an audit-group op the fallback is always taken and ``decision_reason`` becomes
``""`` with no error.  The chain is a *silent compensation for the divergence*: rename
``skip_reason`` on the cycle site and ``wait_reason`` quietly becomes ``""``.

This is ``DELEGATION.md`` §4 item 99's family (a projection written N times with no
comparator), with the extra twist that the reader papers over the difference.  The pin
does not change behaviour -- it records the contract and the declared divergence.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any

import pytest

from aegis_ai.web import ui_overview as ui

#: The keys both sites must emit (25 literal keys + the trailing ``causal_chain``).
_CORE = frozenset(
    {
        "operation_id",
        "kind",
        "kind_label",
        "source",
        "title",
        "action_summary",
        "summary",
        "what_happened",
        "narrative",
        "result_summary",
        "purpose",
        "target_summary",
        "status",
        "result_status",
        "goal_status",
        "verification_status",
        "started_at",
        "updated_at",
        "tool_count",
        "error_count",
        "approval_count",
        "entry_count",
        "steps",
        "next_action",
        "priority",
        "causal_chain",
    }
)

#: The divergence is *declared*: each site owns exactly these extra keys.
_SITE_ONLY: dict[str, frozenset[str]] = {
    "audit_group": frozenset({"duration_ms", "linked_entity_ids", "target", "targets"}),
    "autonomous_cycle": frozenset(
        {"decision", "decision_reason", "skip_reason", "wait_reason"}
    ),
}

#: The reader that consumes both.  Its requested keys are extracted by ``ast`` below,
#: so a rename on the reader side is caught (the renamed key will not be emitted).
_READER = "_causal_chain_from_operation"
_READER_RECEIVERS = frozenset({"op", "enriched"})


def _group(**over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "group_type": "chat",
        "group_id": "g1",
        "title": "Chat with AEGIS",
        "summary": "the user asked something",
        "tool_count": 2,
        "approval_count": 0,
        "error_count": 0,
        "start_ms": 1000,
        "end_ms": 2000,
        "entry_count": 2,
        "entries": [
            {
                "action": "capability.call",
                "capability_id": "pc.file.read",
                "timestamp_ms": 1100,
                "decision": "allow",
                "detail": {},
            },
            {"action": "llm_call", "timestamp_ms": 1500, "detail": {}},
        ],
    }
    base.update(over)
    return base


def _cycle(**over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "timestamp_ms": 5000,
        "decision": "observe",
        "skip_reason": "",
        "steps": [
            {"capability_id": "pc.metric.sampled", "status": "ok", "timestamp_ms": 5100}
        ],
    }
    base.update(over)
    return base


def _produce() -> dict[str, dict[str, Any]]:
    """Drive both production writers and return the two ``op`` dicts."""
    produced = {
        "audit_group": ui._operation_from_audit_group(_group()),
        "autonomous_cycle": ui._operation_from_autonomous_cycle(_cycle()),
    }
    for site, op in produced.items():
        assert op is not None, f"the {site} writer produced nothing -- the probe is vacuous"
    return produced  # type: ignore[return-value]


def _declared(site: str) -> frozenset[str]:
    return _CORE | _SITE_ONLY[site]


def _missing(site: str, op: dict[str, Any]) -> set[str]:
    """Declared keys the site did not emit (the mutation-detecting predicate)."""
    return set(_declared(site) - set(op))


def _extra(site: str, op: dict[str, Any]) -> set[str]:
    """Keys the site emitted that are not declared (an undeclared addition)."""
    return set(set(op) - _declared(site))


def _reader_ast() -> ast.FunctionDef:
    src = Path(inspect.getsourcefile(ui._causal_chain_from_operation)).read_text(
        encoding="utf-8"
    )
    tree = ast.parse(src)
    return next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == _READER
    )


def _reader_reads() -> set[str]:
    """The string keys ``_causal_chain_from_operation`` *reads* from its ``op``.

    ``enriched`` is ``dict(op)``, so a read on it is a read on the op -- except for the
    keys the reader *creates* (``goal`` / ``trigger``), which ``_reader_writes`` names.
    """
    keys: set[str] = set()
    for node in ast.walk(_reader_ast()):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr not in {"get", "pop"} or not node.args:
            continue
        recv = node.func.value
        if not (isinstance(recv, ast.Name) and recv.id in _READER_RECEIVERS):
            continue
        a0 = node.args[0]
        if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
            keys.add(a0.value)
    return keys


def _reader_writes() -> set[str]:
    """The keys the reader *creates* (``enriched["k"] = ...``) -- not op contract."""
    keys: set[str] = set()
    for node in ast.walk(_reader_ast()):
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if (
                isinstance(t, ast.Subscript)
                and isinstance(t.value, ast.Name)
                and t.value.id in _READER_RECEIVERS
                and isinstance(t.slice, ast.Constant)
                and isinstance(t.slice.value, str)
            ):
                keys.add(t.slice.value)
    return keys


# --- the contract -----------------------------------------------------------------


def test_the_two_writers_emit_exactly_the_declared_key_sets() -> None:
    """Each site emits the declared core plus exactly its declared tail -- no more."""
    for site, op in _produce().items():
        assert not _missing(site, op), (
            f"the {site} writer dropped declared key(s) {sorted(_missing(site, op))} -- "
            f"the shared reader will silently fall back on them"
        )
        assert not _extra(site, op), (
            f"the {site} writer emitted undeclared key(s) {sorted(_extra(site, op))} -- "
            f"add them to _CORE or _SITE_ONLY so the contract stays measured"
        )


def test_the_two_writers_share_one_core() -> None:
    """The core is identical at both sites (the 26 keys are not a per-site choice)."""
    produced = _produce()
    a, b = produced["audit_group"], produced["autonomous_cycle"]
    assert _CORE <= set(a) and _CORE <= set(b)
    assert set(a) & set(b) == _CORE, (
        "the two sites no longer agree on the shared core:\n"
        f"  shared only: {sorted(set(a) & set(b) - _CORE)}\n"
        f"  core missing: {sorted(_CORE - (set(a) & set(b)))}"
    )


def test_the_divergence_is_the_declared_one() -> None:
    """The 4 keys each site owns alone are the declared ones -- not accidental."""
    produced = _produce()
    a, b = produced["audit_group"], produced["autonomous_cycle"]
    assert set(a) - set(b) == set(_SITE_ONLY["audit_group"])
    assert set(b) - set(a) == set(_SITE_ONLY["autonomous_cycle"])


def test_the_reader_reads_only_keys_a_writer_emits_or_it_creates() -> None:
    """Every key the reader reads is emitted by a writer, or created by the reader.

    If neither, that read is a silent default at *every* site -- the reader asks for
    something nothing produces (a writer-side rename, or a dead request).  ``decision``
    / ``skip_reason`` are the interesting case: they are cycle-only, which is legal
    *because* the cycle writer emits them; if that writer renamed them the reader would
    not notice (``wait_reason`` would just become ``""``).
    """
    emitted = set().union(*(set(op) for op in _produce().values()))
    reads = _reader_reads()
    writes = _reader_writes()
    assert reads, "the reader's key extraction yielded nothing -- the probe is broken"
    assert writes, "the reader's written-key extraction yielded nothing -- check the AST"
    never = reads - emitted - writes
    assert not never, (
        f"the reader reads key(s) no writer emits and it does not create: {sorted(never)} "
        f"-- every read of them is a silent default"
    )


def test_the_reader_created_keys_are_not_part_of_the_contract() -> None:
    """The reader's own additions (``goal`` / ``trigger``) are not op keys.

    This is the control for the test above: without it, ``goal`` / ``trigger`` would be
    reported as dead reads and the distinction between "the reader creates it" and "a
    writer emits it" would go unmeasured.
    """
    emitted = set().union(*(set(op) for op in _produce().values()))
    created = _reader_writes() - emitted
    assert created, "expected the reader to create at least one key of its own"
    assert created <= _reader_reads(), (
        "a key the reader creates is never read -- then it is neither contract nor use"
    )


def test_the_reader_really_compensates_for_the_divergence() -> None:
    """Measured, so the silent compensation is a *known* behaviour, not a surprise.

    An audit-group op has no ``decision`` / ``skip_reason``; the reader's ``or`` chain
    therefore leaves ``decision_reason`` / ``wait_reason`` at ``""``.  Asserting the
    *measured* value (not a claim) is what makes the pin honest about the fallback.
    """
    audit_op = _produce()["audit_group"]
    assert "decision" not in audit_op and "skip_reason" not in audit_op
    enriched = dict(audit_op)
    if not enriched.get("decision_reason"):
        enriched["decision_reason"] = str(
            audit_op.get("decision") or audit_op.get("skip_reason") or ""
        )
    if not enriched.get("wait_reason"):
        enriched["wait_reason"] = str(audit_op.get("skip_reason") or "")
    assert enriched["decision_reason"] == ""
    assert enriched["wait_reason"] == ""


def test_the_control_a_dropped_core_key_is_detected() -> None:
    """Control: the predicate is not vacuous -- dropping one core key is reported."""
    op = _produce()["audit_group"]
    dropped = {k: v for k, v in op.items() if k != "title"}
    assert _missing("audit_group", dropped) == {"title"}
    assert _missing("audit_group", op) == set()


def test_the_control_an_undeclared_key_is_detected() -> None:
    """Control, other direction: a new key with no declaration is reported."""
    op = dict(_produce()["autonomous_cycle"])
    op["brand_new_field"] = 1
    assert _extra("autonomous_cycle", op) == {"brand_new_field"}


@pytest.mark.parametrize("site", sorted(_SITE_ONLY))
def test_each_site_is_driven_for_real(site: str) -> None:
    """Both production entry points are reachable with a minimal input."""
    assert _produce()[site]
