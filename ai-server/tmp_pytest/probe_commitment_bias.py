#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

p = Path("/app/data/autonomous/execution_log.jsonl")
raw = Counter()
caps = Counter()
with p.open(errors="replace") as f:
    for line in f:
        if "nsupported" not in line and "unsupported" not in line.lower():
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        for i, r in enumerate(e.get("results") or []):
            text = str(r.get("result") or r.get("error") or "")
            if "nsupported" in text or "unsupported" in text.lower():
                raw[text[:220]] += 1
                tasks = e.get("tasks") or []
                if i < len(tasks):
                    caps[str(tasks[i].get("capability_id"))] += 1

print("raw", raw.most_common(15))
print("caps", caps.most_common(15))
state = json.loads(Path("/app/data/autonomous/loop_state.json").read_text())
print("SKIP:\n", state.get("last_skip_reason"))
print("no_effect", state.get("no_effect_counts"))

# recent task caps last 50 with tasks
recent_caps = Counter()
n = 0
for line in reversed(p.read_text(errors="replace").splitlines()):
    try:
        e = json.loads(line)
    except Exception:
        continue
    tasks = e.get("tasks") or []
    if not tasks:
        continue
    for t in tasks:
        recent_caps[str(t.get("capability_id"))] += 1
    n += 1
    if n >= 80:
        break
print("recent80_with_tasks", recent_caps.most_common(20))
