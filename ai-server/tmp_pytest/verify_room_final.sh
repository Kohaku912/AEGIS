#!/bin/bash
set -euo pipefail
sleep 15
docker exec aegis-ai-server-1 python - <<'PY'
from aegis_ai.runtime import get_runtime
import json
rt = get_runtime()
sm = rt.status_manager
# force check if available
for name in ("check_now", "force_check", "refresh", "check_all", "_check_once"):
    if hasattr(sm, name):
        try:
            getattr(sm, name)()
            print("called", name)
        except TypeError:
            pass
        except Exception as e:
            print("call_err", name, e)
print(json.dumps(sm.get_snapshot().get("room-server", {}), ensure_ascii=False)[:1200])
# also direct grpc
import grpc, os
from generated.aegis import common_pb2, room_server_pb2_grpc
host = os.getenv("ROOM_SERVER_HOST", "192.168.50.108")
port = int(os.getenv("ROOM_SERVER_PORT", "50055"))
ch = grpc.insecure_channel(f"{host}:{port}")
stub = room_server_pb2_grpc.RoomServerStub(ch)
r = stub.HealthCheck(common_pb2.HealthCheckRequest(server_id="ai-verify"), timeout=5)
print("grpc_health", r.status.code, r.status.message, r.version)
PY
# Orange Pi self status
PW=$(cat /tmp/opi_pw.txt)
sshpass -p "$PW" ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no root@192.168.50.108 'hostname; ip -br a; systemctl is-active aegis-room-server; nmcli -t -f DEVICE,STATE,CONNECTION device status'
