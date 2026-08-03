import json, time
from pathlib import Path

# Simulate apply_decay from disk state as of last_updated
from aegis_ai.desire.desire_system import DesireSystem
d = DesireSystem(data_dir="/app/data/desires")
print("loaded pressures", {n: x.pressure for n,x in d.get_all_desires().items()})
print("eta", d.seconds_until_threshold(5.0))
before = {n: x.last_updated_at for n,x in d.get_all_desires().items()}
d.apply_decay()
print("after apply", {n: (x.pressure, x.last_updated_at) for n,x in d.get_all_desires().items()})
print("eta2", d.seconds_until_threshold(5.0))

# How often would loop wake while gated?
state=json.loads(Path("/app/data/autonomous/loop_state.json").read_text())
print("skip", state.get("last_skip_reason"), "consec", state.get("consecutive_no_action"))
