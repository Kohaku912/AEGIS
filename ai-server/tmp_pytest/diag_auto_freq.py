from pathlib import Path
import json
from collections import Counter

state = json.loads(Path("/app/data/autonomous/loop_state.json").read_text(encoding="utf-8"))
keys = ["last_decision","last_skip_reason","last_no_action_reason","consecutive_no_action","last_llm_call_ms","last_run_ms","next_run_ms","selected_tool_count"]
print("===LOOP_STATE===")
for k in keys:
    print(f"{k}: {state.get(k)}")
last = int(state.get("last_run_ms") or 0)
nxt = int(state.get("next_run_ms") or 0)
llm = int(state.get("last_llm_call_ms") or 0)
print("next-last_s", round((nxt-last)/1000,1) if last and nxt else None)
print("last-llm_s", round((last-llm)/1000,1) if last and llm else None)

lines = Path("/app/data/autonomous/execution_log.jsonl").read_text(encoding="utf-8").splitlines()[-40:]
ts=[]; decisions=Counter(); skips=Counter()
print("===EXEC_LAST40===")
for line in lines:
    e=json.loads(line)
    t=int(e.get("timestamp_ms") or 0); ts.append(t)
    decisions[str(e.get("last_decision") or "")] += 1
    skips[str(e.get("last_no_action_reason") or e.get("last_skip_reason") or "")[:100]] += 1
print("intervals_s", [round((b-a)/1000,1) for a,b in zip(ts,ts[1:])][-15:])
print("decisions", dict(decisions))
print("reasons top", skips.most_common(8))

# observation cadence
obs = Path("/app/data/autonomous/observation_log.jsonl").read_text(encoding="utf-8").splitlines()[-20:]
ots=[]
for line in obs:
    e=json.loads(line); ots.append(int(e.get("timestamp_ms") or 0))
print("===OBS_INTERVALS===")
print([round((b-a)/1000,1) for a,b in zip(ots,ots[1:])][-10:])
if obs:
    e=json.loads(obs[-1])
    for o in (e.get("observations") or [])[:4]:
        print("OBS", o.get("source"), o.get("observation_type"), o.get("tags"), str(o.get("description") or "")[:120])

from aegis_ai.task.task_manager import TaskManager
tm=TaskManager(data_dir="/app/data/tasks")
print("open_incidents", len(tm.list_open_incidents(limit=5000)))
