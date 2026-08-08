#!/bin/bash
set -euo pipefail
# Try to read ASUS router client list (common endpoints)
GW=192.168.50.1
echo "== gateway =="
curl -s -m 3 "http://$GW/" | head -c 200; echo
# nvram-like client list endpoints used by asuswrt
for path in \
  '/appGet.cgi?hook=get_clientlist()' \
  '/update_clients.asp' \
  '/Main_Login.asp' \
  '/index.asp'
 do
  code=$(curl -s -m 3 -o /tmp/asus_out.txt -w '%{http_code}' "http://$GW$path" || true)
  echo "GET $path -> $code bytes=$(wc -c </tmp/asus_out.txt 2>/dev/null || echo 0)"
  head -c 120 /tmp/asus_out.txt 2>/dev/null; echo
done

# continuous discovery for 90s
export SSHPASS
SSHPASS=$(cat /tmp/opi_pw.txt)
echo "== watch 90s =="
for n in $(seq 1 18); do
  python3 - <<'PY'
import socket
found=[]
for i in range(1,255):
  ip=f'192.168.50.{i}'
  if ip.endswith('.41'):
    continue
  s=socket.socket(); s.settimeout(0.05)
  try:
    s.connect((ip,22)); found.append(ip)
  except Exception:
    pass
  finally:
    s.close()
print('ssh', found)
open('/tmp/opi_watch_ssh.txt','w').write('\n'.join(found))
PY
  while read -r h; do
    [[ -z "$h" ]] && continue
    if sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 root@"$h" 'hostname; ip -br a' 2>/dev/null; then
      echo "$h" > /tmp/opi_host.txt
      echo "FOUND $h"
      exit 0
    fi
  done < /tmp/opi_watch_ssh.txt
  echo "t=${n} none"
  sleep 5
done
echo NOT_FOUND
