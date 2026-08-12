#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
echo "=== pinmux ==="
grep -E "PH5|PH6|PH7|PH8|PH9|PC11" /sys/kernel/debug/pinctrl/300b000.pinctrl/pinmux-pins
echo "=== cards ==="
arecord -l
echo "=== quiet 1s ==="
timeout 8 arecord -D hw:ahubi2s3,0 -f S32_LE -r 16000 -c 2 -d 1 -t raw /tmp/mic_quiet.raw
python3 - <<PY
import struct, math
raw=open("/tmp/mic_quiet.raw","rb").read()
n=len(raw)//4
s=struct.unpack(f"<{n}i", raw[:n*4])
left=s[0::2]
peak=max(abs(x) for x in left)
rms=math.sqrt(sum(x*x for x in left)/len(left))
uniq=len(set(left[:4000]))
print(f"quiet bytes={len(raw)} peak={peak} rms={int(rms)} uniq={uniq} first8={left[:8]}")
PY
echo "=== provider sample ==="
AEGIS_ROOM_SOUND_PROVIDER=alsa AEGIS_ROOM_SOUND_ALSA_DEVICE=hw:ahubi2s3,0 \
PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python - <<PY
from aegis_room.sound_inmp441 import create_sound_provider
s=create_sound_provider()
x=s.sample(1000)
print("available", x.available)
print("rms", x.rms)
print("peak", x.peak)
print("db_fs", x.db_fs)
print("wiring", x.wiring)
print("warning", x.warning or "")
PY
echo "=== grpc get_level via device status ==="
PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python - <<PY
import grpc
from generated.aegis import room_server_pb2, room_server_pb2_grpc
ch=grpc.insecure_channel("127.0.0.1:50055")
stub=room_server_pb2_grpc.RoomServerStub(ch)
r=stub.GetDeviceStatus(room_server_pb2.GetDeviceStatusRequest(device_ids=["sound-inmp441"]), timeout=8)
for d in r.devices:
    print(d.device_id, d.online, d.state_json[:300])
PY
'
