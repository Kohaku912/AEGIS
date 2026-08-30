from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
SRC_DIR = os.path.join(ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def _data_root() -> str:
    return os.environ.get("AEGIS_DATA_DIR") or os.path.join(ROOT, "data")


def run(payload: dict) -> dict:
    reason = str(payload.get("reason", "manual") or "manual").strip() or "manual"
    try:
        from aegis_ai.runtime import peek_runtime

        runtime = peek_runtime()
        sleep_manager = getattr(runtime, "sleep_manager", None) if runtime is not None else None
        if sleep_manager is not None:
            started = bool(sleep_manager.start_sleep(reason=reason))
            status = sleep_manager.get_status() if hasattr(sleep_manager, "get_status") else {}
            return {
                "ok": True,
                "started": started,
                "status": status,
                "result": "Memory sleep consolidation has started." if started else "Memory sleep is already running.",
                "detail": status.get("last_summary") or {},
            }
    except Exception:
        pass

    data_root = _data_root()
    memory_dir = os.path.join(data_root, "memory")
    try:
        from aegis_ai.memory.association_memory import AssociationMemory
        from aegis_ai.memory.episodic_memory import EpisodicMemory
        from aegis_ai.memory.experiential import ExperientialMemory
        from aegis_ai.memory.lesson_memory import LessonMemory
        from aegis_ai.memory.memory_store import MemoryStore
        from aegis_ai.memory.person_memory import PersonMemory
        from aegis_ai.memory.semantic_memory import SemanticMemory
        from aegis_ai.memory.skill_memory import SkillMemory
        from aegis_ai.memory.sleep_consolidation import SleepConsolidationSystem
        from aegis_ai.memory.workflow_memory import WorkflowMemory

        sleep = SleepConsolidationSystem(
            episodic=EpisodicMemory(path=os.path.join(memory_dir, "episodic.jsonl")),
            semantic=SemanticMemory(path=os.path.join(memory_dir, "semantic.jsonl")),
            person=PersonMemory(path=os.path.join(memory_dir, "persons.jsonl")),
            association=AssociationMemory(path=os.path.join(memory_dir, "associations.jsonl")),
            experiential=ExperientialMemory(data_dir=memory_dir),
            lesson=LessonMemory(path=os.path.join(memory_dir, "lessons.jsonl")),
            workflow=WorkflowMemory(path=os.path.join(memory_dir, "workflows.jsonl")),
            skill=SkillMemory(path=os.path.join(memory_dir, "skills.jsonl")),
            data_dir=memory_dir,
        )
        result = sleep.consolidate()
        result["expired_store"] = MemoryStore(data_dir=os.path.join(data_root, "memory_store")).prune_expired()
        return {
            "ok": True,
            "result": (
                f"Memory consolidation completed. {result.get('episodes_summarized', 0)} episodes summarized, "
                f"{result.get('lessons_extracted', 0)} lessons extracted."
            ),
            "detail": result,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    data = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(run(data), ensure_ascii=False))
