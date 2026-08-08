#!/bin/bash
set -euo pipefail
export SSHPASS
SSHPASS=$(cat /tmp/opi_pw.txt)
HOST=${1:-192.168.50.120}
SSH=(sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@"$HOST")

echo "== fix 2.4GHz SSID profile on $HOST =="
"${SSH[@]}" 'bash -s' <<'REMOTE'
set -euo pipefail
WIFI_PASSWORD=anyway_5346
# Actual SSIDs on this ASUS: ASUS_F8_2G / ASUS_F8_5G
nmcli -t -f NAME connection show | grep -Fx ASUS_F8 >/dev/null && nmcli connection delete ASUS_F8 || true
nmcli -t -f NAME connection show | grep -Fx ASUS_F8_2G >/dev/null && nmcli connection delete ASUS_F8_2G || true
nmcli connection add type wifi ifname wlan0 con-name ASUS_F8_2G ssid ASUS_F8_2G \
  wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$WIFI_PASSWORD" \
  connection.autoconnect yes connection.autoconnect-priority 100 \
  ipv4.method auto ipv6.method auto
# Ensure 5G remains lower priority backup
nmcli connection modify ASUS_F8_5G connection.autoconnect yes connection.autoconnect-priority 50 wifi-sec.psk "$WIFI_PASSWORD" || true
# Update boot fix script to use real SSIDs
cat >/usr/local/sbin/aegis-wifi-fix.sh <<'EOF'
#!/bin/bash
rfkill unblock wifi || true
ip link set wlan0 up || true
command -v iw >/dev/null && iw dev wlan0 set power_save off || true
nmcli radio wifi on || true
STATE=$(nmcli -t -f DEVICE,STATE device status | awk -F: '$1=="wlan0"{print $2}')
if [[ "$STATE" != "connected" ]]; then
  nmcli connection up ASUS_F8_2G || nmcli connection up ASUS_F8_5G || true
fi
# Keep ethernet managed
ETH=$(nmcli -t -f DEVICE,TYPE device status | awk -F: '$2=="ethernet"{print $1; exit}')
if [[ -n "${ETH:-}" ]]; then
  nmcli device set "$ETH" managed yes || true
fi
EOF
chmod +x /usr/local/sbin/aegis-wifi-fix.sh
systemctl enable aegis-wifi-fix.service || true
iw dev wlan0 set power_save off || true
nmcli device status
nmcli -f NAME,AUTOCONNECT,AUTOCONNECT-PRIORITY connection show
ip -br a
ping -c 1 -W 2 192.168.50.41 || true
# ufw allow if needed
ufw status || true
REMOTE

echo "== ensure AI env + container =="
# Update .env again with correct hosts including 198
python3 - <<'PY'
from pathlib import Path
path=Path('/opt/aegis/.env')
text=path.read_text(encoding='utf-8')
wanted={
  'ROOM_SERVER_HOST':'192.168.50.108',
  'ROOM_SERVER_HOSTS':'192.168.50.108,192.168.50.120,192.168.50.198,orangepi-room,orangepi-room.local',
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
print(path.read_text())
PY

cd /opt/aegis
# Avoid conflict leftovers
docker rm -f $(docker ps -aq --filter name='[0-9a-f]*_aegis-ai-server') 2>/dev/null || true
docker compose up -d ai-server
sleep 5
CID=$(docker ps -qf name=aegis-ai-server-1)
echo CID=$CID
# Restore modules if missing
PAYLOAD=/tmp/deploy_payload
if [[ -d $PAYLOAD/ai ]] && ! docker exec aegis-ai-server-1 test -f /app/src/aegis_ai/net/endpoint_resolver.py; then
  docker cp "$PAYLOAD/ai/aegis_ai/net" "$CID:/app/src/aegis_ai/net"
  docker cp "$PAYLOAD/ai/aegis_ai/integrations/room/grpc_client.py" "$CID:/app/src/aegis_ai/integrations/room/grpc_client.py"
  docker cp "$PAYLOAD/ai/aegis_ai/integrations/room/light_ir.py" "$CID:/app/src/aegis_ai/integrations/room/light_ir.py"
  docker cp "$PAYLOAD/ai/aegis_ai/status/status_manager.py" "$CID:/app/src/aegis_ai/status/status_manager.py"
  docker cp "$PAYLOAD/ai/server_executor.py" "$CID:/app/src/server_executor.py"
  docker cp "$PAYLOAD/ai/generated/aegis/room_server_pb2.py" "$CID:/app/src/generated/aegis/room_server_pb2.py"
  docker cp "$PAYLOAD/ai/generated/aegis/room_server_pb2_grpc.py" "$CID:/app/src/generated/aegis/room_server_pb2_grpc.py"
  docker cp "$PAYLOAD/ai/capabilities/builtin/room-server/light/set_light.json" "$CID:/app/capabilities/builtin/room-server/light/set_light.json" 2>/dev/null || true
  docker restart aegis-ai-server-1
fi

for i in $(seq 1 40); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo none)
  echo health=$st
  [[ "$st" == healthy ]] && break
  sleep 2
done

docker exec aegis-ai-server-1 printenv ROOM_SERVER_HOST ROOM_SERVER_HOSTS
# TCP from container
docker exec aegis-ai-server-1 python - <<'PY'
import socket, json
for ip in ['192.168.50.108','192.168.50.120','192.168.50.198']:
  s=socket.socket(); s.settimeout(1)
  try:
    s.connect((ip,50055)); print('tcp_ok', ip)
  except Exception as e:
    print('tcp_fail', ip, e)
  finally:
    s.close()
from aegis_ai.net.endpoint_resolver import clear_endpoint_cache, resolve_tcp_endpoint
clear_endpoint_cache('room-server')
print('resolve', resolve_tcp_endpoint('room-server', port=50055, timeout=0.6, allow_lan_scan=True))
from aegis_ai.runtime import get_runtime
sm=get_runtime().status_manager
print(json.dumps(sm.check_now().get('room-server',{}), ensure_ascii=False, indent=2))
PY
