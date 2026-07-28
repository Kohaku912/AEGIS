from __future__ import annotations

from pathlib import Path

from aegis_ai.jsonl_tail import append_jsonl, read_jsonl_tail
from aegis_ai.memory.action_trace import ActionTraceMemory, TraceStatus
from aegis_ai.memory.experiential import ExperientialMemory


def test_jsonl_tail_reads_only_recent_rows(tmp_path: Path):
    path = tmp_path / "events.jsonl"
    for i in range(50):
        append_jsonl(path, {"i": i, "payload": "x" * 20})
    rows = read_jsonl_tail(path, 5)
    assert [row["i"] for row in rows] == [45, 46, 47, 48, 49]
    assert path.read_text(encoding="utf-8").count("\n") == 50


def test_action_trace_keeps_full_disk_history_but_hot_memory(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AEGIS_HOT_ACTION_TRACES", "3")
    path = tmp_path / "action_traces.jsonl"
    atm = ActionTraceMemory(path=str(path))
    for i in range(8):
        trace = atm.begin_trace(goal=f"goal-{i}")
        atm.complete_trace(trace, success=True, result_summary=f"ok-{i}")
    assert path.read_text(encoding="utf-8").count("\n") == 8
    assert len(atm._traces) <= 3

    reloaded = ActionTraceMemory(path=str(path))
    assert len(reloaded._traces) <= 3
    assert all(t.status != TraceStatus.RUNNING for t in reloaded._traces.values())


def test_experiential_append_only_preserves_history(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AEGIS_HOT_EXPERIENCES", "3")
    mem = ExperientialMemory(data_dir=str(tmp_path), max_entries=100)
    for i in range(6):
        mem.record_experience(action=f"act-{i}", observation=f"obs-{i}")
    path = tmp_path / "experiences.jsonl"
    assert path.read_text(encoding="utf-8").count("\n") == 6
    assert len(mem._experiences) == 3

    reloaded = ExperientialMemory(data_dir=str(tmp_path), max_entries=100)
    assert len(reloaded._experiences) == 3
    assert reloaded._experiences[-1].action == "act-5"
