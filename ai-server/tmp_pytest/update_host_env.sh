#!/bin/bash
set -euo pipefail
# Update env for DHCP-tolerant hosts and force PC to current LAN IP.
ENV=/opt/aegis/.env
cp -a "$ENV" "$ENV.bak.$(date +%s)"

python3 - <<'PY'
from pathlib import Path
path = Path("/opt/aegis/.env")
text = path.read_text(encoding="utf-8")
lines = text.splitlines()
wanted = {
    "PC_SERVER_HOST": "192.168.50.195",
    "PC_SERVER_HOSTS": "192.168.50.195,192.168.50.176",
    "ROOM_SERVER_HOST": "orangepi-room",
    "ROOM_SERVER_HOSTS": "orangepi-room,orangepi-room.local,192.168.50.108,192.168.50.120",
    "ROOM_SERVER_PORT": "50055",
    "ROOM_SERVER_ENABLED": "true",
    "AEGIS_LAN_SCAN_ENABLED": "true",
    "AEGIS_LAN_SCAN_PREFIX": "192.168.50",
    "AEGIS_ENDPOINT_CACHE_PATH": "/app/data/endpoint_cache.json",
}
keys = set(wanted)
out = []
seen = set()
for line in lines:
    if not line or line.lstrip().startswith("#") or "=" not in line:
        out.append(line)
        continue
    key = line.split("=", 1)[0].strip()
    if key in keys:
        out.append(f"{key}={wanted[key]}")
        seen.add(key)
    else:
        out.append(line)
for key, value in wanted.items():
    if key not in seen:
        out.append(f"{key}={value}")
path.write_text("\n".join(out) + "\n", encoding="utf-8")
print("updated keys", sorted(wanted))
PY

grep -E 'PC_SERVER_HOST|ROOM_SERVER_HOST|AEGIS_LAN_SCAN|AEGIS_ENDPOINT' "$ENV"

# Recreate ai container to pick up env (compose project assumed under /opt/aegis)
cd /opt/aegis
if [[ -f docker-compose.yml ]]; then
  docker compose up -d --force-recreate ai-server || docker compose up -d --force-recreate aegis-ai-server || true
fi
# fallback recreate by container name if compose service naming differs
if docker ps -a --format '{{.Names}}' | grep -qx aegis-ai-server-1; then
  # Ensure container has latest env from compose; if recreate didn't happen, restart after exporting
  docker inspect aegis-ai-server-1 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'PC_SERVER_HOST|ROOM_SERVER_HOST|AEGIS_LAN' || true
fi
