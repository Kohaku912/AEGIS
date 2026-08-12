#!/bin/bash
set -euo pipefail
HOST=192.168.50.120
SSHPASS=$(cat /tmp/opi_pw.txt)
export SSHPASS
mkdir -p /tmp/aegis-cam
python3 /tmp/cam_brightness.py /tmp/aegis-cam before
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST 'cd /opt/aegis/room-server; PYTHONPATH=/opt/aegis/room-server/src .venv/bin/python - <<'"'"'PY'"'"'
import grpc, os
from generated.aegis import room_server_pb2, room_server_pb2_grpc
ch=grpc.insecure_channel("127.0.0.1:50055")
stub=room_server_pb2_grpc.RoomServerStub(ch)
# power off via service (normal polarity as configured)
for i in range(3):
  r=stub.SetLight(room_server_pb2.SetLightRequest(device_id="light-main", power_on=False, mode="off", brightness=-1))
  print("svc_off", i, r.status.code, r.status.message)
# also try each light mode once in case mapping differs
for code in ["0xD001:0x23", "0xD001:0x20", "0xD001:0x21", "0xD001:0x22"]:
  r=stub.SendIrCommand(room_server_pb2.SendIrCommandRequest(device_type="light", ir_code=code, repeat=3))
  print("code", code, r.status.code)
ch.close()
# direct mmap with active-low toggle
os.environ["AEGIS_ROOM_LIGHT_PROVIDER"]="gpio"
os.environ["AEGIS_ROOM_IR_PIN"]="PC9"
from aegis_room.providers import create_light_provider
for active_low in ("0", "1"):
  os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"]=active_low
  p=create_light_provider()
  ev=p.send_ir_command("light", "0xD001:0x23", 4)
  print("direct", active_low, ev.get("tx"), ev.get("warning"))
PY'
sleep 2
python3 /tmp/cam_brightness.py /tmp/aegis-cam after
python3 - <<'PY'
import json
from pathlib import Path
def load(label):
  # last line of stdout was printed by cam script; recompute from jpg via pgm already done in script output files
  pass
# compare from saved metadata if present; else recompute
import subprocess
def bright(path):
  raw=Path(str(path)+'.pgm')
  subprocess.run(['ffmpeg','-y','-i',str(path),'-vf','scale=160:120,format=gray',str(raw)],capture_output=True)
  pix=raw.read_bytes().split(b'\n',3)[-1]
  return sum(pix)/max(1,len(pix))
b=bright('/tmp/aegis-cam/before.jpg')
a=bright('/tmp/aegis-cam/after.jpg')
print(json.dumps({"before": round(b,2), "after": round(a,2), "delta": round(a-b,2)}, ensure_ascii=False))
PY
