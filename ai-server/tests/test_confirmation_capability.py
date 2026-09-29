"""Tests for the LLM-callable confirmation capability.

``ai-server.confirmation.request`` is how AEGIS raises a question on its own
initiative, and ``ai-server.confirmation.list`` is how it learns the answer. Together
they are the "AEGIS asks" half of the interruption design; the dashboard is the "user
answers" half.

What these tests pin:

* the capability is discoverable and declares itself harmless — a manifest that said
  ``requires_approval`` would put it back inside the retired gate's machinery;
* raising a question never blocks and never reports an effect on the current task;
* the answer is readable, because a question whose answer is unreadable is theatre.
"""

from __future__ import annotations

import threading

import pytest

from aegis_ai.confirmation import ConfirmationStore
from aegis_ai.core_capabilities import AegisCoreCapabilityClient
from aegis_ai.folder_registry import FolderCapabilityRegistry

REQUEST = "ai-server.confirmation.request"
LIST = "ai-server.confirmation.list"


@pytest.fixture()
def store(tmp_path):
    return ConfirmationStore(str(tmp_path))


@pytest.fixture()
def client(store, tmp_path):
    return AegisCoreCapabilityClient(
        data_dir=str(tmp_path),
        server_executor=None,
        personal_managers={"confirmation_store": store},
    )


# ── the manifest ──────────────────────────────────────────────────────────────


def test_both_capabilities_are_registered() -> None:
    from pathlib import Path

    registry = FolderCapabilityRegistry(str(Path(__file__).resolve().parents[1] / "capabilities"))

    assert registry.errors() == []
    for capability_id in (REQUEST, LIST):
        assert registry.get(capability_id) is not None, f"{capability_id} is not registered"


@pytest.mark.parametrize("capability_id", [REQUEST, LIST])
def test_the_manifest_does_not_re_enter_the_gate(capability_id: str) -> None:
    """``requires_approval`` must stay false and the capability fully reversible.

    If either flipped, the retired rule that reads ``requires_approval`` would start
    forcing a confirmation in order to *raise* a confirmation.
    """
    from pathlib import Path

    registry = FolderCapabilityRegistry(str(Path(__file__).resolve().parents[1] / "capabilities"))
    manifest = registry.get(capability_id)

    assert manifest.requires_approval is False
    assert manifest.reversibility == "fully_reversible"
    assert manifest.destructive_effects == []


# ── raising a question ────────────────────────────────────────────────────────


def test_request_records_a_question_visible_to_the_store_and_the_dashboard(client, store) -> None:
    result = client.invoke_capability(
        REQUEST,
        {
            "summary": "Send the revised draft to Sato-san?",
            "reason": "The draft states a delivery date I inferred, not one you confirmed.",
            "capability_id": "mail.send",
            "target": "sato@example.com",
        },
    )

    assert result["ok"] is True
    assert result["approval_id"].startswith("cfm_")
    assert result["status"] == "pending"

    stored = store.get(result["approval_id"])
    assert stored.summary == "Send the revised draft to Sato-san?"
    assert stored.capability_id == "mail.send"
    assert stored.target == "sato@example.com"
    assert store.pending_count() == 1


def test_raising_a_question_never_waits_for_an_answer(client) -> None:
    """The capability must not become a blocking call.

    A watchdog rather than a timing assertion: if ``request`` ever grew a wait, this
    would hang instead of failing.
    """
    done = threading.Event()
    results: list[dict] = []

    def _call() -> None:
        results.append(client.invoke_capability(REQUEST, {"summary": "Still there?"}))
        done.set()

    worker = threading.Thread(target=_call, daemon=True)
    worker.start()

    assert done.wait(timeout=5), "confirmation.request blocked; it must never wait"
    assert results[0]["ok"] is True


def test_raising_a_question_declares_no_effect_on_the_current_task(client) -> None:
    """``task_effect_hint`` tells the caller whether to keep going.

    ``no_effect`` is the honest answer and the load-bearing one: it says "carry on",
    which is the opposite of the retired gate's "stop and wait".
    """
    result = client.invoke_capability(REQUEST, {"summary": "Proceed?"})

    assert result["task_effect_hint"] == "no_effect"


def test_a_question_without_a_summary_is_refused_and_records_nothing(client, store) -> None:
    result = client.invoke_capability(REQUEST, {"reason": "I am unsure."})

    assert result["ok"] is False
    assert "summary" in result["error"]
    assert store.pending_count() == 0


def test_a_bad_deadline_is_refused_and_records_nothing(client, store) -> None:
    result = client.invoke_capability(REQUEST, {"summary": "Proceed?", "expires_at": "tomorrow"})

    assert result["ok"] is False
    assert "epoch milliseconds" in result["error"]
    assert store.pending_count() == 0


