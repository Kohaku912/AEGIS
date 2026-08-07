#!/bin/bash
set -euo pipefail
PW=$(cat /tmp/opi_pw.txt)
export SSHPASS="$PW"
SSH=(sshpass -e ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ServerAliveInterval=30 root@192.168.50.108)

echo "==> wait for apt to finish"
for i in $(seq 1 60); do
  if "${SSH[@]}" 'pgrep -x apt-get >/dev/null || pgrep -x apt >/dev/null || pgrep -x dpkg >/dev/null'; then
    echo "still installing ($i)..."
    sleep 10
  else
    echo "apt idle"
    break
  fi
done

echo "==> finish configure"
"${SSH[@]}" 'export DEBIAN_FRONTEND=noninteractive; dpkg --configure -a; apt-get -f install -y -qq; apt-get install -y -qq ca-certificates curl git sudo ufw chrony network-manager wireless-tools wpasupplicant build-essential pkg-config python3 python3-venv python3-pip python3-dev'

echo "==> hostname/timezone/wifi"
"${SSH[@]}" "WIFI_PASSWORD='anyway_5346' bash /tmp/opi_base_setup.sh" || "${SSH[@]}" '
export DEBIAN_FRONTEND=noninteractive
hostnamectl set-hostname orangepi-room || true
timedatectl set-timezone Asia/Tokyo || true
systemctl enable --now NetworkManager.service || true
rfkill unblock wifi || true
ip link set wlan0 up || true
nmcli radio wifi on || true
nmcli device wifi rescan || true
sleep 2
nmcli device wifi list || true
nmcli connection delete ASUS_F8_5G 2>/dev/null || true
nmcli connection delete ASUS_F8 2>/dev/null || true
if ! nmcli device wifi connect ASUS_F8_5G password anyway_5346 ifname wlan0; then
  nmcli device wifi connect ASUS_F8 password anyway_5346 ifname wlan0
fi
sleep 3
ip -br a
nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status
'

echo "==> DONE_WIFI_PHASE"
