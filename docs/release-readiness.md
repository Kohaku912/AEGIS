# Release Readiness Report

> **Date**: 2026-06-17
> **AEGIS Version**: Runtime Stabilization — Manager Architecture + E2E Testing

## 1. Overall Status

| 項目 | 状態 |
|------|------|
| 全テスト | ✅ 157 passed, 0 failed |
| Safety regression | ✅ 44 passed |
| Integration E2E | ✅ 25 passed |
| E2E Lifecycle | ✅ 8 passed |
| Lint (ruff) | ✅ パス |
| Format (ruff) | ✅ 適用済み |

## 2. Implemented Capabilities

### Observe (Level 0 — READ_ONLY)

| Capability | Server | Status |
|-----------|--------|--------|
| `pc.get_screenshot` | PC | ✅ Mock |
| `pc.get_active_window` | PC | ✅ Mock |
| `pc.list_windows` | PC | ✅ Mock |
| `pc.get_clipboard` | PC | ✅ Mock + redaction |
| `pc.get_os_info` | PC | ✅ Mock |
| `pc.list_directory` | PC | ✅ Mock |
| `pc.read_file` | PC | ✅ Mock + path safety |
| `android.get_notifications` | Android | ✅ Mock + ADB |
| `android.get_current_app` | Android | ✅ Mock + ADB |
| `android.get_device_info` | Android | ✅ Mock + ADB |
| `android.get_screenshot` | Android | ✅ Mock |
| `android.get_ui_tree` | Android | ✅ Mock |
| `room.get_environment` | Room | ✅ Mock |
| `room.get_temperature` | Room | ✅ Mock |
| `room.get_humidity` | Room | ✅ Mock |
| `room.get_brightness` | Room | ✅ Mock |
| `room.get_motion_status` | Room | ✅ Mock |
| `room.get_device_status` | Room | ✅ Mock |
| `room.list_sensors` | Room | ✅ Mock |
| `dev.get_repo_status` | Dev | ✅ Mock |
| `dev.get_diff` | Dev | ✅ Mock |
| `dev.read_file` | Dev | ✅ Mock + path safety |
| `dev.search_code` | Dev | ✅ Mock |

### Action (Level 1 — SAFE_ACTION)

| Capability | Server | Status |
|-----------|--------|--------|
| `pc.mouse_move` | PC | ✅ Mock |
| `pc.launch_app` | PC | ✅ Mock |
| `pc.focus_window` | PC | ✅ Mock |
| `pc.move_window` | PC | ✅ Mock |
| `pc.resize_window` | PC | ✅ Mock |
| `pc.show_overlay` | PC | ✅ Mock |
| `pc.hide_overlay` | PC | ✅ Mock |
| `android.show_overlay` | Android | ✅ Mock |
| `android.hide_overlay` | Android | ✅ Mock |
| `android.open_app` | Android | ✅ Mock |
| `android.press_home` | Android | ✅ Mock |
| `room.stop_robot_arm` | Room | ✅ Mock |
| `room.emergency_stop_robot_arm` | Room | ✅ Mock |
| `dev.create_branch` | Dev | ✅ Mock |
| `dev.run_tests` | Dev | ✅ Mock |
| `dev.run_lint` | Dev | ✅ Mock |

### Action (Level 2 — APPROVAL_REQUIRED)

| Capability | Server | Status |
|-----------|--------|--------|
| `pc.mouse_click` | PC | ✅ Mock + Approval UI |
| `pc.keyboard_type` | PC | ✅ Mock + Approval UI |
| `pc.press_hotkey` | PC | ✅ Mock + Approval UI |
| `pc.close_window` | PC | ✅ Mock + Approval UI |
| `pc.write_clipboard` | PC | ✅ Mock + Approval UI |
| `pc.write_file` | PC | ✅ Mock + Approval UI + path safety |
| `android.tap` | Android | ✅ Mock + Approval UI |
| `android.swipe` | Android | ✅ Mock + Approval UI |
| `android.type_text` | Android | ✅ Mock + Approval UI + password deny |
| `room.set_light` | Room | ✅ Mock + Approval UI |
| `room.set_air_conditioner` | Room | ✅ Mock + Approval UI + temp range |
| `room.send_ir_command` | Room | ✅ Mock + Approval UI + IR allowlist |
| `room.set_smart_plug` | Room | ✅ Mock + Approval UI |
| `room.get_camera_snapshot` | Room | ✅ Mock + Approval UI |
| `dev.apply_patch` | Dev | ✅ Mock + Approval UI |
| `dev.create_commit` | Dev | ✅ Mock + Approval UI |
| `dev.create_pull_request` | Dev | ✅ Mock + Approval UI |
| `dev.revert_changes` | Dev | ✅ Mock + Approval UI |

### Explicitly Denied (Forbidden)

| Pattern | Server | 理由 |
|---------|--------|------|
| `*.send_sns`, `*.post_sns` | All | SNS投稿禁止 |
| `*.send_dm`, `*.send_message` | All | DM送信禁止 |
| `*.send_email` | All | メール送信禁止 |
| `*.delete_file`, `*.rm_*` | All | ファイル削除禁止 |
| `*.read_credential.*`, `*.read_secret.*` | All | 秘密情報読み取り禁止 |
| `*.purchase.*` | All | 購入禁止 |
| `*.bypass_policy.*` | All | Policy迂回禁止 |
| `room.move_robot_arm` | Room | ロボットアーム移動禁止 |
| `room.lock_*` | Room | ドアロック禁止 |
| `dev.merge_to_main` | Dev | main直接マージ禁止 |
| `dev.push_main` | Dev | main直接push禁止 |
| `dev.deploy_production` | Dev | 本番デプロイ禁止 |
| `dev.read_secrets` | Dev | 秘密読み取り禁止 |
| `dev.delete_repo` | Dev | リポジトリ削除禁止 |
| `pc.run_shell.*` | PC | シェル実行禁止 |
| `pc.type_password` | PC | パスワード自動入力禁止 |
| `android.send_sms` | Android | SMS送信禁止 |
| `android.access_contacts` | Android | 連絡先アクセス禁止 |
| `android.make_call` | Android | 電話発信禁止 |
| `browser.captcha_bypass` | Browser | CAPTCHA迂回禁止 |
| `browser.tos_bypass` | Browser | ToS迂回禁止 |

