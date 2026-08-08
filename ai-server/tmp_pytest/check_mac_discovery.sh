#!/bin/bash
set -euo pipefail
echo "== container network =="
docker inspect aegis-ai-server-1 --format '{{json .HostConfig.NetworkMode}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
echo "== host arp sample =="
ip neigh | head -20
cat /proc/net/arp | head -20
echo "== container arp =="
docker exec aegis-ai-server-1 sh -c 'cat /proc/net/arp; command -v ip; ip neigh 2>/dev/null | head' || true
echo "== opi macs =="
export SSHPASS
SSHPASS=$(cat /tmp/opi_pw.txt)
for h in 192.168.50.120 192.168.50.108; do
  echo "-- $h --"
  sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@"$h" \
    'hostname; for i in end0 wlan0; do echo -n "$i "; cat /sys/class/net/$i/address 2>/dev/null; done; ip -br a' 2>&1 | head -20 || true
done
echo "== pc mac via windows not here; from arp =="
ip neigh | grep -E '192.168.50.(195|176)' || true
grep -E 'ROOM_SERVER|PC_SERVER|MAC' /opt/aegis/.env || true
