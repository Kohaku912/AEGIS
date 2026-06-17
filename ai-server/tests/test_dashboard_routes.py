from __future__ import annotations

import json
import os
from types import SimpleNamespace

from aegis_ai.web import dashboard_routes
from aegis_ai.web import chat_tools


def _runtime(tmp_path):
    from approval import ApprovalStore
    from event_bus import EventBus
    from policy_engine import PolicyEngine
    from tool_broker import ToolBroker
    from tool_registry import ToolRegistry

    from aegis_ai.approval import ApprovalQueue
    from aegis_ai.audit import AuditLog
    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai.settings.store import SettingsStore
    from aegis_ai.status.status_manager import StatusManager
    from aegis_ai.event.event_manager import EventManager
    from aegis_ai.audit.audit_manager import AuditManager
    from aegis_ai.memory.memory_manager import MemoryManager

    data_dir = tmp_path / "data"
    catalog = CapabilityCatalog(
        capabilities_dir=str(data_dir / "capabilities"),
        apps_dir=str(data_dir / "apps"),
    )
    registry = ToolRegistry()
    audit_log = AuditLog(path=str(data_dir / "audit.jsonl"))
    approval_store = ApprovalStore()
    policy_engine = PolicyEngine(approval_store=approval_store, data_dir=str(data_dir))
    broker = ToolBroker(registry=registry, policy_engine=policy_engine, audit_log=audit_log, catalog=catalog)
    event_bus = EventBus()
    event_manager = EventManager(event_bus=event_bus, data_dir=str(data_dir))
    audit_manager = AuditManager(audit_log=audit_log, data_dir=str(data_dir))
    status_manager = StatusManager(event_manager=event_manager)
    memory_manager = MemoryManager(event_manager=event_manager)
    return SimpleNamespace(
        settings_store=SettingsStore(
            path=str(tmp_path / "config" / "settings.json"),
            audit_path=str(data_dir / "settings_audit.jsonl"),
        ),
        audit_log=audit_log,
        capability_catalog=catalog,
        folder_registry=catalog.get_folder_registry(),
        tool_registry=registry,
        event_bus=event_bus,
        approval_store=approval_store,
        approval_queue=ApprovalQueue(data_dir=str(data_dir / "approvals"), audit_log=audit_log),
        policy_engine=policy_engine,
        tool_broker=broker,
        llm_gateway=object(),
        autonomous_loop=None,
        start_autonomous_if_enabled=lambda: None,
        status_manager=status_manager,
        event_manager=event_manager,
        audit_manager=audit_manager,
        memory_manager=memory_manager,
    )


