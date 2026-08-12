#!/bin/bash
chmod +x /tmp/poll_safe2.sh
nohup bash /tmp/poll_safe2.sh > /tmp/aegis-cam/poll_safe2.out 2>&1 &
echo poll_pid=$!
sleep 2
tail -n 5 /tmp/aegis-cam/poll_safe2.out
pgrep -af "ir_pin_safe_sweep2|poll_safe2" || true
