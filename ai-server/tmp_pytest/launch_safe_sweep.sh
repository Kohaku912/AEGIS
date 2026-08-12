#!/bin/bash
set -euo pipefail
pkill -f ir_pin_retry_arduino || true
pkill -f opi_pin_blast || true
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/opi_pin_blast_safe.py root@$HOST:/tmp/
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 root@$HOST \
  'uptime; systemctl start aegis-room-server; systemctl is-active aegis-room-server; dmesg | grep -iE "nobody cared|axp" | tail -5'
chmod +x /tmp/ir_pin_safe_sweep.sh /tmp/cam_brightness.py
rm -f /tmp/aegis-cam/pin_safe.log
mkdir -p /tmp/aegis-cam
nohup bash /tmp/ir_pin_safe_sweep.sh > /tmp/aegis-cam/pin_safe.log 2>&1 &
echo started=$!
sleep 5
tail -n 20 /tmp/aegis-cam/pin_safe.log
