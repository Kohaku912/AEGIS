#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  /tmp/sun50i-h616-i2s3-inmp441.dts root@$HOST:/tmp/sun50i-h616-i2s3-inmp441.dts
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
# remove broken ahub_dam_mach if previous overlay left junk - reboot clears
DTS=/tmp/sun50i-h616-i2s3-inmp441.dts
dtc -@ -I dts -O dtb -o /boot/dtb/allwinner/overlay/sun50i-h616-i2s3-inmp441.dtbo "$DTS"
cp -f /boot/dtb/allwinner/overlay/sun50i-h616-i2s3-inmp441.dtbo /boot/dtb/allwinner/overlay/sun50i-h616-i2s3.dtbo
cp -f /boot/dtb/allwinner/overlay/sun50i-h616-i2s3-inmp441.dtbo /boot/overlay-user/sun50i-h616-i2s3-inmp441.dtbo
# drop ahub_dam from user overlays path already handled by new dts
# keep only one overlay source to avoid double-apply: prefer overlays=i2s3
sed -i "/^user_overlays=/d" /boot/armbianEnv.txt
grep -q "^overlays=.*i2s3" /boot/armbianEnv.txt || echo "overlays=i2s3" >> /boot/armbianEnv.txt
cat /boot/armbianEnv.txt
sync
nohup bash -c "sleep 1; reboot" >/dev/null 2>&1 &
'
echo "reboot..."
sleep 20
for i in $(seq 1 36); do
  if OUT=$(sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@$HOST '
    echo UP
    arecord -l
    grep -E "PH5|PH6|PH7|PH8|PH9" /sys/kernel/debug/pinctrl/300b000.pinctrl/pinmux-pins
    python3 - <<PY
import mmap,struct
BASE=0x0300B000; STRIDE=0x24
def mode(pin):
  bank=ord(pin[1])-ord("A"); bit=int(pin[2:])
  off=bank*STRIDE+(bit//8)*4; shift=(bit%8)*4
  with open("/dev/mem","r+b",buffering=0) as f:
    m=mmap.mmap(f.fileno(),0x1000,offset=BASE)
    cfg=struct.unpack_from("<I",m,off)[0]; m.close()
  return (cfg>>shift)&0xF
print("cfg", {p:mode(p) for p in ("PH5","PH6","PH7","PH8","PH9")})
PY
  ' 2>/dev/null); then
    echo "$OUT"
    exit 0
  fi
  echo wait_$i
  sleep 5
done
exit 1
