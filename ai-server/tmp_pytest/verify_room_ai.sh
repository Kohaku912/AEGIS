#!/bin/bash
set -euo pipefail
for i in $(seq 1 30); do
  h=$(docker inspect --format '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  echo "health=$h"
  [ "$h" = healthy ] && break
  sleep 3
done
docker exec aegis-ai-server-1 python - <<'PY'
import socket, os
print('DISABLED', os.getenv('AEGIS_DISABLED_SERVERS'))
print('ROOM_HOST', os.getenv('ROOM_SERVER_HOST'), os.getenv('ROOM_SERVER_PORT'))
for host in ("192.168.50.108", "192.168.50.120"):
    try:
        s = socket.create_connection((host, 50055), timeout=5)
        s.close()
        print('tcp_ok', host)
    except Exception as e:
        print('tcp_fail', host, e)

# Prefer gRPC health via room client if importable
try:
    from aegis_ai.integrations.room.grpc_client import RoomServerGrpcClient
    c = RoomServerGrpcClient(host=os.getenv('ROOM_SERVER_HOST','192.168.50.108'), port=int(os.getenv('ROOM_SERVER_PORT','50055')))
    # try common methods
    for name in ('health_check','health','get_health'):
        if hasattr(c, name):
            print(name, getattr(c, name)())
            break
    else:
        print('client_methods', [m for m in dir(c) if not m.startswith('_')][:30])
except Exception as e:
    print('grpc_client_err', type(e).__name__, e)

from aegis_ai.runtime import get_runtime
rt = get_runtime()
snap = rt.status_manager.get_snapshot()
room = snap.get('android-server') and snap.get('room-server')
print('room_status', snap.get('room-server'))
PY
