#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  /tmp/providers.py /tmp/light_ir_room.py /tmp/server_room.py /tmp/sound_inmp441.py \
  root@$HOST:/tmp/
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
  set -e
  ROOT=/opt/aegis/room-server/src/aegis_room
  cp /tmp/providers.py "$ROOT/providers.py"
  cp /tmp/light_ir_room.py "$ROOT/light_ir.py"
  cp /tmp/server_room.py "$ROOT/server.py"
  cp /tmp/sound_inmp441.py "$ROOT/sound_inmp441.py"
  UNIT=/etc/systemd/system/aegis-room-server.service
  # IR DATA moved to PC11 (board 12); PC9 now INMP441 SD
  if grep -q "AEGIS_ROOM_IR_PIN=" "$UNIT"; then
    sed -i "s/Environment=AEGIS_ROOM_IR_PIN=.*/Environment=AEGIS_ROOM_IR_PIN=PC11/" "$UNIT"
  else
    sed -i "/AEGIS_ROOM_LIGHT_PROVIDER=/a Environment=AEGIS_ROOM_IR_PIN=PC11" "$UNIT"
  fi
  grep -q AEGIS_ROOM_SOUND_PROVIDER= "$UNIT" || sed -i "/AEGIS_ROOM_IR_PIN=/a Environment=AEGIS_ROOM_SOUND_PROVIDER=alsa" "$UNIT"
  grep -q AEGIS_ROOM_SOUND_ALSA_DEVICE= "$UNIT" || sed -i "/AEGIS_ROOM_SOUND_PROVIDER=/a Environment=AEGIS_ROOM_SOUND_ALSA_DEVICE=hw:0,0" "$UNIT"
  systemctl daemon-reload
  systemctl restart aegis-room-server
  sleep 2
  systemctl is-active aegis-room-server
  systemctl show aegis-room-server -p Environment --no-pager
  PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python - <<PY
from aegis_room.providers import resolve_ir_pin, create_light_provider
from aegis_room.sound_inmp441 import create_sound_provider, INMP441_WIRING
info = resolve_ir_pin("PC11")
print("ir_pin", info)
p = create_light_provider()
print("light_provider", p.provider_name, getattr(p, "pin", None))
s = create_sound_provider()
print("sound_provider", None if s is None else s.provider_name)
print("wiring", INMP441_WIRING)
if s is not None:
    sample = s.sample(150)
    print("sample", sample.available, sample.db_fs, sample.warning[:120] if sample.warning else "")
PY
'
