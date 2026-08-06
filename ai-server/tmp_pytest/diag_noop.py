import json, time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

now = int(time.time()*1000)

s = json.loads(Path("/app/data/autonomous/loop_state.json").read_text())
print("=== LOOP ===")
for k in ["last_decision","last_skip_reason","last_no_action_reason","consecutive_no_action","selected_tool_count"]:
    print(f"  {k}: {s.get(k)}")
for k in ["last_llm_call_ms","last_run_ms","next_run_ms","last_action_ms"]:
    v=int(s.get(k) or 0)
    print(f"  {k}: age_s={round((now-v)/1000,1) if v else None}")

d = json.loads(Path("/app/data/desires/desire_state.json").read_text())
print("=== DESIRES ===")
for k,v in d.get("desires",{}).items():
    print(f"  {k} pressure={round(float(v.get('pressure') or 0),3)} value={v.get('value')} last_action_age_s={round((now-int(v.get('last_action_at') or 0))/1000,1)}")

print("=== EXEC LAST 25 ===")
lines = Path("/app/data/autonomous/execution_log.jsonl").read_text(encoding="utf-8").splitlines()[-25:]
dec=Counter(); reasons=Counter()
for line in lines:
    e=json.loads(line)
    t=int(e.get("timestamp_ms") or 0)
    dec[str(e.get("last_decision"))] += 1
    reasons[str(e.get("last_no_action_reason") or "")[:150]] += 1
    print(" ", datetime.fromtimestamp(t/1000,tz=timezone.utc).strftime("%m-%d %H:%M:%S"),
          e.get("last_decision"), "tools=", e.get("selected_tool_count"),
          "tasks=", len(e.get("tasks") or []), "results=", len(e.get("results") or []))
print("decisions", dict(dec))
print("reasons:")
for r,c in reasons.most_common(6):
    print("  ", c, r)
