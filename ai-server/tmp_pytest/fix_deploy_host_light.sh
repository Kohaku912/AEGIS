#!/bin/bash
set -euo pipefail
cd /opt/aegis

# Clean leftover conflicting containers
docker ps -a --format '{{.ID}} {{.Names}}' | grep -E 'aegis-ai-server|aegis-browser' || true
docker rm -f 655a307c273a_aegis-ai-server-1 4fb1e6ea7abc a3915fe6fee2_aegis-browser-server-1 2>/dev/null || true
# Remove any anonymous conflict leftovers by name pattern
for id in $(docker ps -aq --filter name=aegis-ai-server); do
  name=$(docker inspect -f '{{.Name}}' "$id")
  echo "container $id $name"
done

docker compose up -d ai-server browser-server
sleep 4
docker ps --filter name=aegis --format '{{.Names}} {{.Status}}'

CID=$(docker ps -qf name=aegis-ai-server-1)
echo "CID=$CID"
PAYLOAD=/tmp/deploy_payload
copy_into() { docker cp "$1" "$CID:$2"; echo "copied $1"; }

copy_into "$PAYLOAD/ai/aegis_ai/net" /app/src/aegis_ai/net
copy_into "$PAYLOAD/ai/aegis_ai/integrations/room/grpc_client.py" /app/src/aegis_ai/integrations/room/grpc_client.py
copy_into "$PAYLOAD/ai/aegis_ai/integrations/room/light_ir.py" /app/src/aegis_ai/integrations/room/light_ir.py
copy_into "$PAYLOAD/ai/aegis_ai/status/status_manager.py" /app/src/aegis_ai/status/status_manager.py
copy_into "$PAYLOAD/ai/server_executor.py" /app/src/server_executor.py
copy_into "$PAYLOAD/ai/capabilities/builtin/room-server/light/set_light.json" /app/capabilities/builtin/room-server/light/set_light.json
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2.py" /app/src/generated/aegis/room_server_pb2.py
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2.pyi" /app/src/generated/aegis/room_server_pb2.pyi
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2_grpc.py" /app/src/generated/aegis/room_server_pb2_grpc.py

docker restart aegis-ai-server-1
sleep 6
docker ps --filter name=aegis-ai-server-1 --format '{{.Names}} {{.Status}}'
docker exec aegis-ai-server-1 printenv PC_SERVER_HOST PC_SERVER_HOSTS ROOM_SERVER_HOST ROOM_SERVER_HOSTS AEGIS_LAN_SCAN_ENABLED AEGIS_LAN_SCAN_PREFIX

docker exec aegis-ai-server-1 python - <<'PY'
import json
from aegis_ai.runtime import get_runtime
from aegis_ai.capability_catalog import CapabilityCatalog
sm=get_runtime().status_manager
snap=sm.check_now()
for k in ('pc-server','room-server'):
    print(k, json.dumps(snap.get(k,{}), ensure_ascii=False))
cat=CapabilityCatalog()
m=cat.resolve('room-server.light.set_light')
print('manifest', bool(m), getattr(m,'description','')[:80] if m else None)
# schema mode enum
schema=(getattr(m,'input_schema',None) or {})
print('mode_enum', ((schema.get('properties') or {}).get('mode') or {}).get('enum'))
PY
