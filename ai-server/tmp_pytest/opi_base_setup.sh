#!/bin/bash
# Orange Pi Zero3 base setup + Wi-Fi (run ON the device as root)
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
WIFI_SSID_PRIMARY="${WIFI_SSID_PRIMARY:-ASUS_F8_5G}"
WIFI_SSID_FALLBACK="${WIFI_SSID_FALLBACK:-ASUS_F8}"
WIFI_PASSWORD="${WIFI_PASSWORD:?WIFI_PASSWORD required}"
HOSTNAME_NEW="${HOSTNAME_NEW:-orangepi-room}"

echo "==> apt update / base packages"
apt-get update -qq
apt-get install -y -qq \
  ca-certificates curl git sudo ufw chrony \
  network-manager wireless-tools wpasupplicant \
  build-essential pkg-config \
  python3 python3-venv python3-pip python3-dev

echo "==> hostname / timezone"
hostnamectl set-hostname "$HOSTNAME_NEW" || true
timedatectl set-timezone Asia/Tokyo || true
# keep DHCP hostname friendly
if [ -f /etc/hosts ]; then
  sed -i "s/^10.20.0.2.*/10.20.0.2\t$HOSTNAME_NEW/" /etc/hosts || true
  if ! grep -q "$HOSTNAME_NEW" /etc/hosts; then
    echo "10.20.0.2	$HOSTNAME_NEW" >> /etc/hosts
  fi
fi

echo "==> enable NetworkManager"
systemctl enable NetworkManager.service || true
systemctl start NetworkManager.service || true
sleep 2

echo "==> Wi-Fi connect"
rfkill unblock wifi || true
rfkill unblock wlan || true
ip link set wlan0 up || true

# Prefer primary SSID; fall back if needed.
connect_ssid() {
  local ssid="$1"
  echo "Trying SSID=$ssid"
  nmcli radio wifi on || true
  # delete stale profile with same name
  nmcli -t -f NAME connection show 2>/dev/null | grep -Fx "$ssid" >/dev/null 2>&1 && \
    nmcli connection delete "$ssid" || true
  nmcli device wifi rescan || true
  sleep 2
  nmcli device wifi list || true
  if nmcli device wifi connect "$ssid" password "$WIFI_PASSWORD" ifname wlan0; then
    return 0
  fi
  return 1
}

if ! connect_ssid "$WIFI_SSID_PRIMARY"; then
  connect_ssid "$WIFI_SSID_FALLBACK"
fi

sleep 3
echo "==> addresses"
ip -br a
nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status || true
echo "==> wifi check"
nmcli -t -f ACTIVE,SSID,SIGNAL device wifi list | head -20 || true

echo "==> base setup done"
