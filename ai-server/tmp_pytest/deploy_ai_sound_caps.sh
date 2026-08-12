#!/bin/bash
set -euo pipefail
docker exec aegis-ai-server-1 mkdir -p \
  /app/capabilities/builtin/room-server/light \
  /app/capabilities/builtin/room-server/ir \
  /app/capabilities/builtin/room-server/sound \
  /app/src/aegis_ai/integrations/room
docker cp /tmp/set_light.json aegis-ai-server-1:/app/capabilities/builtin/room-server/light/set_light.json
docker cp /tmp/send_ir_command.json aegis-ai-server-1:/app/capabilities/builtin/room-server/ir/send_ir_command.json
docker cp /tmp/get_level.json aegis-ai-server-1:/app/capabilities/builtin/room-server/sound/get_level.json
docker cp /tmp/grpc_client.py aegis-ai-server-1:/app/src/aegis_ai/integrations/room/grpc_client.py
docker restart aegis-ai-server-1
for i in $(seq 1 30); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  echo "health $i $st"
  [ "$st" = "healthy" ] && break
  sleep 2
done
docker exec aegis-ai-server-1 python -c '
from aegis_ai.runtime import get_runtime
rt=get_runtime()
caps=rt.capability_catalog.list_for_llm()
want=("room-server.light.set_light","room-server.ir.send_ir_command","room-server.sound.get_level")
for c in caps:
  if c["id"] in want:
    print("---", c["id"])
    print((c.get("description") or "")[:200])
'
