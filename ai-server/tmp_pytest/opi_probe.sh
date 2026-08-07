#!/bin/bash
set -euo pipefail
USER_NAME=$(cat /tmp/opi_user.txt)
PW=$(cat /tmp/opi_pw.txt)
SSH=(sshpass -p "$PW" ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no root@192.168.50.108)

echo "=== probe ==="
"${SSH[@]}" 'uname -a; . /etc/os-release; echo "$PRETTY_NAME"; ip -br a; echo ---; nmcli -t -f DEVICE,TYPE,STATE,CONNECTION dev status 2>/dev/null || true; echo ---; iwconfig 2>/dev/null || true; ls /sys/class/net; command -v nmtui; command -v nmcli; command -v iwctl; free -h; df -h /'
