from __future__ import annotations

from aegis_ai.memory.advanced import AdvancedMemory, ConversationEntry, Fact
from aegis_ai.memory.memory_manager import MemoryManager
from aegis_ai.memory.episodic import EpisodicMemory


def test_get_context_includes_short_and_long_term_without_substring_query(tmp_path) -> None:
    memory = AdvancedMemory(data_dir=str(tmp_path / "memory"))
    memory._conversations = [
        ConversationEntry(
            entry_id="c1",
            user_msg="今日は部屋の照明を消して",
            bot_msg="わかりました、オフにします",
            timestamp_ms=1,
        ),
        ConversationEntry(
            entry_id="c2",
            user_msg="名前は河原です",
            bot_msg="覚えました",
            timestamp_ms=2,
        ),
    ]
    memory._facts["f1"] = Fact(
        fact_id="f1",
        content="User's name is 河原",
        subject="user",
        predicate="name",
        object="河原",
        importance=0.9,
        valid_at_ms=1,
    )

    context = memory.get_context("照明の話は覚えてる？")
    assert "Recent conversations (short-term memory)" in context
    assert "Stable knowledge (long-term memory)" in context
    assert "河原" in context
    assert "部屋の照明" in context


def test_encode_conversation_writes_advanced_and_episodic(tmp_path) -> None:
    advanced = AdvancedMemory(data_dir=str(tmp_path / "memory"))
    episodic = EpisodicMemory(path=str(tmp_path / "episodic.jsonl"))
    manager = MemoryManager(advanced_memory=advanced, episodic_memory=episodic)

    result = manager.encode_conversation("覚えて: 好きな色は青", "了解しました", source="test")
    assert result["advanced"] is True
    assert result["episodic"] is True
    assert advanced.get_recent_conversations(limit=1)
    assert episodic.list_recent(1, category="conversation")