def _app(monkeypatch, tmp_path):
    monkeypatch.setattr(dashboard_routes, "_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(dashboard_routes.DashboardApp, "_start_autonomous_loop", lambda self: None)
    return dashboard_routes.DashboardApp(runtime=_runtime(tmp_path)).app


def test_dashboard_registers_settings_blueprint(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()

    response = client.get("/api/settings")

    assert response.status_code == 200
    assert "autonomous" in response.get_json()


def test_settings_section_update_persists(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()

    response = client.post(
        "/api/settings/autonomous",
        json={
            "autonomous_loop_enabled": False,
            "support_agent_enabled": True,
            "research_watch_enabled": True,
            "self_dev_proposal_enabled": True,
            "daily_briefing_enabled": True,
            "max_autonomous_runs_per_hour": 12,
            "max_autonomous_runs_per_day": 100,
            "cooldown_seconds": 120,
        },
    )
    settings = client.get("/api/settings").get_json()

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert settings["autonomous"]["autonomous_loop_enabled"] is False
    assert settings["autonomous"]["cooldown_seconds"] == 120


def test_settings_legacy_single_field_update_persists(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()

    response = client.post(
        "/api/settings",
        json={"section": "privacy", "key": "clipboard_capture_enabled", "value": False},
    )
    settings = client.get("/api/settings").get_json()

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert settings["privacy"]["clipboard_capture_enabled"] is False


def test_server_status_reports_degraded_and_unconfigured(monkeypatch, tmp_path) -> None:
    rt = _runtime(tmp_path)
    rt.status_manager._status = {
        "dashboard": {"server_id": "dashboard", "status": "online", "host": "localhost", "port": 8090, "last_check_ms": 0, "error": None},
        "ai-server": {"server_id": "ai-server", "status": "online", "host": "localhost", "port": 50051, "last_check_ms": 0, "error": None},
        "pc-server": {"server_id": "pc-server", "status": "online", "host": "localhost", "port": 50052, "last_check_ms": 0, "error": None},
        "browser-server": {"server_id": "browser-server", "status": "degraded", "host": "localhost", "port": 50053, "last_check_ms": 0, "error": "Missing dependencies: browser-use"},
        "android-server": {"server_id": "android-server", "status": "offline", "host": "localhost", "port": 50054, "last_check_ms": 0, "error": None},
        "room-server": {"server_id": "room-server", "status": "offline", "host": "localhost", "port": 50055, "last_check_ms": 0, "error": None},
        "dev-server": {"server_id": "dev-server", "status": "offline", "host": "localhost", "port": 50056, "last_check_ms": 0, "error": None},
    }
    settings = SimpleNamespace(
        servers=SimpleNamespace(
            pc_server_enabled=True,
            browser_server_enabled=True,
            android_server_enabled=False,
            room_server_enabled=False,
            dev_server_enabled=False,
        )
    )

    payload = dashboard_routes._runtime_server_status(settings=settings, runtime=rt)
    by_id = {server["server_id"]: server for server in payload["servers"]}

    assert by_id["browser-server"]["status"] == "DEGRADED"
    assert "browser-use" in by_id["browser-server"]["degraded_reason"]
    assert by_id["android-server"]["status"] == "UNCONFIGURED"
    assert by_id["room-server"]["status"] == "UNCONFIGURED"
    assert by_id["dev-server"]["status"] == "UNCONFIGURED"
    assert payload["summary"]["degraded_servers"] == 1
    assert payload["summary"]["unconfigured_servers"] == 3


def test_capability_risk_update_allows_127_loopback(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()
    manifest_path = tmp_path / "data" / "capabilities" / "builtin" / "pc-server" / "test" / "sample.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "id": "pc-server.test.sample",
                "server_id": "pc-server",
                "app_id": "test",
                "action": "sample",
                "title": "Sample",
                "risk": {"level": "low", "requires_approval": False},
            }
        ),
        encoding="utf-8",
    )

    response = client.post(
        "/api/capabilities/risk",
        json={"capability_id": "pc-server.test.sample", "risk_level": "SAFE_ACTION"},
        headers={"Origin": "http://127.0.0.1:8090"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    payload = response.get_json()
    updated = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert response.status_code == 200
    assert payload["ok"] is True
    assert updated["risk"]["level"] == "safe"


def test_capability_risk_update_rejects_non_loopback(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()

    response = client.post(
        "/api/capabilities/risk",
        json={"capability_id": "pc-server.test.sample", "risk_level": "SAFE_ACTION"},
        headers={"Origin": "http://evil.example"},
        environ_base={"REMOTE_ADDR": "203.0.113.9"},
    )

    assert response.status_code == 403
    assert "localhost" in response.get_json()["error"]


def test_chat_prompt_includes_actual_server_status(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(dashboard_routes, "_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(
        dashboard_routes,
        "_server_status_context_for_prompt",
        lambda: "SERVER STATUS:\n- browser-server (localhost:50053): DEGRADED mode=fallback. Missing dependencies: browser-use",
    )

    class FakeMemoryContext:
        text = "Memory context"

        def audit_detail(self) -> dict[str, str]:
            return {"memory_profile": "decision"}

    monkeypatch.setattr(
        dashboard_routes,
        "build_shared_memory_context",
        lambda **kwargs: FakeMemoryContext(),
    )

    system_prompt, memory_meta, _ = dashboard_routes._build_chat_system_prompt("open a web page")

    assert "browser-server" in system_prompt
    assert "DEGRADED" in system_prompt
    assert "all servers are running" not in system_prompt.lower()
    assert memory_meta == {"memory_profile": "decision"}


def test_capability_risk_update_rejects_non_localhost_origin(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()

    response = client.post(
        "/api/capabilities/risk",
        json={"capability_id": "pc-server.system.get_os_info", "risk_level": "READ_ONLY"},
        headers={"Origin": "https://example.com"},
    )

    assert response.status_code == 403
    assert "localhost" in response.get_json()["error"]


def test_dashboard_audit_shows_llm_tool_timeline(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    audit_path = data_dir / "audit.jsonl"
    entries = [
        {
            "entry_id": "a1",
            "timestamp_ms": 1000,
            "action": "llm_tool_call",
            "actor": "llm",
            "capability_id": "llm.deepseek-chat",
            "decision": "success",
            "reason": "",
            "detail": {
                "model": "deepseek-chat",
                "tool_calls": [
                    {"function": "pc-server__file__search", "arguments": {"path": "C:\\", "pattern": "*.log"}},
                ],
                "response_preview": "Investigating the log files now.",
                "tokens": 123,
                "duration_ms": 456.7,
            },
        },
        {
            "entry_id": "a2",
            "timestamp_ms": 2000,
            "action": "tool_execution",
            "actor": "autonomous",
            "capability_id": "pc-server.file.search",
            "decision": "ALLOW",
            "reason": "Autonomous maintenance",
            "detail": {
                "execution_status": "execution_error",
                "error": "Access denied",
                "duration_ms": 12,
                "verification_status": "skipped",
                "output": {"error": "Access denied"},
            },
        },
    ]
    audit_path.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n", encoding="utf-8")

    response = client.get("/dashboard/audit")
    body = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "LLM / Tool Timeline" in body
    assert "LLM selected 1 tool(s): pc-server__file__search" in body
    assert "Tool failed: Access denied" in body


def test_dashboard_errors_shows_audit_and_log_errors(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "audit.jsonl").write_text(
        json.dumps(
            {
                "entry_id": "err1",
                "timestamp_ms": 1000,
                "action": "tool_execution",
                "actor": "autonomous",
                "capability_id": "pc-server.file.search",
                "decision": "ALLOW",
                "reason": "Autonomous maintenance",
                "detail": {
                    "execution_status": "execution_error",
                    "error": "Access denied",
                    "output": {"error": "Access denied"},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "dashboard_error.log").write_text(
        "2026-06-16 10:00:00,000 [ERROR] aegis_ai.web.dashboard: Disk full\n",
        encoding="utf-8",
    )

    response = client.get("/dashboard/errors")
    body = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Access denied" in body
    assert "Disk full" in body
    assert "Server Logs" in body


def test_memory_reload_api_returns_summary(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()

    response = client.post("/api/memory/reload")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert "summary" in payload
    assert "chroma_synced" in payload


def test_chat_respond_uses_shared_decision_memory_profile(monkeypatch, tmp_path) -> None:
    class FakeMemoryContext:
        def __init__(self, profile: str) -> None:
            self.text = f"context for {profile}"
            self._profile = profile

        def audit_detail(self) -> dict[str, str]:
            return {"memory_profile": self._profile}

    recorded_profiles: list[str] = []
    recorded_context_meta: list[dict[str, str]] = []

    def fake_builder(*, query: str, data_dir: str, profile: str = "decision") -> FakeMemoryContext:
        recorded_profiles.append(profile)
        return FakeMemoryContext(profile)

    def fake_call_llm_with_tools(
        llm,
        user_message: str,
        system_prompt: str,
        catalog=None,
        max_tool_rounds: int = 15,
        context_meta: dict[str, str] | None = None,
    ) -> dict[str, object]:
        recorded_context_meta.append(context_meta or {})
        return {"response": "Continued.", "tool_calls": [], "tool_results": []}

    monkeypatch.setattr(dashboard_routes, "build_shared_memory_context", fake_builder)
    monkeypatch.setattr(chat_tools, "call_llm_with_tools", fake_call_llm_with_tools)
    client = _app(monkeypatch, tmp_path).test_client()
    response = client.post(
        "/api/chat/respond",
        json={
            "response": "done",
            "pending_context": {
                "original_message": "Continue the setup",
                "browser_task": "Finish the form",
                "memory_profile": "decision",
            },
        },
    )

    assert response.status_code == 200
    assert response.get_json()["response"] == "Continued."
    assert recorded_profiles == ["decision"]
    assert recorded_context_meta == [{"memory_profile": "decision"}]


def test_memory_page_shows_entries_beyond_old_limits(monkeypatch, tmp_path) -> None:
    memory_dir = tmp_path / "data" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    entities = []
    for idx in range(25):
        entities.append(
            {
                "entity_id": f"entity_{idx}",
                "name": f"Entity {idx}",
                "entity_type": "person" if idx % 2 == 0 else "thing",
                "attributes": {},
                "relationships": [],
                "first_seen_ms": 1000 + idx,
                "last_seen_ms": 1000 + idx,
                "mention_count": idx + 1,
                "importance": 0.5,
            }
        )
    (memory_dir / "entities.jsonl").write_text(
        "\n".join(json.dumps(entity) for entity in entities) + "\n",
        encoding="utf-8",
    )

    facts = []
    for idx in range(35):
        facts.append(
            {
                "fact_id": f"fact_{idx}",
                "content": f"Fact {idx}",
                "subject": f"subject_{idx}",
                "predicate": "is",
                "object": "",
                "source": "conversation",
                "valid_at_ms": 2000 + idx,
                "invalid_at_ms": 0,
                "confidence": 0.9,
                "importance": 0.5,
            }
        )
    (memory_dir / "facts.jsonl").write_text(
        "\n".join(json.dumps(fact) for fact in facts) + "\n",
        encoding="utf-8",
    )

    conversations = []
    for idx in range(12):
        conversations.append(
            {
                "entry_id": f"conv_{idx}",
                "user_msg": f"User message {idx}",
                "bot_msg": f"Bot reply {idx}",
                "timestamp_ms": 3000 + idx,
                "entities_mentioned": [f"entity_{idx}"],
                "facts_extracted": [f"fact_{idx}"],
            }
        )
    (memory_dir / "conversations.jsonl").write_text(
        "\n".join(json.dumps(conv) for conv in conversations) + "\n",
        encoding="utf-8",
    )

    experiences = []
    for idx in range(3):
        experiences.append(
            {
                "experience_id": f"exp_{idx}",
                "timestamp_ms": 4000 + idx,
                "action": f"Experience action {idx}",
                "observation": f"Observation {idx}",
                "context": "test",
                "emotion_label": "satisfied",
                "emotion_valence": 0.5,
                "emotion_arousal": 0.2,
                "learning": f"Learning {idx}",
                "importance": 0.4,
                "tags": [],
                "related_desire": "reliability",
                "outcome_success": True,
            }
        )
    (memory_dir / "experiences.jsonl").write_text(
        "\n".join(json.dumps(exp) for exp in experiences) + "\n",
        encoding="utf-8",
    )

    traces = []
    for idx in range(2):
        traces.append(
            {
                "trace_id": f"trace_{idx}",
                "goal": f"Trace goal {idx}",
                "context": "test run",
                "desire_name": "maintenance",
                "plan_description": "",
                "steps": [],
                "status": "completed",
                "success": True,
                "result_summary": f"Trace result {idx}",
                "failure_reason": "",
                "verification_result": "",
                "user_feedback": "",
                "user_satisfaction": 0.0,
                "difficulty": 0.5,
                "novelty": 0.3,
                "tags": [],
                "started_at_ms": 5000 + idx,
                "completed_at_ms": 5100 + idx,
                "consolidated": False,
                "lessons_extracted": False,
            }
        )
    (memory_dir / "action_traces.jsonl").write_text(
        "\n".join(json.dumps(trace) for trace in traces) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(dashboard_routes, "_DATA_DIR", str(tmp_path / "data"))

    # Create mock runtime with memory_manager
    from aegis_ai.memory.advanced import AdvancedMemory
    from aegis_ai.memory.episodic_memory import EpisodicMemory
    from aegis_ai.memory.semantic_memory import SemanticMemory
    from aegis_ai.memory.skill_memory import SkillMemory
    from aegis_ai.memory.lesson_memory import LessonMemory
    from aegis_ai.memory.workflow_memory import WorkflowMemory
    from aegis_ai.memory.experiential import ExperientialMemory
    from aegis_ai.memory.person_memory import PersonMemory
    from aegis_ai.memory.memory_manager import MemoryManager

    memory_dir = str(tmp_path / "data" / "memory")
    advanced_memory = AdvancedMemory(data_dir=memory_dir)
    episodic_memory = EpisodicMemory(path=os.path.join(memory_dir, "episodic.jsonl"))
    semantic_memory = SemanticMemory(path=os.path.join(memory_dir, "semantic.jsonl"))
    skill_memory = SkillMemory(path=os.path.join(memory_dir, "skills.jsonl"))
    lesson_memory = LessonMemory(path=os.path.join(memory_dir, "lessons.jsonl"))
    workflow_memory = WorkflowMemory(path=os.path.join(memory_dir, "workflows.jsonl"))
    experiential_memory = ExperientialMemory(data_dir=memory_dir)
    person_memory = PersonMemory(path=os.path.join(memory_dir, "persons.jsonl"))

    memory_manager = MemoryManager(
        advanced_memory=advanced_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        skill_memory=skill_memory,
        lesson_memory=lesson_memory,
        workflow_memory=workflow_memory,
        experiential_memory=experiential_memory,
        person_memory=person_memory,
    )

    mock_runtime = SimpleNamespace(memory_manager=memory_manager)
    from aegis_ai import runtime as rt_mod
    monkeypatch.setattr(rt_mod, "get_runtime", lambda config=None: mock_runtime)

    snapshot = dashboard_routes._load_memory_snapshot()

    assert len(snapshot.get("entities", [])) >= 25
    entity_names = [e["name"] for e in snapshot.get("entities", [])]
    assert "Entity 24" in entity_names
    assert len(snapshot.get("facts", [])) >= 35
    fact_contents = [f["content"] for f in snapshot.get("facts", [])]
    assert "Fact 34" in fact_contents


def test_autonomous_page_shows_more_than_ten_executions(monkeypatch, tmp_path) -> None:
    client = _app(monkeypatch, tmp_path).test_client()
    auto_dir = tmp_path / "data" / "autonomous"
    auto_dir.mkdir(parents=True, exist_ok=True)
    log_path = auto_dir / "execution_log.jsonl"

    entries = []
    for idx in range(12):
        entries.append(
            {
                "timestamp_ms": 1000 + idx,
                "tasks": [{"desire": "maintenance", "action": f"Action {idx}"}],
                "results": [{"result": f"Result {idx}", "success": idx % 2 == 0}],
            }
        )
    log_path.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n", encoding="utf-8")

    response = client.get("/dashboard/autonomous")
    body = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Action 0" in body
    assert "Action 11" in body
