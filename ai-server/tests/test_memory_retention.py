from __future__ import annotations

from aegis_ai.backup.retention import RetentionManager
from aegis_ai.memory.consolidation import MemoryConsolidator
from aegis_ai.memory.episodic_memory import EpisodicMemory


def test_episodic_prune_and_delete(tmp_path) -> None:
    mem = EpisodicMemory(path=str(tmp_path / "episodic.jsonl"))
    ep = mem.record(action="old", observation="stale")
    ep.timestamp_ms = 1
    mem._rewrite()
    assert mem.prune_expired(now_ms=1_000_000, max_age_ms=100) == 1
    assert mem.delete("missing") is False


def test_retention_deletes_episodic_entry(tmp_path) -> None:
    mem = EpisodicMemory(path=str(tmp_path / "episodic.jsonl"))
    ep = mem.record(action="keep-or-drop", observation="x")
    manager = RetentionManager(episodic_memory=mem)
    assert manager.delete_memory_entry("episode", ep.episode_id) is True
    assert mem.delete(ep.episode_id) is False


def test_consolidator_prunes_expired(tmp_path) -> None:
    mem = EpisodicMemory(path=str(tmp_path / "episodic.jsonl"))
    ep = mem.record(action="old", observation="stale")
    ep.timestamp_ms = 1
    mem._rewrite()
    consolidator = MemoryConsolidator(episodic_memory=mem)
    assert consolidator._consolidate_episodic() >= 1
