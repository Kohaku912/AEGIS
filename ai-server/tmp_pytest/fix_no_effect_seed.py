#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

p = Path("/app/data/autonomous/loop_state.json")
d = json.loads(p.read_text(encoding="utf-8"))
counts = dict(d.get("no_effect_counts") or {})
# Keep sticky observe loops blocked; allow memory tools again.
for sticky in (
    "ai-server.agora.read_posts",
    "ai-server.commitment.list",
    "ai-server.situation.get",
):
    counts[sticky] = max(int(counts.get(sticky) or 0), 1)
for allow in (
    "ai-server.memory.search",
    "ai-server.memory.remember",
):
    counts.pop(allow, None)
d["no_effect_counts"] = counts
p.write_text(json.dumps(d, indent=2), encoding="utf-8")
print(json.dumps(counts, ensure_ascii=False, indent=2))
