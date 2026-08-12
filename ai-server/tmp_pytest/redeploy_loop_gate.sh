#!/bin/bash
set -euo pipefail
docker cp /tmp/autonomous_loop.py aegis-ai-server-1:/app/src/aegis_ai/autonomous/autonomous_loop.py
docker restart aegis-ai-server-1
for i in $(seq 1 20); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  echo "health $i $st"
  [ "$st" = "healthy" ] && break
  sleep 2
done
docker exec aegis-ai-server-1 python <<'PY'
from aegis_ai.runtime import get_runtime
from aegis_ai.web.ui_overview import build_ui_overview
rt=get_runtime()
ov=build_ui_overview(rt)
e=((ov.get("errors") or {}).get("data") or {}).get("items") or []
p=rt.presentation_manager.list_active(limit=500)
print("errors", len(e))
print("presentations", len(p))
PY