def test_an_explicit_deadline_is_honoured(client, store) -> None:
    result = client.invoke_capability(
        REQUEST, {"summary": "Proceed?", "expires_at": 4_000_000_000_000}
    )

    assert store.get(result["approval_id"]).expires_at == 4_000_000_000_000


def test_blank_optional_fields_are_dropped_not_stored_as_empty_strings(client, store) -> None:
    result = client.invoke_capability(REQUEST, {"summary": "Proceed?", "target": "", "risk": None})

    stored = store.get(result["approval_id"])
    assert stored.target == ""
    assert stored.risk == ""


def test_raising_a_question_without_a_store_fails_cleanly(tmp_path) -> None:
    client = AegisCoreCapabilityClient(data_dir=str(tmp_path), server_executor=None)

    result = client.invoke_capability(REQUEST, {"summary": "Proceed?"})

    assert result["ok"] is False
    assert "ConfirmationStore unavailable" in result["error"]


# ── reading the answer ────────────────────────────────────────────────────────


def test_list_defaults_to_the_open_questions(client, store) -> None:
    kept = client.invoke_capability(REQUEST, {"summary": "First?"})
    answered = client.invoke_capability(REQUEST, {"summary": "Second?"})
    store.approve(answered["approval_id"], decided_by="user")

    result = client.invoke_capability(LIST, {})

    assert result["ok"] is True
    assert result["status"] == "pending"
    assert [c["approval_id"] for c in result["confirmations"]] == [kept["approval_id"]]


def test_list_reports_the_users_answer(client, store) -> None:
    """A question whose answer AEGIS cannot read would be theatre."""
    raised = client.invoke_capability(REQUEST, {"summary": "Send it?"})
    store.approve(raised["approval_id"], decided_by="user", note="go ahead")

    result = client.invoke_capability(LIST, {"status": "approved"})

    assert result["count"] == 1
    assert result["confirmations"][0]["status"] == "approved"
    assert result["confirmations"][0]["decided_by"] == "user"
    assert result["confirmations"][0]["note"] == "go ahead"


def test_list_filters_by_status(client, store) -> None:
    kept = client.invoke_capability(REQUEST, {"summary": "Kept?"})
    rejected = client.invoke_capability(REQUEST, {"summary": "Rejected?"})
    store.reject(rejected["approval_id"], decided_by="user")

    pending = client.invoke_capability(LIST, {})
    rejected_only = client.invoke_capability(LIST, {"status": "rejected"})
    everything = client.invoke_capability(LIST, {"status": "any"})

    assert [c["approval_id"] for c in pending["confirmations"]] == [kept["approval_id"]]
    assert [c["approval_id"] for c in rejected_only["confirmations"]] == [rejected["approval_id"]]
    assert everything["count"] == 2


def test_list_returns_one_question_by_id(client) -> None:
    raised = client.invoke_capability(REQUEST, {"summary": "Which one?"})

    result = client.invoke_capability(LIST, {"approval_id": raised["approval_id"]})

    assert result["confirmation"]["summary"] == "Which one?"


def test_list_reports_an_unknown_id(client) -> None:
    result = client.invoke_capability(LIST, {"approval_id": "cfm_nope"})

    assert result["ok"] is False
    assert "unknown confirmation" in result["error"]


@pytest.mark.parametrize(("given", "expected"), [("0", 1), ("-5", 1), ("5000", 100), ("abc", 20)])
def test_list_clamps_a_silly_limit(client, given, expected) -> None:
    """The limit must never turn into an unbounded read or a crash."""
    for index in range(3):
        client.invoke_capability(REQUEST, {"summary": f"Question {index}"})

    result = client.invoke_capability(LIST, {"limit": given})

    assert result["ok"] is True
    assert len(result["confirmations"]) <= expected


def test_an_unknown_confirmation_capability_is_reported(client) -> None:
    result = client.invoke_capability("ai-server.confirmation.teleport", {})

    assert result["ok"] is False
    assert "Unsupported confirmation capability" in result["error"]


# ── the LLM can see them ──────────────────────────────────────────────────────


def test_the_capabilities_are_offered_to_the_llm() -> None:
    """Discoverable by the catalog, or the LLM cannot choose to ask."""
    from pathlib import Path

    from aegis_ai.capability_catalog import CapabilityCatalog

    catalog = CapabilityCatalog(str(Path(__file__).resolve().parents[1] / "capabilities"))
    offered = {item["id"] for item in catalog.list_for_llm()}

    assert REQUEST in offered
    assert LIST in offered
