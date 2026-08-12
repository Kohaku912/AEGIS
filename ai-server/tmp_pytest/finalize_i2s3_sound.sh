#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
DEV=hw:ahubi2s3,0
echo "=== capture test $DEV ==="
timeout 5 arecord -D "$DEV" -f S32_LE -r 16000 -c 2 -d 1 -t raw /tmp/mic4.raw
python3 - <<PY
import struct, math
raw=open("/tmp/mic4.raw","rb").read()
n=len(raw)//4
s=struct.unpack(f"<{n}i", raw[:n*4])
peak=max(abs(x) for x in s)
rms=math.sqrt(sum(x*x for x in s)/len(s))
print("bytes",len(raw),"peak",peak,"rms",int(rms),"unique",len(set(s[:2000])))
print("first8",s[:8])
PY
UNIT=/etc/systemd/system/aegis-room-server.service
# prefer named card so index shifts do not break us
if grep -q AEGIS_ROOM_SOUND_ALSA_DEVICE= "$UNIT"; then
  sed -i "s#Environment=AEGIS_ROOM_SOUND_ALSA_DEVICE=.*#Environment=AEGIS_ROOM_SOUND_ALSA_DEVICE=hw:ahubi2s3,0#" "$UNIT"
else
  sed -i "/AEGIS_ROOM_SOUND_PROVIDER=/a Environment=AEGIS_ROOM_SOUND_ALSA_DEVICE=hw:ahubi2s3,0" "$UNIT"
fi
grep -E "SOUND|IR_PIN" "$UNIT"
systemctl daemon-reload
systemctl restart aegis-room-server
sleep 2
systemctl is-active aegis-room-server
# ensure IR pin still PC11 after reboot
tr "\0" "\n" < /proc/$(systemctl show -p MainPID --value aegis-room-server)/environ | grep AEGIS_ROOM_ | sort
AEGIS_ROOM_SOUND_PROVIDER=alsa AEGIS_ROOM_SOUND_ALSA_DEVICE=hw:ahubi2s3,0 \
PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python - <<PY
from aegis_room.sound_inmp441 import create_sound_provider
s=create_sound_provider()
x=s.sample(1000)
print("sample", x.available, "rms", x.rms, "peak", x.peak, "db", x.db_fs, "warn", x.warning)
PY
'
