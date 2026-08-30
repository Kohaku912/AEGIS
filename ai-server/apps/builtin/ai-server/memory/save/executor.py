from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
SRC_DIR = os.path.join(ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from aegis_ai.llm.factory import create_llm_provider
from aegis_ai.memory.memory_ingest import save_memory_payload


data = json.loads(sys.stdin.read() or "{}")
content = str(data.get("content", "") or "").strip()
if not content:
    print(json.dumps({"ok": False, "error": "No content provided"}))
    sys.exit(1)

kind = str(data.get("type", "conversation") or "conversation").strip().lower()
needs_llm = kind not in {"person", "people", "persona", "entity", "contact", "profile"}
llm = None
if needs_llm:
    try:
        llm = create_llm_provider()
    except Exception:
        llm = None

data_root = os.environ.get("AEGIS_DATA_DIR") or os.path.join(ROOT, "data")
result = save_memory_payload(data, data_dir=data_root, llm_provider=llm)

try:
    from aegis_ai.runtime import peek_runtime

    runtime = peek_runtime()
    manager = getattr(runtime, "memory_manager", None) if runtime is not None else None
    if manager is not None and result.ok and "person_memory" not in result.saved_to:
        if manager.write_memory(content, memory_type="episodic", tags=["memory.save"]):
            result.saved_to.append("episodic")
except Exception:
    pass

print(json.dumps(result.to_dict(), ensure_ascii=False))
