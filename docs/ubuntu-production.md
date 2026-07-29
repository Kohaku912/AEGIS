# AEGIS Ubuntu Production Runbook

## Policy

AEGIS production on Ubuntu is private-network only. Do not expose Dashboard,
AI gRPC, Browser, or Dev ports directly to the WAN. For Android outside the
LAN, use **Cloudflare Tunnel** (`grpc.kawahara.pp.ua`) with Access Service
Tokens — see `infra/cloudflared/README.md`. WireGuard remains an acceptable
self-managed VPN alternative; do not publish raw host ports.

Secrets must live in `.env` or mounted volumes. Do not bake API keys or pairing
tokens into Docker images.

## Install

```bash
sudo bash scripts/ubuntu/install.sh
cp .env.example .env
$EDITOR .env
```

`install.sh` creates `/opt/aegis` as a symlink to the checked-out repository
unless `AEGIS_INSTALL_DIR` is set. The generated `aegis.service` uses that exact
working directory, so systemd and the shell scripts resolve the same files.

Minimum production values:

```dotenv
AEGIS_RUNTIME_MODE=production
AEGIS_PRODUCTION_BIND_HOST=127.0.0.1
AEGIS_AUTH_MODE=passkey
AEGIS_WEBAUTHN_RP_ID=kawahara.pp.ua
AEGIS_WEBAUTHN_ORIGINS=https://kawahara.pp.ua
AEGIS_SESSION_SECRET=change-me-long-random-session-secret
AEGIS_AUTH_BOOTSTRAP_TOKEN=change-me-one-time-bootstrap-token
AEGIS_ANDROID_PAIRING_TOKEN=change-me
LLM_API_KEY=...
```

`AEGIS_DASHBOARD_ACCESS_TOKEN` is no longer accepted for normal production
login. During migration it may be used only as a bootstrap/recovery token when
no passkey user exists. Remove `AEGIS_AUTH_BOOTSTRAP_TOKEN` after the first
admin passkey is registered.

Start uses `docker-compose.yml` plus `docker-compose.production.yml`, exports
`AEGIS_BIND_HOST=127.0.0.1` by default, and starts only `ai-server` and
`browser-server`. `dev-server` is behind the `dev` profile. `room-server` is
behind the `room` profile and refuses the mock provider in production.

For Android outside LAN, expose Core gRPC via Cloudflare Tunnel hostname
`grpc.kawahara.pp.ua` (origin `127.0.0.1:50051`, Access Service Token). On home
Wi‑Fi the companion app may use LAN `192.168.50.41:50051` and fall back to the
tunnel on cellular. Details: `infra/cloudflared/README.md`.

## Start / Stop

```bash
sudo systemctl enable aegis
sudo systemctl start aegis
sudo systemctl status aegis
```

Manual start:

```bash
bash scripts/ubuntu/start.sh
```

Health check:

```bash
bash scripts/ubuntu/healthcheck.sh
```

After systemd start, `healthcheck.sh` verifies `aegis.service`, Docker Compose
state, and Dashboard health. Release readiness is intentionally separate so an
incomplete real-device gate cannot prevent the Core from recovering after a
reboot:

```bash
AEGIS_RUN_READINESS_CHECK=1 bash scripts/ubuntu/healthcheck.sh
```

### Network recovery

The installer also enables **aegis-network-watchdog.timer** and
**aegis-pcie-performance.service**. The watchdog checks the local gateway every
minute, retries the saved ASUS_F8_5G profile, falls back to ASUS_F8, and restarts
Cloudflare Tunnel after connectivity and Core health return. Both Wi-Fi
profiles use permanent MAC addresses, disabled power saving, and unlimited
autoconnect retries.

Profile names and the gateway can be changed with AEGIS_PRIMARY_WIFI,
AEGIS_FALLBACK_WIFI, and AEGIS_NETWORK_GATEWAY in a systemd service override.
Use systemctl status on the two units and review NetworkManager, cloudflared,
and aegis-network-watchdog journals when diagnosing a connection loss.
The Cloudflare drop-in allows 300 seconds for Core health after boot, matching
the readiness helper instead of terminating it after 15 seconds.

## Dedicated Display

Install the read-only Display kiosk units for the graphical-session user:

```bash
sudo AEGIS_KIOSK_USER=tatuki bash scripts/ubuntu/install.sh
systemctl --user daemon-reload
systemctl --user enable --now aegis-kiosk.service aegis-display-power.service
```

Provision one read-only token for both the Core container and kiosk. Keep the
kiosk-only environment file separate so the browser process never inherits the
rest of the production secrets:

```bash
cd /opt/aegis
token="$(openssl rand -hex 32)"
sed -i '/^AEGIS_DISPLAY_TOKEN=/d' .env
printf 'AEGIS_DISPLAY_TOKEN=%s\n' "$token" >> .env
printf 'AEGIS_DISPLAY_TOKEN=%s\n' "$token" > .env.display
chmod 600 .env .env.display
unset token
```

The kiosk opens only `http://127.0.0.1:8090/display/presentations`. The kiosk
disables GNOME automatic suspend because the AI Core must remain running.
`aegis-display-power.service` independently switches the panel off after ten
minutes without an operation-state change and wakes it for task, approval,
presentation, server-state, or attention changes. Set
`AEGIS_DISPLAY_IDLE_SECONDS` in the user unit override to tune the interval.

## Volumes

`docker-compose.yml` uses named volumes for:

- `aegis-data`: audit, memory, capability overrides, Android state
- `aegis-reports`: evaluation/readiness reports
- `browser-profiles`, `browser-sessions`, `browser-traces`

Before production migration, run:

```powershell
.\scripts\e2e\run-all-real.ps1 -Rebuild
.\scripts\e2e\run-readiness-report.ps1
```

Production is not accepted unless `data/reports/e2e/latest/summary.json`
contains `overall_status: pass`.

## Backup

```bash
mkdir -p backups
docker run --rm -v aegis_aegis-data:/data -v "$PWD/backups:/backup" alpine \
  tar czf /backup/aegis-data-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
docker run --rm -v aegis_aegis-reports:/reports -v "$PWD/backups:/backup" alpine \
  tar czf /backup/aegis-reports-$(date +%Y%m%d-%H%M%S).tar.gz -C /reports .
```

## Restore

Stop AEGIS first:

```bash
sudo systemctl stop aegis
docker run --rm -v aegis_aegis-data:/data -v "$PWD/backups:/backup" alpine \
  sh -c 'rm -rf /data/* && tar xzf /backup/aegis-data.tar.gz -C /data'
sudo systemctl start aegis
```

## Readiness Gate

The production gate fails when any of these are true:

- production blocker mock/stub count is non-zero
- Manager Docker E2E fails
- Docker restart/rebuild persistence fails
- PC real observe/action fails
- Android Tailscale/LAN-outside test fails
- Browser/Dev real service checks fail
- Dashboard auth/secrets/backup documentation is missing
