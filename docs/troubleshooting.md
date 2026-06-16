# AEGIS Troubleshooting

> **Status**: Beta
> **Last Updated**: 2026-06-12

## サーバー接続問題

### Server disconnected

```
症状: Dashboard でサーバーが OFFLINE
確認: docker compose ps
解決: docker compose restart <service-name>
```

### Port 使用中

```
症状: "address already in use"
確認: netstat -tlnp | grep 50051
解決: .env でポート変更、または該当プロセス停止
```

## Approval 問題

### Approval stuck

```
症状: 承認が pending のまま
確認: http://0.0.0.0:8080/approvals
解決: 承認するか reject するか
```

## テスト問題

### テスト失敗

```bash
cd ai-server
pytest --tb=short -q
# 失敗したテストの詳細を確認
```

## 設定問題

### 設定リセット

```bash
cd ai-server
python -c "from aegis_ai.settings.store import SettingsStore; SettingsStore().reset_to_defaults()"
```
