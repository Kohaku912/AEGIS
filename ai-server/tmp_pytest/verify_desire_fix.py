import json
from pathlib import Path
from aegis_ai.desire.desire_system import DesireSystem
from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

d = DesireSystem(data_dir="/app/data/desires")
print("pressures", {n: round(x.pressure,3) for n,x in d.get_all_desires().items()})
print("eta", round(d.seconds_until_threshold(5.0),1))
assert hasattr(AutonomousLoop, "_pressure_due")
s = json.loads(Path("/app/data/autonomous/loop_state.json").read_text())
print("skip", s.get("last_skip_reason"), "consec", s.get("consecutive_no_action"))
# confirm source has force_desire
src = Path("/app/src/aegis_ai/autonomous/autonomous_loop.py").read_text()
assert "force_desire" in src
assert "skipping LLM interval" in src
print("deploy_ok")
