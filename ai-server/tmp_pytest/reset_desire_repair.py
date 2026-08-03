import json
from pathlib import Path

# Reset sticky desire pressures so refill starts clean (~30m to threshold)
desire_path = Path("/app/data/desires/desire_state.json")
pressure_path = Path("/app/data/desires/pressure/pressure_state.json")
if desire_path.exists():
    data = json.loads(desire_path.read_text(encoding="utf-8"))
    for _name, dim in (data.get("desires") or {}).items():
        dim["pressure"] = 0.0
        dim["drift_rate"] = 0.0
    desire_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("reset desire_state pressures")
if pressure_path.exists():
    data = json.loads(pressure_path.read_text(encoding="utf-8"))
    data["pressures"] = {
        k: 0.0 for k in (data.get("pressures") or {"user_support": 0, "social": 0, "growth": 0})
    }
    data["drift_rates"] = {k: 0.0 for k in data["pressures"]}
    pressure_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("reset pressure_state", data["pressures"])

from aegis_ai.personal_ai.repair import RepairManager

rm = RepairManager(data_dir="/app/data/personal_ai")
result = rm.dismiss_matching(
    categories={
        "transient",
        "server_down",
        "llm_failed",
        "permission",
        "auth",
        "policy_denied",
        "validation",
        "tool_failed",
    },
    final_results={"recorded", "needs_followup", "rollback_failed", "not_retryable"},
    error_substrings=[
        "android",
        "unavailable",
        "timeout",
        "browserstartevent",
        "permission",
        "locked",
        "dev-server",
        "unavail",
    ],
    dry_run=False,
    limit=2000,
)
print("dismissed", result)

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.desire.desire_system import DesireSystem

assert hasattr(AutonomousLoop, "_compute_idle_sleep_seconds")
assert hasattr(DesireSystem, "release_cycle_pressure")
print("ok")
