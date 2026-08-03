import json, time
from pathlib import Path
from datetime import datetime, timezone

now = int(time.time()*1000)
print("now", datetime.fromtimestamp(now/1000, tz=timezone.utc).isoformat())

d = json.loads(Path("/app/data/desires/desire_state.json").read_text())
print("file pressures", {k: round(float(v.get("pressure") or 0),3) for k,v in d.get("desires",{}).items()})
print("saved_at age_s", round((now-int(d.get("saved_at_ms") or 0))/1000,1))
for k,v in d.get("desires",{}).items():
    lu=int(v.get("last_updated_at") or 0)
    print(k, "last_updated_age_s", round((now-lu)/1000,1) if lu else None)

p = Path("/app/data/desires/pressure/pressure_state.json")
if p.exists():
    pd=json.loads(p.read_text())
    print("engine", {k: round(float(v),3) for k,v in (pd.get("pressures") or {}).items()})

s=json.loads(Path("/app/data/autonomous/loop_state.json").read_text())
print("loop", {k:s.get(k) for k in ["last_decision","last_skip_reason","consecutive_no_action"]})
for k in ["last_llm_call_ms","last_run_ms","next_run_ms"]:
    v=int(s.get(k) or 0)
    print(k, "age_s", round((now-v)/1000,1) if v else None, "in_s", round((v-now)/1000,1) if v and v>now else None)

# Live DesireSystem
from aegis_ai.desire.desire_system import DesireSystem
ds=DesireSystem(data_dir="/app/data/desires")
print("loaded", {n: round(x.pressure,3) for n,x in ds.get_all_desires().items()})
ds.apply_decay()
print("after_decay", {n: round(x.pressure,3) for n,x in ds.get_all_desires().items()})
print("eta", round(ds.seconds_until_threshold(5.0),1))
