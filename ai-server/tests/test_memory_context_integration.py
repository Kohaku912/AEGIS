from __future__ import annotations

import json
from types import SimpleNamespace

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.audit import AuditLog
from aegis_ai.briefing.provider import BriefingSection, DailyBriefing, DailyBriefingProvider
from aegis_ai.browser_use.executor import BrowserUseTaskExecutor
from aegis_ai.llm.memory_context import build_shared_memory_context
from aegis_ai.llm.providers.openai_provider import OpenAIProvider
from aegis_ai.memory.memory_store import MemoryStore
from aegis_ai.memory.memory_types import MemoryRecord, MemorySource, MemoryType, Sensitivity, Visibility


class _FakeContext:
    def __init__(self, profile: str) -> None:
        self.text = f"context for {profile}"
        self._profile = profile

    def audit_detail(self) -> dict[str, object]:
        return {"memory_profile": self._profile}


class _SummaryLLM:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 0,
        context_meta: dict[str, object] | None = None,
    ) -> SimpleNamespace:
        self.calls.append({"prompt": prompt, "context_meta": context_meta})
        return SimpleNamespace(success=True, content="summary")


class _AutonomousToolLLM:
    def __init__(self, tool_calls: list[dict[str, object]]) -> None:
        self.tool_calls = tool_calls
        self.context_meta: dict[str, object] | None = None
        self.prompt = ""

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, object]],
        system_prompt: str = "",
        max_tokens: int = 0,
        context_meta: dict[str, object] | None = None,
    ) -> SimpleNamespace:
        self.prompt = prompt
        self.context_meta = context_meta
        return SimpleNamespace(success=True, tool_calls=self.tool_calls, error="")


class _FakeCatalog:
    def list_for_tools(self, valid_cap_ids: set[str] | None = None) -> list[dict[str, object]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "ai-server__memory__save",
                    "description": "Save memory",
                    "parameters": {"type": "object", "properties": {"text": {"type": "string"}}},
                },
            }
        ]

    def tool_name_to_cap_id(self, tool_name: str) -> str:
        return tool_name.replace("__", ".")

    def resolve(self, cap_id: str) -> object | None:
        if cap_id == "ai-server.memory.save":
            return SimpleNamespace(input_schema={"type": "object", "required": ["text"]})
        return None


class _FakeBroker:
    def __init__(self) -> None:
        self._catalog = _FakeCatalog()

    def list_safe_capabilities(self) -> list[object]:
        return [SimpleNamespace(id="ai-server.memory.save")]

    def list_autonomous_capabilities(self) -> list[object]:
        return [SimpleNamespace(id="ai-server.memory.save")]


def test_shared_memory_context_includes_recent_failures_without_query_hits(tmp_path) -> None:
    data_dir = tmp_path / "data"
    (data_dir / "memory").mkdir(parents=True, exist_ok=True)
    (data_dir / "autonomous").mkdir(parents=True, exist_ok=True)

    execution_entries = [
        {
            "timestamp_ms": 1000,
            "tasks": [{"action": "Retry browser task", "capability_id": "browser-server.page.browse"}],
            "results": [{"success": False, "result": "Timeout while loading page"}],
        },
        {
            "timestamp_ms": 2000,
            "tasks": [{"action": "Retry browser task", "capability_id": "browser-server.page.browse"}],
            "results": [{"success": False, "result": "Timeout while loading page"}],
        },
    ]
    (data_dir / "autonomous" / "execution_log.jsonl").write_text(
        "\n".join(json.dumps(entry) for entry in execution_entries) + "\n",
        encoding="utf-8",
    )

    trace_entry = {
        "trace_id": "trace_1",
        "goal": "Open browser settings",
        "context": "test",
        "desire_name": "reliability",
        "plan_description": "",
        "steps": [],
        "status": "failed",
        "success": False,
        "result_summary": "",
        "failure_reason": "Browser session was stale",
        "verification_result": "",
        "user_feedback": "",
        "user_satisfaction": 0.0,
        "difficulty": 0.5,
        "novelty": 0.2,
        "tags": [],
        "started_at_ms": 1000,
        "completed_at_ms": 1100,
        "consolidated": False,
        "lessons_extracted": False,
    }
    (data_dir / "memory" / "action_traces.jsonl").write_text(
        json.dumps(trace_entry) + "\n",
        encoding="utf-8",
    )

    store = MemoryStore(data_dir=str(data_dir / "memory_store"))
    store.add_memory(MemoryRecord(
        memory_type=MemoryType.FAILURE_LESSON.value,
        title="Browser browse failed",
        content="The last browser browse attempt timed out. Avoid reusing the same stale flow.",
        source=MemorySource.REFLECTION.value,
        related_desire="reliability",
        confidence=0.9,
        importance=0.9,
        visibility=Visibility.LLM_VISIBLE.value,
        sensitivity=Sensitivity.NORMAL.value,
    ))
    store.add_memory(MemoryRecord(
        memory_type=MemoryType.USER_PREFERENCE.value,
        title="User preference",
        content="Prefer concise answers.",
        source=MemorySource.USER_EXPLICIT.value,
        confidence=0.9,
        importance=0.7,
        visibility=Visibility.LLM_VISIBLE.value,
        sensitivity=Sensitivity.NORMAL.value,
    ))

    decision = build_shared_memory_context(query="unrelated topic", data_dir=str(data_dir), profile="decision")
    summary = build_shared_memory_context(query="unrelated topic", data_dir=str(data_dir), profile="summary")

    assert "RECENT AUTONOMOUS EXECUTIONS:" in decision.text
    assert "Repeated recent failures:" in decision.text
    assert "ACTION TRACE HINTS:" in decision.text
    assert "Failure lessons:" in decision.text
    assert "User preferences:" in decision.text
    assert "ACTION TRACE HINTS:" not in summary.text
    assert "User preferences:" not in summary.text


