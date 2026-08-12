#!/bin/bash
set -euo pipefail
# ensure capability manifests are in the container
if [ -f /tmp/set_light.json ]; then
  docker exec aegis-ai-server-1 mkdir -p /app/capabilities/builtin/room-server/light /app/capabilities/builtin/room-server/ir
  docker cp /tmp/set_light.json aegis-ai-server-1:/app/capabilities/builtin/room-server/light/set_light.json
  docker cp /tmp/send_ir_command.json aegis-ai-server-1:/app/capabilities/builtin/room-server/ir/send_ir_command.json
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
rt = get_runtime()
caps = rt.capability_catalog.list_for_llm()
want = ("room-server.light.set_light", "room-server.ir.send_ir_command")
ids = [c["id"] for c in caps if c["id"] in want]
print("FOUND", ids)
for c in caps:
    if c["id"] in want:
        print("---", c["id"])
        print(c.get("description", "")[:240])
        print("params", [p.get("name") if isinstance(p, dict) else p for p in c.get("params", [])][:12])
PY
