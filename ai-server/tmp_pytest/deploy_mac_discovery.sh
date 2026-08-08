#!/bin/bash
set -euo pipefail
cd /opt/aegis

# Update .env MAC/host settings without dumping secrets
python3 - <<'PY'
from pathlib import Path
path = Path('/opt/aegis/.env')
text = path.read_text(encoding='utf-8')
wanted = {
    'ROOM_SERVER_HOST': '192.168.50.120',
    'ROOM_SERVER_HOSTS': '192.168.50.108,192.168.50.120,192.168.50.198,orangepi-room,orangepi-room.local',
    'ROOM_SERVER_MACS': '20:86:a0:62:98:e0,02:00:50:a7:b0:58',
    'ROOM_SERVER_ENABLED': 'true',
    'PC_SERVER_HOST': '192.168.50.195',
    'PC_SERVER_HOSTS': '192.168.50.195,192.168.50.176',
    'PC_SERVER_MACS': '44:af:28:14:f2:f8,d8:5e:d3:5b:d7:fa',
    'AEGIS_LAN_SCAN_ENABLED': 'true',
    'AEGIS_LAN_SCAN_PREFIX': '192.168.50',
    'AEGIS_NEIGHBOR_TABLE_PATH': '/app/data/neighbors.json',
    'AEGIS_ENDPOINT_CACHE_PATH': '/app/data/endpoint_cache.json',
}
lines = text.splitlines()
out = []
seen = set()
for line in lines:
    if not line or line.lstrip().startswith('#') or '=' not in line:
        out.append(line)
        continue
    key = line.split('=', 1)[0].strip()
    if key in wanted:
        out.append(f'{key}={wanted[key]}')
        seen.add(key)
    else:
        out.append(line)
for key, value in wanted.items():
    if key not in seen:
        out.append(f'{key}={value}')
path.write_text('\n'.join(out) + '\n', encoding='utf-8')
for key in sorted(wanted):
    print(key, '=', wanted[key])
PY

# Install neighbor refresh
install -m 0755 /tmp/aegis-refresh-neighbors.sh /usr/local/sbin/aegis-refresh-neighbors.sh
cat >/etc/systemd/system/aegis-refresh-neighbors.service <<'EOF'
[Unit]
Description=Refresh AEGIS LAN neighbor table for MAC discovery
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=oneshot
Environment=AEGIS_LAN_SCAN_PREFIX=192.168.50
ExecStart=/usr/local/sbin/aegis-refresh-neighbors.sh
EOF
cat >/etc/systemd/system/aegis-refresh-neighbors.timer <<'EOF'
[Unit]
Description=Periodic AEGIS neighbor refresh

[Timer]
OnBootSec=30s
OnUnitActiveSec=60s
AccuracySec=5s
Unit=aegis-refresh-neighbors.service

