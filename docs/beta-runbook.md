# AEGIS Beta Runbook

> **Status**: Beta
> **Last Updated**: 2026-06-12

## 1. 初回セットアップ

### 1.1 環境準備

```bash
# リポジトリ取得
git clone https://github.com/Kohaku912/AEGIS.git
cd AEGIS

# 環境変数コピー（実際の秘密は入れない）
cp .env.example .env
```

### 1.2 Python 環境

```bash
cd ai-server
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -e ".[dev]"
```

### 1.3 Proto 生成

```bash
cd ai-server
python -m grpc_tools.protoc -I../protos --python_out=src/generated --grpc_python_out=src/generated ../protos/aegis/*.proto
```

### 1.4 テスト実行（CI安全）

```bash
cd ai-server
pytest --ignore=tests/test_approval_ui.py --ignore=tests/test_android_local.py -q
```

### 1.5 Docker Compose 起動

```bash
cd AEGIS
docker compose up -d
docker compose ps
```

### 1.6 Android セットアップ（オプション）

```bash
cd android-server
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
# Settings → Notification access → AEGIS Android → ON
```

---

## 2. 起動手順

### 2.1 AEGIS Core（AI Server）

```bash
cd ai-server
python -m aegis_ai.main
```

### 2.2 Dashboard 起動

```bash
cd ai-server
python -c "from aegis_ai.web.dashboard_routes import DashboardApp; DashboardApp().run()"
# http://127.0.0.1:8090
```

### 2.3 Approval UI 起動

```bash
cd ai-server
python -c "from aegis_ai.web.app import ApprovalWebApp; from approval import ApprovalStore; ApprovalWebApp(ApprovalStore()).run()"
# http://127.0.0.1:8080
```

### 2.4 Docker Compose で全サービス起動

```bash
docker compose up -d
docker compose ps
```

---

## 3. 日常確認

### 3.1 Dashboard 確認

```
http://127.0.0.1:8090
```

確認項目:
- [ ] Servers: 全サーバー ONLINE
- [ ] Events: 最近のイベント確認
- [ ] Tasks: pending approval がないか
- [ ] Errors: エラーがないか
- [ ] Memory: メモリ使用量

### 3.2 Pending Approval 確認

```
http://127.0.0.1:8080/approvals
```

### 3.3 テスト実行

```bash
cd ai-server
pytest -q --tb=short
```

---

## 4. 安全な停止

```bash
# Docker Compose 場合
docker compose down

# 直接実行の場合
# Ctrl+C で AEGIS Core を停止
```

---

## 5. よくある問題

| 問題 | 解決策 |
|------|--------|
| Server disconnected | `docker compose ps` で確認 → `docker compose restart` |
| Approval stuck | Dashboard → Tasks → 確認、または `http://127.0.0.1:8080/approvals` |
| テスト失敗 | `pytest --tb=short` で詳細確認 |
| Port 使用中 | `.env` でポート変更、または `docker compose down` 後再起動 |

---

## 6. 緊急停止

```bash
# 全サービス停止
docker compose down

# 設定をリセット
cd ai-server
python -c "from aegis_ai.settings.store import SettingsStore; SettingsStore().reset_to_defaults()"
```

---

## 7. Beta おすすめ設定

| 設定 | 推奨値 | 理由 |
|------|--------|------|
| `autonomous_loop_enabled` | false | 手動確認后再有効化 |
| `support_agent_enabled` | true | 提案のみ、自動実行なし |
| `self_dev_proposal_enabled` | true | 提案のみ、PR は承認必要 |
| `camera_snapshot_enabled` | false | プライバシー保護 |
| `sensitive_data_storage_enabled` | false | セキュリティ |

---

## 8. ユーザー承認が必要な操作

| 操作 | Safety Level | 承認方法 |
|------|-------------|---------|
| SNS/DM/Email 送信 | 禁止 | PolicyEngine で拒否 |
| ファイル削除 | 禁止 | PolicyEngine で拒否 |
| PC マウス/キーボード | Level 2 | Approval UI |
| Android タップ/入力 | Level 2 | Approval UI |
| Room 物理操作 | Level 2 | Approval UI |
| Dev patch/PR | Level 2 | Approval UI |
| 外部 LLM + 機密データ | 制限 | Settings で制御 |
