#!/bin/bash
set -euo pipefail
docker exec aegis-ai-server-1 printenv AEGIS_DISABLED_SERVERS
docker exec aegis-ai-server-1 printenv ROOM_SERVER_HOST
docker exec aegis-ai-server-1 printenv ROOM_SERVER_PORT
docker exec aegis-ai-server-1 python -c 'import socket; socket.create_connection(("192.168.50.108",50055),timeout=5).close(); print("tcp_ok")'
docker exec aegis-ai-server-1 python -c 'from aegis_ai.runtime import get_runtime; import json; s=get_runtime().status_manager.get_snapshot().get("room-server",{}); print(json.dumps(s, ensure_ascii=False)[:800])'
