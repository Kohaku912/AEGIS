#!/bin/bash
set -euo pipefail
PW=$(cat /tmp/opi_pw.txt)
export SSHPASS="$PW"
SSH=(sshpass -e ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ConnectTimeout=15 root@192.168.50.108)

echo "==> remote apt/dpkg state"
"${SSH[@]}" 'ps aux | grep -E "apt|dpkg|locale" | grep -v grep || true; pgrep -a apt || true; dpkg --configure -a || true; apt-get -f install -y || true; command -v nmcli; command -v ufw; ip -br a; hostname'
