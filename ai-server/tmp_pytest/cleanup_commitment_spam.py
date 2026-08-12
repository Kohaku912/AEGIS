#!/usr/bin/env python3
"""One-shot cleanup: cancel duplicate monitor commitments and dismiss Done spam."""
from __future__ import annotations

from aegis_ai.runtime import get_runtime


def main() -> None:
    rt = get_runtime()
    cm = rt.commitment_manager
    cancelled = 0
    for item in list(cm.list_commitments(status="open") or []):
        title = str(item.get("title") or "")
        cid = str(item.get("commitment_id") or "")
        if not cid:
            continue
        if "Monitor browser-server timeout" in title:
            cm.transition(cid, "cancelled", reason="cleanup_duplicate_monitor_commitment")
            cancelled += 1
            print("cancelled", cid, title[:80])

    pm = getattr(rt, "presentation_manager", None)
    dismissed = 0
    if pm is not None:
        specs = []
        if hasattr(pm, "list_active"):
            specs = pm.list_active() or []
        elif hasattr(pm, "list"):
            specs = pm.list() or []
        elif hasattr(pm, "list_presentations"):
            specs = pm.list_presentations() or []
        for spec in specs:
            if isinstance(spec, dict):
                pid = str(spec.get("presentation_id") or "")
                title = str(spec.get("title") or "")
                summary = str(spec.get("summary") or "")
                content = str(spec.get("content") or "")
                status = str(spec.get("status") or "")
            else:
                pid = str(getattr(spec, "presentation_id", "") or "")
                title = str(getattr(spec, "title", "") or "")
                summary = str(getattr(spec, "summary", "") or "")
                content = str(getattr(spec, "content", "") or "")
                status = str(getattr(getattr(spec, "status", None), "value", getattr(spec, "status", "")) or "")
            blob = f"{title}\n{summary}\n{content}".lower()
            if status.lower() in {"dismissed", "expired"}:
                continue
            if "commitment.list" in blob or summary.strip().lower() in {"done", ""} or content.strip().lower() == "done":
                if pid and hasattr(pm, "dismiss"):
                    pm.dismiss(pid)
                    dismissed += 1
                    print("dismissed", pid, title[:60])

    if hasattr(rt.task_manager, "sweep_stale_incidents"):
        print("sweep", rt.task_manager.sweep_stale_incidents())
    print({"cancelled_commitments": cancelled, "dismissed_presentations": dismissed})


if __name__ == "__main__":
    main()
