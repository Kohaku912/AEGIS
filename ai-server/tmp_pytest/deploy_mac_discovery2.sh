#!/bin/bash
set -euo pipefail
cd /opt/aegis

# .env already updated in previous attempt; ensure keys again quietly
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
lines = text.splitlines(); out=[]; seen=set()
for line in lines:
    if not line or line.lstrip().startswith('#') or '=' not in line:
        out.append(line); continue
    key=line.split('=',1)[0].strip()
    if key in wanted:
        out.append(f'{key}={wanted[key]}'); seen.add(key)
    else:
        out.append(line)
for k,v in wanted.items():
    if k not in seen: out.append(f'{k}={v}')
path.write_text('\n'.join(out)+'\n', encoding='utf-8')
print('env_ok')
PY

cp -a /tmp/deploy_mac/docker-compose.yml /opt/aegis/docker-compose.yml
mkdir -p /opt/aegis/ai-server/src/aegis_ai/net /opt/aegis/ai-server/capabilities/builtin/room-server/light
cp -a /tmp/deploy_mac/ai/aegis_ai/net/. /opt/aegis/ai-server/src/aegis_ai/net/
cp -a /tmp/deploy_mac/ai/aegis_ai/status/status_manager.py /opt/aegis/ai-server/src/aegis_ai/status/
cp -a /tmp/deploy_mac/ai/aegis_ai/integrations/room/. /opt/aegis/ai-server/src/aegis_ai/integrations/room/
cp -a /tmp/deploy_mac/ai/server_executor.py /opt/aegis/ai-server/src/
cp -a /tmp/deploy_mac/ai/capabilities/builtin/room-server/light/set_light.json /opt/aegis/ai-server/capabilities/builtin/room-server/light/

# refresh neighbors into volume (user can write if volume perms allow; else timer does)
python3 - <<'PY'
import json, re, subprocess, time
from pathlib import Path
out = Path('/var/lib/docker/volumes/aegis_aegis-data/_data/neighbors.json')
try:
    text = subprocess.check_output(['ip','-4','neigh','show'], text=True, timeout=3)
except Exception:
    text = ''
neighbors=[]
for line in text.splitlines():
    parts=line.split()
    if 'lladdr' not in parts: continue
    ip=parts[0]; mac=parts[parts.index('lladdr')+1]; state=parts[-1]
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
        neighbors.append({'ip':ip,'mac':mac.lower(),'state':state})
try:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'updated_at_ms':int(time.time()*1000),'neighbors':neighbors}, indent=2)+'\n')
    print('neighbors_written', len(neighbors))
except PermissionError:
    print('neighbors_write_skipped_permission')
PY

docker rm -f $(docker ps -aq --filter name='_aegis-ai-server') 2>/dev/null || true
docker compose up -d ai-server
sleep 5
CID=$(docker ps -qf name=aegis-ai-server-1)
echo CID=$CID
docker cp /tmp/deploy_mac/ai/aegis_ai/net "$CID:/app/src/aegis_ai/net"
docker cp /tmp/deploy_mac/ai/aegis_ai/status/status_manager.py "$CID:/app/src/aegis_ai/status/status_manager.py"
docker cp /tmp/deploy_mac/ai/aegis_ai/integrations/room/grpc_client.py "$CID:/app/src/aegis_ai/integrations/room/grpc_client.py"
docker cp /tmp/deploy_mac/ai/aegis_ai/integrations/room/light_ir.py "$CID:/app/src/aegis_ai/integrations/room/light_ir.py"
docker cp /tmp/deploy_mac/ai/server_executor.py "$CID:/app/src/server_executor.py"
docker cp /tmp/deploy_mac/ai/capabilities/builtin/room-server/light/set_light.json "$CID:/app/capabilities/builtin/room-server/light/set_light.json"
docker cp /tmp/deploy_mac/ai/generated/aegis/room_server_pb2.py "$CID:/app/src/generated/aegis/room_server_pb2.py"
docker cp /tmp/deploy_mac/ai/generated/aegis/room_server_pb2_grpc.py "$CID:/app/src/generated/aegis/room_server_pb2_grpc.py"
docker restart aegis-ai-server-1
for i in $(seq 1 40); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo none)
  echo health=$st
  [[ "$st" == healthy ]] && break
  sleep 2
done

docker exec aegis-ai-server-1 printenv ROOM_SERVER_MACS PC_SERVER_MACS
docker exec aegis-ai-server-1 sh -c 'ls -la /host/proc/net/arp /app/data/neighbors.json 2>&1 | head'
docker exec aegis-ai-server-1 python -c "import json; from aegis_ai.net.endpoint_resolver import clear_endpoint_cache, read_neighbor_table, resolve_by_mac, resolve_tcp_endpoint; clear_endpoint_cache(); n=read_neighbor_table(); print('arp_hits', {k:v for k,v in n.items() if str(v).startswith('192.168.50.')}); print('mac_room', resolve_by_mac('room-server', port=50055, timeout=0.7, refresh_arp=True)); print('mac_pc', resolve_by_mac('pc-server', port=50052, timeout=0.7, refresh_arp=True)); print('tcp_room', resolve_tcp_endpoint('room-server', port=50055, timeout=0.7)); print('tcp_pc', resolve_tcp_endpoint('pc-server', port=50052, timeout=0.7)); from aegis_ai.runtime import get_runtime; s=get_runtime().status_manager.check_now(); print(json.dumps({k:s.get(k) for k in ('pc-server','room-server')}, ensure_ascii=False, indent=2)); c=json.load(open('/app/capabilities/builtin/room-server/light/set_light.json')); print('light_modes', c['input_schema']['properties']['mode']['enum'])"
