from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
SRC_DIR = os.path.join(ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from aegis_ai.memory.sleep_consolidation import SleepConsolidationSystem


def run(payload: dict) -> dict:
    reason = str(payload.get("reason", "manual") or "manual").strip()

    data_dir = os.path.join(ROOT, "data", "memory")
    try:
        sleep = SleepConsolidationSystem(data_dir=data_dir)
        result = sleep.consolidate()
        return {
            "ok": True,
            "result": f"Memory consolidation completed. {result.get('episodes_summarized', 0)} episodes summarized, {result.get('lessons_extracted', 0)} lessons extracted.",
            "detail": result,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    data = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(run(data), ensure_ascii=False))
