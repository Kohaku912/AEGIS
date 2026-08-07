#!/bin/bash
set -euo pipefail
ENV=/opt/aegis/.env
if grep -q '^ROOM_SERVER_ENABLED=' "$ENV"; then
  sed -i 's/^ROOM_SERVER_ENABLED=.*/ROOM_SERVER_ENABLED=true/' "$ENV"
else
  echo 'ROOM_SERVER_ENABLED=true' >> "$ENV"
fi
grep -E 'ROOM_SERVER_|AEGIS_DISABLED' "$ENV"
cd /opt/aegis
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d ai-server
for i in $(seq 1 40); do
  h=$(docker inspect --format '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  echo "health=$h"
  [ "$h" = healthy ] && break
  sleep 3
done
docker exec aegis-ai-server-1 printenv ROOM_SERVER_ENABLED AEGIS_DISABLED_SERVERS ROOM_SERVER_HOST
sleep 8
docker exec aegis-ai-server-1 python -c 'from aegis_ai.runtime import get_runtime; import json; print(json.dumps(get_runtime().status_manager.get_snapshot().get("room-server",{}), ensure_ascii=False)[:1000])'
