from pathlib import Path
import json
from collections import Counter
from datetime import datetime, timezone

# Recent operations
ops_path = Path("/app/data/operations")
files = sorted(ops_path.glob("*.jsonl")) if ops_path.exists() else []
print("ops_files", [str(f) for f in files[-3:]])
rows=[]
for f in files[-2:]:
    for line in f.read_text(encoding="utf-8").splitlines()[-200:]:
        try: rows.append(json.loads(line))
        except: pass
rows = sorted(rows, key=lambda r: int(r.get("started_at_ms") or r.get("timestamp_ms") or 0))[-30:]
print("===OPS_LAST30===")
for r in rows:
    t=int(r.get("started_at_ms") or r.get("timestamp_ms") or 0)
    print(datetime.fromtimestamp(t/1000, tz=timezone.utc).isoformat(), r.get("kind") or r.get("type") or r.get("source"), r.get("outcome") or r.get("status"), str(r.get("title") or r.get("summary") or "")[:100])

# obligation sources in agency
from aegis_ai.agency.state import AgencyStateBuilder
# find how obligations built
print("\n===OBLIGATION_PROBE===")
# inspect latest observation full
obs = Path("/app/data/autonomous/observation_log.jsonl").read_text(encoding="utf-8").splitlines()[-3:]
for line in obs:
    e=json.loads(line)
    print("ts", e.get("timestamp_ms"), "n", len(e.get("observations") or []))
    for o in e.get("observations") or []:
        print(" ", o.get("source"), o.get("observation_type"), o.get("tags"), str(o.get("description") or "")[:160])
        if o.get("payload"):
            p=o.get("payload")
            if isinstance(p, dict):
                print("   payload_keys", list(p.keys())[:12])
                if "obligations" in p: print("   obligations", p.get("obligations")[:3])
                if "items" in p: print("   items_sample", str(p.get("items"))[:300])

# event_observe_more path - check loop decisions around evaluate_event
lines = Path("/app/data/autonomous/execution_log.jsonl").read_text(encoding="utf-8").splitlines()[-5:]
for line in lines:
    e=json.loads(line)
    print("EXEC", {k:e.get(k) for k in ["timestamp_ms","last_decision","last_skip_reason","last_no_action_reason","selected_tool_count","trigger_reason","source"] if k in e or True})
