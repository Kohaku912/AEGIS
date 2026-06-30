# Dev Server — Design & Usage

> **Status**: Phase 5 — Self-development scaffold
> **Language**: Python (AEGIS Core integration via `dev_server_client.py`)
> **Sandbox**: Workspace directory isolation (OpenHands/SWE-agent inspired)

## Overview

The Dev Server provides AEGIS with sandboxed self-development capabilities.
All operations go through ToolBroker → PolicyEngine → Approval UI (for Level 2+).
Main merge is **FORBIDDEN** — user is the only merge authority.

## Implemented Capabilities

### Observe (Level 0 — READ_ONLY)

| Capability | Status |
|-----------|--------|
| `dev.get_repo_status` | ✅ Mock provider |
| `dev.get_diff` | ✅ Mock provider |
| `dev.read_file` | ✅ Mock provider + path safety |
| `dev.search_code` | ✅ Mock provider |

### Action (Level 1 — SAFE_ACTION)

| Capability | Status |
|-----------|--------|
| `dev.create_branch` | ✅ Mock provider |
| `dev.run_tests` | ✅ Mock provider + auto-detect language |
| `dev.run_lint` | ✅ Mock provider + auto-detect language |

### Action (Level 2 — APPROVAL_REQUIRED)

| Capability | Status |
|-----------|--------|
| `dev.apply_patch` | ✅ Mock provider + Approval UI |
| `dev.create_commit` | ✅ Mock provider + Approval UI |
| `dev.create_pull_request` | ✅ Mock provider + Approval UI + GITHUB_TOKEN |
| `dev.revert_changes` | ✅ Mock provider + Approval UI |

### Explicitly Denied

| Capability | Reason |
|-----------|--------|
| `dev.push_main` | Direct push to main forbidden |
| `dev.merge_to_main` | User is only merge authority |
| `dev.deploy_production` | Production deploy forbidden |
| `dev.read_secrets` | Secrets access forbidden |
| `dev.delete_repo` | Repo deletion forbidden |
| `dev.disable_policy_engine` | Policy bypass forbidden |
| `dev.modify_approval_bypass` | Approval bypass forbidden |
| `dev.install_system_package` | System modification forbidden |
| `dev.mount_docker_socket` | Docker socket access forbidden |

## Technology Decisions

| 項目 | 選択 |
|------|------|
| Sandbox | **OpenHands/SWE-agent参考**（ワークスペース分離 + subprocess） |
| GitHub PR | **PR作成まで実装**（`GITHUB_TOKEN` 環境変数） |
| Token | **`GITHUB_TOKEN` 環境変数のみ** |
| test/lint | **全言語 auto-detect**（Python, Kotlin, TypeScript, Rust） |
| SelfDevAgent | **フル自動（PR作成まで、merge のみユーザー）** |

## Language Auto-Detection

The Dev Server auto-detects the project language by indicator files:

| Language | Indicators | Test Command | Lint Command |
|----------|-----------|-------------|-------------|
| Python | `pyproject.toml`, `setup.py` | `pytest` | `ruff check .` |
| Kotlin | `build.gradle.kts` | `./gradlew test` | `./gradlew ktlintCheck` |
| TypeScript | `tsconfig.json` | `npm test` | `npx eslint .` |
| JavaScript | `package.json` | `npm test` | `npx eslint .` |
| Rust | `Cargo.toml` | `cargo test` | `cargo clippy` |

## Self-Development Workflow

```
1. ANALYZE   — Read Reflection Log, find improvement opportunities
2. PROPOSE   — Create improvement proposal with risk assessment
3. BRANCH    — Create git branch (e.g., aegis/improve-event-bus)
4. PATCH     — Apply code changes (unified diff)
5. TEST      — Run test suite (auto-detect language)
6. LINT      — Run linter (auto-detect language)
7. COMMIT    — Create git commit
8. PR        — Create GitHub pull request (requires GITHUB_TOKEN)
9. REFLECT   — Write reflection to ReflectionLog
```

### Safety Constraints

- **main merge is FORBIDDEN** — `dev.merge_to_main` is in PolicyEngine deny patterns
- **PR creation requires Level 2 approval** — goes through Approval UI
- **Test failure → revert** — changes are reverted if tests fail
- **Lint failure → revert** — changes are reverted if lint fails
- **All attempts audited** — every step logged to AuditLog

## Current Dev Server Runtime

- Dev Server runs as a Docker Compose gRPC service on `50056`.
- The repository is mounted write-capable at `/workspace` by design.
- Docker socket is not mounted and must remain unavailable.
- Safe read/status operations may be automatic; writes and code execution remain subject to policy and approval gates.
- **Reflection written** — success/failure recorded in ReflectionLog

## File Safety

### Denied Paths

| Pattern | Reason |
|---------|--------|
| `.env`, `.env.local` | Environment secrets |
| `credentials.json` | Credentials |
| `.pem`, `.key`, `.crt` | Certificates |
| `id_rsa`, `id_ed25519` | SSH keys |

## GitHub PR Integration

When `GITHUB_TOKEN` environment variable is set:
- `dev.create_pull_request` creates a real GitHub PR
- Uses `gh` CLI or GitHub API

When `GITHUB_TOKEN` is NOT set:
- `dev.create_pull_request` returns instructions for manual PR creation
- Branch and commit are still created locally

## Testing

```bash
cd ai-server

# Dev Server E2E
pytest tests/test_dev_server_e2e.py -v

# All tests
pytest --ignore=tests/test_approval_ui.py --ignore=tests/test_android_local.py -v
```
