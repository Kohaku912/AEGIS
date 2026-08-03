import json, os
from aegis_ai.desire.desire_system import DesireSystem
ds=DesireSystem(data_dir="/app/data/desires")
ds.apply_decay()
print("stats", json.dumps(ds.get_stats(), ensure_ascii=False)[:800])
print("---")
print("pressure", json.dumps(ds.get_pressure_state(), ensure_ascii=False)[:800])
