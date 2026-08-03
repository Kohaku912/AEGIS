from pathlib import Path
import json
from collections import Counter

# Commitments / social / repair / tasks that feed obligations
paths = {
  "commitments": Path("/app/data/commitments"),
  "social": Path("/app/data/social"),
  "repair": Path("/app/data"),
  "tasks": Path("/app/data/tasks"),
}
for name,p in paths.items():
    print(name, "exists", p.exists(), "sample", list(p.glob("*"))[:8] if p.exists() else [])

# repair history
for cand in [Path("/app/data/repair_history.jsonl"), Path("/app/data/personal_ai/repair_history.jsonl"), Path("/app/data/repairs.jsonl")]:
    if cand.exists():
        lines=cand.read_text(encoding="utf-8").splitlines()
        print("repair_file", cand, "n", len(lines))
        kinds=Counter(); results=Counter(); errors=Counter()
        active=[]
        latest={}
        for line in lines:
            e=json.loads(line)
            key=str(e.get("repair_id") or e.get("capability_id") or e.get("error") or id(e))
            latest[key]=e
        for e in latest.values():
            results[str(e.get("result"))] += 1
            kinds[str(e.get("category"))] += 1
            err=str(e.get("error") or "")[:80]
            if "Android" in err or "android" in err: errors[err]+=1
            if str(e.get("result") or "") not in {"recovered","infra_noise","dismissed","rolled_back","repair_disabled","not_retryable"}:
                if str(e.get("category") or "") not in {"transient","server_down","llm_failed"}:
                    active.append(e)
        print("results", dict(results))
        print("active_count", len(active))
        for e in active[:15]:
            print("A", e.get("result"), e.get("category"), str(e.get("error"))[:120], e.get("capability_id"))
        print("android_errors", errors.most_common(5))

# commitments
for cand in Path("/app/data").rglob("*commitment*"):
    print("found", cand)
for cand in [Path("/app/data/commitments/commitments.jsonl"), Path("/app/data/commitments.jsonl")]:
    if cand.exists():
        lines=cand.read_text(encoding="utf-8").splitlines()
        print("commitments", cand, len(lines))
        open_c=[]
        for line in lines[-200:]:
            e=json.loads(line)
            if str(e.get("status")) not in {"completed","failed","cancelled","expired","postponed"}:
                open_c.append(e)
        print("openish", len(open_c))
        for e in open_c[:10]:
            print("C", e.get("status"), e.get("title") or e.get("description"), e.get("commitment_id"))

# social items
for cand in Path("/app/data").rglob("*social*"):
    if cand.is_file() and cand.suffix in {".jsonl",".json"}:
        print("social_file", cand, cand.stat().st_size)

# status.changed frequency in events
ev = Path("/app/data/events")
if ev.exists():
    files=sorted(ev.glob("*.jsonl"))[-2:]
    print("event_files", files)
    types=Counter(); recent=[]
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines()[-500:]:
            try: e=json.loads(line)
            except: continue
            t=str(e.get("event_type") or e.get("type") or "")
            types[t]+=1
            if t in {"status.changed","task.failed","task.completed","browser.discovery","commitment.due"}:
                recent.append((e.get("timestamp_ms") or e.get("created_at_ms"), t, str(e.get("payload") or e)[:120]))
    print("event_types top", types.most_common(15))
    print("immediate-ish last10:")
    for r in recent[-10:]:
        print(r)
