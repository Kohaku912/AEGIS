import json
from pathlib import Path

# Check desire state
desire_path = Path("data/desires/desire_state.json")
if desire_path.exists():
    with open(desire_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("=== Desire State ===")
    for name, info in data.get("desires", {}).items():
        if isinstance(info, dict):
            val = info.get("value", 0)
            exp = info.get("expected_value", 0)
            print(f"  {name}: value={val:.1f}, expected={exp:.1f}, gap={exp - val:.1f}")
        else:
            print(f"  {name}: {info}")
else:
    print("No desire state file found")

# Check autonomous loop state
loop_path = Path("data/autonomous/loop_state.json")
if loop_path.exists():
    with open(loop_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("\n=== Autonomous Loop State ===")
    print(json.dumps(data, indent=2))
else:
    print("\nNo autonomous loop state file found")

# Check execution log
log_path = Path("data/autonomous/execution_log.jsonl")
if log_path.exists():
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    print(f"\n=== Execution Log ({len(lines)} entries) ===")
    for line in lines[-3:]:
        if line.strip():
            entry = json.loads(line)
            ts = entry.get("timestamp_ms", 0)
            tasks = entry.get("tasks", [])
            results = entry.get("results", [])
            print(f"  [{ts}] {len(tasks)} tasks, {len(results)} results")
else:
    print("\nNo execution log found")
