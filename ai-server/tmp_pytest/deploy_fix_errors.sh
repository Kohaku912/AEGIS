#!/bin/bash
set -euo pipefail
# Install ddgs, deploy code fixes, cleanup error UI
docker exec aegis-ai-server-1 pip install -q 'ddgs>=9.0' || docker exec aegis-ai-server-1 python -m pip install -q 'ddgs>=9.0'
docker cp /tmp/autonomous_loop.py aegis-ai-server-1:/app/src/aegis_ai/autonomous/autonomous_loop.py
docker cp /tmp/repair.py aegis-ai-server-1:/app/src/aegis_ai/personal_ai/repair.py
docker cp /tmp/cleanup_fix_errors.py aegis-ai-server-1:/tmp/cleanup_fix_errors.py
docker restart aegis-ai-server-1
for i in $(seq 1 30); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  echo "health $i $st"
  [ "$st" = "healthy" ] && break
  sleep 2
done
docker exec aegis-ai-server-1 python -c 'import ddgs; print("ddgs", getattr(ddgs, "__version__", "ok"))'
docker exec aegis-ai-server-1 python /tmp/cleanup_fix_errors.py
