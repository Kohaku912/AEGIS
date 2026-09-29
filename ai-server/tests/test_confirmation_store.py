"""Tests for the AEGIS-initiated confirmation store.

What is under test is a *question*, not a gate. The store records what AEGIS chose to
ask and what the user answered; it has no authority over execution. The tests below
therefore pin the store's own semantics, and ``test_forced_gate_stays_retired.py``
separately pins that nothing blocks a capability on it.
"""

from __future__ import annotations

import json
import threading

import pytest

from aegis_ai.confirmation import (
    EVENT_CREATED,
    EVENT_RESOLVED,
    ConfirmationRequest,
    ConfirmationStatus,
    ConfirmationStore,
    new_confirmation_id,
)
from aegis_ai.confirmation.store import USER_EDITABLE_FIELDS


@pytest.fixture()
def store(tmp_path):
    return ConfirmationStore(str(tmp_path))


def _raise(store: ConfirmationStore, **overrides) -> ConfirmationRequest:
    fields = {
        "summary": "Send the revised draft to Sato-san?",
        "capability_id": "mail.send",
        "target": "sato@example.com",
    }
    fields.update(overrides)
    return store.request(**fields)


# ── creation ──────────────────────────────────────────────────────────────────


def test_request_returns_an_open_confirmation(store) -> None:
    item = _raise(store)

    assert item.approval_id.startswith("cfm_")
    assert item.status == ConfirmationStatus.PENDING.value
    assert item.is_open
    assert store.pending_count() == 1


def test_request_never_waits_for_an_answer(store) -> None:
    """The defining difference from the retired gate.

    ``request()`` returns a live, unanswered question. If it ever grew a wait, this test
    would hang rather than fail — so the assertion is on a watchdog thread instead.
    """
    done = threading.Event()
    result: list[ConfirmationRequest] = []

    def _call() -> None:
        result.append(_raise(store))
        done.set()

    worker = threading.Thread(target=_call, daemon=True)
    worker.start()
    assert done.wait(timeout=5), "ConfirmationStore.request() blocked; it must never wait"

    item = result[0]
    assert item.is_open
    assert store.get(item.approval_id).is_open


def test_request_returns_a_snapshot_not_the_live_object(store) -> None:
    """Every read is a copy, so a caller cannot mutate the store without persistence."""
    item = _raise(store)

    item.status = ConfirmationStatus.APPROVED.value

    assert store.get(item.approval_id).is_open


def test_default_ttl_is_applied_and_explicit_ttl_is_respected(store) -> None:
    defaulted = _raise(store)
    assert defaulted.expires_at is not None
    # Non-vacuity: the assertion above only means something if the TTL is positive.
    assert defaulted.expires_at > defaulted.created_at

    explicit = _raise(store, created_at=1_000, expires_at=1_005)
    assert explicit.expires_at == 1_005


def test_ids_are_unique(store) -> None:
    ids = {_raise(store).approval_id for _ in range(200)}
    assert len(ids) == 200


def test_creation_emits_a_created_event(store) -> None:
    seen: list[tuple[str, str]] = []
    store.add_listener(lambda event, item: seen.append((event, item.approval_id)))

    item = _raise(store)

    assert seen == [(EVENT_CREATED, item.approval_id)]


# ── decisions ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("approve", ConfirmationStatus.APPROVED),
        ("reject", ConfirmationStatus.REJECTED),
        ("cancel", ConfirmationStatus.CANCELLED),
    ],
)
def test_each_decision_moves_the_request_and_records_who_and_when(store, method, expected) -> None:
    item = _raise(store)

    resolved = getattr(store, method)(item.approval_id, decided_by="user", note="because")

    assert resolved is not None
    assert resolved.status == expected.value
    assert resolved.decided_by == "user"
    assert resolved.note == "because"
    assert resolved.resolved_at is not None
    assert store.pending_count() == 0


def test_an_answered_question_cannot_be_answered_again(store) -> None:
    """A stale dashboard tab must not rewrite a decision the user has moved on from."""
    item = _raise(store)
    store.approve(item.approval_id, decided_by="user")

    assert store.reject(item.approval_id) is None
    assert store.get(item.approval_id).status == ConfirmationStatus.APPROVED.value


def test_resolving_an_unknown_id_is_a_no_op(store) -> None:
    assert store.approve("cfm_does_not_exist") is None


def test_resolution_emits_a_resolved_event(store) -> None:
    seen: list[str] = []
    store.add_listener(lambda event, item: seen.append(event))
    item = _raise(store)

    store.approve(item.approval_id)

    assert seen == [EVENT_CREATED, EVENT_RESOLVED]


# ── "yes, but like this" ──────────────────────────────────────────────────────


def test_modify_and_approve_narrows_the_description(store) -> None:
    item = _raise(store)

    edited = store.modify_and_approve(
        item.approval_id,
        edits={"target": "sato@example.co.jp", "preview": "shorter"},
        decided_by="user",
    )

    assert edited is not None
    assert edited.target == "sato@example.co.jp"
    assert edited.preview == "shorter"
    assert edited.status == ConfirmationStatus.APPROVED.value


