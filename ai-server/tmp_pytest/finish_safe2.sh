#!/bin/bash
set -e
pkill -f ir_pin_safe_sweep2 || true
bash /tmp/opi_health.sh || true
python3 /tmp/summarize_safe2.py
echo "==== log tail ===="
tail -n 30 /tmp/aegis-cam/pin_safe2.log || true
