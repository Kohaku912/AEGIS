#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

sudo usermod -aG docker "${SUDO_USER:-$USER}" || true

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Edit it before production start."
fi

sudo mkdir -p /etc/aegis
sudo cp infra/systemd/aegis.service /etc/systemd/system/aegis.service
sudo systemctl daemon-reload
echo "Install complete. Edit .env, then run: sudo systemctl enable --now aegis"
