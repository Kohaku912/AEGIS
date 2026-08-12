#!/bin/bash
for i in $(seq 1 50); do
  if grep -qE "NO_CLEAR_HIT|LIKELY_HIT|OPI_DOWN" /tmp/aegis-cam/pin_safe2.log 2>/dev/null; then
    echo DONE
    break
  fi
  if ! pgrep -f ir_pin_safe_sweep2 >/dev/null; then
    echo SWEEP_EXITED
    break
  fi
  SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
  up=$(sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@192.168.50.120 "cut -d. -f1 /proc/uptime" 2>/dev/null || echo DOWN)
  prog=$(grep -E "^=== PIN|delta " /tmp/aegis-cam/pin_safe2.log 2>/dev/null | tail -n 1)
  echo "t=$i opi=$up :: $prog"
  if [ "$up" = "DOWN" ]; then echo OPI_DOWN; break; fi
  sleep 8
done
echo "==== FINAL ===="
tail -n 55 /tmp/aegis-cam/pin_safe2.log
