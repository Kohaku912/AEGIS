#!/bin/bash
set -euo pipefail
PW_FILE=/tmp/opi_pw.txt
if [[ ! -f "$PW_FILE" ]]; then
  echo "missing $PW_FILE"
  exit 1
fi
PW=$(cat "$PW_FILE")
export SSHPASS="$PW"

scan() {
  python3 - <<'PY'
import socket
found={}
for i in range(1,255):
    ip=f"192.168.50.{i}"
    for port in (22,50052,50055):
        s=socket.socket(); s.settimeout(0.04)
        try:
            s.connect((ip,port))
            found.setdefault(port,[]).append(ip)
        except Exception:
            pass
        finally:
            s.close()
print("ssh22", found.get(22,[]))
print("pc50052", found.get(50052,[]))
print("room50055", found.get(50055,[]))
PY
}

echo "== LAN scan =="
scan

echo "== try known room SSH =="
for h in 192.168.50.108 192.168.50.120 orangepi-room; do
  echo "-- $h --"
  sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=4 root@"$h" 'hostname; ip -br a; systemctl is-active aegis-room-server; ss -lntp | grep 50055 || true' 2>/dev/null || echo "ssh fail"
done

echo "== try PC TCP =="
for h in 192.168.50.176 192.168.50.195; do
  timeout 2 bash -c "echo >/dev/tcp/$h/50052" 2>/dev/null && echo "pc $h OK" || echo "pc $h FAIL"
done
