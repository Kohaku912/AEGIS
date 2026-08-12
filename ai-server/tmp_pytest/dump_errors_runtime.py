#!/usr/bin/env python3
import json
from aegis_ai.runtime import get_runtime
from aegis_ai.web.ui_overview import build_ui_overview

rt = get_runtime()
ov = build_ui_overview(rt)

def show(label, obj, limit=40):
    print(f"\n===== {label} =====")
    if not isinstance(obj, dict):
        print(type(obj), repr(obj)[:500])
        return
    print("keys", list(obj.keys())[:40])
    for list_key in ("items", "entries", "errors", "repairs", "presentations", "notifications", "alerts", "values"):
        items = obj.get(list_key)
        if isinstance(items, list):
            print(f"{list_key} count={len(items)}")
            for it in items[:limit]:
                if isinstance(it, dict):
                    slim = {k: it.get(k) for k in (
                        "id", "repair_id", "presentation_id", "notification_id", "alert_id",
                        "title", "summary", "message", "error", "final_result", "status",
                        "capability_id", "importance", "source", "created_at", "updated_at",
                        "kind", "type", "severity", "code", "category", "timestamp_ms"
                    ) if it.get(k) is not None}
                    print(json.dumps(slim, ensure_ascii=False)[:500])
                else:
                    print(repr(it)[:300])
            return
    print(json.dumps(obj, ensure_ascii=False)[:1200])

for key in ("errors", "repairs", "presentations", "notifications", "attention", "servers"):
    show(key, ov.get(key))

rm = getattr(rt, "repair_manager", None)
if rm:
    hist = rm.list_history(limit=80)
    print("\n===== RAW REPAIR HISTORY (unresolved) =====")
    unresolved = []
    for e in hist:
        fr = str(e.get("final_result") or "").lower()
        if fr in {"dismissed", "recovered", "infra_noise", "rolled_back"}:
            continue
        unresolved.append(e)
    print("unresolved", len(unresolved), "of", len(hist))
    for e in unresolved[:40]:
        print(json.dumps({
            "repair_id": e.get("repair_id"),
            "capability_id": e.get("capability_id"),
            "category": e.get("category"),
            "final_result": e.get("final_result"),
            "error": str(e.get("error") or "")[:200],
            "timestamp_ms": e.get("timestamp_ms"),
        }, ensure_ascii=False))

pm = getattr(rt, "presentation_manager", None)
if pm:
    active = pm.list_active(limit=80)
    print("\n===== ACTIVE PRESENTATIONS =====", len(active))
    for p in active:
        d = p if isinstance(p, dict) else getattr(p, "__dict__", {})
        if not isinstance(d, dict):
            # PresentationSpec-like
            d = {
                "presentation_id": getattr(p, "presentation_id", None),
                "title": getattr(p, "title", None),
                "summary": getattr(p, "summary", None),
                "importance": getattr(p, "importance", None),
                "source": getattr(p, "source", None),
            }
        print(json.dumps({k: d.get(k) for k in (
            "presentation_id", "title", "summary", "importance", "source", "intent", "modality"
        ) if d.get(k) is not None}, ensure_ascii=False)[:450])

nm = getattr(rt, "notification_manager", None)
if nm:
    print("\n===== NOTIFICATIONS =====")
    for meth in ("list_recent", "list_unread", "list"):
        if hasattr(nm, meth):
            try:
                items = getattr(nm, meth)(limit=30)
            except TypeError:
                items = getattr(nm, meth)()
            print(meth, len(items) if isinstance(items, list) else type(items))
            if isinstance(items, list):
                for n in items[:20]:
                    print(json.dumps(n if isinstance(n, dict) else {"raw": str(n)}, ensure_ascii=False)[:350])
            break

hm = getattr(rt, "health_alert_manager", None)
if hm and hasattr(hm, "get_active_alerts"):
    alerts = hm.get_active_alerts()
    print("\n===== HEALTH ALERTS =====", len(alerts) if isinstance(alerts, list) else alerts)
    if isinstance(alerts, list):
        for a in alerts[:20]:
            print(json.dumps(a, ensure_ascii=False)[:350])

tm = getattr(rt, "task_manager", None)
if tm and hasattr(tm, "list_open_incidents"):
    inc = tm.list_open_incidents()
    print("\n===== OPEN INCIDENTS =====", len(inc) if isinstance(inc, list) else inc)
    if isinstance(inc, list):
        for i in inc[:20]:
            print(json.dumps(i if isinstance(i, dict) else {"raw": str(i)}, ensure_ascii=False)[:400])
