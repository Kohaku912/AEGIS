#!/bin/bash
set -euo pipefail
SRC=/tmp/deploy-toolfailed
cd "$SRC"
docker cp ai/src/aegis_ai/core_capabilities.py aegis-ai-server-1:/app/src/aegis_ai/core_capabilities.py
docker cp ai/src/aegis_ai/integrations/duckduckgo_search.py aegis-ai-server-1:/app/src/aegis_ai/integrations/duckduckgo_search.py
docker cp ai/src/aegis_ai/autonomous/autonomous_loop.py aegis-ai-server-1:/app/src/aegis_ai/autonomous/autonomous_loop.py
docker cp ai/src/aegis_ai/desire/fulfillment.py aegis-ai-server-1:/app/src/aegis_ai/desire/fulfillment.py
docker cp ai/src/aegis_ai/approval/channels/pc_overlay.py aegis-ai-server-1:/app/src/aegis_ai/approval/channels/pc_overlay.py
docker cp ai/src/tool_broker.py aegis-ai-server-1:/app/src/tool_broker.py
docker cp ai/pyproject.toml aegis-ai-server-1:/app/pyproject.toml
docker cp ai/apps/builtin/browser-server/search/query/executor.json aegis-ai-server-1:/app/apps/builtin/browser-server/search/query/executor.json
docker cp browser/main.py aegis-browser-server-1:/app/src/aegis_browser/main.py
docker exec aegis-ai-server-1 pip install --no-cache-dir 'ddgs>=9.0' || true
docker exec aegis-browser-server-1 pip install --no-cache-dir 'ddgs>=9.0' || true
docker exec aegis-ai-server-1 python -m compileall -q /app/src/aegis_ai/core_capabilities.py /app/src/aegis_ai/integrations/duckduckgo_search.py /app/src/aegis_ai/autonomous/autonomous_loop.py /app/src/aegis_ai/desire/fulfillment.py /app/src/aegis_ai/approval/channels/pc_overlay.py /app/src/tool_broker.py
docker restart aegis-ai-server-1 aegis-browser-server-1
for i in $(seq 1 40); do
  ai=$(docker inspect --format '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  br=$(docker inspect --format '{{.State.Health.Status}}' aegis-browser-server-1 2>/dev/null || echo starting)
  echo "health ai=$ai browser=$br"
  if [ "$ai" = healthy ] && [ "$br" = healthy ]; then break; fi
  sleep 2
done
docker exec aegis-ai-server-1 python - <<'PY'
from aegis_ai.core_capabilities import AegisCoreCapabilityClient
from aegis_ai.integrations.duckduckgo_search import DuckDuckGoSearch
import inspect
src = inspect.getsource(AegisCoreCapabilityClient.invoke_capability)
assert "ai-server.search.web" in src
r = DuckDuckGoSearch().search("AEGIS AI assistant", max_results=3)
print("search_ok", r.success, "n=", len(r.results), "err=", (r.error or "")[:80])
print("deploy_verify_ok")
PY
docker exec aegis-browser-server-1 python -c 'src=open("/app/src/aegis_browser/main.py",encoding="utf-8").read(); assert "_handle_fast_search" in src; print("browser_fast_search_ok")'