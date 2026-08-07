#!/bin/bash
set -euo pipefail
# Persist sources under /opt/aegis so future rebuilds keep changes.
DEST=/opt/aegis/ai-server
PAYLOAD=/tmp/deploy_payload
if [[ -d "$DEST/src/aegis_ai" ]]; then
  cp -a "$PAYLOAD/ai/aegis_ai/net" "$DEST/src/aegis_ai/"
  cp -a "$PAYLOAD/ai/aegis_ai/integrations/room/grpc_client.py" "$DEST/src/aegis_ai/integrations/room/"
  cp -a "$PAYLOAD/ai/aegis_ai/integrations/room/light_ir.py" "$DEST/src/aegis_ai/integrations/room/"
  cp -a "$PAYLOAD/ai/aegis_ai/status/status_manager.py" "$DEST/src/aegis_ai/status/"
  cp -a "$PAYLOAD/ai/server_executor.py" "$DEST/src/"
  mkdir -p "$DEST/capabilities/builtin/room-server/light"
  cp -a "$PAYLOAD/ai/capabilities/builtin/room-server/light/set_light.json" "$DEST/capabilities/builtin/room-server/light/"
  cp -a "$PAYLOAD/ai/generated/aegis/room_server_pb2.py" "$DEST/src/generated/aegis/"
  cp -a "$PAYLOAD/ai/generated/aegis/room_server_pb2.pyi" "$DEST/src/generated/aegis/"
  cp -a "$PAYLOAD/ai/generated/aegis/room_server_pb2_grpc.py" "$DEST/src/generated/aegis/"
  echo "synced to $DEST"
fi

# Aggressive Orange Pi hunt
python3 - <<'PY'
import socket, subprocess, concurrent.futures
prefix='192.168.50.'

def probe(ip, port, timeout=0.15):
    s=socket.socket(); s.settimeout(timeout)
    try:
        s.connect((ip,port)); return True
    except Exception:
        return False
    finally:
        s.close()

open22=[]; open55=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=64) as ex:
    futs={(ex.submit(probe, f'{prefix}{i}', 22), ('22', f'{prefix}{i}')) for i in range(1,255)}
    futs|={(ex.submit(probe, f'{prefix}{i}', 50055), ('55', f'{prefix}{i}')) for i in range(1,255)}
    for fut, (kind, ip) in futs:
        if fut.result():
            (open22 if kind=='22' else open55).append(ip)
print('ssh', sorted(open22, key=lambda x:int(x.split('.')[-1])))
print('room', sorted(open55, key=lambda x:int(x.split('.')[-1])))
PY

# ARP after ping sweep
ping -c 1 -b 192.168.50.255 >/dev/null 2>&1 || true
ip neigh | grep -i '192.168.50' | head -n 40 || true

# If room package present and we find host later helper
ls -la /tmp/room-light-pkg.tar
