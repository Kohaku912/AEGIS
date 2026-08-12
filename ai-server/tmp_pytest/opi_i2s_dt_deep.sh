#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
dtc -I dtb -O dts -o /tmp/running.dts /sys/firmware/fdt 2>/dev/null
echo "=== ahub / i2s / daudio symbols ==="
grep -nE "ahub|i2s|daudio|snd-mach|snd-plat" /tmp/running.dts | head -100
echo "=== modules ==="
lsmod | grep -iE "snd|ahub|i2s|sunxi" || true
echo "=== sound cards detailed ==="
cat /proc/asound/cards
ls -la /dev/snd/
echo "=== pinmux-pins if debugfs ==="
if [ -r /sys/kernel/debug/pinctrl/300b000.pinctrl/pinmux-pins ]; then
  grep -E "PC6|PC8|PC9|PC11|PH6|PH7|PH8|PH9" /sys/kernel/debug/pinctrl/300b000.pinctrl/pinmux-pins || true
fi
echo "=== armbianEnv overlays path ==="
ls /boot/dtb/allwinner/overlay | grep h616 | head
cat /boot/armbianEnv.txt
# Does this image use overlays= or user_overlays=?
ls /boot/overlay-user 2>/dev/null || mkdir -p /boot/overlay-user
'