def test_autonomous_loop_rejects_invalid_tool_calls_and_audits_them(tmp_path) -> None:
    llm = _AutonomousToolLLM([
        {"function": "pc-server__memory__search", "arguments": {"query": "account info"}},
    ])
    loop = AutonomousLoop(
        llm_provider=llm,
        tool_broker=_FakeBroker(),
        data_dir=str(tmp_path / "data" / "autonomous"),
        audit_log=AuditLog(path=str(tmp_path / "data" / "audit.jsonl")),
    )

    tasks = loop._generate_tasks([
        {"name": "reliability", "value": 2.0, "expected": 7.0, "gap": 5.0, "frustration": 5.0},
    ])

    assert tasks == []
    assert llm.context_meta is not None
    assert llm.context_meta.get("memory_profile") == "decision"

    audit_records = loop._audit_log.read_all()
    assert any(
        record["action"] == "autonomous_tool_selection"
        and record["decision"] == "REJECT"
        and "pc-server__memory__search" in record["reason"]
        for record in audit_records
    )

    store = MemoryStore(data_dir=str(tmp_path / "data" / "memory_store"))
    lessons = store.search_memories(memory_type="failure_lesson", related_desire="reliability", limit=5)
    assert any("pc-server__memory__search" in lesson.title or "pc-server__memory__search" in lesson.content for lesson in lessons)


def test_daily_briefing_summary_uses_summary_memory_profile(monkeypatch) -> None:
    llm = _SummaryLLM()
    profiles: list[str] = []

    def fake_builder(*, query: str, data_dir: str, profile: str = "decision") -> _FakeContext:
        profiles.append(profile)
        return _FakeContext(profile)

    monkeypatch.setattr("aegis_ai.briefing.provider.build_shared_memory_context", fake_builder)

    provider = DailyBriefingProvider(llm_provider=llm)
    briefing = DailyBriefing(
        date="2026-06-16",
        sections=[BriefingSection(title="Health", content="All systems nominal.")],
    )

    summary = provider._generate_summary(briefing)

    assert summary == "summary"
    assert profiles == ["summary"]
    assert llm.calls[0]["context_meta"] == {"memory_profile": "summary"}


def test_browser_executor_summary_uses_summary_memory_profile(monkeypatch) -> None:
    llm = _SummaryLLM()
    profiles: list[str] = []

    def fake_builder(*, query: str, data_dir: str, profile: str = "decision") -> _FakeContext:
        profiles.append(profile)
        return _FakeContext(profile)

    monkeypatch.setattr("aegis_ai.browser_use.executor.build_shared_memory_context", fake_builder)

    executor = BrowserUseTaskExecutor(llm_client=llm)
    result = executor._summarize_page_content(
        title="Example",
        text="A" * 400,
        task="Summarize the page",
    )

    assert result == "summary"
    assert profiles == ["summary"]
    assert llm.calls[0]["context_meta"] == {"memory_profile": "summary"}


def test_openai_provider_returns_error_when_vision_is_unsupported(monkeypatch) -> None:
    provider = OpenAIProvider(
        model="deepseek-chat",
        api_key="test-key",
        base_url="https://api.deepseek.com",
        audit_log=None,
    )

    result = provider.generate_with_image(
        prompt="Summarize this screenshot.",
        image_base64="ZmFrZQ==",
        system_prompt="You convert screenshots into concise observations.",
        max_tokens=200,
        detail="low",
        context_meta={"memory_profile": "summary"},
    )

    assert result.success is False
    assert "does not support vision" in result.error


def test_openai_provider_returns_error_for_deepseek_v4_pro(monkeypatch) -> None:
    provider = OpenAIProvider(
        model="deepseek-v4-pro",
        api_key="test-key",
        base_url="https://api.deepseek.com",
        audit_log=None,
    )

    result = provider.generate_with_image(
        prompt="Summarize this screenshot.",
        image_base64="ZmFrZQ==",
        system_prompt="You convert screenshots into concise observations.",
        max_tokens=200,
        detail="low",
    )

    assert result.success is False
    assert "does not support vision" in result.error

