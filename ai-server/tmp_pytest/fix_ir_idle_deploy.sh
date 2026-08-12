#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120

sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  /tmp/providers.py root@$HOST:/opt/aegis/room-server/src/aegis_room/providers.py

sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST 'bash -s' <<'EOS'
set -e
UNIT=/etc/systemd/system/aegis-room-server.service
# Force Arduino-compatible idle (DATA LOW) + LSB NEC
if grep -q AEGIS_ROOM_IR_ACTIVE_LOW "$UNIT"; then
  sed -i 's/Environment=AEGIS_ROOM_IR_ACTIVE_LOW=.*/Environment=AEGIS_ROOM_IR_ACTIVE_LOW=0/' "$UNIT" || true
fi
if ! grep -q AEGIS_ROOM_IR_ACTIVE_LOW "$UNIT"; then
  sed -i '/AEGIS_ROOM_IR_PIN=/a Environment=AEGIS_ROOM_IR_ACTIVE_LOW=0' "$UNIT"
fi
if ! grep -q AEGIS_ROOM_IR_BIT_ORDER "$UNIT"; then
  sed -i '/AEGIS_ROOM_IR_ACTIVE_LOW=/a Environment=AEGIS_ROOM_IR_BIT_ORDER=lsb' "$UNIT"
else
  sed -i 's/Environment=AEGIS_ROOM_IR_BIT_ORDER=.*/Environment=AEGIS_ROOM_IR_BIT_ORDER=lsb/' "$UNIT"
fi
systemctl daemon-reload
systemctl restart aegis-room-server
sleep 1
systemctl is-active aegis-room-server
systemctl show aegis-room-server -p Environment --no-pager

PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python - <<'PY'
import os, time
os.environ["AEGIS_ROOM_LIGHT_PROVIDER"]="gpio"
os.environ["AEGIS_ROOM_IR_PIN"]="PC9"
os.environ["AEGIS_ROOM_IR_ACTIVE_LOW"]="0"
os.environ["AEGIS_ROOM_IR_BIT_ORDER"]="lsb"
from aegis_room.providers import create_light_provider
p=create_light_provider()
idle=p.ensure_safe_idle()
print("idle_after_init", idle)
assert idle["level"]==0, idle
# prove the wire can toggle, then must return LOW
import mmap, struct
PIO=0x0300B000; STRIDE=0x24; bank,bit=2,9
bank_off=bank*STRIDE; cfg_off=bank_off+(bit//8)*4; cfg_shift=(bit%8)*4; dat_off=bank_off+0x10
with open("/dev/mem","r+b",buffering=0) as f:
  m=mmap.mmap(f.fileno(),0x1000,offset=PIO)
  def level():
    return (struct.unpack_from("<I",m,dat_off)[0]>>bit)&1
  def set_level(h):
    d=struct.unpack_from("<I",m,dat_off)[0]
    d = (d| (1<<bit)) if h else (d & ~(1<<bit))
    struct.pack_into("<I",m,dat_off,d)
  set_level(1); time.sleep(0.05); hi=level()
  set_level(0); time.sleep(0.05); lo=level()
  print({"toggle_hi":hi,"toggle_lo":lo})
  assert hi==1 and lo==0
  m.close()
idle2=p.ensure_safe_idle()
print("idle_final", idle2)
assert idle2["level"]==0
# short IR off burst then confirm still low
ev=p.send_ir_command("light","0xD001:0x23",2)
print("tx", ev.get("tx"))
print("idle_post_tx", p.ensure_safe_idle())
print("OK_PC9_PARKED_LOW")
PY
EOS
