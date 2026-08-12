#!/bin/bash
for i in $(seq 1 45); do
  if grep -qE "NO_CLEAR_HIT|LIKELY_HIT|OPI_DOWN|TX_FAIL" /tmp/aegis-cam/pin_safe.log 2>/dev/null; then
    echo DONE
    break
  fi
  SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
  up=$(sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=4 root@192.168.50.120 "cut -d. -f1 /proc/uptime" 2>/dev/null || echo DOWN)
  prog=$(grep -E "^=== PIN|delta " /tmp/aegis-cam/pin_safe.log 2>/dev/null | tail -n 1)
  echo "t=$i opi=$up :: $prog"
  if [ "$up" = "DOWN" ]; then
    echo OPI_DOWN
    break
  fi
  sleep 6
done
echo "==== TAIL ===="
tail -n 50 /tmp/aegis-cam/pin_safe.log
