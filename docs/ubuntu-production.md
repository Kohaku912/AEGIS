# AEGIS Ubuntu Production Runbook

## Policy

AEGIS production on Ubuntu is private-network only. Do not expose Dashboard,
AI gRPC, Browser, or Dev ports directly to the WAN. Use Tailscale first;
WireGuard is an acceptable self-managed alternative.

Secrets must live in `.env` or mounted volumes. Do not bake API keys or pairing
tokens into Docker images.

## Install

```bash
sudo bash scripts/ubuntu/install.sh
cp .env.example .env
$EDITOR .env
```

Minimum production values:

```dotenv
AEGIS_RUNTIME_MODE=production
AEGIS_DASHBOARD_ACCESS_TOKEN=change-me
AEGIS_ANDROID_PAIRING_TOKEN=change-me
LLM_API_KEY=...
```

For Android outside LAN, install Tailscale on Ubuntu and Android, then use the
Ubuntu Tailscale IP or MagicDNS name as the Android host.

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
