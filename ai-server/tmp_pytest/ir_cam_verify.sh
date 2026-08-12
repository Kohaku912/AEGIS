#!/bin/bash
set -euo pipefail
HOST=192.168.50.120
SSHPASS=$(cat /tmp/opi_pw.txt)
export SSHPASS
mkdir -p /tmp/aegis-cam
python3 /tmp/cam_brightness.py /tmp/aegis-cam before
# fire IR off on OPi (gpio PC9), repeat
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
cd /opt/aegis/room-server
PYTHONPATH=/opt/aegis/room-server/src \
.venv/bin/python - <<PY
import grpc
from generated.aegis import room_server_pb2, room_server_pb2_grpc
ch=grpc.insecure_channel("127.0.0.1:50055")
stub=room_server_pb2_grpc.RoomServerStub(ch)
for i in range(3):
  r=stub.SetLight(room_server_pb2.SetLightRequest(device_id="light-main", power_on=False, mode="off", brightness=-1))
  print("off", i, r.status.code, r.status.message)
r=stub.SendIrCommand(room_server_pb2.SendIrCommandRequest(device_type="light", ir_code="0xD001:0x23", repeat=5))
print("ir", r.status.code)
# also try active-low path via env in-process
import os
os.environ["AEGIS_ROOM_LIGHT_PROVIDER"]="gpio"
os.environ["AEGIS_ROOM_IR_PIN"]="PC9"
os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"]="1"
from aegis_room.providers import create_light_provider
p=create_light_provider()
ev=p.send_ir_command("light","0xD001:0x23",5)
print("active_low", ev.get("tx"), ev.get("warning"))
ch.close()
PY
'
sleep 1
python3 /tmp/cam_brightness.py /tmp/aegis-cam after
python3 - <<PY
import json
from pathlib import Path
b=json.loads(Path("/tmp/aegis-cam/before.jpg").with_name(".."))
PY
# compare json lines from script stdout already printed; also write summary
python3 - <<'PY'
import json,glob
from pathlib import Path
# cam_brightness prints json; recompute from saved jpgs if needed
import subprocess, os
shots={}
for label in ("before","after"):
  p=Path(f"/tmp/aegis-cam/{label}.jpg")
  print(label, "exists", p.exists(), "bytes", p.stat().st_size if p.exists() else 0)
PY
