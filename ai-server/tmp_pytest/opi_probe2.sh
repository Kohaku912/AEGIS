#!/bin/bash
set -euo pipefail
PW=$(cat /tmp/opi_pw.txt)
SSH=(sshpass -p "$PW" ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no root@192.168.50.108)

"${SSH[@]}" 'python3 --version 2>&1; apt-cache policy python3 | head -5; ls /usr/bin/python3*; cat /etc/armbian-release 2>/dev/null | head -20; rfkill list 2>/dev/null || true; dmesg | grep -iE "wlan|brcm|wifi|80211" | tail -20'