[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now aegis-refresh-neighbors.timer
/usr/local/sbin/aegis-refresh-neighbors.sh || true
ls -la /var/lib/docker/volumes/aegis_aegis-data/_data/neighbors.json || true
head -c 400 /var/lib/docker/volumes/aegis_aegis-data/_data/neighbors.json || true
echo

# Sync compose + code into /opt/aegis
cp -a /tmp/deploy_mac/docker-compose.yml /opt/aegis/docker-compose.yml
mkdir -p /opt/aegis/ai-server/src/aegis_ai/net
cp -a /tmp/deploy_mac/ai/aegis_ai/net/. /opt/aegis/ai-server/src/aegis_ai/net/
cp -a /tmp/deploy_mac/ai/aegis_ai/status/status_manager.py /opt/aegis/ai-server/src/aegis_ai/status/
cp -a /tmp/deploy_mac/ai/aegis_ai/integrations/room/. /opt/aegis/ai-server/src/aegis_ai/integrations/room/
cp -a /tmp/deploy_mac/ai/server_executor.py /opt/aegis/ai-server/src/
mkdir -p /opt/aegis/ai-server/capabilities/builtin/room-server/light
cp -a /tmp/deploy_mac/ai/capabilities/builtin/room-server/light/set_light.json /opt/aegis/ai-server/capabilities/builtin/room-server/light/
cp -a /tmp/deploy_mac/ai/generated/aegis/room_server_pb2.py /opt/aegis/ai-server/src/generated/aegis/ 2>/dev/null || true
cp -a /tmp/deploy_mac/ai/generated/aegis/room_server_pb2_grpc.py /opt/aegis/ai-server/src/generated/aegis/ 2>/dev/null || true

# Recreate AI container to pick up arp mount + env
docker rm -f $(docker ps -aq --filter name='_aegis-ai-server') 2>/dev/null || true
docker compose up -d ai-server
sleep 6
CID=$(docker ps -qf name=aegis-ai-server-1)
echo CID=$CID

# docker cp modules into running image (image may not have latest until rebuild)
docker cp /tmp/deploy_mac/ai/aegis_ai/net "$CID:/app/src/aegis_ai/net"
docker cp /tmp/deploy_mac/ai/aegis_ai/status/status_manager.py "$CID:/app/src/aegis_ai/status/status_manager.py"
docker cp /tmp/deploy_mac/ai/aegis_ai/integrations/room/grpc_client.py "$CID:/app/src/aegis_ai/integrations/room/grpc_client.py"
docker cp /tmp/deploy_mac/ai/aegis_ai/integrations/room/light_ir.py "$CID:/app/src/aegis_ai/integrations/room/light_ir.py"
docker cp /tmp/deploy_mac/ai/server_executor.py "$CID:/app/src/server_executor.py"
docker cp /tmp/deploy_mac/ai/capabilities/builtin/room-server/light/set_light.json "$CID:/app/capabilities/builtin/room-server/light/set_light.json"
docker cp /tmp/deploy_mac/ai/generated/aegis/room_server_pb2.py "$CID:/app/src/generated/aegis/room_server_pb2.py" 2>/dev/null || true
docker cp /tmp/deploy_mac/ai/generated/aegis/room_server_pb2_grpc.py "$CID:/app/src/generated/aegis/room_server_pb2_grpc.py" 2>/dev/null || true

docker restart aegis-ai-server-1
for i in $(seq 1 40); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo none)
  echo health=$st
  [[ "$st" == healthy ]] && break
  sleep 2
done

docker exec aegis-ai-server-1 printenv ROOM_SERVER_MACS PC_SERVER_MACS ROOM_SERVER_HOST
docker exec aegis-ai-server-1 ls -la /host/proc/net/arp /app/data/neighbors.json 2>/dev/null || true

docker exec aegis-ai-server-1 python -c "
import json
from aegis_ai.net.endpoint_resolver import clear_endpoint_cache, read_neighbor_table, resolve_by_mac, resolve_tcp_endpoint
clear_endpoint_cache()
print('neighbors', {k:v for k,v in read_neighbor_table().items() if v.startswith('192.168.50.')})
print('mac_room', resolve_by_mac('room-server', port=50055, timeout=0.6, refresh_arp=True))
print('mac_pc', resolve_by_mac('pc-server', port=50052, timeout=0.6, refresh_arp=True))
print('tcp_room', resolve_tcp_endpoint('room-server', port=50055, timeout=0.6))
print('tcp_pc', resolve_tcp_endpoint('pc-server', port=50052, timeout=0.6))
from aegis_ai.runtime import get_runtime
sm=get_runtime().status_manager
snap=sm.check_now()
print(json.dumps({k:snap.get(k) for k in ('pc-server','room-server')}, ensure_ascii=False, indent=2))
import json as J
cap=J.load(open('/app/capabilities/builtin/room-server/light/set_light.json'))
print('light_mode', cap['input_schema']['properties']['mode']['enum'])
print('light_desc', cap['description'][:100])
"
