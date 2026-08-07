#!/bin/bash
set -euo pipefail
CID=$(docker ps -qf name=aegis-ai-server-1)
echo "CID=$CID"
PAYLOAD=/tmp/deploy_payload
copy_into() { docker cp "$1" "$CID:$2"; echo "copied $1 -> $2"; }
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
# wait healthy
for i in $(seq 1 30); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  echo "health=$st"
  [[ "$st" == "healthy" ]] && break
  sleep 2
done
docker exec aegis-ai-server-1 ls /app/src/aegis_ai/net
docker exec aegis-ai-server-1 python -c "from aegis_ai.net.endpoint_resolver import resolve_tcp_endpoint; print('pc', resolve_tcp_endpoint('pc-server', port=50052, timeout=0.3))"
docker exec aegis-ai-server-1 python -c "import json; from aegis_ai.runtime import get_runtime; sm=get_runtime().status_manager; s=sm.check_now(); print(json.dumps({k:s.get(k) for k in ('pc-server','room-server')}, ensure_ascii=False, indent=2))"
