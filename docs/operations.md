# AEGIS Operations Guide

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
