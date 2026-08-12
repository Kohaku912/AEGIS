#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
echo "=== h616 overlays ==="
ls /boot/dtb*/allwinner/overlay/*h616* 2>/dev/null | head -80
ls /boot/dtb-*/allwinner/overlay 2>/dev/null | rg -i "h616|i2s" || ls /boot/dtb-*/allwinner/overlay 2>/dev/null | grep -iE "h616|i2s" || true
echo "=== armbianEnv ==="
cat /boot/armbianEnv.txt 2>/dev/null || true
echo "=== aplay/arecord cards ==="
cat /proc/asound/cards 2>/dev/null || true
echo "=== pinmux PC6/8/9/11 ==="
# dump cfg if script exists; else just note
PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python - <<PY
import mmap, struct
BASE=0x0300B000
STRIDE=0x24
def bank_bit(name):
    return ord(name[1])-ord("A"), int(name[2:])
with open("/dev/mem","r+b",buffering=0) as f:
    m=mmap.mmap(f.fileno(),0x1000,offset=BASE)
    for pin in ("PC6","PC8","PC9","PC11"):
        bank,bit=bank_bit(pin)
        off=bank*STRIDE+(bit//8)*4
        shift=(bit%8)*4
        cfg=struct.unpack_from("<I",m,off)[0]
        mode=(cfg>>shift)&0xF
        print(pin, "cfg_mode", mode)
    m.close()
PY
'
