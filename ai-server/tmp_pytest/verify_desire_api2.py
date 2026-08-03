from aegis_ai.desire.desire_system import DesireSystem
import json
ds=DesireSystem(data_dir="/app/data/desires")
ds.apply_decay()
print(json.dumps({"stats": {k: ds.get_stats()[k] for k in ["pressures","average_pressure","seconds_until_threshold"]}, "sample": ds.get_pressure_state()["user_support"]}, ensure_ascii=False, indent=2))
