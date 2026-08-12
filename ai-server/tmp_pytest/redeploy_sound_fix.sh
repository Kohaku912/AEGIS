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
echo "=== arecord -l ==="
arecord -l 2>&1 || true
echo "=== overlays ==="
ls /boot/dtb*/*/overlay* 2>/dev/null | head -5
ls /boot/dtb/allwinner/overlay 2>/dev/null | head -40 || true
ls /boot/dtb/orangepi/overlay 2>/dev/null | head -40 || true
grep -iE "overlay|i2s|param" /boot/armbianEnv.txt /boot/orangepiEnv.txt /boot/uEnv.txt 2>/dev/null || true
echo "=== sample ==="
AEGIS_ROOM_SOUND_PROVIDER=alsa AEGIS_ROOM_SOUND_ALSA_DEVICE=hw:0,0 \
PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python -c \
"from aegis_room.sound_inmp441 import create_sound_provider; s=create_sound_provider(); x=s.sample(250); print(x.available, x.db_fs, x.warning[:200] if x.warning else \"\")"
'
