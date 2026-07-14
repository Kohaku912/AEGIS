# AEGIS Operations Guide

## Retention And Rotation

- Docker service logs use `json-file` rotation at 10 MiB with five files per
  service, configured in `docker-compose.yml`.
- Retain audit/event JSONL for 90 days, and longer while an incident, approval,
  or task investigation remains open.
- Retain the latest E2E report plus 30 dated readiness runs. Keep failed release
  evidence for 180 days.
- Retain successful browser traces/screenshots for 14 days and failed traces
  for 30 days, subject to earlier privacy deletion.
- Retain auth events and capability override audit records for one year.

Docker log limits are automatic. File artifact retention is an operator
maintenance task until the scheduled retention worker is enabled.

> **Status**: Beta
> **Last Updated**: 2026-06-17

## 日常運用

### 起動

```bash
docker compose up -d
```

### 確認

```bash
docker compose ps
# Dashboard: http://0.0.0.0:8090
# Approvals: http://0.0.0.0:8080/approvals
# Manager API: http://0.0.0.0:8090/api/tasks, /api/events, /api/audit, /api/status
# Memory API: http://0.0.0.0:8090/api/memory/advanced
# Sleep API: http://0.0.0.0:8090/api/sleep/status
```

### 停止

```bash
docker compose down
```

## 監視

- Dashboard: http://0.0.0.0:8090
- Health: http://0.0.0.0:8090/health
- Server Status: http://0.0.0.0:8090/api/status (StatusManager.get_snapshot())
- Tasks: http://0.0.0.0:8090/api/tasks
- Events: http://0.0.0.0:8090/api/events
- Audit: http://0.0.0.0:8090/api/audit
- Notifications: http://0.0.0.0:8090/api/notifications
- Autonomous Loop Status: http://0.0.0.0:8090/api/autonomous/status
- Desire States: http://0.0.0.0:8090/api/desires
- Manual Trigger: `POST http://0.0.0.0:8090/api/autonomous/trigger`
- Start/Stop Loop: `POST /api/autonomous/start`, `POST /api/autonomous/stop`

## バックアップ

```bash
cd ai-server
python -c "
from aegis_ai.backup import DataExporter
from aegis_ai.settings.store import SettingsStore
from aegis_ai.audit import AuditLog
from aegis_ai.memory.episodic import EpisodicMemory

exporter = DataExporter(
    settings_store=SettingsStore(),
    audit_log=AuditLog(),
    episodic_memory=EpisodicMemory(),
)
exporter.export_all('data/backups/', redacted=True)
"
```

## 設定変更

設定は `config/settings.json` に永続化されます（`data/settings.json` ではありません）。

```bash
# Dashboard → Settings UI で変更
# または直接:
cd ai-server
python -c "
from aegis_ai.settings.store import SettingsStore
store = SettingsStore()
settings = store.get()
settings.autonomous.support_agent_enabled = True
store.update(settings, changed_by='user', reason='Enable support')
"
```

## Current Operations Notes

- Start core Docker services with `docker compose up -d ai-server browser-server room-server dev-server`.
- Keep PC Server host-native for Windows automation on `50052`.
- Android reconnects to AI gRPC `50051`; verify pairing token and device permissions from the Android State tab.
- Audit review starts at `/dashboard/audit`, which groups events by chat turn, autonomous cycle, task, or approval.
- Autonomous LLM calls are gated by `AEGIS_MIN_LLM_INTERVAL_MS=1800000` by default. Desire observation continues every minute, but LLM calls still require pressure above threshold and provider/budget availability.
- AGORA normal reads are unread-only. If no unread posts exist, no memory sync occurs and old posts are not reread.
