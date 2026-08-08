#!/bin/bash
set -euo pipefail
export SSHPASS
SSHPASS=$(cat /tmp/opi_pw.txt)

echo "== ping known =="
for h in 192.168.50.108 192.168.50.120 192.168.50.109 192.168.50.110; do
  if ping -c 1 -W 1 "$h" >/dev/null 2>&1; then echo "ping OK $h"; else echo "ping FAIL $h"; fi
done

echo "== arp after sweep =="
# ping common range quickly
for i in $(seq 100 130); do ping -c 1 -W 1 "192.168.50.$i" >/dev/null 2>&1 & done
wait
ip neigh show | grep '192.168.50' | sort -t. -k4 -n || true

echo "== tcp22 slow probe 100-140 =="
python3 - <<'PY'
import socket
for i in range(100,141):
    ip=f'192.168.50.{i}'
    s=socket.socket(); s.settimeout(0.5)
    try:
        s.connect((ip,22)); print('ssh', ip)
    except Exception:
        pass
    finally:
        s.close()
    s=socket.socket(); s.settimeout(0.5)
    try:
        s.connect((ip,50055)); print('room', ip)
    except Exception:
        pass
    finally:
        s.close()
PY

echo "== try ssh .108 =="
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@192.168.50.108 'hostname; ip -br a; uptime' 2>&1 | head -40 || true

echo "== try ssh from arp REACHABLE unknown hosts =="
# Exclude known ubuntu/gateway/pc
KNOWN='192.168.50.1 192.168.50.41 192.168.50.195'
while read -r ip; do
  echo "$KNOWN" | grep -qw "$ip" && continue
  echo "-- try $ip --"
  if sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=4 root@"$ip" 'hostname; ip -br a' 2>/dev/null; then
    echo "$ip" > /tmp/opi_host.txt
    echo FOUND "$ip"
    break
  fi
done < <(ip neigh | awk '/192\.168\.50\./{print $1}' | sort -u)
