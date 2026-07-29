from __future__ import annotations

from types import SimpleNamespace

from flask import Flask

from aegis_ai.web.routes.chat import init_chat_routes


class _Tasks:
    def __init__(self) -> None:
        self.created = 0

    def create_task(self, **_kwargs):
        self.created += 1
        return {"task_id": f"task-{self.created}"}

    def start_task(self, _task_id):
        return None

    def complete_task(self, _task_id, **_kwargs):
        return None

    def fail_task(self, _task_id, **_kwargs):
        return None


def test_chat_request_id_prevents_duplicate_execution(monkeypatch) -> None:
    app = Flask(__name__)
    tasks = _Tasks()
    owner = SimpleNamespace(
        app=app,
        _runtime=SimpleNamespace(
            task_manager=tasks,
            goal_service=None,
            tool_broker=SimpleNamespace(_catalog=object()),
            llm_gateway=object(),
        ),
        _append_chat_history=lambda *_args: None,
        _chat_history_path="unused.jsonl",
    )
    calls = []
    monkeypatch.setattr(
        "aegis_ai.web.routes.chat._build_chat_system_prompt",
        lambda text: ("system", {}, text),
    )
    monkeypatch.setattr(
        "aegis_ai.web.routes.chat._call_llm_with_runtime",
        lambda *_args, **_kwargs: calls.append("called") or {"response": "ok", "tool_results": []},
    )
    init_chat_routes(owner)
    client = app.test_client()

    first = client.post("/api/chat/send", json={"text": "hello", "request_id": "same-id"})
    second = client.post("/api/chat/send", json={"text": "hello", "request_id": "same-id"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.get_json() == second.get_json()
    assert calls == ["called"]
    assert tasks.created == 1


def test_chat_accepts_legacy_message_field(monkeypatch) -> None:
    app = Flask(__name__)
    tasks = _Tasks()
    owner = SimpleNamespace(
        app=app,
        _runtime=SimpleNamespace(
            task_manager=tasks,
            goal_service=None,
            tool_broker=SimpleNamespace(_catalog=object()),
            llm_gateway=object(),
        ),
        _append_chat_history=lambda *_args: None,
        _chat_history_path="unused.jsonl",
    )
    monkeypatch.setattr("aegis_ai.web.routes.chat._build_chat_system_prompt", lambda text: ("system", {}, text))
    monkeypatch.setattr(
        "aegis_ai.web.routes.chat._call_llm_with_runtime",
        lambda *_args, **_kwargs: {"response": "ok", "tool_results": []},
    )
    init_chat_routes(owner)

    response = app.test_client().post("/api/chat/send", json={"message": "legacy"})
    assert response.status_code == 200
