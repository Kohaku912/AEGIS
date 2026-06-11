# AEGIS Daily Use

> **Status**: Beta
> **Last Updated**: 2026-06-12

## 毎日の流れ

### 1. 起動

```bash
cd AEGIS
docker compose up -d
```

### 2. 確認

```
http://127.0.0.1:8090          # Dashboard
http://127.0.0.1:8080/approvals # Approval UI
```

### 3. 使いたい操作

| 操作 | 方法 |
|------|------|
| Web 検索 | Browser Server 経由（read-only） |
| データ確認 | Dashboard → Memory |
| 設定変更 | Dashboard → Settings |
| 承認操作 | Approval UI で確認・承認 |

### 4. 終了

```bash
docker compose down
```

## Safety Reminder

- 承認なしで危険操作は実行されません
- Dashboard は read-only です
- 設定変更は AuditLog に記録されます
