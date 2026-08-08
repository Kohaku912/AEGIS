#!/bin/bash
# Fix Orange Pi networking: ethernet managed + persistent WiFi (prefer 2.4GHz)
set -euo pipefail
WIFI_SSID_5G="${WIFI_SSID_5G:-ASUS_F8_5G}"
WIFI_SSID_24="${WIFI_SSID_24:-ASUS_F8_2G}"
WIFI_PASSWORD="${WIFI_PASSWORD:-anyway_5346}"

echo "== hostname/interfaces =="
hostname
ip -br a || true
rfkill unblock wifi || true
rfkill unblock wlan || true

echo "== make ethernet managed by NetworkManager =="
# Armbian often leaves end0 unmanaged via /usr/lib/NetworkManager/conf.d or 10-globally-managed-devices
mkdir -p /etc/NetworkManager/conf.d
cat >/etc/NetworkManager/conf.d/10-aegis-manage-all.conf <<'EOF'
[keyfile]
unmanaged-devices=
EOF
# Remove common Armbian unmanaged rules if present
if [[ -f /usr/lib/NetworkManager/conf.d/10-globally-managed-devices.conf ]]; then
  # Override with empty unmanaged list in /etc (takes precedence when merged carefully)
  cat >/etc/NetworkManager/conf.d/10-globally-managed-devices.conf <<'EOF'
[keyfile]
unmanaged-devices=
EOF
fi
systemctl restart NetworkManager || true
sleep 2
nmcli device set end0 managed yes 2>/dev/null || nmcli device set eth0 managed yes 2>/dev/null || true
nmcli device status || true

echo "== configure WiFi profiles (2.4G preferred for stability) =="
# Delete stale profiles then recreate with autoconnect + no powersave
for ssid in "$WIFI_SSID_24" "$WIFI_SSID_5G"; do
  nmcli -t -f NAME connection show 2>/dev/null | grep -Fx "$ssid" >/dev/null 2>&1 && nmcli connection delete "$ssid" || true
done

# Prefer 2.4GHz: higher priority
nmcli connection add type wifi ifname wlan0 con-name "$WIFI_SSID_24" ssid "$WIFI_SSID_24" \
  wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$WIFI_PASSWORD" \
  connection.autoconnect yes connection.autoconnect-priority 100 \
  ipv4.method auto ipv6.method auto || true

nmcli connection add type wifi ifname wlan0 con-name "$WIFI_SSID_5G" ssid "$WIFI_SSID_5G" \
  wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$WIFI_PASSWORD" \
  connection.autoconnect yes connection.autoconnect-priority 50 \
  ipv4.method auto ipv6.method auto || true

# Disable WiFi powersave (common cause of silent disconnect on Orange Pi)
IW=$(command -v iw || true)
if [[ -n "$IW" ]]; then
  iw dev wlan0 set power_save off || true
fi
mkdir -p /etc/NetworkManager/conf.d
cat >/etc/NetworkManager/conf.d/20-aegis-wifi-powersave.conf <<'EOF'
[connection]
wifi.powersave=2
EOF
# 2 = disable powersave in NM

# Also systemd oneshot to force power_save off on boot
cat >/usr/local/sbin/aegis-wifi-fix.sh <<'EOF'
#!/bin/bash
rfkill unblock wifi || true
ip link set wlan0 up || true
command -v iw >/dev/null && iw dev wlan0 set power_save off || true
nmcli radio wifi on || true
# Prefer active 2.4G if neither connected
STATE=$(nmcli -t -f DEVICE,STATE device status | awk -F: '$1=="wlan0"{print $2}')
if [[ "$STATE" != "connected" ]]; then
  nmcli connection up ASUS_F8_2G || nmcli connection up ASUS_F8_5G || true
fi
EOF
chmod +x /usr/local/sbin/aegis-wifi-fix.sh
cat >/etc/systemd/system/aegis-wifi-fix.service <<'EOF'
[Unit]
Description=AEGIS WiFi resilience for Orange Pi
After=NetworkManager.service
Wants=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/aegis-wifi-fix.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now aegis-wifi-fix.service || true

echo "== connect WiFi now =="
nmcli device wifi rescan || true
sleep 2
nmcli device wifi list || true
# Try 2.4 first
if ! nmcli connection up "$WIFI_SSID_24"; then
  nmcli device wifi connect "$WIFI_SSID_24" password "$WIFI_PASSWORD" ifname wlan0 || true
fi
if ! nmcli -t -f DEVICE,STATE device | grep -q '^wlan0:connected'; then
  nmcli connection up "$WIFI_SSID_5G" || nmcli device wifi connect "$WIFI_SSID_5G" password "$WIFI_PASSWORD" ifname wlan0 || true
fi

# Ensure ethernet also gets DHCP via NM if cable present
ETH=$(nmcli -t -f DEVICE,TYPE device status | awk -F: '$2=="ethernet"{print $1; exit}')
if [[ -n "${ETH:-}" ]]; then
  nmcli device set "$ETH" managed yes || true
  nmcli device connect "$ETH" || true
fi

sleep 2
echo "== final status =="
nmcli device status || true
nmcli -f NAME,UUID,TYPE,AUTOCONNECT,AUTOCONNECT-PRIORITY connection show || true
ip -br a || true
iw dev wlan0 get power_save 2>/dev/null || true
ping -c 2 -W 2 192.168.50.1 || true
echo DONE_WIFI_FIX
