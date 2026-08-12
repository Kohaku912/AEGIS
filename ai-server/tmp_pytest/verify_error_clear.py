#!/usr/bin/env python3
from aegis_ai.runtime import get_runtime
from aegis_ai.web.ui_overview import build_ui_overview

rt = get_runtime()
ov = build_ui_overview(rt)
errors = (((ov.get("errors") or {}).get("data") or {}).get("items") or [])
pres = rt.presentation_manager.list_active(limit=500)
print("errors", len(errors))
print("presentations", len(pres))
