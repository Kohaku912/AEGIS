#!/usr/bin/env python3
import json
from pathlib import Path

p = Path("/tmp/aegis-cam/pin_sweep_safe2/results.jsonl")
rows = [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
rows.sort(key=lambda r: r["delta"])
print("n", len(rows))
print(f"{'board':>5} {'soc':<6} {'bright':>7} {'delta':>7}")
for r in rows:
    print(f"{r['board']:>5} {r['soc']:<6} {r['brightness']:>7.2f} {r['delta']:>+7.2f}")
print("best", rows[0] if rows else None)
if rows and rows[0]["delta"] <= -15:
    print("LIKELY_HIT")
elif rows:
    print("NO_CLEAR_HIT")
