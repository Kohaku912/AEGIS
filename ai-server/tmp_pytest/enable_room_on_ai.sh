#!/bin/bash
set -euo pipefail
echo "network=$(docker inspect aegis-ai-server-1 --format '{{.HostConfig.NetworkMode}}')"
docker exec aegis-ai-server-1 python - <<'PY'
import socket
for host in ("192.168.50.108", "192.168.50.120"):
    try:
        s = socket.create_connection((host, 50055), timeout=5)
        s.close()
        print(f"ok {host}")
    except Exception as e:
        print(f"fail {host}: {e}")
PY

ENV=/opt/aegis/.env
if grep -q '^AEGIS_DISABLED_SERVERS=' "$ENV"; then
  sed -i 's/^AEGIS_DISABLED_SERVERS=.*/AEGIS_DISABLED_SERVERS=dev-server/' "$ENV"
else
  echo 'AEGIS_DISABLED_SERVERS=dev-server' >> "$ENV"
fi
grep -E 'AEGIS_DISABLED_SERVERS|ROOM_SERVER_HOST|ROOM_SERVER_PORT' "$ENV"

cd /opt/aegis
# Recreate ai-server to pick env (compose production overlay)
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d ai-server
sleep 5
docker ps --filter name=aegis-ai-server-1 --format '{{.Names}} {{.Status}}'
docker exec aegis-ai-server-1 printenv AEGIS_DISABLED_SERVERS ROOM_SERVER_HOST ROOM_SERVER_PORT
