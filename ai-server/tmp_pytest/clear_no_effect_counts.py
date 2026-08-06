#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

p = Path("/app/data/autonomous/loop_state.json")
d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
d["no_effect_counts"] = {}
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(d, indent=2), encoding="utf-8")
print("cleared_no_effect_counts")
print("last_decision", d.get("last_decision"))
