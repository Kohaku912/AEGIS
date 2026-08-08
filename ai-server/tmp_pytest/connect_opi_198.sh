#!/bin/bash
set -euo pipefail
export SSHPASS
SSHPASS=$(cat /tmp/opi_pw.txt)

for h in 192.168.50.198 192.168.50.120 192.168.50.108; do
  echo "== try $h =="
  if sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=6 root@"$h" 'echo AUTH_OK; hostname; ip -br a; nmcli -t -f DEVICE,TYPE,STATE,CONNECTION d 2>/dev/null || true; systemctl is-active aegis-room-server 2>/dev/null || true' 2>&1; then
    echo "$h" > /tmp/opi_host.txt
    echo "FOUND $h"
    exit 0
  fi
done
echo NOT_FOUND
# also probe tcp
python3 - <<'PY'
import socket
for ip in ['192.168.50.198','192.168.50.120','192.168.50.108']:
  for port in (22,50055):
    s=socket.socket(); s.settimeout(1)
    try:
      s.connect((ip,port)); print(f'open {ip}:{port}')
    except Exception as e:
      print(f'closed {ip}:{port} {e}')
    finally:
      s.close()
PY
