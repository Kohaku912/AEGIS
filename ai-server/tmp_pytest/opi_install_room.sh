#!/bin/bash
# Install AEGIS room-server on Orange Pi (run ON the device as root)
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
INSTALL_ROOT="${INSTALL_ROOT:-/opt/aegis/room-server}"
SERVICE_NAME=aegis-room-server
AI_SERVER_HOST="${AI_SERVER_HOST:-192.168.50.41}"

if [ ! -d "$INSTALL_ROOT/src" ]; then
  echo "Missing $INSTALL_ROOT/src — copy room-server tree first" >&2
  exit 1
fi

echo "==> install uv (for Python 3.12 on Bookworm)"
if [ ! -x /root/.local/bin/uv ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="/root/.local/bin:$PATH"
uv --version

echo "==> create venv with Python 3.12"
cd "$INSTALL_ROOT"
uv python install 3.12
uv venv --python 3.12 .venv
# editable install
uv pip install -e .

echo "==> systemd unit"
cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=AEGIS Room Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_ROOT}
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=${INSTALL_ROOT}/src
Environment=AEGIS_ROOM_HOST=0.0.0.0
Environment=AEGIS_ROOM_PORT=50055
Environment=AEGIS_ROOM_LIGHT_PROVIDER=mock
Environment=AEGIS_ROOM_DEVICE_ID=light-main
ExecStart=${INSTALL_ROOT}/.venv/bin/python -m aegis_room.main
Restart=on-failure
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}.service
systemctl restart ${SERVICE_NAME}.service
sleep 2
systemctl --no-pager --full status ${SERVICE_NAME}.service || true

echo "==> health check"
"${INSTALL_ROOT}/.venv/bin/python" - <<'PY'
import grpc
from generated.aegis import common_pb2, room_server_pb2_grpc
ch = grpc.insecure_channel("127.0.0.1:50055")
stub = room_server_pb2_grpc.RoomServerStub(ch)
r = stub.HealthCheck(common_pb2.HealthCheckRequest(server_id="local-health"), timeout=5)
print("health", r.status.code, r.status.message, r.version, "uptime_ms", r.uptime_ms)
raise SystemExit(0 if r.status.code == 0 else 1)
PY

echo "==> open firewall for LAN room gRPC (optional)"
if command -v ufw >/dev/null 2>&1; then
  ufw allow 22/tcp || true
  ufw allow from 192.168.50.0/24 to any port 50055 proto tcp || true
  ufw --force enable || true
  ufw status || true
fi

echo "room-server installed; AI Core should use ROOM_SERVER_HOST=${HOSTNAME:-orangepi} / 192.168.50.108:50055"
echo "AI server host note: ${AI_SERVER_HOST}"
