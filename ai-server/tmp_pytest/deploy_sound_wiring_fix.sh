#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  /tmp/sound_inmp441.py root@$HOST:/opt/aegis/room-server/src/aegis_room/sound_inmp441.py
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
systemctl restart aegis-room-server
sleep 1
systemctl is-active aegis-room-server
# show mixer paths that might route capture
for c in audiocodec HDMI ahubi2s3; do
  echo "=== amixer -c $c ==="
  amixer -c "$c" 2>/dev/null | head -60 || true
done
echo "=== note: until INMP441 is on PH6/PH7/PH9, DIN stays floating (-1 samples) ==="
'
# AI capability refresh
docker exec aegis-ai-server-1 mkdir -p /app/capabilities/builtin/room-server/sound
docker cp /tmp/get_level.json aegis-ai-server-1:/app/capabilities/builtin/room-server/sound/get_level.json
docker restart aegis-ai-server-1
for i in $(seq 1 20); do
  st=$(docker inspect -f '{{.State.Health.Status}}' aegis-ai-server-1 2>/dev/null || echo starting)
  echo "health $i $st"
  [ "$st" = "healthy" ] && break
  sleep 2
done
docker exec aegis-ai-server-1 python -c 'from aegis_ai.runtime import get_runtime; caps=get_runtime().capability_catalog.list_for_llm();
print([c["id"] for c in caps if "sound" in c["id"]]);
print(next(c["description"][:160] for c in caps if c["id"]=="room-server.sound.get_level"))'
