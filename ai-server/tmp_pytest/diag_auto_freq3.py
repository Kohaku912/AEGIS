from pathlib import Path
import json
from collections import Counter

# operations timestamps fields
ops = Path("/app/data/operations/operations.jsonl").read_text(encoding="utf-8").splitlines()[-50:]
print("===OPS_KEYS===")
e=json.loads(ops[-1])
print(sorted(e.keys()))
print({k:e.get(k) for k in ["operation_id","kind","outcome","started_ms","ended_ms","created_at_ms","timestamp_ms","title","summary","why","result"]})

# cadence of operations by any time field
times=[]
for line in ops:
    r=json.loads(line)
    t = r.get("started_ms") or r.get("created_at_ms") or r.get("ended_ms") or r.get("timestamp_ms") or 0
    times.append(int(t or 0))
print("ops_intervals_s", [round((b-a)/1000,1) for a,b in zip(times,times[1:]) if a and b][-15:])
print("ops_outcomes", Counter(json.loads(l).get("outcome") for l in ops))

# loop state desires / pressure
state=json.loads(Path("/app/data/autonomous/loop_state.json").read_text(encoding="utf-8"))
print("===STATE_EXTRA===")
for k in sorted(state.keys()):
    if any(x in k for x in ["pressure","desire","pending","bypass","decision","skip","consecutive","interval","observation"]):
        v=state[k]
        if isinstance(v,(dict,list)) and len(str(v))>200: v=str(v)[:200]
        print(k, ":", v)

# find obligation builder
from aegis_ai.agency import state as st
print("agency.state attrs", [a for a in dir(st) if not a.startswith("_")][:40])
