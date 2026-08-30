from __future__ import annotations

from aegis_ai.backup.retention import RetentionManager
from aegis_ai.llm.memory_context import build_shared_memory_context
from aegis_ai.memory.advanced import AdvancedMemory
from aegis_ai.memory.episodic_memory import EpisodicMemory
from aegis_ai.memory.memory_manager import MemoryManager
from aegis_ai.memory.memory_store import MemoryStore
from aegis_ai.memory.memory_types import MemoryRecord, MemoryType


def test_encode_conversation_writes_production_episodic_jsonl(tmp_path) -> None:
    path = tmp_path / "episodic.jsonl"
    manager = MemoryManager(
        advanced_memory=AdvancedMemory(data_dir=str(tmp_path / "memory")),
        episodic_memory=EpisodicMemory(path=str(path)),
    )
    result = manager.encode_conversation("好きな色は青", "了解しました", source="test")
    assert result["advanced"] is True
    assert result["episodic"] is True
    assert path.exists()
    reloaded = EpisodicMemory(path=str(path))
    recent = reloaded.recall_recent(count=1, category="conversation")
    assert recent
    assert "青" in recent[0].action


def test_search_memory_uses_recall_similar_and_store_lessons(tmp_path) -> None:
    episodic = EpisodicMemory(path=str(tmp_path / "episodic.jsonl"))
    episodic.record("opened AGORA", "three new posts", category="autonomous", tags=["social"])
    store = MemoryStore(tmp_path / "memory_store")
    store.add_memory(
        MemoryRecord(
            memory_type=MemoryType.DESIRE_LESSON.value,
            title="social: agora.read_posts -> useful",
            content="Reading AGORA reduced social pressure.",
            importance=0.8,
        )
    )
    manager = MemoryManager(episodic_memory=episodic, memory_store=store)
    hits = manager.search_memory("AGORA", types=["episodic", "desire_lesson"], limit=10)
    kinds = {hit["memory_type"] for hit in hits}
    assert "episodic" in kinds
    assert "desire_lesson" in kinds


def test_deduplicate_merges_same_title_desire_lessons(tmp_path) -> None:
    store = MemoryStore(tmp_path / "memory_store")
    store.add_memory(MemoryRecord(memory_type=MemoryType.DESIRE_LESSON.value, title="social: read", content="a"))
    store.add_memory(MemoryRecord(memory_type=MemoryType.DESIRE_LESSON.value, title="social: read", content="b"))
    manager = MemoryManager(memory_store=store)
    assert manager.deduplicate() == 1
    active = [r for r in store.get_all() if r.memory_type == MemoryType.DESIRE_LESSON.value and not r.superseded_by]
    assert len(active) == 1


def test_shared_context_includes_desire_lesson(tmp_path) -> None:
    data_dir = tmp_path / "data"
    store = MemoryStore(data_dir / "memory_store")
    store.add_memory(
        MemoryRecord(
            memory_type=MemoryType.DESIRE_LESSON.value,
            title="growth: search.web -> useful",
            content="Web search taught a new fact.",
            importance=0.9,
        )
    )
    context = build_shared_memory_context(query="growth", data_dir=str(data_dir), profile="decision")
    assert "Desire lessons:" in context.text
    assert "search.web" in context.text


def test_mark_consolidated_persists_rewrite(tmp_path) -> None:
    path = tmp_path / "episodic.jsonl"
    mem = EpisodicMemory(path=str(path))
    ep = mem.record("chat", "hello")
    mem.mark_consolidated(ep.episode_id, "summarized")
    reloaded = EpisodicMemory(path=str(path))
    assert reloaded._index[ep.episode_id].consolidated is True
    assert reloaded._index[ep.episode_id].summary == "summarized"


def test_retention_prunes_expired_store_records(tmp_path) -> None:
    store = MemoryStore(tmp_path / "memory_store")
    store.add_memory(
        MemoryRecord(
            memory_type=MemoryType.DESIRE_LESSON.value,
            title="expired",
            content="old",
            expires_at=1,
        )
    )
    cleaned = RetentionManager(memory_store=store).cleanup_expired()
    assert cleaned["expired_store"] == 1
    assert store.count() == 0
