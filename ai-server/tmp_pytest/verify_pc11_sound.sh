#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
systemctl is-active aegis-room-server
tr "\0" "\n" < /proc/$(systemctl show -p MainPID --value aegis-room-server)/environ | grep -E "AEGIS_ROOM_(IR_PIN|SOUND|LIGHT)" | sort
PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python - <<PY
import os
os.environ["AEGIS_ROOM_LIGHT_PROVIDER"]="gpio"
os.environ["AEGIS_ROOM_IR_PIN"]="PC11"
os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"]="0"
os.environ["AEGIS_ROOM_SOUND_PROVIDER"]="alsa"
os.environ["AEGIS_ROOM_SOUND_ALSA_DEVICE"]="hw:0,0"
from aegis_room.providers import create_light_provider
from aegis_room.sound_inmp441 import create_sound_provider
from aegis_room.server import VERSION
p=create_light_provider()
print("version", VERSION)
print("ir", p.provider_name, p.pin, p._pin_info)
s=create_sound_provider()
print("sound", s.provider_name)
sample=s.sample(200)
print("available", sample.available, "db_fs", sample.db_fs, "warn", (sample.warning or "")[:160])
PY
arecord -l 2>&1 | head -20 || true
'
