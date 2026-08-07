#!/bin/bash
# Orchestrate Orange Pi setup from Ubuntu jump host
set -euo pipefail
PW=$(cat /tmp/opi_pw.txt)
export SSHPASS="$PW"
SSH=(sshpass -e ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no root@192.168.50.108)
SCP=(sshpass -e scp -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no)

WIFI_PASSWORD="${WIFI_PASSWORD:-anyway_5346}"

echo "==> copy setup scripts"
"${SCP[@]}" /tmp/opi_base_setup.sh /tmp/opi_install_room.sh root@192.168.50.108:/tmp/
"${SSH[@]}" "sed -i 's/\r$//' /tmp/opi_base_setup.sh /tmp/opi_install_room.sh"

echo "==> run base setup + wifi"
"${SSH[@]}" "WIFI_PASSWORD='$WIFI_PASSWORD' bash /tmp/opi_base_setup.sh"

echo "==> sync room-server sources"
"${SSH[@]}" "mkdir -p /opt/aegis/room-server"
# Prefer a prepared tarball on Ubuntu
if [ -f /tmp/room-server.tgz ]; then
  "${SCP[@]}" /tmp/room-server.tgz root@192.168.50.108:/tmp/room-server.tgz
  "${SSH[@]}" "rm -rf /opt/aegis/room-server/*; tar -xzf /tmp/room-server.tgz -C /opt/aegis/room-server"
else
  echo "missing /tmp/room-server.tgz" >&2
  exit 1
fi

echo "==> install room-server"
"${SSH[@]}" "bash /tmp/opi_install_room.sh"

echo "==> remote verify from Ubuntu"
python3 - <<'PY'
import grpc,sys
sys.path.insert(0,'/tmp')  # unused
# Use a quick TCP connect; full grpc client may need generated stubs on Ubuntu host
import socket
s=socket.create_connection(('192.168.50.108',50055),timeout=5)
s.close()
print('tcp_50055_ok')
PY

"${SSH[@]}" "ip -br a; systemctl is-active aegis-room-server; journalctl -u aegis-room-server -n 30 --no-pager"
