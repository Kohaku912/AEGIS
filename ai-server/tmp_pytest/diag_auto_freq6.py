from pathlib import Path
import json
from collections import Counter
import time

now=int(time.time()*1000)

# Simulate active repair obligations like AgentState
repair_path=Path("/app/data/personal_ai/repair_history.jsonl")
lines=repair_path.read_text(encoding="utf-8").splitlines()
noise_categories={"transient","server_down","llm_failed"}
terminal={"recovered","infra_noise","dismissed","rolled_back","repair_disabled","not_retryable"}
latest={}
for line in lines:
    e=json.loads(line)
    rid=str(e.get("repair_id") or "")
    cid=str(e.get("capability_id") or "")
    key=rid or f"{cid}|{e.get('error','')}"
    if not key: continue
    prev=latest.get(key)
    if prev is None or int(e.get("timestamp") or 0) >= int(prev.get("timestamp") or 0):
        latest[key]=e
active=[]
for e in latest.values():
    result=str(e.get("result") or "").strip()
    cat=str(e.get("category") or "").strip()
    if result in terminal: continue
    if cat in noise_categories: continue
    # age?
    ts=int(e.get("timestamp") or 0)
    active.append(e)
print("collapsed_latest", len(latest), "active_after_filter", len(active))
errc=Counter(str(e.get("error") or "")[:100] for e in active)
print("top_errors", errc.most_common(12))
# how many would be in top 12 shown
print("first12:")
for e in sorted(active, key=lambda x: -int(x.get("timestamp") or 0))[:13]:
    age_h=(now-int(e.get("timestamp") or 0))/3600000 if e.get("timestamp") else None
    print(" ", e.get("category"), str(e.get("error"))[:90], "age_h", round(age_h,1) if age_h is not None else None, "result", repr(e.get("result")))

# desires
des=Path("/app/data/desires")
print("desire files", list(des.glob("*")) if des.exists() else None)
for f in des.glob("*.json"):
    print(f.name, f.read_text(encoding="utf-8")[:500])

# LLM usage recent
for cand in [Path("/app/data/llm_usage.jsonl"), Path("/app/data/llm/usage.jsonl"), Path("/app/data/cost/usage.jsonl")]:
    if cand.exists():
        print("usage", cand)
ls=[]
for p in Path("/app/data").rglob("*usage*"):
    if p.is_file() and p.suffix in {".jsonl",".json"} and p.stat().st_size<50_000_000:
        print("cand", p, p.stat().st_size)

# audit autonomous recent
audit=Path("/app/data/audit.jsonl")
if audit.exists():
    rows=[]
    for line in audit.read_text(encoding="utf-8").splitlines()[-300:]:
        try: e=json.loads(line)
        except: continue
        act=str(e.get("action") or e.get("event") or "")
        if "autonomous" in act.lower() or "llm" in act.lower() or str(e.get("group_type"))=="autonomous":
            rows.append(e)
    print("audit_autoish", len(rows))
    for e in rows[-8:]:
        print(e.get("timestamp") or e.get("ts"), e.get("action"), e.get("decision"), str(e.get("reason") or "")[:80])

# execution last 10 with absolute times
import datetime
lines=Path("/app/data/autonomous/execution_log.jsonl").read_text(encoding="utf-8").splitlines()[-12:]
print("===EXEC===")
for line in lines:
    e=json.loads(line)
    t=int(e.get("timestamp_ms") or 0)
    print(datetime.datetime.utcfromtimestamp(t/1000).isoformat()+"Z", e.get("last_decision"), e.get("last_no_action_reason") or e.get("last_skip_reason"), "tools", e.get("selected_tool_count"))

# observation last and whether novelty changes
obs=Path("/app/data/autonomous/observation_log.jsonl").read_text(encoding="utf-8").splitlines()[-6:]
print("===OBS===")
for line in obs:
    e=json.loads(line)
    t=int(e.get("timestamp_ms") or 0)
    desc=[str(o.get("description"))[:80] for o in (e.get("observations") or [])[:3]]
    print(datetime.datetime.utcfromtimestamp(t/1000).isoformat()+"Z", desc)
