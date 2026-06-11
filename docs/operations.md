# AEGIS Operations Guide

> **Status**: Beta
> **Last Updated**: 2026-06-12

## 日常運用

### 起動

```bash
docker compose up -d
```

### 確認

```bash
docker compose ps
# Dashboard: http://127.0.0.1:8090
# Approvals: http://127.0.0.1:8080/approvals
```

### 停止

```bash
docker compose down
```

## 監視

- Dashboard: http://127.0.0.1:8090
- Health: http://127.0.0.1:8090/health
- API: http://127.0.0.1:8090/api/dashboard/overview

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

```bash
# Dashboard → Settings で変更
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
