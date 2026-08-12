#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  /tmp/providers.py root@$HOST:/opt/aegis/room-server/src/aegis_room/providers.py
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST \
  'systemctl restart aegis-room-server; sleep 1; systemctl is-active aegis-room-server; PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python -c "from aegis_room.providers import resolve_ir_pin
try:
  resolve_ir_pin(\"PH5\")
  print(\"FAIL_allowed_PH5\")
except ValueError as e:
  print(\"ok_forbid\", e)
print(resolve_ir_pin(\"PC9\"))"'
