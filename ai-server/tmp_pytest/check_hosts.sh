#!/bin/bash
set -euo pipefail
echo "== .env =="
grep -E 'PC_SERVER|ROOM_SERVER|AEGIS_DISABLED' /opt/aegis/.env || true
echo "== container env =="
docker exec aegis-ai-server-1 printenv PC_SERVER_HOST PC_SERVER_PORT ROOM_SERVER_HOST ROOM_SERVER_PORT ROOM_SERVER_ENABLED || true
echo "== status =="
docker exec aegis-ai-server-1 python - <<'PY'
import json
from aegis_ai.runtime import get_runtime
sm = get_runtime().status_manager
sm.check_now()
s = sm.get_snapshot()
for k in ("pc-server", "room-server"):
    print(k, json.dumps(s.get(k, {}), ensure_ascii=False))
PY
echo "== probes =="
for h in 192.168.50.108 192.168.50.120 orangepi-room; do
  timeout 2 bash -c "echo >/dev/tcp/$h/50055" 2>/dev/null && echo "room $h:50055 OK" || echo "room $h:50055 FAIL"
done
# find PC
for h in $(grep -E '^PC_SERVER_HOST=' /opt/aegis/.env | cut -d= -f2-); do
  timeout 2 bash -c "echo >/dev/tcp/$h/50052" 2>/dev/null && echo "pc $h:50052 OK" || echo "pc $h:50052 FAIL"
done
# scan common LAN for open ports (quick)
python3 - <<'PY'
import socket
lan="192.168.50."
found_pc=[]; found_room=[]
for i in range(1,255):
    ip=f"{lan}{i}"
    for port, bucket in ((50052, found_pc),(50055, found_room)):
        s=socket.socket(); s.settimeout(0.05)
        try:
            s.connect((ip,port)); bucket.append(ip)
        except Exception:
            pass
        finally:
            s.close()
print("pc candidates", found_pc)
print("room candidates", found_room)
PY
