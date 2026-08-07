#!/bin/bash
set -euo pipefail
rm -rf /tmp/deploy_payload
tar -xf /tmp/deploy_payload.tar -C /tmp
CID=$(docker ps -aqf name=^aegis-ai-server-1$ | head -n1)
# Prefer running container; if restarting, still target by name
CID=$(docker ps -qf name=aegis-ai-server-1)
echo "CID=$CID status=$(docker inspect -f '{{.State.Status}}' aegis-ai-server-1)"
PAYLOAD=/tmp/deploy_payload
copy_into() { docker cp "$1" "aegis-ai-server-1:$2"; echo "copied $1"; }
copy_into "$PAYLOAD/ai/aegis_ai/net" /app/src/aegis_ai/net
copy_into "$PAYLOAD/ai/aegis_ai/integrations/room/grpc_client.py" /app/src/aegis_ai/integrations/room/grpc_client.py
copy_into "$PAYLOAD/ai/aegis_ai/integrations/room/light_ir.py" /app/src/aegis_ai/integrations/room/light_ir.py
copy_into "$PAYLOAD/ai/aegis_ai/status/status_manager.py" /app/src/aegis_ai/status/status_manager.py
copy_into "$PAYLOAD/ai/server_executor.py" /app/src/server_executor.py
copy_into "$PAYLOAD/ai/capabilities/builtin/room-server/light/set_light.json" /app/capabilities/builtin/room-server/light/set_light.json
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2.py" /app/src/generated/aegis/room_server_pb2.py
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2.pyi" /app/src/generated/aegis/room_server_pb2.pyi
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2_grpc.py" /app/src/generated/aegis/room_server_pb2_grpc.py

# Quick syntax/import check before restart
docker start aegis-ai-server-1 >/dev/null 2>&1 || true
sleep 1
docker exec aegis-ai-server-1 python -c "from generated.aegis import room_server_pb2 as m; print('fields', [f.name for f in m.SetLightRequest.DESCRIPTOR.fields]); from aegis_ai.net.endpoint_resolver import resolve_tcp_endpoint; print('resolver_ok')"

docker restart aegis-ai-server-1
for i in $(seq 1 40); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo none)
  echo "health=$st"
  [[ "$st" == "healthy" ]] && break
  sleep 2
done
docker exec aegis-ai-server-1 python -c "import json; from aegis_ai.runtime import get_runtime; sm=get_runtime().status_manager; s=sm.check_now(); print(json.dumps({k:s.get(k) for k in ('pc-server','room-server')}, ensure_ascii=False, indent=2))"
