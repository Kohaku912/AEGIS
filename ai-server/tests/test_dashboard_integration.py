"""Dashboard integration tests — verifies all sidebar URLs and key APIs return correct responses."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from aegis_ai.web import dashboard_routes


class _FakeSettings:
    class autonomous:
        autonomous_loop_enabled = False
        support_agent_enabled = False
        self_dev_proposal_enabled = False
    class privacy:
        clipboard_capture_enabled = False
        camera_snapshot_enabled = False


def _make_runtime(tmp_path):
    return SimpleNamespace(
        status_manager=SimpleNamespace(
            get_snapshot=lambda: {},
            get_server_status=lambda s: None,
            check_now=lambda: {},
        ),
        task_manager=SimpleNamespace(
            list_tasks=lambda **kw: [],
            list_running=lambda: [],
            list_waiting_approval=lambda: [],
            create_task=lambda **kw: {"task_id": "t1", "status": "created"},
            get_task=lambda tid: None,
        ),
        event_manager=SimpleNamespace(
            list_recent=lambda **kw: {"events": [], "next_cursor": None},
            get_event=lambda eid: None,
        ),
        audit_manager=SimpleNamespace(
            _log=SimpleNamespace(read_all=lambda: []),
            list_recent=lambda **kw: {"entries": [], "total": 0, "total_pages": 0},
            get_detail=lambda aid: None,
            summarize=lambda **kw: {},
        ),
        notification_manager=SimpleNamespace(
            list_recent=lambda **kw: [],
            list_unread=lambda **kw: [],
        ),
        memory_manager=SimpleNamespace(
            search_memory=lambda q, limit=20: [],
            get_stats=lambda: {},
        ),
        sleep_manager=SimpleNamespace(get_status=lambda: {}),
        folder_registry=SimpleNamespace(list_all=lambda: [], errors=lambda: []),
        tool_broker=SimpleNamespace(_catalog=SimpleNamespace(reload=lambda: {})),
        policy_engine=SimpleNamespace(_risk_overrides={}),
        audit_log=SimpleNamespace(log_decision=lambda *a, **kw: None),
        settings_store=SimpleNamespace(get=lambda: _FakeSettings()),
        autonomous_loop=SimpleNamespace(
            get_status=lambda: {"running": False, "execution_count": 0},
            get_threshold=lambda: 2.0,
        ),
        tool_registry=SimpleNamespace(get_capabilities_by_server_type=lambda st: []),
        llm_gateway=None,
        event_bus=SimpleNamespace(list_recent_events=lambda *a, **kw: []),
        prompt_registry=SimpleNamespace(
            list_prompts=lambda: [],
            get=lambda pid: {"template": "", "editable": True, "protected": False},
            get_metadata=lambda pid: {"hash": "", "version": "1"},
            render=lambda pid: "",
        ),
        settings_resolver=SimpleNamespace(
            resolve=lambda **kw: SimpleNamespace(
                provider="openai", model="test", max_tokens=1000,
                temperature=0.7, reasoning_level="medium",
                timeout_seconds=30, max_tool_rounds=5,
                api_key_env="", base_url="",
            ),
        ),
    )


def _app(monkeypatch, tmp_path):
    monkeypatch.setattr(dashboard_routes, "_load_settings_for_status", lambda: _FakeSettings())
    monkeypatch.setattr(dashboard_routes, "_get_mem_backend", lambda name, **kw: None)
    monkeypatch.setattr(dashboard_routes, "build_shared_memory_context", lambda **kw: SimpleNamespace(text="", audit_detail=lambda: {}))
    monkeypatch.setattr(dashboard_routes, "_load_chat_history_entries", lambda: [])
    monkeypatch.setattr(dashboard_routes, "_load_audit_entries", lambda: [])
    monkeypatch.setattr(dashboard_routes, "_load_error_log_entries", lambda: [])
    monkeypatch.setattr(dashboard_routes, "_load_memory_snapshot", lambda: {
        "summary": {}, "entities": [], "facts": [], "persons": [],
        "semantic_entries": [], "advanced_conversations": [],
        "experiences": [], "action_traces": [], "conversations": [],
    })
    return dashboard_routes.DashboardApp(runtime=_make_runtime(tmp_path)).app


@pytest.fixture
def client(monkeypatch, tmp_path):
    return _app(monkeypatch, tmp_path).test_client()


def test_all_dashboard_pages_and_apis(client):
    spa_urls = ["/", "/dashboard", "/dashboard/memory", "/chat", "/settings"]
    for url in spa_urls:
        resp = client.get(url)
        assert resp.status_code == 200, f"{url} returned {resp.status_code}"
        assert b"/assets/index-" in resp.data, f"{url} did not serve the SPA shell"

    api_urls = [
        "/api/ui/overview",
        "/api/tasks", "/api/status", "/api/notifications", "/api/memory/stats",
    ]
    for url in api_urls:
        resp = client.get(url)
        assert resp.status_code == 200, f"{url} returned {resp.status_code}: {resp.data[:200]}"
        data = json.loads(resp.data)
        assert isinstance(data, (dict, list)), f"{url} returned non-JSON type"
