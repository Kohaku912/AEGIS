#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
echo "=== uname / model ==="
uname -a
cat /proc/device-tree/model 2>/dev/null; echo
echo "=== i2s / ahub nodes ==="
find /sys/firmware/devicetree/base -iname "*i2s*" -o -iname "*ahub*" -o -iname "*audio*" 2>/dev/null | head -80
echo "=== status ==="
for n in /proc/device-tree/soc*/i2s* /proc/device-tree/soc*/ahub* /sys/firmware/devicetree/base/soc*/i2s* /sys/firmware/devicetree/base/*/i2s*; do
  [ -e "$n" ] || continue
  echo "-- $n"
  [ -f "$n/status" ] && echo -n "status="; cat "$n/status"; echo
  [ -f "$n/compatible" ] && echo -n "compat="; cat "$n/compatible" | tr "\0" " "; echo
done 2>/dev/null | head -60
echo "=== dtc decompile sound-related from running dtb ==="
DTB=$(ls /boot/dtb*/allwinner/sun50i-h618*.dtb 2>/dev/null | head -1)
echo "dtb=$DTB"
ls /boot/dtb*/allwinner/sun50i-h618* 2>/dev/null | head
ls /boot/dtb/allwinner/sun50i-h618* 2>/dev/null | head
if command -v dtc >/dev/null; then
  dtc -I dtb -O dts -o /tmp/running.dts /sys/firmware/fdt 2>/dev/null || true
  if [ -f /tmp/running.dts ]; then
    rg -n -i "i2s|ahub|dai|simple-audio|pcm510|inmp|sound" /tmp/running.dts | head -80
  fi
fi
echo "=== packages ==="
which dtc cpp dtc || true
dpkg -l | grep -iE "device-tree|dtc|linux-headers" | head -20
'
