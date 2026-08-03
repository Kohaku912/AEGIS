from pathlib import Path
import json
from collections import Counter

# Live agent state obligations
from aegis_ai.runtime import get_runtime
rt = get_runtime()
builder = getattr(rt, "agent_state_builder", None) or getattr(rt, "_agent_state_builder", None)
print("builder", type(builder))
if builder:
    state = builder.build()
    print("mission", getattr(state, "mission", None))
    obs = state.obligations if hasattr(state, "obligations") else []
    print("obligation_count", len(obs))
    kinds=Counter()
    for o in obs:
        d = o.to_dict() if hasattr(o, "to_dict") else dict(o)
        kinds[d.get("kind")] += 1
        print("OBL", d.get("kind"), d.get("source"), str(d.get("summary"))[:140], "id=", str(d.get("obligation_id"))[:40])
    print("kinds", dict(kinds))

# desire pressures
des = getattr(rt, "desire_system", None) or getattr(getattr(rt, "desire", None), "system", None)
loop = getattr(rt, "autonomous_loop", None)
print("loop", type(loop))
if loop:
    st = loop.get_status()
    print("status_keys", list(st.keys())[:30])
    print({k: st.get(k) for k in ["running","last_decision","last_skip_reason","consecutive_no_action","next_run_in_seconds","pressure","desires"]})
    print("pending_obs", len(getattr(loop, "_pending_actionable_observations", []) or []))
    for o in (getattr(loop, "_pending_actionable_observations", []) or [])[:5]:
        print(" P", o.get("source"), o.get("observation_type"), o.get("tags"), str(o.get("description") or "")[:120])
    print("priority_obligations", len(loop._priority_obligations()) if hasattr(loop, "_priority_obligations") else None)
    print("bypass", loop._has_interval_bypass_work() if hasattr(loop, "_has_interval_bypass_work") else None)
    print("backoff_ms", loop._no_action_backoff_ms() if hasattr(loop, "_no_action_backoff_ms") else None)
    print("min_exec", loop._min_execution_interval_ms, "obs_iv", loop._observation_interval_ms, "min_llm", loop._min_llm_interval_ms)

# repair history Android
repair = getattr(rt, "repair_manager", None)
if repair and hasattr(repair, "list_history"):
    hist = repair.list_history(limit=50)
    android = [h for h in hist if "android" in str(h).lower() or "Android" in str(h.get("error",""))]
    print("repair_total", len(hist), "androidish", len(android))
    for h in android[:8]:
        print("R", h.get("repair_id"), h.get("result"), h.get("category"), str(h.get("error"))[:100], h.get("timestamp"))
