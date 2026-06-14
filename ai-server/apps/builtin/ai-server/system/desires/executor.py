import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))
from aegis_ai.desire.desire_system import DesireSystem

data = json.loads(sys.stdin.read())
data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'desires')
ds = DesireSystem(data_dir=os.path.abspath(data_dir))
desires = []
for name, d in ds.get_all_desires().items():
    frustration = max(0, d.expected_value - d.value)
    desires.append(f"- {name}: {d.value:.1f}/10 (expected {d.expected_value:.1f}, frustration {frustration:.1f})")
print(json.dumps({"ok": True, "result": "Desire States:\n" + "\n".join(desires)}))
