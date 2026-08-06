import json
from pathlib import Path
from datetime import datetime, timezone

# find llm usage / cost logs
cands = []
for p in Path("/app/data").rglob("*.jsonl"):
    n = p.name.lower()
    if any(k in n for k in ["llm","usage","cost","token"]):
        cands.append(p)
print("candidates:", [str(c) for c in cands])
for p in cands[:4]:
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()[-8:]
    print("===", p, "n=", len(lines))
    for line in lines:
        try: e=json.loads(line)
        except: continue
        keep = {k: e.get(k) for k in ["timestamp_ms","created_at","profile","model","prompt_tokens","completion_tokens","total_tokens","finish_reason","caller","task","purpose","success","error"] if k in e}
        print("  ", json.dumps(keep, ensure_ascii=False)[:300])
        if not keep:
            print("   keys:", list(e.keys())[:20])
