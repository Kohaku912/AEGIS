#!/usr/bin/env python3
"""Fix live AEGIS error noise: dismiss resolved repairs + spam presentations."""
from __future__ import annotations

import json
from aegis_ai.runtime import get_runtime
from aegis_ai.web.ui_overview import build_ui_overview

rt = get_runtime()

# 1) Dismiss unresolved repairs that are infra/policy noise or now-fixed deps
rm = rt.repair_manager
dismissed = rm.dismiss_matching(
    dry_run=False,
    limit=500,
    categories={"transient", "server_down", "llm_failed", "tool_failed", "permission", "policy_denied"},
    final_results={"recorded", "needs_followup", "rollback_failed", "not_retryable", "repair_disabled"},
    error_substrings=[
        "timeout",
        "timed out",
        "ddgs package not installed",
        "unsupported ai capability",
        "already replied",
        "android permission missing",
        "android_permission_missing",
        "no results",
        "completion verification failed",
        "unavailable",
        "connection",
    ],
)
print("repair_dismiss", json.dumps(dismissed, ensure_ascii=False))

# 2) Dismiss spam / fixed presentations
pm = rt.presentation_manager
active = pm.list_active(limit=200)
dismiss_ids = []
for p in active:
    title = str(p.get("title") or "")
    summary = str(p.get("summary") or "")
    source = str(p.get("source") or "")
    intent = str(p.get("intent") or "")
    low_title = title.lower()
    low_sum = summary.lower()
    spam = False
    if "no memory found" in low_sum:
        spam = True
    if "memory sleep consolidation has started" in low_sum:
        spam = True
    if "interruption.status" in low_title:
        spam = True
    if "already replied" in low_sum:
        spam = True
    if intent == "unrepairable_failure" and "already replied" in low_sum:
        spam = True
    if source == "autonomous_loop" and low_sum.strip() in {"ok", "done", '{"ok": true}'}:
        spam = True
    # Raw JSON interruption dumps
    if low_sum.startswith('{"ok": true') and "batched" in low_sum:
        spam = True
    if spam:
        dismiss_ids.append(str(p.get("presentation_id") or ""))

gone = 0
for pid in dismiss_ids:
    if not pid:
        continue
    try:
        pm.dismiss(pid)
        gone += 1
    except Exception as exc:
        print("dismiss_fail", pid, exc)
print(f"presentations_dismissed {gone}/{len(dismiss_ids)}")

# 3) Verify search works after ddgs install (best-effort)
try:
    from aegis_ai.integrations.duckduckgo_search import DuckDuckGoSearch

    resp = DuckDuckGoSearch(timeout=8).search("AEGIS test", max_results=2)
    print("search_ok", resp.success, "n", len(resp.results), "err", resp.error)
except Exception as exc:
    print("search_exc", exc)

ov = build_ui_overview(rt)
errors = (((ov.get("errors") or {}).get("data") or {}).get("items") or [])
print("errors_remaining", len(errors))
for e in errors[:15]:
    print(json.dumps({k: e.get(k) for k in ("id", "title", "message", "capability_id")}, ensure_ascii=False)[:300])
active2 = pm.list_active(limit=200)
print("presentations_remaining", len(active2))
spam_left = sum(1 for p in active2 if "no memory found" in str(p.get("summary") or "").lower())
print("no_memory_spam_left", spam_left)