def test_modify_and_approve_cannot_rewrite_what_aegis_proposed(store) -> None:
    """The user narrows the description; they do not redirect the action.

    If ``capability_id`` were editable, answering "yes" could make AEGIS run something
    it never reasoned about — which is the failure mode this whitelist exists to stop.
    """
    item = _raise(store)

    edited = store.modify_and_approve(
        item.approval_id,
        edits={"capability_id": "shell.exec", "tool_name": "rm", "approval_id": "cfm_other"},
        decided_by="user",
    )

    assert edited.capability_id == "mail.send"
    assert edited.tool_name == ""
    assert edited.approval_id == item.approval_id


def test_the_decision_note_wins_over_an_edit_to_note(store) -> None:
    """``note`` has exactly one source. It is deliberately not in the editable set."""
    assert "note" not in USER_EDITABLE_FIELDS
    item = _raise(store)

    edited = store.modify_and_approve(
        item.approval_id,
        edits={"note": "from the edit payload"},
        decided_by="user",
        note="the decision note",
    )

    assert edited.note == "the decision note"


def test_modify_and_approve_refuses_an_answered_question(store) -> None:
    item = _raise(store)
    store.approve(item.approval_id)

    assert store.modify_and_approve(item.approval_id, edits={"target": "x"}) is None


# ── outcome reporting ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("method", "expected"),
    [("mark_executed", ConfirmationStatus.EXECUTED), ("mark_failed", ConfirmationStatus.FAILED)],
)
def test_outcome_is_reported_for_an_approved_request(store, method, expected) -> None:
    item = _raise(store)
    store.approve(item.approval_id, decided_by="user")

    settled = getattr(store, method)(item.approval_id, note="done")

    assert settled is not None
    assert settled.status == expected.value
    assert settled.note == "done"


def test_outcome_cannot_be_reported_for_an_unanswered_request(store) -> None:
    """APPROVED -> EXECUTED is a report about the action, not a way to skip the answer."""
    item = _raise(store)

    assert store.mark_executed(item.approval_id) is None
    assert store.get(item.approval_id).is_open


def test_outcome_requires_approval_not_merely_a_decision(store) -> None:
    """The guard is APPROVED, not "any decided status".

    If a rejected request could reach EXECUTED, the record would say AEGIS carried out
    the very thing the user declined.
    """
    item = _raise(store)
    store.reject(item.approval_id)

    assert store.mark_executed(item.approval_id) is None
    assert store.mark_failed(item.approval_id) is None
    assert store.get(item.approval_id).status == ConfirmationStatus.REJECTED.value


def test_outcome_cannot_be_settled_twice(store) -> None:
    item = _raise(store)
    store.approve(item.approval_id)

    assert store.mark_executed(item.approval_id) is not None
    assert store.mark_failed(item.approval_id) is None
    assert store.get(item.approval_id).status == ConfirmationStatus.EXECUTED.value


# ── expiry ────────────────────────────────────────────────────────────────────


def test_expire_stale_lapses_only_questions_past_their_deadline(store) -> None:
    stale = store.request(summary="stale", capability_id="a.b", created_at=1_000, expires_at=2_000)
    fresh = store.request(summary="fresh", capability_id="a.b", created_at=1_000, expires_at=9_000)

    expired = store.expire_stale(moment_ms=3_000)

    assert [item.approval_id for item in expired] == [stale.approval_id]
    assert store.get(stale.approval_id).status == ConfirmationStatus.EXPIRED.value
    assert store.get(fresh.approval_id).is_open


def test_expiry_is_idempotent(store) -> None:
    item = _raise(store, created_at=1_000, expires_at=2_000)

    assert len(store.expire_stale(moment_ms=3_000)) == 1
    assert store.expire_stale(moment_ms=3_000) == []


def test_expiry_leaves_decided_requests_alone(store) -> None:
    item = _raise(store, created_at=1_000, expires_at=2_000)
    store.approve(item.approval_id, decided_by="user")

    assert store.expire_stale(moment_ms=3_000) == []
    assert store.get(item.approval_id).status == ConfirmationStatus.APPROVED.value


# ── reads ─────────────────────────────────────────────────────────────────────


def test_pending_is_oldest_first_regardless_of_insertion_order(store) -> None:
    second = _raise(store, summary="second", created_at=2_000)
    first = _raise(store, summary="first", created_at=1_000)

    assert [item.approval_id for item in store.pending()] == [first.approval_id, second.approval_id]


def test_pending_excludes_answered_questions(store) -> None:
    kept = _raise(store)
    answered = _raise(store)
    store.approve(answered.approval_id)

    assert [item.approval_id for item in store.pending()] == [kept.approval_id]


def test_all_is_newest_first_and_capped(store) -> None:
    oldest = _raise(store, created_at=1_000)
    newest = _raise(store, created_at=2_000)

    assert [item.approval_id for item in store.all()] == [newest.approval_id, oldest.approval_id]
    assert len(store.all(limit=1)) == 1


