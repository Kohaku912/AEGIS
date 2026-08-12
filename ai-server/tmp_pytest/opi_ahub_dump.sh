#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
# dump ahub1 + dma fragments for overlay reference
awk "/ahub1_plat|ahub1_mach|dma@|dma: |ahub_dam_plat/,0" /tmp/running.dts 2>/dev/null | head -5
sed -n "/ahub_dam_plat@5097000/,/^[[:space:]]*};/p" /tmp/running.dts | head -40
echo "==== ahub1_plat ===="
sed -n "/ahub1_plat {/,/^[[:space:]]*};/p" /tmp/running.dts | head -50
echo "==== ahub1_mach ===="
sed -n "/ahub1_mach {/,/^[[:space:]]*ahub1_codec/,/^[[:space:]]*};/p" /tmp/running.dts | head -60
echo "==== dma label ===="
grep -nE "dma[@:]|dma =" /tmp/running.dts | head -20
grep -n "dma {" /tmp/running.dts | head
sed -n "/dma@3002000 {/,/^[[:space:]]*status/p" /tmp/running.dts | head -30
ls /sys/bus/platform/drivers/ | grep -iE "ahub|snd|sunxi" || true
'
