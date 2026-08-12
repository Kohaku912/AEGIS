#!/bin/bash
set -e
pkill -f ir_pin_safe_sweep || true
pkill -f poll_safe_sweep || true
SSHPASS=$(cat /tmp/opi_pw.txt)
export SSHPASS
HOST=192.168.50.120
ping -c2 -W2 $HOST
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 root@$HOST '
uptime
systemctl start aegis-room-server
systemctl is-active aegis-room-server
dmesg | grep -iE "nobody cared|axp|Under|throttl" | tail -10
'
