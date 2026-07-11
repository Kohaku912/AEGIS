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
sudo systemctl daemon-reload
echo "Install complete. Workdir: $INSTALL_DIR"
echo "Edit .env, then run: sudo systemctl enable --now aegis && scripts/ubuntu/healthcheck.sh"
