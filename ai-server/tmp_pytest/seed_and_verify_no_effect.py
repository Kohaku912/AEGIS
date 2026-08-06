#!/usr/bin/env python3
"""Seed sticky no_effect denylist and print verification."""
from __future__ import annotations

import json
from pathlib import Path

p = Path("/app/data/autonomous/loop_state.json")
d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
counts = dict(d.get("no_effect_counts") or {})
for cap in (
    "ai-server.agora.read_posts",
    "ai-server.commitment.list",
    "ai-server.situation.get",
):
    counts[cap] = max(int(counts.get(cap) or 0), 1)
d["no_effect_counts"] = counts
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(d, indent=2), encoding="utf-8")
print("seeded_no_effect", json.dumps(counts, ensure_ascii=False))
print("last_decision", d.get("last_decision"))
print("consecutive_no_action", d.get("consecutive_no_action"))
