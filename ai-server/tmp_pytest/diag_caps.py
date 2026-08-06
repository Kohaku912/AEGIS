import json
from pathlib import Path
# recent results full output for agora
lines=Path("/app/data/autonomous/execution_log.jsonl").read_text(encoding="utf-8").splitlines()[-12:]
for line in lines:
    e=json.loads(line)
    if e.get("last_decision")!="action_selected":
        continue
    print("===", e.get("timestamp_ms"), e.get("last_decision"))
    for t in e.get("tasks") or []:
        print(" task", t.get("capability_id"), t.get("desire"), t.get("action","")[:80])
    for r in e.get("results") or []:
        out=r.get("full_output") or r.get("result")
        s=json.dumps(out, ensure_ascii=False)[:400] if not isinstance(out,str) else out[:400]
        print(" result success=", r.get("success"), "out=", s)

# status of servers / available caps from loop state
s=json.loads(Path("/app/data/autonomous/loop_state.json").read_text())
print("loop keys sample:", {k:s.get(k) for k in ["last_decision","last_no_action_reason","selected_tool_count","consecutive_no_action","last_candidate_capability_ids","available_capability_count"]})
print("candidates:", s.get("last_candidate_capability_ids"))
print("axes:", s.get("last_decision_axes"))
