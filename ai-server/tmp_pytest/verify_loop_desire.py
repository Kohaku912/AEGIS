import json
from pathlib import Path

s = json.loads(Path("/app/data/autonomous/loop_state.json").read_text(encoding="utf-8"))
print(
    {
        k: s.get(k)
        for k in [
            "last_skip_reason",
            "consecutive_no_action",
            "next_run_ms",
            "last_run_ms",
            "last_decision",
        ]
    }
)
d = json.loads(Path("/app/data/desires/desire_state.json").read_text(encoding="utf-8"))
print("pressures", {k: v.get("pressure") for k, v in d.get("desires", {}).items()})
