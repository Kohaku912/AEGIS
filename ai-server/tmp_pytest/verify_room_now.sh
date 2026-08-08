#!/bin/bash
set -euo pipefail
CID=$(docker ps -qf name=aegis-ai-server-1)
PAYLOAD=/tmp/deploy_payload
if [[ -d $PAYLOAD/ai ]]; then
  docker cp "$PAYLOAD/ai/aegis_ai/net" "$CID:/app/src/aegis_ai/net" 2>/dev/null || true
  docker cp "$PAYLOAD/ai/aegis_ai/integrations/room/grpc_client.py" "$CID:/app/src/aegis_ai/integrations/room/grpc_client.py" 2>/dev/null || true
  docker cp "$PAYLOAD/ai/aegis_ai/integrations/room/light_ir.py" "$CID:/app/src/aegis_ai/integrations/room/light_ir.py" 2>/dev/null || true
  docker cp "$PAYLOAD/ai/aegis_ai/status/status_manager.py" "$CID:/app/src/aegis_ai/status/status_manager.py" 2>/dev/null || true
  docker cp "$PAYLOAD/ai/server_executor.py" "$CID:/app/src/server_executor.py" 2>/dev/null || true
  docker cp "$PAYLOAD/ai/generated/aegis/room_server_pb2.py" "$CID:/app/src/generated/aegis/room_server_pb2.py" 2>/dev/null || true
  docker cp "$PAYLOAD/ai/generated/aegis/room_server_pb2_grpc.py" "$CID:/app/src/generated/aegis/room_server_pb2_grpc.py" 2>/dev/null || true
fi
# probe room from container
docker exec aegis-ai-server-1 python -c "import socket
for ip in ['192.168.50.108','192.168.50.120','192.168.50.198']:
 s=socket.socket(); s.settimeout(1)
 try:
  s.connect((ip,50055)); print('tcp_ok', ip)
 except Exception as e:
  print('tcp_fail', ip, type(e).__name__)
 finally:
  s.close()"

docker exec aegis-ai-server-1 python -c "import json; from aegis_ai.net.endpoint_resolver import clear_endpoint_cache, resolve_tcp_endpoint; clear_endpoint_cache('room-server'); print('resolve', resolve_tcp_endpoint('room-server', port=50055, timeout=0.6, allow_lan_scan=True)); from aegis_ai.runtime import get_runtime; print(json.dumps(get_runtime().status_manager.check_now().get('room-server',{}), ensure_ascii=False, indent=2))"
