#!/bin/bash
set -euo pipefail
ROOT=/opt/aegis
STAGE=/tmp/aegis-host-light-deploy
rm -rf "$STAGE"
mkdir -p "$STAGE"

# Files will be uploaded beside this script under /tmp/deploy_payload/
PAYLOAD=/tmp/deploy_payload
if [[ ! -d "$PAYLOAD" ]]; then
  echo "missing $PAYLOAD"
  exit 1
fi

# Update .env
bash /tmp/update_host_env.sh

# Copy AI modules into container
CID=$(docker ps -qf name=aegis-ai-server-1)
if [[ -z "$CID" ]]; then
  echo "ai container not running"
  exit 1
fi

copy_into() {
  local src="$1"
  local dst="$2"
  docker cp "$src" "$CID:$dst"
  echo "copied $src -> $dst"
}

# Python modules
copy_into "$PAYLOAD/ai/aegis_ai/net" /app/src/aegis_ai/net
copy_into "$PAYLOAD/ai/aegis_ai/integrations/room/grpc_client.py" /app/src/aegis_ai/integrations/room/grpc_client.py
copy_into "$PAYLOAD/ai/aegis_ai/integrations/room/light_ir.py" /app/src/aegis_ai/integrations/room/light_ir.py
copy_into "$PAYLOAD/ai/aegis_ai/status/status_manager.py" /app/src/aegis_ai/status/status_manager.py
copy_into "$PAYLOAD/ai/server_executor.py" /app/src/server_executor.py
copy_into "$PAYLOAD/ai/capabilities/builtin/room-server/light/set_light.json" /app/capabilities/builtin/room-server/light/set_light.json
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2.py" /app/src/generated/aegis/room_server_pb2.py
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2.pyi" /app/src/generated/aegis/room_server_pb2.pyi
copy_into "$PAYLOAD/ai/generated/aegis/room_server_pb2_grpc.py" /app/src/generated/aegis/room_server_pb2_grpc.py

# Ensure net package init exists
docker exec "$CID" python - <<'PY'
from pathlib import Path
p=Path('/app/src/aegis_ai/net/__init__.py')
print('net package', p.exists(), 'files', sorted(x.name for x in p.parent.iterdir()))
PY

# Recreate container so env changes apply (compose)
cd /opt/aegis
if docker compose ps --services 2>/dev/null | grep -q .; then
  SVC=$(docker compose ps --services | grep -E 'ai' | head -n1 || true)
  echo "compose service=$SVC"
  if [[ -n "$SVC" ]]; then
    docker compose up -d --force-recreate "$SVC"
  else
    docker restart aegis-ai-server-1
  fi
else
  docker restart aegis-ai-server-1
fi

sleep 5
docker ps --filter name=aegis-ai-server-1 --format '{{.Names}} {{.Status}}'
docker exec aegis-ai-server-1 printenv PC_SERVER_HOST PC_SERVER_HOSTS ROOM_SERVER_HOST ROOM_SERVER_HOSTS AEGIS_LAN_SCAN_ENABLED || true

docker exec aegis-ai-server-1 python - <<'PY'
import json
from aegis_ai.runtime import get_runtime
sm=get_runtime().status_manager
snap=sm.check_now()
for k in ('pc-server','room-server'):
    print(k, json.dumps(snap.get(k,{}), ensure_ascii=False))
PY
