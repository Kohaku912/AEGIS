#!/bin/bash
set -euo pipefail
docker cp /tmp/grpc_client.py aegis-ai-server-1:/app/src/aegis_ai/integrations/room/grpc_client.py
# optional: ship net package if present on host upload
if [ -f /tmp/endpoint_resolver.py ]; then
  docker exec aegis-ai-server-1 mkdir -p /app/src/aegis_ai/net
  docker cp /tmp/endpoint_resolver.py aegis-ai-server-1:/app/src/aegis_ai/net/endpoint_resolver.py
  docker cp /tmp/net_init.py aegis-ai-server-1:/app/src/aegis_ai/net/__init__.py || true
fi
docker restart aegis-ai-server-1
for i in $(seq 1 30); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  echo "health $i $st"
  [ "$st" = "healthy" ] && break
  sleep 2
done
docker exec aegis-ai-server-1 python <<'PY'
from aegis_ai.runtime import get_runtime
rt=get_runtime()
caps=rt.capability_catalog.list_for_llm()
ids=[c['id'] for c in caps if c['id'].startswith('room-server.') and ('light' in c['id'] or '.ir.' in c['id'])]
print('ids', ids)
for c in caps:
  if c['id']=='room-server.light.set_light':
    print('desc', c['description'][:180])
PY
