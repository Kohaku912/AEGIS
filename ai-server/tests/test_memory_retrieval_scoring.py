from __future__ import annotations

from aegis_ai.memory.advanced import AdvancedMemory, ConversationEntry, Fact
from aegis_ai.memory.action_trace import ActionTraceMemory
from aegis_ai.memory.episodic_memory import EpisodicMemory
from aegis_ai.memory.lesson_memory import LessonMemory
from aegis_ai.memory.memory_store import MemoryStore
from aegis_ai.memory.memory_types import MemoryRecord, MemoryType
from aegis_ai.memory.semantic_memory import SemanticMemory
from aegis_ai.memory.skill_memory import SkillMemory
from aegis_ai.memory.workflow_memory import WorkflowMemory


def test_advanced_memory_retrieves_related_facts_without_exact_substring(tmp_path) -> None:
    memory = AdvancedMemory(data_dir=str(tmp_path / "advanced"))
    memory._facts["fact-1"] = Fact(
        fact_id="fact-1",
        content="User prefers concise operational summaries",
        subject="user",
        predicate="prefers",
        object="concise summaries",
        importance=0.9,
        valid_at_ms=1,
    )
    memory._conversations = [
        ConversationEntry(
            entry_id="conv-1",
            user_msg="Please keep the status update concise",
            bot_msg="Understood",
            timestamp_ms=2,
        )
    ]

    facts = memory._search_facts("brief operational summary")
    conversations = memory._search_conversations("concise status summary")

    assert facts
    assert facts[0].fact_id == "fact-1"
    assert conversations
    assert conversations[0].entry_id == "conv-1"


def test_memory_store_search_uses_weighted_relevance_not_only_substring(tmp_path) -> None:
    store = MemoryStore(data_dir=str(tmp_path / "memory_store"))
    store.add_memory(
        MemoryRecord(
            memory_type=MemoryType.USER_PREFERENCE.value,
            title="Communication style",
            content="Prefers concise operational summaries",
            tags=["communication"],
            importance=0.8,
            confidence=0.9,
        )
    )

    hits = store.search_memories(query="brief summary", memory_type=MemoryType.USER_PREFERENCE.value, limit=5)

    assert hits
    assert hits[0].title == "Communication style"


def test_semantic_memory_search_matches_related_terms(tmp_path) -> None:
    memory = SemanticMemory(path=str(tmp_path / "semantic.jsonl"))
    memory.add(
        content="Use concise operational status updates for dashboard summaries.",
        category="knowledge",
        tags=["dashboard", "summary"],
        importance=0.8,
    )

    hits = memory.search("brief dashboard summary", limit=5)

    assert hits
    assert "dashboard" in hits[0].content.lower()


def test_episodic_memory_recall_similar_uses_semantic_weighting(tmp_path) -> None:
    memory = EpisodicMemory(path=str(tmp_path / "episodic.jsonl"))
    memory.record(
        "prepared status draft",
        "wrote a concise operational summary for the cockpit",
        lesson="brief status drafts reduce friction",
        category="workflow",
        tags=["dashboard", "summary"],
    )

    hits = memory.recall_similar("brief dashboard summary", count=3)

    assert hits
    assert "dashboard" in " ".join(hits[0].tags).lower()


def test_workflow_memory_matches_description_and_steps_not_only_name(tmp_path) -> None:
    memory = WorkflowMemory(path=str(tmp_path / "workflows.jsonl"))
    memory.add(
        name="Ops Routine",
        description="Resume paused follow-up goals after approval blockers are cleared.",
        goal_pattern="",
        steps=[
            {
                "description": "Open control hub and continue blocked backlog items",
                "tool_call": "internal.control_hub",
                "expected_result": "follow-up goal resumed",
            }
        ],
        tags=["approval", "backlog"],
    )

    hit = memory.find_matching("continue blocked approval backlog")

    assert hit is not None
    assert hit.name == "Ops Routine"


def test_skill_memory_matches_description_and_tags_not_only_goal_pattern(tmp_path) -> None:
    memory = SkillMemory(path=str(tmp_path / "skills.jsonl"))
    memory.add_skill(
        name="General Operations",
        description="Triage policy denials and unblock approval-dependent tasks.",
        execution_steps=[{"tool": "internal", "action": "triage"}],
        tags=["policy", "approval"],
    )

    hit = memory.find_skill("policy denied approval path")

    assert hit is not None
    assert hit.name == "General Operations"


def test_lesson_memory_matches_tags_and_applicability_context(tmp_path) -> None:
    memory = LessonMemory(path=str(tmp_path / "lessons.jsonl"))
    memory.add(
        content="Escalate blocked flows through the control hub.",
        lesson_type="warning",
        applicability="paused follow up",
        tags=["approval", "blocked"],
    )

    hits = memory.get_relevant("blocked approval follow up", count=3)

    assert hits
    assert hits[0].lesson_type == "warning"


def test_action_trace_memory_matches_context_and_plan_not_only_goal(tmp_path) -> None:
    memory = ActionTraceMemory(path=str(tmp_path / "action_traces.jsonl"))
    trace = memory.begin_trace(
        goal="maintenance",
        context="approval backlog accumulated in control hub",
        plan_description="resume paused follow-up goals after approvals resolve",
        tags=["approval", "followup"],
    )
    memory.add_step(
        trace,
        description="continue blocked follow-up task",
        tool_call="task.continue",
        tool_result="task resumed",
    )
    memory.complete_trace(trace, success=True, result_summary="approval backlog reduced")

    hits = memory.search_similar("resume blocked approval backlog", count=3)

    assert hits
    assert hits[0].trace_id == trace.trace_id
