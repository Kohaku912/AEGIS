"""Cycle 141 pin: the ``_recent_l1_summaries`` writer/reader key contract is compared.

The chain (runtime.py):

* **Writer** -- ``_append_recent_l1_summary`` (``:438``) appends one dict per L1 run to
  ``runtime._recent_l1_summaries`` (a ``deque(maxlen=50)``).
* **Reader A (pass-through)** -- ``_get_recent_l1_summaries`` (``:461``) returns a slice.
* **Reader B (L1 prompt)** -- ``_compact_recent_l1_for_l1`` (``:475``) rebuilds a 5-field
  projection and is placed into the L1 context bundle as ``"recent_l1"`` (``:657``) --
  i.e. it reaches the **LLM prompt**.
* **Reader C (L2 prompt)** -- the same stored dicts are handed to L2 via
  ``l1_summaries_provider`` (``:1591``) and rendered by ``L2Context.to_prompt``
  (``autonomous/l2_models.py:92``).

Every consumer reads the writer's keys **by name with a silent default**
(``entry.get("event_type") or ""``). So a writer-side rename does not raise: the field
becomes ``""`` / ``0.0`` / ``"background"`` and the prompt quietly loses information.

Measured 2026-10-10 (HEAD ``6f63b99``), real writer driven directly:

* One production write yields 12 keys; reader B yields all five of its fields populated.
* Renaming the writer's ``"event_type"`` key to ``"event_tp"`` makes reader B return
  ``event_type == ""`` -- **no error, no warning** -- while reader A (pass-through) still
  shows ``event_tp``. Nothing in the suite noticed before this file.

The pin drives the **production** writer (not a hand-built dict, which would make the
assertion vacuous) and compares each reader's **requested key set** against the writer's
**emitted key set**, so a rename on either side is red.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

import aegis_ai.runtime as runtime_module
from aegis_ai.runtime import (
    _append_recent_l1_summary,
    _build_l1_context_capsule,
    _compact_recent_l1_for_l1,
    _get_recent_l1_summaries,
)

#: The keys ``_append_recent_l1_summary`` is expected to emit (measured 2026-10-10).
_WRITER_KEYS = frozenset(
    {
        "event_id",
        "event_type",
        "meaning",
        "value",
        "priority",
        "required_intelligence",
        "confidence",
        "action_type",
        "summary_bucket",
        "observed_action",
        "possible_intent",
        "occurred_at_ms",
    }
)

#: The keys ``_compact_recent_l1_for_l1`` reads out of each stored entry.
_READER_B_KEYS = frozenset(
    {"event_type", "summary_bucket", "meaning", "action_type", "priority"}
)

#: The keys the L2 prompt (``L2Context.to_prompt``) reads out of each stored entry.
_READER_C_KEYS = frozenset(
    {"summary_bucket", "action_type", "meaning", "observed_action", "possible_intent"}
)


def _event() -> SimpleNamespace:
    return SimpleNamespace(
        event_id="evt-1", event_type="social.inbox.received", timestamp_ms=1234
    )


def _observation() -> SimpleNamespace:
    return SimpleNamespace(
        event_id="evt-1",
        meaning="a message arrived",
        value=0.5,
        priority=7.0,
        required_intelligence="low",
        confidence=0.9,
        raw={"summary_bucket": "urgent", "observed_action": "read", "possible_intent": "reply"},
    )


def _decision() -> SimpleNamespace:
    return SimpleNamespace(action=SimpleNamespace(type="observe"))


def _write_one() -> Any:
    """Drive the **production** writer; return the runtime whose deque it filled."""
    runtime = SimpleNamespace()
    _append_recent_l1_summary(runtime, _event(), _observation(), _decision())
    return runtime


def test_the_production_writer_emits_the_declared_key_set() -> None:
    runtime = _write_one()
    entry = runtime._recent_l1_summaries[-1]
    assert set(entry) == _WRITER_KEYS, (
        f"the writer's key set moved: added={sorted(set(entry) - _WRITER_KEYS)}, "
        f"removed={sorted(_WRITER_KEYS - set(entry))}"
    )


def test_reader_b_asks_only_for_keys_the_writer_emits() -> None:
    """A reader key with no writer key is a silent default -- assert the subset."""
    runtime = _write_one()
    emitted = set(runtime._recent_l1_summaries[-1])
    missing = _READER_B_KEYS - emitted
    assert not missing, (
        f"_compact_recent_l1_for_l1 reads {sorted(missing)}, which the writer does not "
        f"emit -- those fields silently become ''/0.0/'background' in the L1 prompt"
    )


def test_reader_c_asks_only_for_keys_the_writer_emits() -> None:
    runtime = _write_one()
    emitted = set(runtime._recent_l1_summaries[-1])
    missing = _READER_C_KEYS - emitted
    assert not missing, (
        f"L2Context.to_prompt reads {sorted(missing)}, which the writer does not emit -- "
        f"those fields silently default in the L2 prompt"
    )


def test_reader_b_fields_are_populated_from_a_production_write() -> None:
    """The contract holds *positively*, not just as an empty-subset check."""
    runtime = _write_one()
    compact = _compact_recent_l1_for_l1(runtime, limit=3)
    assert compact, "the compaction returned nothing for a non-empty deque"
    row = compact[0]
    assert set(row) == set(_READER_B_KEYS), f"compaction key set moved: {sorted(row)}"
    empty = {k: v for k, v in row.items() if v in ("", 0.0, 0, None)}
    assert not empty, (
        f"a production write left reader-B fields at their silent defaults: {empty}"
    )


def test_the_two_deque_readers_agree_on_the_row_count() -> None:
    """Reader A (pass-through) and reader B (compaction) see the same entries."""
    runtime = _write_one()
    for i in range(4):
        ev = _event()
        ev.event_id = f"evt-{i}"
        _append_recent_l1_summary(runtime, ev, _observation(), _decision())

    passthrough = _get_recent_l1_summaries(runtime, limit=10)
    compact = _compact_recent_l1_for_l1(runtime, limit=3)
    assert len(compact) == min(3, len(passthrough)) == 3, (
        f"pass-through={len(passthrough)} compact={len(compact)} -- the compaction's "
        f"limit no longer tracks the pass-through reader"
    )


def test_a_writer_side_rename_is_caught_by_the_key_contract() -> None:
    """Control: this is exactly what the pin above *cannot* be vacuous about.

    Simulate the mutation's effect -- an entry whose ``event_type`` key is renamed --
    and show reader B silently loses the value (the defect the subset assertion
    prevents), while reader A still shows the renamed key.
    """
    runtime = SimpleNamespace()
    entry = {
        "event_tp": "social.inbox.received",  # renamed -- .get("event_type") now defaults
        "summary_bucket": "urgent",
        "meaning": "a message arrived",
        "action_type": "observe",
        "priority": 7.0,
    }
    runtime._recent_l1_summaries = [entry]

    compact = _compact_recent_l1_for_l1(runtime, limit=3)
    assert compact[0]["event_type"] == "", "the silent default did not fire"
    assert _get_recent_l1_summaries(runtime, limit=3)[0].get("event_tp") == (
        "social.inbox.received"
    ), "the pass-through reader was supposed to keep the renamed key -- the hazard is " \
       "that reader B loses it while reader A does not notice"


def test_the_l1_context_capsule_builds_recent_l1_from_the_writer_entries() -> None:
    """Drive the *call site* the L1 prompt actually uses (``runtime.py:657``).

    The direct reader-B tests bypass ``_build_l1_context_capsule``; this one drives the
    capsule so a change to the call (e.g. a different limit, or dropping ``recent_l1``)
    is measured, not just the helper's behaviour in isolation.
    """
    runtime = SimpleNamespace()
    for i in range(5):
        ev = _event()
        ev.event_id = f"evt-{i}"
        _append_recent_l1_summary(runtime, ev, _observation(), _decision())

    capsule = _build_l1_context_capsule(runtime, {"type": "social.inbox.received"})
    assert "recent_l1" in capsule, "the L1 context capsule no longer carries recent_l1"
    recent = capsule["recent_l1"]

    expected = _compact_recent_l1_for_l1(runtime, limit=3)
    assert recent == expected, (
        "the capsule's recent_l1 does not match the reader driven with the same limit -- "
        "the call site (runtime.py:657) changed its limit or its helper"
    )
    assert len(recent) == 3, (
        f"the capsule carried {len(recent)} recent_l1 rows, not the 3 the L1 prompt expects"
    )


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()
