#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
echo "=== pinmux PH/PC ==="
grep -E "PC6|PC8|PC9|PC11|PH5|PH6|PH7|PH8|PH9" /sys/kernel/debug/pinctrl/300b000.pinctrl/pinmux-pins || true
echo "=== amixer ahubi2s3 ==="
amixer -c ahubi2s3 scontrols 2>&1 | head -40
amixer -c ahubdam scontrols 2>&1 | head -40 || true
echo "=== try capture hw:2,0 ==="
arecord -D hw:2,0 -f S32_LE -r 16000 -c 2 -d 1 -t raw /tmp/mic1.raw 2>&1 | tee /tmp/arecord1.log || true
ls -la /tmp/mic1.raw 2>/dev/null || true
# try plughw
arecord -D plughw:2,0 -f S16_LE -r 16000 -c 1 -d 1 /tmp/mic2.wav 2>&1 | tee /tmp/arecord2.log || true
ls -la /tmp/mic2.wav 2>/dev/null || true
# list all cards controls related to APBIF / I2S3
for c in 0 1 2 3; do
  echo "-- card $c"
  amixer -c $c 2>/dev/null | grep -iE "i2s3|apbif|rx|tx|src|hub" | head -20 || true
done
# dmesg audio
dmesg | grep -iE "ahub|i2s3|snd|inmp" | tail -30
'
