#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  /tmp/providers.py /tmp/light_ir.py /tmp/server.py root@$HOST:/tmp/
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
  cp /tmp/providers.py /opt/aegis/room-server/src/aegis_room/providers.py
  cp /tmp/light_ir.py /opt/aegis/room-server/src/aegis_room/light_ir.py
  cp /tmp/server.py /opt/aegis/room-server/src/aegis_room/server.py
  # ensure Arduino defaults on unit
  UNIT=/etc/systemd/system/aegis-room-server.service
  grep -q AEGIS_ROOM_IR_REPEAT "$UNIT" || sed -i "/AEGIS_ROOM_IR_BIT_ORDER=/a Environment=AEGIS_ROOM_IR_REPEAT=3" "$UNIT"
  grep -q AEGIS_ROOM_IR_ADDR_MODE "$UNIT" || sed -i "/AEGIS_ROOM_IR_REPEAT=/a Environment=AEGIS_ROOM_IR_ADDR_MODE=auto" "$UNIT"
  systemctl daemon-reload
  systemctl restart aegis-room-server
  sleep 1
  systemctl is-active aegis-room-server
  systemctl show aegis-room-server -p Environment --no-pager
'
