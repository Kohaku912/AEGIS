#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/opi_pin_blast_safe.py root@$HOST:/tmp/
chmod +x /tmp/ir_pin_safe_sweep2.sh
pkill -f ir_pin_safe_sweep || true
rm -f /tmp/aegis-cam/pin_safe2.log /tmp/aegis-cam/pin_safe2_nohup.out
mkdir -p /tmp/aegis-cam
nohup bash /tmp/ir_pin_safe_sweep2.sh > /tmp/aegis-cam/pin_safe2_nohup.out 2>&1 &
echo started=$!
sleep 8
tail -n 25 /tmp/aegis-cam/pin_safe2.log || tail -n 25 /tmp/aegis-cam/pin_safe2_nohup.out
