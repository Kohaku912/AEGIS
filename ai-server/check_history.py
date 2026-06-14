import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

desire_path = Path("data/desires/desire_state.json")
if desire_path.exists():
    with open(desire_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for name, info in data.get("desires", {}).items():
        if isinstance(info, dict):
            history = info.get("update_history", [])
            val = info.get("value", 0)
            print(f"{name}: value={val:.1f}, updates={len(history)}")
            for h in history[-2:]:
                ts = h.get("ts", 0)
                old = h.get("old", 0)
                new = h.get("new", 0)
                reason = h.get("reason", "")[:80]
                print(f"  [{ts}] {old:.1f} -> {new:.1f}: {reason}")
