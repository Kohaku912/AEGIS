import json, time
from pathlib import Path

now = int(time.time() * 1000)

# Clear gates so desire refill can own pacing
loop_path = Path("/app/data/autonomous/loop_state.json")
data = json.loads(loop_path.read_text(encoding="utf-8"))
data["consecutive_no_action"] = 0
data["last_skip_reason"] = "desire_pacing_reset"
data["last_no_action_reason"] = ""
# Allow desire fire as soon as pressure hits threshold (~30m from now)
data["last_llm_call_ms"] = now - 1_800_000
data["next_run_ms"] = now + 1_800_000
loop_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("loop reset")

# Start pressure accumulation from 0 with current last_updated
from aegis_ai.desire.desire_system import DesireSystem
d = DesireSystem(data_dir="/app/data/desires")
for name, obj in d.get_all_desires().items():
    if obj.hidden:
        continue
    obj.pressure = 0.0
    obj.last_updated_at = now
    if d._pressure_engine is not None:
        d._pressure_engine._pressures[name] = 0.0
        d._pressure_engine._drift_rates[name] = 0.0
d._save()
print("desire reset pressures", {n: x.pressure for n,x in d.get_all_desires().items()})
print("eta_s", d.seconds_until_threshold(5.0))
