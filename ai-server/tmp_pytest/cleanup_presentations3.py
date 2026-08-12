#!/usr/bin/env python3
from collections import Counter
from aegis_ai.runtime import get_runtime
from aegis_ai.web.ui_overview import build_ui_overview

rt = get_runtime()
pm = rt.presentation_manager
active = pm.list_active(limit=1000)
print("active_before", len(active))
gone = 0
for p in active:
    title = str(p.get("title") or "").lower()
    summary = str(p.get("summary") or "").lower()
    source = str(p.get("source") or "")
    pid = str(p.get("presentation_id") or "")
    if source != "autonomous_loop":
        continue
    spam = False
    if "commitment.list" in title:
        spam = True
    if "agora.read_posts" in title or "agora.read" in title:
        spam = True
    if "no open commitment" in summary or summary in {"done", "ok"}:
        spam = True
    if "memory.save" in title and ("saved" in summary or "ok" in summary or len(summary) < 40):
        spam = True
    if "user_model.get" in title:
        spam = True
    if "delegation_policy.list" in title:
        spam = True
    if "permissions.get_status" in title:
        spam = True
    if "screenshot" in title and source == "autonomous_loop":
        # Autonomous screenshot dumps are not user errors; hide.
        spam = True
    if "user_activity.snapshot" in title:
        spam = True
    if "android-server.approval.request" in title:
        spam = True
    if spam and pid and pm.dismiss(pid).get("ok"):
        gone += 1
print("dismissed", gone)
active2 = pm.list_active(limit=1000)
print("active_after", len(active2))
c = Counter(str(p.get("title") or "")[:70] for p in active2)
print("remaining", c.most_common(20))
ov = build_ui_overview(rt)
errors = (((ov.get("errors") or {}).get("data") or {}).get("items") or [])
print("errors", len(errors))
