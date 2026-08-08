#!/bin/bash
set -euo pipefail
export SSHPASS
SSHPASS=$(cat /tmp/opi_pw.txt)
HOST=$(cat /tmp/opi_host.txt)
SSH=(sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"$HOST")
SCP=(sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null)

echo "HOST=$HOST"

echo "== copy wifi fix + room package =="
"${SCP[@]}" /tmp/opi_fix_wifi.sh root@"$HOST":/tmp/opi_fix_wifi.sh
"${SCP[@]}" /tmp/room-light-pkg.tar root@"$HOST":/tmp/room-light-pkg.tar

echo "== run wifi fix =="
"${SSH[@]}" 'bash /tmp/opi_fix_wifi.sh' || true

echo "== deploy room-server update =="
"${SSH[@]}" 'bash -s' <<'REMOTE'
set -euo pipefail
systemctl stop aegis-room-server || true
mkdir -p /opt/aegis
rm -rf /opt/aegis/room-server.new
mkdir -p /opt/aegis/room-server.new
tar -xf /tmp/room-light-pkg.tar -C /opt/aegis/room-server.new
# tarball may contain room-light-pkg/ top dir
if [[ -d /opt/aegis/room-server.new/room-light-pkg ]]; then
  rm -rf /opt/aegis/room-server
  mv /opt/aegis/room-server.new/room-light-pkg /opt/aegis/room-server
  rm -rf /opt/aegis/room-server.new
else
  rm -rf /opt/aegis/room-server
  mv /opt/aegis/room-server.new /opt/aegis/room-server
fi
cd /opt/aegis/room-server
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
uv sync
# ensure systemd unit env
mkdir -p /etc/aegis
cat >/etc/aegis/room-server.env <<'EOF'
AEGIS_ROOM_LIGHT_PROVIDER=mock
AEGIS_ROOM_DEVICE_ID=light-main
AEGIS_RUNTIME_MODE=development
EOF
if [[ ! -f /etc/systemd/system/aegis-room-server.service ]]; then
cat >/etc/systemd/system/aegis-room-server.service <<'EOF'
[Unit]
Description=AEGIS Room Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=-/etc/aegis/room-server.env
WorkingDirectory=/opt/aegis/room-server
ExecStart=/opt/aegis/room-server/.venv/bin/python -m aegis_room.main
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF
fi
systemctl daemon-reload
systemctl enable --now aegis-room-server
sleep 2
systemctl is-active aegis-room-server
ss -lntp | grep 50055 || true
# local health
/opt/aegis/room-server/.venv/bin/python - <<'PY'
import grpc
from generated.aegis import common_pb2, room_server_pb2_grpc
ch=grpc.insecure_channel('127.0.0.1:50055')
r=room_server_pb2_grpc.RoomServerStub(ch).HealthCheck(common_pb2.HealthCheckRequest(server_id='local'), timeout=5)
print('health', r.status.code, r.status.message, r.version)
PY
ip -br a
nmcli -t -f DEVICE,TYPE,STATE,CONNECTION d || true
iw dev wlan0 get power_save 2>/dev/null || true
REMOTE

echo "== update AI env candidates =="
python3 - <<'PY'
from pathlib import Path
path=Path('/opt/aegis/.env')
text=path.read_text(encoding='utf-8')
wanted={
  'ROOM_SERVER_HOST':'192.168.50.108',
  'ROOM_SERVER_HOSTS':'192.168.50.108,192.168.50.120,192.168.50.198,orangepi-room,orangepi-room.local',
  'ROOM_SERVER_PORT':'50055',
  'ROOM_SERVER_ENABLED':'true',
  'AEGIS_LAN_SCAN_ENABLED':'true',
  'AEGIS_LAN_SCAN_PREFIX':'192.168.50',
}
lines=text.splitlines(); out=[]; seen=set()
for line in lines:
  if not line or line.lstrip().startswith('#') or '=' not in line:
    out.append(line); continue
  k=line.split('=',1)[0].strip()
  if k in wanted:
    out.append(f'{k}={wanted[k]}'); seen.add(k)
  else:
    out.append(line)
for k,v in wanted.items():
  if k not in seen: out.append(f'{k}={v}')
path.write_text('\n'.join(out)+'\n', encoding='utf-8')
print('env updated')
PY
grep -E 'ROOM_SERVER_HOST|AEGIS_LAN' /opt/aegis/.env

echo "== verify from AI container =="
# ensure container has latest resolver already; just check_now after env — may need recreate for env
docker restart aegis-ai-server-1 || true
sleep 8
# inject env into running container is hard; update compose env by recreate if needed
# For now override via endpoint cache + hosts by calling resolver with current env
docker exec aegis-ai-server-1 printenv ROOM_SERVER_HOST ROOM_SERVER_HOSTS || true
# If HOSTS not present in container, recreate
if ! docker exec aegis-ai-server-1 printenv ROOM_SERVER_HOSTS >/dev/null 2>&1 || [[ -z "$(docker exec aegis-ai-server-1 printenv ROOM_SERVER_HOSTS)" ]]; then
  cd /opt/aegis
  docker compose up -d --force-recreate ai-server || docker restart aegis-ai-server-1
  sleep 10
fi

# If recreate wiped code, re-copy payload
if ! docker exec aegis-ai-server-1 test -d /app/src/aegis_ai/net; then
  echo "re-copying AI modules"
  CID=$(docker ps -qf name=aegis-ai-server-1)
  PAYLOAD=/tmp/deploy_payload
  if [[ -d "$PAYLOAD/ai" ]]; then
    docker cp "$PAYLOAD/ai/aegis_ai/net" "$CID:/app/src/aegis_ai/net"
    docker cp "$PAYLOAD/ai/aegis_ai/integrations/room/grpc_client.py" "$CID:/app/src/aegis_ai/integrations/room/grpc_client.py"
    docker cp "$PAYLOAD/ai/aegis_ai/integrations/room/light_ir.py" "$CID:/app/src/aegis_ai/integrations/room/light_ir.py"
    docker cp "$PAYLOAD/ai/aegis_ai/status/status_manager.py" "$CID:/app/src/aegis_ai/status/status_manager.py"
    docker cp "$PAYLOAD/ai/server_executor.py" "$CID:/app/src/server_executor.py"
    docker cp "$PAYLOAD/ai/generated/aegis/room_server_pb2.py" "$CID:/app/src/generated/aegis/room_server_pb2.py"
    docker cp "$PAYLOAD/ai/generated/aegis/room_server_pb2_grpc.py" "$CID:/app/src/generated/aegis/room_server_pb2_grpc.py"
    docker restart aegis-ai-server-1
    sleep 8
  fi
fi

for i in $(seq 1 30); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo none)
  echo health=$st
  [[ "$st" == healthy ]] && break
  sleep 2
done

docker exec aegis-ai-server-1 python -c "import json; from aegis_ai.net.endpoint_resolver import clear_endpoint_cache, resolve_tcp_endpoint; clear_endpoint_cache('room-server'); print('resolve', resolve_tcp_endpoint('room-server', port=50055, timeout=0.5)); from aegis_ai.runtime import get_runtime; sm=get_runtime().status_manager; s=sm.check_now(); print(json.dumps(s.get('room-server',{}), ensure_ascii=False, indent=2))"
