"""Tests for the confirmation endpoints.

Two things are under test and they are easy to confuse:

* the endpoints serve the **question** — AEGIS's own initiative, rendered for the user;
* the endpoints never **gate** anything — answering one cannot start or unblock an
  action, and nothing in the execution path calls them.

``test_forced_gate_stays_retired.py`` owns the second claim. This module owns the first.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from flask import Flask

from aegis_ai.confirmation import ConfirmationStore
from aegis_ai.web.routes.approval import init_approval_routes


@pytest.fixture()
def store(tmp_path):
    return ConfirmationStore(str(tmp_path))


@pytest.fixture()
def client(store):
    app = Flask(__name__)
    init_approval_routes(SimpleNamespace(app=app, _runtime=SimpleNamespace(confirmation_store=store)))
    return app.test_client()


def _raise(store: ConfirmationStore, **overrides):
    fields = {
        "summary": "Send the revised draft to Sato-san?",
        "capability_id": "mail.send",
        "target": "sato@example.com",
    }
    fields.update(overrides)
    return store.request(**fields)


# ── reads ─────────────────────────────────────────────────────────────────────


def test_pending_lists_open_confirmations_oldest_first(client, store) -> None:
    first = _raise(store, summary="first", created_at=1_000)
    second = _raise(store, summary="second", created_at=2_000)
    answered = _raise(store, summary="answered")
    store.approve(answered.approval_id)

    payload = client.get("/api/approvals/pending").get_json()

    assert payload["pending_count"] == 2
    assert [row["approval_id"] for row in payload["approvals"]] == [first.approval_id, second.approval_id]


def test_pending_is_an_empty_list_when_nothing_was_asked(client) -> None:
    """An empty queue means AEGIS has no question, not that work is blocked."""
    payload = client.get("/api/approvals/pending").get_json()

    assert payload == {"approvals": [], "pending_count": 0}


def test_detail_returns_one_confirmation(client, store) -> None:
    item = _raise(store)

    payload = client.get(f"/api/approvals/{item.approval_id}").get_json()

    assert payload["approval_id"] == item.approval_id
    assert payload["target"] == "sato@example.com"


def test_detail_404s_for_an_unknown_id(client) -> None:
    response = client.get("/api/approvals/cfm_nope")

    assert response.status_code == 404
    assert response.get_json()["error"] == "unknown_confirmation"


# ── decisions ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("path", "expected"),
    [("approve", "approved"), ("reject", "rejected"), ("cancel", "cancelled")],
)
def test_a_decision_is_recorded(client, store, path, expected) -> None:
    item = _raise(store)

    response = client.post(f"/api/approvals/{item.approval_id}/{path}", json={"decided_by": "user"})

    assert response.status_code == 200
    assert response.get_json()["ok"] is True
    assert store.get(item.approval_id).status == expected
    assert store.pending_count() == 0


def test_modify_and_approve_applies_the_users_narrowing(client, store) -> None:
    item = _raise(store)

    response = client.post(
        f"/api/approvals/{item.approval_id}/modify-and-approve",
        json={"edits": {"target": "sato@example.co.jp"}, "note": "cc the team"},
    )

    assert response.status_code == 200
    updated = store.get(item.approval_id)
    assert updated.status == "approved"
    assert updated.target == "sato@example.co.jp"
    assert updated.note == "cc the team"


def test_modify_and_approve_ignores_an_attempt_to_redirect_the_action(client, store) -> None:
    """A decision answers the question; it does not rewrite what AEGIS proposed."""
    item = _raise(store)

    client.post(
        f"/api/approvals/{item.approval_id}/modify-and-approve",
        json={"edits": {"capability_id": "shell.exec"}},
    )

    assert store.get(item.approval_id).capability_id == "mail.send"


def test_a_decision_on_an_unknown_id_is_404(client) -> None:
    response = client.post("/api/approvals/cfm_nope/approve", json={})

    assert response.status_code == 404


def test_a_second_decision_is_409(client, store) -> None:
    """Answering twice would let a stale tab rewrite a settled decision."""
    item = _raise(store)
    client.post(f"/api/approvals/{item.approval_id}/approve", json={})

    response = client.post(f"/api/approvals/{item.approval_id}/reject", json={})

    assert response.status_code == 409
    assert response.get_json()["error"] == "confirmation_not_open"
    assert response.get_json()["status"] == "approved"


def test_a_decision_body_is_optional(client, store) -> None:
    """The shipped client posts ``{}``; that must not be a 400."""
    item = _raise(store)

    response = client.post(f"/api/approvals/{item.approval_id}/approve", json={})

    assert response.status_code == 200


def test_a_malformed_body_does_not_break_a_decision(client, store) -> None:
    item = _raise(store)

    response = client.post(
        f"/api/approvals/{item.approval_id}/approve",
        data="not json at all",
        content_type="application/json",
    )

    assert response.status_code == 200
    assert store.get(item.approval_id).status == "approved"


# ── store unavailable ─────────────────────────────────────────────────────────


def test_reads_report_503_when_the_store_is_missing() -> None:
    """An honest 503, not a fabricated empty queue or a second store."""
    app = Flask(__name__)
    init_approval_routes(SimpleNamespace(app=app, _runtime=SimpleNamespace(confirmation_store=None)))
    client = app.test_client()

    response = client.get("/api/approvals/pending")

    assert response.status_code == 503
    assert response.get_json()["error"] == "confirmation_store_unavailable"


def test_a_decision_reports_503_when_the_store_is_missing() -> None:
    app = Flask(__name__)
    init_approval_routes(SimpleNamespace(app=app, _runtime=SimpleNamespace(confirmation_store=None)))

    response = app.test_client().post("/api/approvals/cfm_x/approve", json={})

    assert response.status_code == 503


# ── server-sent events ────────────────────────────────────────────────────────


def _first_frame(response) -> dict:
    """Read exactly one SSE frame and stop, so the generator is not driven forever."""
    iterator = iter(response.response)
    try:
        chunk = next(iterator)
    finally:
        response.close()
    text = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
    return json.loads(text.removeprefix("data: ").strip())


def test_the_event_stream_greets_the_client(client) -> None:
    response = client.get("/api/approvals/events")

    assert response.status_code == 200
    assert response.mimetype == "text/event-stream"
    assert _first_frame(response)["type"] == "connected"


def test_the_event_stream_pushes_a_raised_confirmation(store) -> None:
    """A client must learn about a new question without polling."""
    app = Flask(__name__)
    init_approval_routes(SimpleNamespace(app=app, _runtime=SimpleNamespace(confirmation_store=store)))
    response = app.test_client().get("/api/approvals/events", buffered=False)

    iterator = iter(response.response)
    try:
        assert json.loads(next(iterator).decode("utf-8").removeprefix("data: ").strip())["type"] == "connected"

        item = _raise(store)
        frame = json.loads(next(iterator).decode("utf-8").removeprefix("data: ").strip())

        assert frame["type"] == "approval.created"
        assert frame["approval"]["approval_id"] == item.approval_id
    finally:
        response.close()


def test_closing_the_stream_removes_its_listener(store) -> None:
    """A closed tab must not leave a listener appending to a queue nobody drains."""
    app = Flask(__name__)
    init_approval_routes(SimpleNamespace(app=app, _runtime=SimpleNamespace(confirmation_store=store)))
    response = app.test_client().get("/api/approvals/events", buffered=False)

    iterator = iter(response.response)
    next(iterator)
    response.close()

    # If the listener leaked, this would still be delivered to a dead generator.
    assert store._listeners == []  # noqa: SLF001 - the leak is exactly what is under test


# ── the central auth regime still covers these paths ──────────────────────────


@pytest.mark.parametrize(
    "path",
    [
        "/api/approvals/cfm_x/approve",
        "/api/approvals/cfm_x/reject",
        "/api/approvals/cfm_x/cancel",
        "/api/approvals/cfm_x/modify-and-approve",
    ],
)
def test_decisions_stay_under_the_central_csrf_regime(path: str) -> None:
    """These routes do not implement CSRF themselves — ``session_middleware`` does.

    That is deliberate: one implementation cannot drift from itself. This test pins
    that the paths remain inside it, so moving a route outside the regime is caught.
    """
    from aegis_ai.auth.session_middleware import _csrf_required

    with Flask(__name__).test_request_context(path, method="POST"):
        assert _csrf_required(path) is True


@pytest.mark.parametrize(
    "path",
    [
        "/api/approvals/cfm_x/approve",
        "/api/approvals/cfm_x/cancel",
        "/api/approvals/cfm_x/modify-and-approve",
    ],
)
def test_answering_still_requires_a_fresh_passkey(path: str) -> None:
    """Phase 5a did not change the authentication regime — pin that it did not.

    A confirmation is AEGIS's own question, so the *fresh-auth* requirement here is
    about proving the person answering is the user, not about gating a capability.
    Whether that ceremony is proportionate for a question that blocks nothing is an
    open question for the owner; this test only records that nothing was changed by
    accident.
    """
    from aegis_ai.auth.session_middleware import _fresh_required

    with Flask(__name__).test_request_context(path, method="POST"):
        assert _fresh_required(path) is True
