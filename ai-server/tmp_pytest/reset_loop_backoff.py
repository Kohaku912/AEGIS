import json
from pathlib import Path
import time

path = Path("/app/data/autonomous/loop_state.json")
data = json.loads(path.read_text(encoding="utf-8"))
now = int(time.time() * 1000)
data["consecutive_no_action"] = 0
data["last_skip_reason"] = "desire_refill_reset"
data["last_no_action_reason"] = ""
data["next_run_ms"] = now + 1_800_000  # 30 min fallback; desire fire can still happen when pressure hits
data["last_llm_call_ms"] = now  # avoid immediate LLM spam; desire still drives after 30m pressure
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("loop_state reset", {k: data.get(k) for k in ["consecutive_no_action","next_run_ms","last_skip_reason"]})
