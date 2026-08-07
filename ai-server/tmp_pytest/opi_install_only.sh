#!/bin/bash
set -euo pipefail
PW=$(cat /tmp/opi_pw.txt)
export SSHPASS="$PW"
SSH=(sshpass -e ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ServerAliveInterval=30 root@192.168.50.108)
SCP=(sshpass -e scp -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no)

echo "==> ensure install script present"
"${SCP[@]}" /tmp/opi_install_room.sh /tmp/room-server.tgz root@192.168.50.108:/tmp/
"${SSH[@]}" "sed -i 's/\r$//' /tmp/opi_install_room.sh; mkdir -p /opt/aegis/room-server; rm -rf /opt/aegis/room-server/*; tar -xzf /tmp/room-server.tgz -C /opt/aegis/room-server; ls -la /opt/aegis/room-server; ls /opt/aegis/room-server/src/aegis_room | head"

echo "==> install room-server (uv + systemd)"
"${SSH[@]}" 'bash /tmp/opi_install_room.sh'

echo "==> verify from jump host"
"${SSH[@]}" 'systemctl is-active aegis-room-server; ss -lntp | grep 50055 || netstat -lntp 2>/dev/null | grep 50055 || true; journalctl -u aegis-room-server -n 40 --no-pager'
python3 - <<'PY'
import socket
for host in ("192.168.50.108", "192.168.50.120"):
    try:
        s = socket.create_connection((host, 50055), timeout=5)
        s.close()
        print(f"tcp_ok {host}:50055")
    except Exception as e:
        print(f"tcp_fail {host}:50055 {e}")
PY
