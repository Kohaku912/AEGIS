#!/bin/bash
set -euo pipefail
docker exec aegis-ai-server-1 python <<'PY'
import json
from aegis_ai.runtime import get_runtime
rt=get_runtime()

# Build overview pieces similar to ui_overview
from aegis_ai.web import ui_overview as uo

# Call internal helpers if available
funcs=[n for n in dir(uo) if n.startswith('_') and not n.startswith('__')]
print("helpers", [n for n in funcs if any(k in n for k in ('error','repair','present','notif','attention','health'))])

ov = None
try:
    ov = uo.build_ui_overview(rt)
except TypeError:
    try:
        ov = uo.build_overview(rt)
    except Exception as e:
        print("build fail", e)
except Exception as e:
    print("build fail2", e)

if ov is None:
    # fallback: inspect managers directly
    data={}
else:
    data=ov if isinstance(ov, dict) else {}

def show(label, obj, limit=25):
    print(f"\n===== {label} =====")
    if isinstance(obj, dict):
        print("keys", list(obj.keys())[:30])
        items = obj.get("items") or obj.get("entries") or obj.get("errors") or obj.get("repairs") or obj.get("presentations") or obj.get("notifications") or obj.get("alerts")
        if items is None:
            # maybe values are the list
            for k,v in obj.items():
                if isinstance(v, list):
                    print(f"list-key {k} len={len(v)}")
                    items=v
                    break
        if isinstance(items, list):
            print("count", len(items))
            for it in items[:limit]:
                if isinstance(it, dict):
                    slim={k:it.get(k) for k in (
                        "id","repair_id","presentation_id","notification_id","alert_id",
                        "title","summary","message","error","final_result","status",
                        "capability_id","importance","source","created_at","updated_at",
                        "kind","type","severity","code"
                    ) if it.get(k) is not None}
                    print(json.dumps(slim, ensure_ascii=False)[:450])
                else:
                    print(it)
        else:
            print(json.dumps(obj, ensure_ascii=False)[:800])
    elif isinstance(obj, list):
        print("count", len(obj))
        for it in obj[:limit]:
            print(json.dumps(it, ensure_ascii=False)[:450] if isinstance(it, dict) else it)
    else:
        print(repr(obj)[:500])

if data:
    for key in ("errors","repairs","presentations","notifications","attention","servers","connection"):
        show(key, data.get(key))
else:
    print("no overview; dumping managers")

# Direct managers
rm=getattr(rt,"repair_manager",None)
if rm:
    hist=rm.list_history(limit=50) if hasattr(rm,"list_history") else None
    if hist is None and hasattr(rm,"get_status"):
        print("repair status", rm.get_status())
    show("repair_history", hist if hist is not None else getattr(rm,"history",[]))

pm=getattr(rt,"presentation_manager",None)
if pm and hasattr(pm,"list_active"):
    show("active_presentations", pm.list_active(limit=50))

nm=getattr(rt,"notification_manager",None)
if nm:
    if hasattr(nm,"list_recent"):
        show("notifications", nm.list_recent(limit=30))
    elif hasattr(nm,"list"):
        show("notifications", nm.list(limit=30))

hm=getattr(rt,"health_alert_manager",None) or getattr(rt,"health_manager",None)
if hm and hasattr(hm,"get_active_alerts"):
    show("health_alerts", hm.get_active_alerts())

# commitments open
cm=getattr(rt,"commitment_manager",None)
if cm and hasattr(cm,"list"):
    try:
        items=cm.list(status="open")
        show("open_commitments", items if not isinstance(items, dict) else items)
    except TypeError:
        show("open_commitments", cm.list())

# tasks with failed
tm=getattr(rt,"task_manager",None)
if tm and hasattr(tm,"list_open_incidents"):
    show("open_incidents", tm.list_open_incidents())
PY
