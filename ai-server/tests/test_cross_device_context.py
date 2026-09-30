"""Cross-device context sharing — the assistant's context follows the user, not the device.

The chat history is one local file shared by every surface, and each entry records the
``source`` that wrote it. This suite pins that the **assistant** uses it that way:

- a conversation is a conversation regardless of which device produced each turn;
- turns of a different conversation never leak into one;
- an entry that cannot be attributed to a conversation is never folded into one;
- with no conversation id, the previous behaviour is unchanged (a recent-turns excerpt
  framed as background only).

Everything here is local: the helpers read the entries they are handed and touch no I/O.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from flask import Flask

from aegis_ai.web.chat_history import (
    UNKNOWN_DEVICE,
    context_excerpt,
    conversation_entries,
    device_label,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _entry(user: str, bot: str, *, conversation_id: str = "", source: str = "") -> dict:
    entry: dict = {"user": user, "bot": bot}
    if conversation_id:
        entry["conversation_id"] = conversation_id
    if source:
        entry["source"] = source
    return entry


# ── The conversation is the unit, not the device ──────────────────────────────


def test_a_turn_from_another_device_is_in_the_same_conversation() -> None:
    """The core claim: dashboard and phone are one conversation, so both turns are returned."""
    entries = [
        _entry("open the report", "opened it", conversation_id="c1", source="dashboard"),
        _entry("now email it", "sending", conversation_id="c1", source="android"),
    ]

    scoped = conversation_entries(entries, conversation_id="c1")

    assert [e["user"] for e in scoped] == ["open the report", "now email it"]


def test_the_excerpt_labels_the_device_each_turn_came_from() -> None:
    """The model must be able to see that the user moved between devices."""
    entries = [
        _entry("open the report", "opened it", conversation_id="c1", source="dashboard"),
        _entry("now email it", "sending", conversation_id="c1", source="android"),
    ]

    excerpt, scope = context_excerpt(entries, conversation_id="c1")

    assert scope == "conversation"
    assert "[dashboard] Past user: open the report" in excerpt
    assert "[android] Past user: now email it" in excerpt


def test_an_entry_with_no_source_is_labelled_not_left_blank() -> None:
    """An unattributed turn must not read as if it came from the current device."""
    assert device_label({}) == UNKNOWN_DEVICE
    assert device_label({"source": "  "}) == UNKNOWN_DEVICE
    assert device_label({"source": "android"}) == "android"

    excerpt, _ = context_excerpt(
        [_entry("hello", "hi", conversation_id="c1")], conversation_id="c1"
    )
    assert f"[{UNKNOWN_DEVICE}] Past user: hello" in excerpt


# ── What must never be included ───────────────────────────────────────────────


def test_turns_of_another_conversation_do_not_leak_in() -> None:
    entries = [
        _entry("secret from c2", "ok", conversation_id="c2", source="dashboard"),
        _entry("mine", "ok", conversation_id="c1", source="android"),
    ]

    scoped = conversation_entries(entries, conversation_id="c1")

    assert [e["user"] for e in scoped] == ["mine"]


def test_an_entry_without_a_conversation_id_is_never_matched() -> None:
    """An entry that cannot be attributed to a conversation is not folded into one.

    This is the fail-closed direction: the dashboard used to write entries with no
    conversation id, and matching on an empty id would have merged *every* such entry into
    whichever conversation asked first.
    """
    entries = [
        _entry("unattributed", "ok", source="dashboard"),
        _entry("attributed", "ok", conversation_id="c1", source="dashboard"),
    ]

    scoped = conversation_entries(entries, conversation_id="c1")

    assert [e["user"] for e in scoped] == ["attributed"]
    assert conversation_entries(entries, conversation_id="") == []


def test_the_excerpt_is_bounded_by_the_limit() -> None:
    entries = [
        _entry(f"turn {index}", "ok", conversation_id="c1", source="android")
        for index in range(10)
    ]

    scoped = conversation_entries(entries, conversation_id="c1", limit=3)

    assert [e["user"] for e in scoped] == ["turn 7", "turn 8", "turn 9"]


# ── The fallback is unchanged behaviour ───────────────────────────────────────


def test_without_a_conversation_id_it_falls_back_to_the_recent_turns() -> None:
    entries = [
        _entry("old", "ok", conversation_id="c1", source="dashboard"),
        _entry("newer", "ok", conversation_id="c2", source="android"),
    ]

    excerpt, scope = context_excerpt(entries)

    assert scope == "recent"
    assert "old" in excerpt and "newer" in excerpt
    # The fallback keeps the original, unlabelled shape.
    assert "[" not in excerpt


def test_an_unknown_conversation_falls_back_rather_than_showing_nothing() -> None:
    """A client that invents a new id every turn still gets continuity, as it did before."""
    entries = [_entry("earlier", "ok", conversation_id="c1", source="dashboard")]

    excerpt, scope = context_excerpt(entries, conversation_id="brand-new")

    assert scope == "recent"
    assert "earlier" in excerpt


def test_the_conversation_scope_wins_when_both_are_possible() -> None:
    entries = [
        _entry("other conversation", "ok", conversation_id="c2", source="dashboard"),
        _entry("mine", "ok", conversation_id="c1", source="android"),
    ]

    excerpt, scope = context_excerpt(entries, conversation_id="c1")

    assert scope == "conversation"
    assert "mine" in excerpt
    assert "other conversation" not in excerpt


# ── The prompt says which of the two it is ────────────────────────────────────


def _prompt_for(monkeypatch, entries: list[dict], *, conversation_id: str = "") -> str:
    from aegis_ai.web import dashboard_legacy, dashboard_routes

    class _MemoryContext:
        text = "memory"

        def audit_detail(self) -> dict:
            return {"memory_profile": "decision"}

    monkeypatch.setattr(
        dashboard_routes, "build_shared_memory_context", lambda **kwargs: _MemoryContext()
    )
    monkeypatch.setattr(dashboard_legacy, "_load_chat_history_entries", lambda: entries)
    monkeypatch.setattr(
        dashboard_routes, "_server_status_context_for_prompt", lambda: "servers ok"
    )

    system_prompt, _, _ = dashboard_routes._build_chat_system_prompt(
        "what next?", conversation_id=conversation_id
    )
    return system_prompt


def test_a_conversation_scoped_prompt_frames_it_as_one_continuous_conversation(monkeypatch) -> None:
    entries = [
        _entry("open the report", "opened it", conversation_id="c1", source="dashboard"),
        _entry("now email it", "sending", conversation_id="c1", source="android"),
    ]

    prompt = _prompt_for(monkeypatch, entries, conversation_id="c1")

    assert "one continuous conversation" in prompt
    assert "[android] Past user: now email it" in prompt
    # The fallback's warning is for a different situation and must not be here.
    assert "Do not continue old tasks" not in prompt


def test_the_fallback_prompt_keeps_the_original_framing(monkeypatch) -> None:
    """The pre-existing behaviour is unchanged when no conversation is named."""
    entries = [_entry("earlier", "ok", conversation_id="c1", source="dashboard")]

    prompt = _prompt_for(monkeypatch, entries)

    assert "Previous conversation excerpt for continuity only" in prompt
    assert "Do not continue old tasks" in prompt
    assert "one continuous conversation" not in prompt


def test_internal_bookkeeping_entries_never_reach_the_prompt(monkeypatch) -> None:
    entries = [
        {"user": "Previous task: open the browser", "bot": "ok", "conversation_id": "c1"},
        _entry("real turn", "ok", conversation_id="c1", source="android"),
    ]

    prompt = _prompt_for(monkeypatch, entries, conversation_id="c1")

    assert "real turn" in prompt
    assert "Previous task:" not in prompt


# ── The dashboard is one device among several ─────────────────────────────────


def _chat_owner(captured: dict) -> object:
    class _Tasks:
        def __init__(self) -> None:
            self.created = 0

        def create_task(self, **kwargs):
            self.created += 1
            return {"task_id": "t1"}

        def start_task(self, task_id: str) -> None:
            pass

        def complete_task(self, task_id: str, **kwargs) -> None:
            pass

        def fail_task(self, task_id: str, **kwargs) -> None:
            pass

    def _append(user_msg, bot_msg, image="", *, source="dashboard", conversation_id=""):
        captured.setdefault("appends", []).append(conversation_id)

    return SimpleNamespace(
        app=Flask(__name__),
        _runtime=SimpleNamespace(
            task_manager=_Tasks(),
            goal_service=None,
            tool_broker=SimpleNamespace(_catalog=object()),
            llm_gateway=object(),
        ),
        _append_chat_history=_append,
        _chat_history_path="unused.jsonl",
    )


def _client_for(monkeypatch, captured: dict, *, conversation_id_seen: dict | None = None):
    from aegis_ai.web.routes.chat import init_chat_routes

    def _prompt(text, *, conversation_id=""):
        if conversation_id_seen is not None:
            conversation_id_seen["value"] = conversation_id
        return "system", {}, text

    monkeypatch.setattr("aegis_ai.web.routes.chat._build_chat_system_prompt", _prompt)
    monkeypatch.setattr(
        "aegis_ai.web.routes.chat._call_llm_with_runtime",
        lambda *_args, **_kwargs: {"response": "ok", "tool_results": []},
    )
    owner = _chat_owner(captured)
    init_chat_routes(owner)
    return owner.app.test_client()


def test_the_dashboard_route_reuses_a_supplied_conversation_id(monkeypatch) -> None:
    """A client that names its conversation joins it — this is what makes the phone and the
    dashboard one context."""
    captured: dict = {}
    seen: dict = {}
    client = _client_for(monkeypatch, captured, conversation_id_seen=seen)

    response = client.post(
        "/api/chat/send", json={"text": "hello", "conversation_id": "phone-conversation"}
    )

    assert response.status_code == 200
    assert seen["value"] == "phone-conversation"
    assert captured["appends"] == ["phone-conversation"]
    assert response.get_json()["conversation_id"] == "phone-conversation"


def test_the_dashboard_mints_a_conversation_when_the_client_names_none(monkeypatch) -> None:
    captured: dict = {}
    client = _client_for(monkeypatch, captured)

    response = client.post("/api/chat/send", json={"text": "hello"})

    minted = response.get_json()["conversation_id"]
    assert minted.startswith("chat_")
    # The history entry carries it too, or the turn would be invisible to the shared context.
    assert captured["appends"] == [minted]


def test_a_pending_question_carries_the_conversation_id(monkeypatch) -> None:
    """The answer must come back into the same conversation, not start a new one."""
    from aegis_ai.web.routes.chat import init_chat_routes

    app = Flask(__name__)
    owner = SimpleNamespace(
        app=app,
        _runtime=SimpleNamespace(
            task_manager=SimpleNamespace(
                create_task=lambda **kwargs: {"task_id": "t1"},
                start_task=lambda *a, **k: None,
                pause_task=lambda *a, **k: None,
                complete_task=lambda *a, **k: None,
                fail_task=lambda *a, **k: None,
            ),
            goal_service=None,
            tool_broker=SimpleNamespace(_catalog=object()),
            llm_gateway=object(),
        ),
        _append_chat_history=lambda *a, **k: None,
        _chat_history_path="unused.jsonl",
    )
    monkeypatch.setattr(
        "aegis_ai.web.routes.chat._build_chat_system_prompt",
        lambda text, **_kwargs: ("system", {}, text),
    )
    monkeypatch.setattr(
        "aegis_ai.web.routes.chat._call_llm_with_runtime",
        lambda *_args, **_kwargs: {
            "response": "",
            "needs_user_input": True,
            "question": "which file?",
            "options": [],
            "pending_context": {},
        },
    )
    init_chat_routes(owner)

    response = app.test_client().post(
        "/api/chat/send", json={"text": "do it", "conversation_id": "c-42"}
    )

    body = response.get_json()
    assert body["needs_user_input"] is True
    assert body["pending_context"]["conversation_id"] == "c-42"


def test_the_chat_service_passes_its_conversation_id_to_the_prompt(monkeypatch) -> None:
    """The shared dashboard/mobile path must scope the prompt to the conversation too."""
    from aegis_ai.web import chat_service

    seen: dict = {}

    def _prompt(text, *, conversation_id=""):
        seen["conversation_id"] = conversation_id
        return "system", {"memory_profile": "decision"}, ""

    monkeypatch.setattr(chat_service, "_build_chat_system_prompt", _prompt)
    monkeypatch.setattr(
        chat_service, "_call_llm_with_runtime", lambda *_a, **_k: {"response": "ok"}
    )
    runtime = SimpleNamespace(
        task_manager=None,
        goal_service=None,
        llm_gateway=object(),
        tool_broker=SimpleNamespace(_catalog=object()),
    )

    chat_service.execute_chat_message(
        runtime,
        "hello",
        origin_channel="android_chat",
        conversation_id="phone-conversation",
    )

    assert seen["conversation_id"] == "phone-conversation"


@pytest.mark.parametrize("conversation_id", ["", "   "])
def test_a_blank_conversation_id_is_treated_as_absent(monkeypatch, conversation_id) -> None:
    """A whitespace id must not become a conversation everything shares."""
    entries = [_entry("x", "y", conversation_id="c1", source="android")]
    excerpt, scope = context_excerpt(entries, conversation_id=conversation_id)
    assert scope == "recent"
    assert "[" not in excerpt
