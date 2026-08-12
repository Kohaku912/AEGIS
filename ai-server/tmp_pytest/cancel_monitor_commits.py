#!/usr/bin/env python3
from aegis_ai.runtime import get_runtime

rt = get_runtime()
cm = rt.commitment_manager
for item in list(cm.list_commitments(status="open") or []):
    title = str(item.get("title") or "")
    cid = str(item.get("commitment_id") or "")
    if "Monitor browser-server timeout" in title and cid:
        print("cancel", cm.transition(cid, "cancelled", reason="cleanup_duplicate_monitor_commitment"))
print("open", [(i.get("commitment_id"), i.get("title")) for i in cm.list_commitments(status="open")])
