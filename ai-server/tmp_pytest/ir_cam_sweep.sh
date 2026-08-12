#!/bin/bash
# Host-side: for each IR variant, measure USB-cam brightness before/after.
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
mkdir -p /tmp/aegis-cam/sweep
python3 /tmp/cam_brightness.py /tmp/aegis-cam/sweep baseline
echo "BASELINE done"

run_tx() {
  local al="$1" bo="$2" am="$3" code="$4" label="$5"
  sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST \
    "AEGIS_ROOM_LIGHT_PROVIDER=gpio AEGIS_ROOM_IR_PIN=PC9 AEGIS_ROOM_IR_ACTIVE_LOW=$al AEGIS_ROOM_IR_BIT_ORDER=$bo AEGIS_ROOM_IR_ADDR_MODE=$am PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python -c \"
from aegis_room.providers import create_light_provider
p=create_light_provider()
ev=p.send_ir_command('light','$code',4)
print(ev.get('tx'), ev.get('warning'))
\""
  sleep 1.2
  python3 /tmp/cam_brightness.py /tmp/aegis-cam/sweep "$label"
}

# Deployed providers.py must already be on OPi
run_tx 0 msb extended '0xD001:0x23' v01_msb_ext_hi
run_tx 1 msb extended '0xD001:0x23' v02_msb_ext_lo
run_tx 0 lsb extended '0xD001:0x23' v03_lsb_ext_hi
run_tx 1 lsb extended '0xD001:0x23' v04_lsb_ext_lo
run_tx 1 lsb standard '0xD001:0x23' v05_lsb_std_lo
run_tx 1 msb standard '0x01:0x23' v06_msb_std01_lo
run_tx 1 lsb standard '0x01:0x23' v07_lsb_std01_lo

python3 - <<'PY'
import json, subprocess
from pathlib import Path
def bright(jpg):
    raw=Path(str(jpg)+'.meas.pgm')
    subprocess.run(['ffmpeg','-y','-i',str(jpg),'-vf','scale=160:120,format=gray',str(raw)],capture_output=True)
    pix=raw.read_bytes().split(b'\n',3)[-1]
    return round(sum(pix)/max(1,len(pix)),2)
base=Path('/tmp/aegis-cam/sweep')
rows=[]
base_b=bright(base/'baseline.jpg')
for p in sorted(base.glob('v*.jpg')):
    b=bright(p)
    rows.append({"label": p.stem, "brightness": b, "delta_vs_baseline": round(b-base_b,2)})
print(json.dumps({"baseline": base_b, "variants": rows}, ensure_ascii=False, indent=2))
PY
