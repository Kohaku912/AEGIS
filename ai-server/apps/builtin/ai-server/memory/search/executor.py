from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
SRC_DIR = os.path.join(ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

data = json.loads(sys.stdin.read() or "{}")
query = str(data.get("query", "") or "").strip()
if not query:
    print(json.dumps({"ok": False, "error": "No query provided"}))
    sys.exit(1)

limit = min(max(int(data.get("limit") or 10), 1), 50)
hits = []

try:
    from aegis_ai.runtime import peek_runtime

    runtime = peek_runtime()
    manager = getattr(runtime, "memory_manager", None) if runtime is not None else None
    if manager is not None and hasattr(manager, "search_memory"):
        hits = manager.search_memory(query, limit=limit)
except Exception:
    hits = []

if not hits:
    from aegis_ai.memory.advanced import AdvancedMemory
    from aegis_ai.memory.memory_store import MemoryStore

    data_root = os.environ.get("AEGIS_DATA_DIR") or os.path.join(ROOT, "data")
    advanced = AdvancedMemory(data_dir=os.path.join(data_root, "memory"))
    context = advanced.get_context(query)
    if context:
        hits.append({"type": "advanced", "content": context, "source": "advanced"})
    store = MemoryStore(data_dir=os.path.join(data_root, "memory_store"))
    for record in store.search_memories(query=query, limit=limit):
        hits.append({"type": record.memory_type, "content": record.to_context_string(240), "source": "store"})

print(json.dumps({
    "ok": True,
    "query": query,
    "results": hits[:limit],
    "result": "No memory found." if not hits else f"Found {len(hits[:limit])} memory item(s).",
}))
