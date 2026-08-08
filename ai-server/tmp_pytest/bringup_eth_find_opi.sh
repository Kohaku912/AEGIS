#!/bin/bash
set -euo pipefail
export SSHPASS
SSHPASS=$(cat /tmp/opi_pw.txt)

echo "== bring up ethernet =="
sudo ip link set enp1s0 up || true
sleep 2
ip -br a
# request DHCP on ethernet if possible
if command -v nmcli >/dev/null; then
  sudo nmcli device set enp1s0 managed yes || true
  sudo nmcli device connect enp1s0 || sudo dhclient -v enp1s0 || true
fi
sleep 3
ip -br a
ip neigh | grep -v FAILED | sort || true

echo "== probe candidates =="
for h in 192.168.50.204 192.168.50.108 192.168.50.120 192.168.50.176 192.168.50.107; do
  echo "-- $h --"
  ping -c 1 -W 1 "$h" >/dev/null 2>&1 && echo ping_ok || echo ping_fail
  timeout 2 bash -c "echo >/dev/tcp/$h/22" 2>/dev/null && echo tcp22_ok || echo tcp22_fail
  sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@"$h" \
    'echo AUTH_OK; hostname; ip -br a; nmcli -t -f DEVICE,TYPE,STATE,CONNECTION d 2>/dev/null || true' 2>&1 | head -30 || true
done

# Also check link-local / direct ethernet peers
echo "== ethernet direct =="
ip -br link show enp1s0
sudo journalctl -u NetworkManager -n 30 --no-pager 2>/dev/null | tail -20 || true
