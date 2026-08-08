#!/bin/bash
set -euo pipefail
python3 - <<'PY'
import socket, concurrent.futures
def probe(ip, port=22):
    s=socket.socket(); s.settimeout(0.25)
    try:
        s.connect((ip,port)); return True
    except Exception:
        return False
    finally:
        s.close()
ssh=[]; room=[]
with concurrent.futures.ThreadPoolExecutor(64) as ex:
    f22={ex.submit(probe,f'192.168.50.{i}',22):i for i in range(1,255)}
    f55={ex.submit(probe,f'192.168.50.{i}',50055):i for i in range(1,255)}
    for fut,i in f22.items():
        if fut.result(): ssh.append(f'192.168.50.{i}')
    for fut,i in f55.items():
        if fut.result(): room.append(f'192.168.50.{i}')
print('ssh', ssh)
print('room', room)
PY
echo "== ping =="
for h in 192.168.50.108 192.168.50.120 192.168.50.204; do
  ping -c 1 -W 1 "$h" >/dev/null 2>&1 && echo OK "$h" || echo FAIL "$h"
done
echo "== neigh =="
ip neigh | awk '/REACHABLE|DELAY|STALE/'
echo "== ubuntu eth =="
ip -br link show enp1s0