def test_get_returns_a_copy_not_the_live_object(store) -> None:
    """Callers must not be able to mutate the store by holding a reference."""
    item = _raise(store)

    store.get(item.approval_id).status = ConfirmationStatus.APPROVED.value

    assert store.get(item.approval_id).is_open


def test_clear_removes_everything(store) -> None:
    _raise(store)

    store.clear()

    assert store.all() == []
    assert store.pending_count() == 0


# ── persistence ───────────────────────────────────────────────────────────────


def test_state_survives_a_restart(tmp_path) -> None:
    first = ConfirmationStore(str(tmp_path))
    item = _raise(first)
    first.approve(item.approval_id, decided_by="user")

    reopened = ConfirmationStore(str(tmp_path))

    assert reopened.get(item.approval_id).status == ConfirmationStatus.APPROVED.value
    assert reopened.get(item.approval_id).decided_by == "user"


def test_last_write_wins_for_a_repeated_id(tmp_path) -> None:
    """Append-only persistence: the newest line for an id is the truth."""
    first = ConfirmationStore(str(tmp_path))
    item = _raise(first)
    first.approve(item.approval_id)
    first.mark_executed(item.approval_id, note="carried out")

    reopened = ConfirmationStore(str(tmp_path))

    assert reopened.get(item.approval_id).status == ConfirmationStatus.EXECUTED.value
    assert reopened.get(item.approval_id).note == "carried out"


def test_a_torn_final_line_is_skipped_without_losing_history(tmp_path) -> None:
    first = ConfirmationStore(str(tmp_path))
    _raise(first, summary="one")
    _raise(first, summary="two")

    path = tmp_path / "confirmation" / "confirmations.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"approval_id": "cfm_truncated", "summ')

    reopened = ConfirmationStore(str(tmp_path))

    assert len(reopened.all()) == 2


def test_persistence_is_append_only_so_an_edit_keeps_the_original(tmp_path) -> None:
    """The agreed version is live; the JSONL still holds what AEGIS first proposed."""
    first = ConfirmationStore(str(tmp_path))
    item = _raise(first)
    first.modify_and_approve(item.approval_id, edits={"target": "narrowed@example.com"})

    lines = [
        json.loads(line)
        for line in (tmp_path / "confirmation" / "confirmations.jsonl").read_text("utf-8").splitlines()
    ]
    targets = [line["target"] for line in lines if line.get("approval_id") == item.approval_id]

    assert targets == ["sato@example.com", "narrowed@example.com"]


def test_an_unwritable_data_dir_does_not_lose_the_live_request(tmp_path) -> None:
    """Losing the on-disk history must not lose the question the user still has to answer.

    The unwritable case is produced for real rather than mocked: ``tmp_path`` holds a
    regular file, so ``mkdir(parents=True)`` under it raises ``NotADirectoryError``.
    """
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("this is a file, not a directory", encoding="utf-8")
    store = ConfirmationStore(str(blocker / "data"))

    item = store.request(summary="still answerable", capability_id="mail.send")

    assert store.get(item.approval_id).is_open
    assert store.pending_count() == 1
    assert store.approve(item.approval_id, decided_by="user") is not None


# ── listeners ─────────────────────────────────────────────────────────────────


def test_unsubscribe_stops_delivery(store) -> None:
    seen: list[str] = []
    unsubscribe = store.add_listener(lambda event, item: seen.append(event))
    _raise(store)

    unsubscribe()
    _raise(store)

    assert seen == [EVENT_CREATED]


def test_unsubscribe_is_idempotent(store) -> None:
    unsubscribe = store.add_listener(lambda event, item: None)

    unsubscribe()
    unsubscribe()  # must not raise


def test_a_broken_listener_does_not_break_the_store_or_its_siblings(store) -> None:
    """One dead SSE client must not stop the others from being notified."""
    seen: list[str] = []

    def _explode(event, item) -> None:
        raise RuntimeError("stream closed")

    store.add_listener(_explode)
    store.add_listener(lambda event, item: seen.append(event))

    item = _raise(store)

    assert seen == [EVENT_CREATED]
    assert store.get(item.approval_id).is_open


# ── the model ─────────────────────────────────────────────────────────────────


def test_from_dict_ignores_unknown_keys() -> None:
    """Old records must still load after the model grows or shrinks."""
    request = ConfirmationRequest.from_dict(
        {"approval_id": "cfm_x", "summary": "s", "a_field_that_never_existed": 1}
    )

    assert request.approval_id == "cfm_x"
    assert request.summary == "s"


def test_is_expired_at_handles_a_missing_deadline() -> None:
    assert not ConfirmationRequest(approval_id="cfm_x").is_expired_at(2**62)


def test_new_confirmation_id_is_prefixed() -> None:
    """The prefix keeps a confirmation distinguishable from a retired approval."""
    assert new_confirmation_id().startswith("cfm_")
