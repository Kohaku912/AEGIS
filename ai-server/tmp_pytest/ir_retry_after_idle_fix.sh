#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
OUT=/tmp/aegis-cam/retry_idlefix
mkdir -p "$OUT"

sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 root@$HOST \
  'systemctl start aegis-room-server; systemctl is-active aegis-room-server'

echo "=== BEFORE ==="
python3 /tmp/cam_brightness.py "$OUT" before

echo "=== IR OFF on PC9 ==="
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST 'bash -s' <<'EOS'
set -e
cd /opt/aegis/room-server
export PYTHONPATH=/opt/aegis/room-server/src
.venv/bin/python <<'PY'
import grpc, time, os
from generated.aegis import room_server_pb2, room_server_pb2_grpc
from aegis_room.providers import create_light_provider

os.environ["AEGIS_ROOM_LIGHT_PROVIDER"] = "gpio"
os.environ["AEGIS_ROOM_IR_PIN"] = "PC9"
os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"] = "0"
os.environ["AEGIS_ROOM_IR_BIT_ORDER"] = "lsb"

p = create_light_provider()
print("idle_before", p.ensure_safe_idle())

ch = grpc.insecure_channel("127.0.0.1:50055")
stub = room_server_pb2_grpc.RoomServerStub(ch)
for i in range(3):
    r = stub.SetLight(room_server_pb2.SetLightRequest(
        device_id="light-main", power_on=False, mode="off", brightness=-1
    ))
    print("svc_off", i, r.status.code, r.status.message)
    time.sleep(0.25)

ev = p.send_ir_command("light", "0xD001:0x23", 5)
print("direct", ev.get("tx"), ev.get("warning"))
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

def bright(path: Path) -> float:
    raw = path.with_suffix(".meas.pgm")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(path), "-vf", "scale=160:120,format=gray", str(raw)],
        capture_output=True,
    )
    pix = raw.read_bytes().split(b"\n", 3)[-1]
    return sum(pix) / max(1, len(pix))

b = bright(Path("/tmp/aegis-cam/retry_idlefix/before.jpg"))
a = bright(Path("/tmp/aegis-cam/retry_idlefix/after.jpg"))
print(json.dumps({"before": round(b, 2), "after": round(a, 2), "delta": round(a - b, 2)}, ensure_ascii=False))
PY
