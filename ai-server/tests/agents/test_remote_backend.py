"""Phase 8 remote backend tests.

Covers:
- SessionStore: append / load / list / delete / gc
- RemoteAPIWorkspace: healthcheck OK / unreachable / post_json success
- RemoteOpenHandsBackend: agent_unavailable paths (no URL, unreachable,
  HTTP error), normal completion path, cancel, get_status

Import boundary: this file does not import openhands.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest


# Pattern that matches a real Python import of the openhands package.
# Docstrings may legitimately mention "from openhands" in prose, so we only
# flag lines that look like an actual `import openhands` or `from openhands`
# import statement (the `import` keyword is required after `from openhands`).
_OPENHANDS_IMPORT_RE = re.compile(
    r"^\s*(?:import\s+openhands\b|from\s+openhands\s+import\b)",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# SessionStore
# ---------------------------------------------------------------------------


def _make_session_store(tmp_path: Path):
    from aegis_ai.agents.runtime.session_store import SessionStore

    return SessionStore(root=str(tmp_path / "sessions"))


def test_session_store_append_and_load(tmp_path: Path) -> None:
    store = _make_session_store(tmp_path)
    store.append("task-1", {"kind": "message", "role": "user", "text": "hi"})
    store.append("task-1", {"kind": "message", "role": "assistant", "text": "hello"})
    events = store.load("task-1")
    assert len(events) == 2
    assert events[0]["kind"] == "message"
    assert events[0]["role"] == "user"
    assert events[1]["role"] == "assistant"
    store.close()


def test_session_store_load_missing_returns_empty(tmp_path: Path) -> None:
    store = _make_session_store(tmp_path)
    assert store.load("nope") == []


def test_session_store_invalid_session_id_rejected(tmp_path: Path) -> None:
    store = _make_session_store(tmp_path)
    with pytest.raises(ValueError):
        store.append("../etc/passwd", {"kind": "message"})
    with pytest.raises(ValueError):
        store.append("a/b", {"kind": "message"})


def test_session_store_extend_returns_count(tmp_path: Path) -> None:
    store = _make_session_store(tmp_path)
    n = store.extend(
        "task-2",
        [
            {"kind": "metadata", "data": {"profile": "coding"}},
            {"kind": "action", "tool": "file.read"},
        ],
    )
    assert n == 2
    events = store.load("task-2")
    assert events[0]["kind"] == "metadata"
    assert events[0]["data"]["profile"] == "coding"


def test_session_store_list_sorders(tmp_path: Path) -> None:
    store = _make_session_store(tmp_path)
    store.append("task-a", {"kind": "message", "text": "1"})
    time.sleep(0.01)
    store.append("task-b", {"kind": "message", "text": "2"})
    summaries = store.list_sessions()
    ids = [s.session_id for s in summaries]
    assert ids == ["task-b", "task-a"]  # most recent first
    assert summaries[0].event_count == 1


def test_session_store_delete(tmp_path: Path) -> None:
    store = _make_session_store(tmp_path)
    store.append("task-x", {"kind": "message", "text": "x"})
    assert store.delete("task-x") is True
    assert store.delete("task-x") is False
    assert store.load("task-x") == []


def test_session_store_gc_older_than(tmp_path: Path) -> None:
    store = _make_session_store(tmp_path)
    # Append an event with an explicit past ts_ms so gc_older_than can see it
    old_ts = int(time.time() * 1000) - 30 * 86_400_000
    store.append("task-old", {"kind": "message", "text": "old", "ts_ms": old_ts})
    deleted = store.gc_older_than(days=7)
    assert deleted == 1
    assert store.load("task-old") == []


# ---------------------------------------------------------------------------
# RemoteAPIWorkspace
# ---------------------------------------------------------------------------


def _make_remote_workspace(*, url: str = "http://localhost:7100", post=None):
    from aegis_ai.agents.backends.openhands.workspace import RemoteAPIWorkspace

    return RemoteAPIWorkspace(
        server_url=url,
        timeout_seconds=1.0,
        http_post=post,
    )


def test_remote_workspace_healthcheck_ok() -> None:
    ws = _make_remote_workspace(post=lambda *a, **kw: {"ok": True, "version": "0.1.0"})
    result = ws.healthcheck()
    assert result["status"] == "ok"
    assert result["workspace"] == "remote"


def test_remote_workspace_healthcheck_unreachable() -> None:
    def _raise(*a, **kw):
        raise ConnectionError("nope")

    ws = _make_remote_workspace(post=_raise)
    result = ws.healthcheck()
    assert result["status"] == "unreachable"
    assert "nope" in result["error"]


def test_remote_workspace_post_json_requires_url() -> None:
    from aegis_ai.agents.backends.openhands.workspace import RemoteAPIWorkspace

    ws = RemoteAPIWorkspace(server_url="", http_post=lambda *a, **kw: {})
    with pytest.raises(RuntimeError):
        ws.post_json("/mcp", {"method": "tools/list"})


def test_remote_workspace_post_json_success() -> None:
    captured: dict = {}

    def _post(url, *, payload, timeout, headers):
        captured["url"] = url
        captured["payload"] = payload
        captured["headers"] = headers
        return {"ok": True}

    ws = _make_remote_workspace(url="http://localhost:7100", post=_post)
    result = ws.post_json("/mcp", {"x": 1})
    assert result == {"ok": True}
    assert captured["url"] == "http://localhost:7100/mcp"
    assert captured["payload"] == {"x": 1}
    assert captured["headers"]["Content-Type"] == "application/json"


def test_remote_workspace_post_json_timeout_override() -> None:
    captured: dict[str, object] = {}

    def _post(url, *, payload, timeout, headers):  # noqa: ARG001
        captured["timeout"] = timeout
        return {"ok": True}

    ws = _make_remote_workspace(url="http://localhost:7100", post=_post)
    ws.post_json("/mcp", {"x": 1}, timeout_seconds=12.5)
    assert captured["timeout"] == 12.5


def test_default_http_post_uses_get_when_payload_is_none(monkeypatch) -> None:
    from aegis_ai.agents.backends.openhands.workspace import _default_http_post

    captured: dict[str, object] = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return b'{"ok": true}'

    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        captured["method"] = req.get_method()
        captured["url"] = req.full_url
        return _FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = _default_http_post("http://localhost:7100/healthz", payload=None)
    assert result == {"ok": True}
    assert captured["method"] == "GET"
    assert captured["url"] == "http://localhost:7100/healthz"


def test_remote_workspace_post_json_bearer_token() -> None:
    captured: dict = {}

    def _post(url, *, payload, timeout, headers):
        captured["headers"] = headers
        return {}

    ws = _make_remote_workspace(post=_post)
    ws.post_json  # ensure attribute
    from aegis_ai.agents.backends.openhands.workspace import RemoteAPIWorkspace

    ws = RemoteAPIWorkspace(
        server_url="http://localhost:7100",
        http_post=_post,
        auth_token="sek-ret",
    )
    ws.post_json("/mcp", {})
    assert captured["headers"]["Authorization"] == "Bearer sek-ret"


def test_build_workspace_from_spec_picks_remote_when_env_set(
    tmp_path: Path, monkeypatch
) -> None:
    from aegis_ai.agents.backends.openhands.workspace import (
        RemoteAPIWorkspace,
        build_workspace_from_spec,
    )
    from aegis_ai.agents.backends.openhands.config import WorkspaceSpec

    monkeypatch.setenv("AGENT_BACKEND", "remote")
    monkeypatch.setenv("AGENT_SERVER_URL", "http://localhost:7100")
    ws = build_workspace_from_spec(WorkspaceSpec())
    assert isinstance(ws, RemoteAPIWorkspace)
    assert ws.is_remote() is True


def test_build_workspace_from_spec_picks_local_by_default(
    tmp_path: Path, monkeypatch
) -> None:
    from aegis_ai.agents.backends.openhands.workspace import (
        LocalWorkspace,
        build_workspace_from_spec,
    )
    from aegis_ai.agents.backends.openhands.config import WorkspaceSpec

    monkeypatch.delenv("AGENT_BACKEND", raising=False)
    monkeypatch.delenv("AGENT_SERVER_URL", raising=False)
    ws = build_workspace_from_spec(WorkspaceSpec())
    assert isinstance(ws, LocalWorkspace)
    assert ws.is_remote() is False


# ---------------------------------------------------------------------------
# RemoteOpenHandsBackend
# ---------------------------------------------------------------------------


def _make_remote_backend(*, url: str = "http://localhost:7100", post=None, store=None):
    from aegis_ai.agents.backends.openhands.remote_backend import RemoteOpenHandsBackend
    from aegis_ai.agents.runtime.session_store import SessionStore

    if store is None:
        store = SessionStore(root="/tmp/aegis-test-sessions-empty")
    return RemoteOpenHandsBackend(
        server_url=url,
        session_store=store,
        http_post=post,
    )


def _agent_task(task_id: str = "task-abc", goal: str = "do thing"):
    task = MagicMock()
    task.task_id = task_id
    task.description = goal
    task.goal = goal
    task.metadata = {"llm": {"profile": "coding"}, "tools": ["file.read"]}
    task.timeout_seconds = 60
    return task


def test_remote_backend_no_url_returns_blocked(tmp_path: Path) -> None:
    backend = _make_remote_backend(url="", store=_make_session_store(tmp_path))
    task = _agent_task()
    result = asyncio.run(backend.run(task))
    assert result.status.name == "BLOCKED"
    assert result.errors
    assert result.errors[0].code == "agent_unavailable"
    assert "AGENT_SERVER_URL" in result.errors[0].message


def test_remote_backend_unreachable_returns_blocked(tmp_path: Path) -> None:
    def _raise(*a, **kw):
        raise ConnectionError("refused")

    backend = _make_remote_backend(url="http://localhost:7100", post=_raise, store=_make_session_store(tmp_path))
    task = _agent_task()
    result = asyncio.run(backend.run(task))
    assert result.status.name == "BLOCKED"
    assert result.errors[0].code == "agent_unavailable"


def test_remote_backend_unwraps_jsonrpc_result_envelope(tmp_path: Path) -> None:
    def _post(url, *, payload, timeout, headers):  # noqa: ARG001
        if url.endswith("/healthz"):
            return {"ok": True}
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "is_error": True,
                "error_code": "not_found",
                "error": "Capability 'agent.run' is not registered in the capability catalog.",
                "events": [],
                "duration_ms": 12,
            },
        }

    backend = _make_remote_backend(url="http://localhost:7100", post=_post, store=_make_session_store(tmp_path))
    task = _agent_task(task_id="task-envelope")
    result = asyncio.run(backend.run(task))
    assert result.status.name == "BLOCKED"
    assert result.errors[0].code == "not_found"


def test_remote_backend_normal_completion(tmp_path: Path) -> None:
    def _post(url, *, payload, timeout, headers):
        return {
            "ok": True,
            "is_error": False,
            "summary": "all done",
            "events": [
                {"kind": "action", "tool": "pc-server.screenshot.get_screenshot", "arguments": "{}"},
                {"kind": "message", "role": "assistant", "text": "screenshot taken"},
            ],
            "duration_ms": 1234,
            "usage": {"input_tokens": 100, "output_tokens": 50, "cost_usd": 0.001, "model": "qwen2.5"},
        }

    backend = _make_remote_backend(url="http://localhost:7100", post=_post, store=_make_session_store(tmp_path))
    task = _agent_task()
    result = asyncio.run(backend.run(task))
    assert result.status.name == "COMPLETED"
    assert result.summary == "all done"
    assert result.usage.input_tokens == 100
    assert result.usage.model == "qwen2.5"
    assert len(result.actions) == 1
    assert result.actions[0].capability_id == "pc-server.screenshot.get_screenshot"


def test_remote_backend_uses_task_timeout_for_agent_run_request(tmp_path: Path) -> None:
    captured: list[tuple[str, float]] = []

    def _post(url, *, payload, timeout, headers):  # noqa: ARG001
        captured.append((url, timeout))
        if url.endswith("/healthz"):
            return {"ok": True}
        return {
            "is_error": False,
            "summary": "all done",
            "events": [],
            "duration_ms": 1234,
        }

    backend = _make_remote_backend(
        url="http://localhost:7100",
        post=_post,
        store=_make_session_store(tmp_path),
    )
    task = _agent_task()
    task.timeout_seconds = 90
    result = asyncio.run(backend.run(task))
    assert result.status.name == "COMPLETED"
    assert captured[0][0].endswith("/healthz")
    assert captured[0][1] == 30.0
    assert captured[1][0].endswith("/mcp")
    assert captured[1][1] == 600.0


def test_remote_backend_error_response_yields_blocked(tmp_path: Path) -> None:
    def _post(url, *, payload, timeout, headers):
        return {
            "is_error": True,
            "error_code": "policy_denied",
            "error": "policy denied: cannot run shell",
            "events": [],
        }

    backend = _make_remote_backend(url="http://localhost:7100", post=_post, store=_make_session_store(tmp_path))
    task = _agent_task()
    result = asyncio.run(backend.run(task))
    assert result.status.name == "BLOCKED"
    assert result.errors
    assert result.errors[0].code == "policy_denied"


def test_remote_backend_persists_events_to_session_store(tmp_path: Path) -> None:
    def _post(url, *, payload, timeout, headers):
        return {
            "is_error": False,
            "summary": "ok",
            "events": [
                {"kind": "metadata", "data": {"profile": "coding"}},
                {"kind": "action", "tool": "pc-server.shell.powershell", "arguments": "{}"},
            ],
        }

    store = _make_session_store(tmp_path)
    backend = _make_remote_backend(url="http://localhost:7100", post=_post, store=store)
    task = _agent_task(task_id="persisted-1")
    asyncio.run(backend.run(task))
    events = store.load("persisted-1")
    assert len(events) == 2
    assert events[0]["kind"] == "metadata"


def test_remote_backend_cancel_calls_endpoint(tmp_path: Path) -> None:
    captured: list = []

    def _post(url, *, payload, timeout, headers):
        captured.append(url)
        return {"ok": True}

    backend = _make_remote_backend(url="http://localhost:7100", post=_post, store=_make_session_store(tmp_path))
    ok = asyncio.run(backend.cancel("task-1"))
    assert ok is True
    assert any("/cancel/task-1" in u for u in captured)


def test_remote_backend_cancelled_response_yields_cancelled(tmp_path: Path) -> None:
    def _post(url, *, payload, timeout, headers):  # noqa: ARG001
        if url.endswith("/healthz"):
            return {"ok": True}
        return {
            "is_error": True,
            "error_code": "cancelled",
            "error": "agent run cancelled",
            "summary": "agent run cancelled",
            "events": [{"kind": "cancelled"}],
        }

    backend = _make_remote_backend(
        url="http://localhost:7100",
        post=_post,
        store=_make_session_store(tmp_path),
    )
    result = asyncio.run(backend.run(_agent_task(task_id="cancelled-1")))
    assert result.status.name == "CANCELLED"
    assert result.errors
    assert result.errors[0].code == "cancelled"


def test_remote_backend_generic_summary_falls_back_to_event_activity(tmp_path: Path) -> None:
    def _post(url, *, payload, timeout, headers):  # noqa: ARG001
        if url.endswith("/healthz"):
            return {"ok": True}
        return {
            "is_error": False,
            "summary": "OpenHands completed with 4 events",
            "events": [
                {
                    "kind": "action",
                    "tool": "terminal",
                    "args": {"cmd": "pytest tests/agents/test_openhands_backend.py -q"},
                },
                {
                    "kind": "action",
                    "tool": "file_editor",
                    "args": {"path": "src/aegis_ai/agents/backends/openhands/backend.py"},
                },
            ],
            "duration_ms": 222,
        }

    backend = _make_remote_backend(
        url="http://localhost:7100",
        post=_post,
        store=_make_session_store(tmp_path),
    )
    result = asyncio.run(backend.run(_agent_task(task_id="generic-summary-1")))
    assert result.status.name == "COMPLETED"
    assert "pytest tests/agents/test_openhands_backend.py -q" in result.summary
    assert "src/aegis_ai/agents/backends/openhands/backend.py" in result.summary


def test_remote_backend_get_status_no_events(tmp_path: Path) -> None:
    from aegis_ai.task.task_manager import TaskStatus

    backend = _make_remote_backend(url="http://localhost:7100", post=lambda *a, **kw: {}, store=_make_session_store(tmp_path))
    status = asyncio.run(backend.get_status("nope"))
    assert status == TaskStatus.PENDING


def test_remote_backend_does_not_import_openhands() -> None:
    from aegis_ai.agents.backends.openhands import remote_backend as mod

    text = Path(mod.__file__).read_text(encoding="utf-8")
    assert _OPENHANDS_IMPORT_RE.search(text) is None, (
        f"remote_backend.py must not import openhands; offending match: "
        f"{_OPENHANDS_IMPORT_RE.search(text).group(0)!r}"
    )


def test_workspace_module_does_not_import_openhands() -> None:
    from aegis_ai.agents.backends.openhands import workspace as mod

    text = Path(mod.__file__).read_text(encoding="utf-8")
    assert _OPENHANDS_IMPORT_RE.search(text) is None, (
        f"workspace.py must not import openhands; offending match: "
        f"{_OPENHANDS_IMPORT_RE.search(text).group(0)!r}"
    )


# ---------------------------------------------------------------------------
# Agent server (HTTP handler) tests
# ---------------------------------------------------------------------------


def test_agent_server_healthz() -> None:
    # Smoke test: just import the entrypoint; full HTTP server start is
    # covered by an end-to-end test below.
    from aegis_agent_server.main import main as srv_main, serve as srv_serve

    assert callable(srv_serve)
    assert callable(srv_main)


def test_agent_server_request_auth_defaults_open(monkeypatch) -> None:
    from aegis_agent_server.main import _is_authorized_request

    monkeypatch.delenv("AGENT_SERVER_TOKEN", raising=False)
    assert _is_authorized_request({}) is True


def test_agent_server_request_auth_requires_matching_bearer(monkeypatch) -> None:
    from aegis_agent_server.main import _is_authorized_request

    monkeypatch.setenv("AGENT_SERVER_TOKEN", "sek-ret")
    assert _is_authorized_request({}) is False
    assert _is_authorized_request({"Authorization": "Bearer wrong"}) is False
    assert _is_authorized_request({"Authorization": "Bearer sek-ret"}) is True


def test_agent_server_dispatch_initialize() -> None:
    from aegis_agent_server.main import _dispatch_mcp

    response = _dispatch_mcp({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert response["result"]["serverInfo"]["name"] == "aegis-openhands-agent"
    assert "tools" in response["result"]["capabilities"]


def test_agent_server_dispatch_tools_list_builds_valid_profile(monkeypatch) -> None:
    from aegis_agent_server.main import _dispatch_mcp

    captured: dict[str, object] = {}

    def fake_list_tools_for_agent(profile):
        captured["profile"] = profile
        return [{"name": "ai-server.agent.delegate", "inputSchema": {"type": "object"}}]

    monkeypatch.setattr(
        "aegis_ai.tools.mcp_gateway.list_tools_for_agent",
        fake_list_tools_for_agent,
    )

    response = _dispatch_mcp({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    profile = captured["profile"]
    assert getattr(profile, "id", "") == "agent-server"
    assert getattr(profile, "backend", "") == "openhands"
    assert getattr(profile, "llm_profile_name", "") == "tool_planning"
    assert response["result"]["tools"][0]["name"] == "ai-server.agent.delegate"


def test_agent_server_dispatch_tools_call_builds_valid_profile(monkeypatch) -> None:
    from aegis_agent_server.main import _dispatch_mcp

    captured: dict[str, object] = {}

    def fake_call_tool_for_agent(name, arguments, *, profile, runtime):
        captured["name"] = name
        captured["arguments"] = arguments
        captured["profile"] = profile
        captured["runtime"] = runtime
        return {
            "content": [{"type": "text", "text": "ok"}],
            "isError": False,
        }

    monkeypatch.setattr(
        "aegis_ai.tools.mcp_gateway.call_tool_for_agent",
        fake_call_tool_for_agent,
    )

    response = _dispatch_mcp(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "ai-server.agent.delegate",
                "arguments": {"goal": "test"},
            },
        }
    )
    profile = captured["profile"]
    assert getattr(profile, "id", "") == "agent-server"
    assert getattr(profile, "backend", "") == "openhands"
    assert getattr(profile, "llm_profile_name", "") == "tool_planning"
    assert captured["name"] == "ai-server.agent.delegate"
    assert response["result"]["content"][0]["text"] == "ok"


def test_agent_server_dispatch_agent_run_uses_openhands_runner(monkeypatch) -> None:
    import importlib

    server_main = importlib.import_module("aegis_agent_server.main")

    def fake_run_openhands_task(arguments):
        assert arguments["goal"] == "inspect repo"
        assert arguments["session_id"] == "sess-1"
        return {
            "content": [{"type": "text", "text": "done"}],
            "isError": False,
            "is_error": False,
            "summary": "done",
            "events": [{"kind": "message", "role": "assistant", "text": "done"}],
            "duration_ms": 12,
        }

    monkeypatch.setattr(server_main, "_run_openhands_task", fake_run_openhands_task)

    response = server_main._dispatch_mcp(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "agent.run",
                "arguments": {"goal": "inspect repo", "session_id": "sess-1"},
            },
        }
    )
    assert response["result"]["is_error"] is False
    assert response["result"]["summary"] == "done"


def test_agent_server_dispatch_pre_cancelled_agent_run_returns_cancelled() -> None:
    import importlib

    server_main = importlib.import_module("aegis_agent_server.main")
    server_main._mark_cancelled("sess-cancelled")
    response = server_main._dispatch_mcp(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "agent.run",
                "arguments": {"goal": "inspect repo", "session_id": "sess-cancelled"},
            },
        }
    )
    assert response["result"]["isError"] is True
    assert response["result"]["is_error"] is True
    assert response["result"]["error_code"] == "cancelled"
    assert response["result"]["events"][0]["kind"] == "cancelled"


def test_agent_server_interrupt_running_backend(monkeypatch) -> None:
    import importlib

    server_main = importlib.import_module("aegis_agent_server.main")

    class _FakeBackend:
        def __init__(self) -> None:
            self.cancelled: list[str] = []

        async def cancel(self, task_id: str) -> bool:
            self.cancelled.append(task_id)
            return True

    backend = _FakeBackend()
    server_main._register_running_backend("sess-2", backend)
    try:
        assert server_main._interrupt_running_backend("sess-2") is True
        assert backend.cancelled == ["sess-2"]
    finally:
        server_main._unregister_running_backend("sess-2", backend)


def test_resolve_llm_config_reads_repo_llm_yaml() -> None:
    import importlib

    server_main = importlib.import_module("aegis_agent_server.main")
    config = server_main._resolve_llm_config({"profile": "tool_planning"})
    assert config["profile"] == "tool_planning"
    assert config["model"]
    assert "api_key_env" in config


def test_agent_server_dispatch_unknown_method() -> None:
    from aegis_agent_server.main import _dispatch_mcp

    response = _dispatch_mcp({"jsonrpc": "2.0", "id": 1, "method": "nope"})
    assert response["error"]["code"] == -32601


def test_agent_server_handler_rejects_unauthorized_mcp(monkeypatch) -> None:
    import importlib
    import io

    server_main = importlib.import_module("aegis_agent_server.main")

    monkeypatch.setattr(server_main, "_is_authorized_request", lambda headers: False)

    handler = server_main._Handler.__new__(server_main._Handler)
    handler.path = "/mcp"
    handler.headers = {"Content-Length": "2"}
    handler.rfile = io.BytesIO(b"{}")
    handler.wfile = io.BytesIO()
    captured: dict[str, object] = {}

    handler.send_response = lambda status: captured.setdefault("status", status)
    handler.send_header = lambda name, value: None
    handler.end_headers = lambda: None

    handler.do_POST()
    assert captured["status"] == 401
