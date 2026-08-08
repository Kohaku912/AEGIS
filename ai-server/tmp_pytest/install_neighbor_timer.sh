#!/bin/bash
set -euo pipefail
install -m 0755 /tmp/aegis-refresh-neighbors.sh /usr/local/sbin/aegis-refresh-neighbors.sh
cat >/etc/systemd/system/aegis-refresh-neighbors.service <<'EOF'
[Unit]
Description=Refresh AEGIS LAN neighbor table for MAC discovery
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=oneshot
Environment=AEGIS_LAN_SCAN_PREFIX=192.168.50
ExecStart=/usr/local/sbin/aegis-refresh-neighbors.sh
EOF
cat >/etc/systemd/system/aegis-refresh-neighbors.timer <<'EOF'
[Unit]
Description=Periodic AEGIS neighbor refresh

[Timer]
OnBootSec=30s
OnUnitActiveSec=60s
AccuracySec=5s
Unit=aegis-refresh-neighbors.service

[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now aegis-refresh-neighbors.timer
/usr/local/sbin/aegis-refresh-neighbors.sh
