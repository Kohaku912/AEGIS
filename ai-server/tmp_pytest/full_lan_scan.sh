#!/bin/bash
set -euo pipefail
echo "== interfaces =="
ip -br a
echo "== full ping+arp =="
python3 - <<'PY'
import subprocess, concurrent.futures, socket
prefix='192.168.50.'

def ping(ip):
    r=subprocess.run(['ping','-c','1','-W','1',ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ip, r.returncode==0

alive=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=64) as ex:
    for ip, ok in ex.map(ping, [f'{prefix}{i}' for i in range(1,255)]):
        if ok: alive.append(ip)
print('alive', alive)

def tcp(ip,port):
    s=socket.socket(); s.settimeout(0.4)
    try:
        s.connect((ip,port)); return True
    except Exception:
        return False
    finally:
        s.close()
ssh=[]; room=[]
for ip in [f'{prefix}{i}' for i in range(1,255)]:
    if tcp(ip,22): ssh.append(ip)
    if tcp(ip,50055): room.append(ip)
print('ssh', ssh)
print('room', room)
PY
echo "== neigh REACHABLE/DELAY/STALE =="
ip neigh | awk '/REACHABLE|DELAY|STALE|PROBE/{print}' | sort
