#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
OUT=/tmp/aegis-cam/retry_arduino_nec
mkdir -p "$OUT"

sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  /tmp/providers.py root@$HOST:/opt/aegis/room-server/src/aegis_room/providers.py
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST \
  'systemctl restart aegis-room-server; sleep 1; systemctl is-active aegis-room-server'

echo "=== BEFORE ==="
python3 /tmp/cam_brightness.py "$OUT" before

sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST 'bash -s' <<'EOS'
set -e
export PYTHONPATH=/opt/aegis/room-server/src
export AEGIS_ROOM_LIGHT_PROVIDER=gpio
export AEGIS_ROOM_IR_PIN=PC9
export AEGIS_ROOM_IR_ACTIVE_LOW=0
export AEGIS_ROOM_IR_BIT_ORDER=lsb
export AEGIS_ROOM_IR_ADDR_MODE=auto
cd /opt/aegis/room-server
.venv/bin/python <<'PY'
import grpc, time, os
from generated.aegis import room_server_pb2, room_server_pb2_grpc
from aegis_room.providers import OrangePiGpioIrProvider, create_light_provider

p = create_light_provider()
# sanity: payload must match Arduino sendNEC(0xD001, 0x23)
assert p._build_nec_payload(0xD001, 0x23) == 0xDC23D001, hex(p._build_nec_payload(0xD001, 0x23))
print("payload_ok", hex(p._build_nec_payload(0xD001, 0x23)))
print("idle", p.ensure_safe_idle())

ch = grpc.insecure_channel("127.0.0.1:50055")
stub = room_server_pb2_grpc.RoomServerStub(ch)
# Arduino uses sendNEC(..., 3) => 1 frame + 3 repeats; send a few full frames
for i in range(2):
    r = stub.SetLight(room_server_pb2.SetLightRequest(
        device_id="light-main", power_on=False, mode="off", brightness=-1
    ))
    print("svc_off", i, r.status.code, r.status.message)
    time.sleep(0.2)
ev = p.send_ir_command("light", "0xD001:0x23", 4)
print("tx", ev.get("tx"))
print("idle_after", p.ensure_safe_idle())
ch.close()
PY
EOS

sleep 2
echo "=== AFTER ==="
python3 /tmp/cam_brightness.py "$OUT" after
python3 - <<'PY'
import json, subprocess
from pathlib import Path

def bright(path):
    raw = Path(str(path)+".meas.pgm")
    subprocess.run(["ffmpeg","-y","-i",str(path),"-vf","scale=160:120,format=gray",str(raw)],capture_output=True)
    pix=raw.read_bytes().split(b"\n",3)[-1]
    return sum(pix)/max(1,len(pix))
b=bright("/tmp/aegis-cam/retry_arduino_nec/before.jpg")
a=bright("/tmp/aegis-cam/retry_arduino_nec/after.jpg")
print(json.dumps({"before":round(b,2),"after":round(a,2),"delta":round(a-b,2)}))
PY
