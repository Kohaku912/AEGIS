#!/bin/bash
set -euo pipefail
export SSHPASS
SSHPASS=$(cat /tmp/opi_pw.txt)
for h in 192.168.50.120 192.168.50.108; do
  echo "== $h =="
  if sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@"$h" \
    'echo OK; for i in end0 wlan0; do echo "$i $(cat /sys/class/net/$i/address 2>/dev/null)"; done; ip -br a'; 2>/dev/null; then
    break
  fi
done
echo "== host neigh for room/pc =="
# refresh
for ip in 192.168.50.108 192.168.50.120 192.168.50.195 192.168.50.176; do ping -c 1 -W 1 $ip >/dev/null 2>&1 || true; done
ip neigh | grep -E '192.168.50.(108|120|195|176|198)' || true
echo "== volumes =="
docker inspect aegis-ai-server-1 --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}' | head -40
