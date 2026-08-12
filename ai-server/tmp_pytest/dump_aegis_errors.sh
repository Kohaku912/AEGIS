#!/bin/bash
set -euo pipefail
# Dump current errors/presentations/repairs/notifications/health from live AI server
python3 <<'PY'
import json, urllib.request
base="http://127.0.0.1:8090"
def get(path):
    try:
        with urllib.request.urlopen(base+path, timeout=15) as r:
            return json.load(r)
    except Exception as e:
        return {"_error": str(e), "path": path}

# Try overview first
ov=get("/api/ui/overview")
if "_error" in ov:
    ov=get("/display/overview")
print("=== OVERVIEW KEYS ===")
if isinstance(ov, dict):
    print(sorted(ov.keys())[:40])
    errors=ov.get("errors") or ov.get("error") or []
    repairs=ov.get("repairs") or []
    presentations=ov.get("presentations") or []
    notifs=ov.get("notifications") or []
    attention=ov.get("attention") or []
    print("\n=== ERRORS", len(errors) if isinstance(errors,list) else type(errors))
    if isinstance(errors, list):
        for e in errors[:30]:
            if isinstance(e, dict):
                print(json.dumps({k:e.get(k) for k in ("id","repair_id","title","summary","message","error","final_result","capability_id","status","created_at","updated_at") if k in e or True}, ensure_ascii=False)[:400])
            else:
                print(e)
    print("\n=== REPAIRS", len(repairs) if isinstance(repairs,list) else type(repairs))
    if isinstance(repairs, list):
        for e in repairs[:20]:
            print(json.dumps(e, ensure_ascii=False)[:350])
    print("\n=== PRESENTATIONS", len(presentations) if isinstance(presentations,list) else type(presentations))
    if isinstance(presentations, list):
        for p in presentations[:30]:
            print(json.dumps({k:p.get(k) for k in ("presentation_id","id","title","summary","importance","source","status","created_at")}, ensure_ascii=False)[:350])
    print("\n=== NOTIFICATIONS", len(notifs) if isinstance(notifs,list) else type(notifs))
    if isinstance(notifs, list):
        for n in notifs[:20]:
            print(json.dumps(n, ensure_ascii=False)[:300])
    print("\n=== ATTENTION", len(attention) if isinstance(attention,list) else type(attention))
    if isinstance(attention, list):
        for a in attention[:20]:
            print(json.dumps(a, ensure_ascii=False)[:300])
else:
    print(ov)

print("\n=== /api/repair ===")
print(json.dumps(get("/api/repair"), ensure_ascii=False)[:2000])
print("\n=== /api/presentations ===")
print(json.dumps(get("/api/presentations"), ensure_ascii=False)[:2000])
print("\n=== /api/health/alerts ===")
print(json.dumps(get("/api/health/alerts"), ensure_ascii=False)[:1500])
print("\n=== /api/notifications ===")
print(json.dumps(get("/api/notifications"), ensure_ascii=False)[:1500])
PY
