#!/bin/bash
set -euo pipefail
PW_FILE=/tmp/opi_pw.txt
if [[ ! -f "$PW_FILE" ]]; then
  echo "missing password file $PW_FILE"
  exit 1
fi
export SSHPASS
SSHPASS=$(cat "$PW_FILE")

python3 - <<'PY'
import socket, concurrent.futures
prefix='192.168.50.'
def probe(ip, port, timeout=0.12):
    s=socket.socket(); s.settimeout(timeout)
    try:
        s.connect((ip,port)); return True
    except Exception:
        return False
    finally:
        s.close()
open22=[]; open55=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=64) as ex:
    f22={ex.submit(probe,f'{prefix}{i}',22): f'{prefix}{i}' for i in range(1,255)}
    f55={ex.submit(probe,f'{prefix}{i}',50055): f'{prefix}{i}' for i in range(1,255)}
    for fut,ip in f22.items():
        if fut.result(): open22.append(ip)
    for fut,ip in f55.items():
        if fut.result(): open55.append(ip)
print('ssh', ','.join(sorted(open22, key=lambda x:int(x.split('.')[-1]))))
print('room', ','.join(sorted(open55, key=lambda x:int(x.split('.')[-1]))))
open('/tmp/opi_scan_ssh.txt','w').write('\n'.join(open22)+'\n')
open('/tmp/opi_scan_room.txt','w').write('\n'.join(open55)+'\n')
PY

echo "== probe candidates =="
while read -r h; do
  [[ -z "$h" || "$h" == "192.168.50.41" ]] && continue
  echo "-- $h --"
  sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=4 root@"$h" \
    'hostname; cat /etc/hostname 2>/dev/null; ip -br a; nmcli -t -f DEVICE,TYPE,STATE,CONNECTION dev status 2>/dev/null || true; systemctl is-active aegis-room-server 2>/dev/null || true' 2>/dev/null \
    && echo "$h" > /tmp/opi_host.txt && break || echo fail
done < /tmp/opi_scan_ssh.txt

if [[ -f /tmp/opi_host.txt ]]; then
  echo "FOUND $(cat /tmp/opi_host.txt)"
else
  echo "NOT_FOUND"
fi
