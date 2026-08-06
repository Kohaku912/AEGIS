import json
from pathlib import Path
from datetime import datetime, timezone

# Pull actual LLM no_action reasons from audit
p = Path("/app/data/audit.jsonl")
rows=[]
if p.exists():
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines()[-4000:]:
        try: e=json.loads(line)
        except: continue
        if str(e.get("action") or "") in {"autonomous_no_action","autonomous_preflight","autonomous_fulfillment_evaluated"}:
            rows.append(e)
print("audit autonomous rows", len(rows))
for e in rows[-12:]:
    print("---", e.get("action"), e.get("decision"))
    print("  reason:", str(e.get("reason") or "")[:400].replace("\n"," "))
    det = e.get("detail") or {}
    if isinstance(det, dict):
        print("  cand_count:", len(det.get("candidate_capability_ids") or []))
        print("  axes:", det.get("decision_axes"))
