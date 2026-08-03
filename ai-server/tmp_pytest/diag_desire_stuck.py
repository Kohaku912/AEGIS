import json, time
from pathlib import Path
from datetime import datetime, timezone

now = int(time.time() * 1000)
print("now", now, datetime.fromtimestamp(now/1000, tz=timezone.utc).isoformat())

# Desire state
for p in [
    Path("/app/data/desires/desire_state.json"),
    Path("/app/data/desires/pressure/pressure_state.json"),
    Path("/app/data/autonomous/loop_state.json"),
]:
    print("\n===", p, "exists", p.exists())
    if not p.exists():
        continue
    data = json.loads(p.read_text(encoding="utf-8"))
    if "desires" in data:
        for k,v in data["desires"].items():
            print(k, "pressure", v.get("pressure"), "last_updated", v.get("last_updated_at"),
                  "age_s", round((now - int(v.get("last_updated_at") or 0))/1000,1) if v.get("last_updated_at") else None,
                  "last_action", v.get("last_action_at"))
        print("saved_at", data.get("saved_at_ms"))
    elif "pressures" in data:
        print("pressures", data.get("pressures"))
        print("drift", data.get("drift_rates"))
        print("last_updated", data.get("last_updated_ms"),
              "age_s", round((now-int(data.get("last_updated_ms") or 0))/1000,1) if data.get("last_updated_ms") else None)
    else:
        keys = ["last_decision","last_skip_reason","consecutive_no_action","last_llm_call_ms","last_run_ms","next_run_ms","running"]
        for k in keys:
            v = data.get(k)
            if k.endswith("_ms") and v:
                print(k, v, "age_s", round((now-int(v))/1000,1), datetime.fromtimestamp(int(v)/1000, tz=timezone.utc).isoformat())
            else:
                print(k, v)
        if data.get("next_run_ms"):
            print("next_in_s", round((int(data["next_run_ms"])-now)/1000,1))

# observation / exec recent
for name in ["observation_log.jsonl","execution_log.jsonl"]:
    p = Path("/app/data/autonomous")/name
    if not p.exists():
        print(name, "missing"); continue
    lines = p.read_text(encoding="utf-8").splitlines()
    print(f"\n{name} lines={len(lines)} last:")
    if lines:
        e=json.loads(lines[-1])
        t=int(e.get("timestamp_ms") or 0)
        print(" age_s", round((now-t)/1000,1) if t else None, "keys", list(e.keys())[:8])