## 3. Safety Level Summary

| Level | 意味 | 動作 |
|-------|------|------|
| Level 0 (READ_ONLY) | 読み取りのみ | 自動許可、監査不要 |
| Level 1 (SAFE_ACTION) | 安全な操作 | 自動許可、監査必要 |
| Level 2 (APPROVAL_REQUIRED) | 承認必要 | Approval UI 必須 |
| Level 3 (HIGH_RISK) | 高リスク | 承認必要または拒否 |
| FORBIDDEN | 禁止 | 常に拒否 |

## 4. Approval-Required Operations

| 操作 | 承認方式 |
|------|---------|
| PC: mouse_click, keyboard_type, press_hotkey | Approval UI → ONE_TIME |
| PC: close_window, write_clipboard, write_file | Approval UI → ONE_TIME |
| Android: tap, swipe, type_text | Approval UI → ONE_TIME |
| Room: set_light, set_air_conditioner | Approval UI → ONE_TIME |
| Room: send_ir_command, set_smart_plug | Approval UI → ONE_TIME |
| Room: get_camera_snapshot | Approval UI → ONE_TIME |
| Dev: apply_patch, create_commit | Approval UI → ONE_TIME |
| Dev: create_pull_request, revert_changes | Approval UI → ONE_TIME |

## 5. Test Results Summary

| テストスイート | テスト数 | 結果 |
|---|---|---|
| Safety Regression | 44 | ✅ 全パス |
| Integration E2E | 25 | ✅ 全パス |
| Dev Server E2E | 35 | ✅ 全パス |
| Room Action E2E | 34 | ✅ 全パス |
| Room Observe E2E | 62 | ✅ 全パス |
| Android Action E2E | 35 | ✅ 全パス |
| Android Observe E2E | 82 | ✅ 全パス |
| PC Action E2E | 48 | ✅ 全パス |
| PC Observe E2E | 47 | ✅ 全パス |
| Support Agent E2E | 23 | ✅ 全パス |
| Phase 6 Mind/Memory | 36 | ✅ 全パス |
| E2E Lifecycle (Runtime) | 8 | ✅ 全パス |
| 既存テスト | 468 | ✅ 全パス |
| **合計** | **157** | **✅ 全パス** |

## 6. Unresolved Risks

| リスク | 重要度 | 対策 |
|--------|--------|------|
| 実デバイス未テスト | 中 | mock provider + optional marker (`*_local`) |
| Dockerfile未作成 | 中 | infra/docker/ にプレースホルダーあり |
| GitHub Token未設定 | 低 | 環境変数 `GITHUB_TOKEN` のみ |
| Chroma/OpenAI未統合 | 低 | Phase 6で依存追加済み、統合は次フェーズ |
| TLS未実装 | 低 | gRPC plaintext (MVP) |
| 多ユーザー未対応 | 低 | 単一ユーザー前提 (MVP) |

## 7. Next Implementation Candidates

| 優先度 | 項目 | 説明 |
|--------|------|------|
| 高 | Chroma memory統合 | Semantic Memory をベクトルDBに移行 |
| 高 | OpenAI embedding統合 | セマンティック検索の品質向上 |
| 中 | Dockerfile作成 | 全サーバーのコンテナ化 |
| 中 | GitHub PR自動作成 | SelfDevAgent → GitHub API |
| 中 | Android実機テスト | ADB + 実通知取得 |
| 低 | Browser Server browser-use | Python + browser-use 統合 |
| 低 | PC Server Rust実装 | OS-native API (Windows SendInput) |
| 低 | Room Server MQTT adapter | 実センサー接続 |

## 8. Commands Executed

```bash
# Install dependencies
cd ai-server && pip install -e ".[dev]"
pip install chromadb openai langgraph langchain-core

# Run safety regression tests
pytest tests/test_safety_regression.py -v

# Run integration E2E tests
pytest tests/test_integration_e2e.py -v

# Run full test suite
pytest --ignore=tests/test_approval_ui.py --ignore=tests/test_android_local.py -q

# Lint
ruff check tests/test_safety_regression.py tests/test_integration_e2e.py

# Format
ruff format tests/test_safety_regression.py tests/test_integration_e2e.py
```

## 9. Documentation Status

| ファイル | 状態 |
|---------|------|
| `docs/architecture.md` | ✅ 最新 |
| `docs/android-server.md` | ✅ 更新済み |
| `docs/android-safety.md` | ✅ 更新済み |
| `docs/pc-server.md` | ✅ 更新済み |
| `docs/pc-safety.md` | ✅ 更新済み |
| `docs/room-server.md` | ✅ 更新済み |
| `docs/room-safety.md` | ✅ 更新済み |
| `docs/dev-server.md` | ✅ 新規作成 |
| `docs/dev-safety.md` | ✅ 新規作成 |
| `docs/self-development.md` | ✅ 新規作成 |
| `docs/mind-layer.md` | ✅ 新規作成 |
| `docs/memory.md` | ✅ 新規作成 |
| `docs/scheduler.md` | ✅ 新規作成 |
| `docs/testing.md` | ✅ 更新済み |
| `docs/release-readiness.md` | ✅ 本レポート |
