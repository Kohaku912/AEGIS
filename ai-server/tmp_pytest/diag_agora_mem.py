import json, time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

now = int(time.time()*1000)
lines = Path("/app/data/autonomous/execution_log.jsonl").read_text(encoding="utf-8").splitlines()[-40:]
print("=== EXEC LAST", len(lines), "===")
caps=Counter(); effects=Counter(); decisions=Counter()
for line in lines:
    e=json.loads(line)
    t=int(e.get("timestamp_ms") or 0)
    decisions[str(e.get("last_decision"))] += 1
    tasks=e.get("tasks") or []
    results=e.get("results") or []
    caps_this=[t.get("capability_id") or t.get("action") for t in tasks]
    for c in caps_this: caps[str(c)] += 1
    print(datetime.fromtimestamp(t/1000,tz=timezone.utc).strftime("%m-%d %H:%M:%S"),
          e.get("last_decision"), "tools=", e.get("selected_tool_count"),
          "caps=", caps_this)
print("cap counts", dict(caps.most_common(15)))
print("decisions", dict(decisions))

# desire state
d=json.loads(Path("/app/data/desires/desire_state.json").read_text())
print("=== DESIRES ===")
for k,v in d.get("desires",{}).items():
    print(k, "pressure=", round(float(v.get("pressure") or 0),3), "value=", v.get("value"))

# audit fulfillment
audit=Path("/app/data/audit.jsonl")
rows=[]
if audit.exists():
    for line in audit.read_text(encoding="utf-8", errors="replace").splitlines()[-3000:]:
        try: e=json.loads(line)
        except: continue
        if e.get("action") in {"autonomous_fulfillment_evaluated","autonomous_action_selected","autonomous_no_action"}:
            rows.append(e)
print("=== FULFILLMENT AUDIT", len(rows), "===")
for e in rows[-15:]:
    det=e.get("detail") or {}
    print(e.get("action"), e.get("decision"), e.get("capability_id"),
          "score=", det.get("fulfillment_score"), "pressure=", det.get("pressure_reduction"),
          "eval=", (det.get("details") or {}).get("evaluator"),
          "reason=", str(e.get("reason") or "")[:120])
