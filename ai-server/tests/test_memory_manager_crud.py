from aegis_ai.memory.memory_manager import MemoryManager
from aegis_ai.memory.memory_store import MemoryStore


def test_preference_write_search_update_and_forget_are_real(tmp_path):
    store = MemoryStore(tmp_path / "memory-store")
    manager = MemoryManager(memory_store=store)

    memory_id = manager.write_memory(
        "Prefers concise operational summaries",
        memory_type="preference",
        source_task_id="task-1",
        confidence=0.9,
        importance=0.8,
        tags=["communication"],
    )

    hits = manager.search_memory("concise", types=["preference"], limit=10)
    assert memory_id
    assert hits[0]["memory_id"] == memory_id
    assert hits[0]["confidence"] == 0.9

    updated = manager.update_memory(memory_id, {"importance": 0.95, "unknown": "ignored"})
    assert updated is not None
    assert updated["importance"] == 0.95
    assert "unknown" not in updated

    assert manager.forget(memory_id) is True
    assert manager.get_memory(memory_id) is None


def test_forget_does_not_report_mock_success_without_owning_backend():
    manager = MemoryManager()
    assert manager.forget("missing") is False
