#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
INSTALL_DIR="${AEGIS_INSTALL_DIR:-/opt/aegis}"

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

sudo usermod -aG docker "${SUDO_USER:-$USER}" || true

if [ "$ROOT_DIR" != "$INSTALL_DIR" ]; then
  sudo mkdir -p "$(dirname "$INSTALL_DIR")"
  if [ -e "$INSTALL_DIR" ] && [ ! -L "$INSTALL_DIR" ]; then
    echo "$INSTALL_DIR already exists and is not a symlink. Set AEGIS_INSTALL_DIR or move the repo there." >&2
    exit 1
  fi
  sudo ln -sfn "$ROOT_DIR" "$INSTALL_DIR"
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Edit it before production start."
fi

sudo mkdir -p /etc/aegis
sudo sed "s#/opt/aegis#$INSTALL_DIR#g" infra/systemd/aegis.service \
  | sudo tee /etc/systemd/system/aegis.service >/dev/null
sudo sed "s#/opt/aegis#$INSTALL_DIR#g" infra/systemd/aegis-network-watchdog.service \
  | sudo tee /etc/systemd/system/aegis-network-watchdog.service >/dev/null
sudo install -m 0644 infra/systemd/aegis-network-watchdog.timer \
  /etc/systemd/system/aegis-network-watchdog.timer
sudo install -m 0644 infra/systemd/aegis-pcie-performance.service \
  /etc/systemd/system/aegis-pcie-performance.service
if systemctl list-unit-files cloudflared.service >/dev/null 2>&1; then
  sudo install -d /etc/systemd/system/cloudflared.service.d
  sudo install -m 0644 infra/systemd/cloudflared-aegis.conf \
    /etc/systemd/system/cloudflared.service.d/aegis-readiness.conf
fi
sudo systemctl daemon-reload
sudo systemctl enable aegis-network-watchdog.timer aegis-pcie-performance.service

if [ -n "${AEGIS_KIOSK_USER:-}" ]; then
  kiosk_home="$(getent passwd "$AEGIS_KIOSK_USER" | cut -d: -f6)"
  if [ -z "$kiosk_home" ]; then
    echo "Unknown AEGIS_KIOSK_USER=$AEGIS_KIOSK_USER" >&2
    exit 1
  fi
  sudo install -d -o "$AEGIS_KIOSK_USER" -g "$AEGIS_KIOSK_USER" "$kiosk_home/.config/systemd/user"
  sudo install -o "$AEGIS_KIOSK_USER" -g "$AEGIS_KIOSK_USER" -m 0644 \
    infra/systemd/aegis-kiosk.service "$kiosk_home/.config/systemd/user/aegis-kiosk.service"
  sudo install -o "$AEGIS_KIOSK_USER" -g "$AEGIS_KIOSK_USER" -m 0644 \
    infra/systemd/aegis-display-power.service "$kiosk_home/.config/systemd/user/aegis-display-power.service"
  sudo loginctl enable-linger "$AEGIS_KIOSK_USER"
  echo "Installed kiosk units for $AEGIS_KIOSK_USER. Enable them from that user's graphical session."
fi
echo "Install complete. Workdir: $INSTALL_DIR"
echo "Edit .env, then run: sudo systemctl enable --now aegis && scripts/ubuntu/healthcheck.sh"
