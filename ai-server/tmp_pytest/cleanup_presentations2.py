#!/usr/bin/env python3
from aegis_ai.runtime import get_runtime
from aegis_ai.web.ui_overview import build_ui_overview

rt = get_runtime()
pm = rt.presentation_manager
active = pm.list_active(limit=500)
print("active_before", len(active))
gone = 0
for p in active:
    title = str(p.get("title") or "").lower()
    summary = str(p.get("summary") or "").lower()
    source = str(p.get("source") or "")
    pid = str(p.get("presentation_id") or "")
    spam = False
    if "no memory found" in summary or "memory.search" in title:
        spam = True
    if "memory.sleep" in title or "memory sleep consolidation" in summary:
        spam = True
    if "interruption.status" in title:
        spam = True
    if "already replied" in summary:
        spam = True
    if source == "repair_manager":
        spam = True
    if spam and pid:
        r = pm.dismiss(pid)
        if r.get("ok"):
            gone += 1
        else:
            print("fail", pid, r)
print("dismissed", gone)
active2 = pm.list_active(limit=500)
print("active_after", len(active2))
print("no_memory_left", sum(1 for p in active2 if "no memory found" in str(p.get("summary") or "").lower() or "memory.search" in str(p.get("title") or "").lower()))
ov = build_ui_overview(rt)
errors = (((ov.get("errors") or {}).get("data") or {}).get("items") or [])
print("errors", len(errors))
# sample remaining titles
from collections import Counter
c = Counter()
for p in active2:
    t = str(p.get("title") or "")
    if "memory.search" in t.lower():
        key = "memory.search"
    elif "agora.read" in t.lower():
        key = "agora.read"
    elif "agora.post" in t.lower():
        key = "agora.post"
    else:
        key = t[:60]
    c[key] += 1
print("remaining_kinds", c.most_common(15))
