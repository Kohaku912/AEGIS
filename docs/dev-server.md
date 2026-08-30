# Dev Server — Design & Usage

> **Status**: Implemented gRPC service (sandboxed repo operations)
> **Language**: Python (`dev-server/src/dev_server.py`)
> **AI Server client**: `ai-server/src/aegis_ai/integrations/dev/grpc_client.py`
> **Sandbox**: Workspace directory isolation; argv subprocess (no shell)

## Overview

The Dev Server gives AEGIS sandboxed self-development on a mounted git
workspace. It exposes repo status, diff, test, lint, branch, patch, commit,
PR, and revert through gRPC on port **50056**.

Main merge / direct commit to `main` or `master` is **FORBIDDEN**. The user
is the only merge authority.

## Implemented Capabilities (proto RPCs)

Canonical IDs are `dev-server.<app>.<action>`.

### Observe

| Capability | RPC | Notes |
|-----------|-----|-------|
| `dev-server.repo.status` | `GetRepoStatus` | Branch, commit, porcelain files, ahead/behind |
| `dev-server.diff.get_diff` | `GetDiff` | Per-file unified diff vs base (`main`/`master`) |
| `dev-server.test.get_results` | `GetTestResults` | Last `RunTests` result (empty if none) |
| `dev-server.system.health_check` | `HealthCheck` | Online + uptime |

`read_file` / `search_code` are **not** in `dev_server.proto` and are not exposed.

### Action

| Capability | RPC | Notes |
|-----------|-----|-------|
| `dev-server.branch.create` | `CreateBranch` | Switch existing or `git switch -c` from base |
| `dev-server.test.run_tests` | `RunTests` | Language auto-detect; missing toolchain returns error |
| `dev-server.lint.run_lint` | `RunLint` | Language auto-detect or explicit linter |
| `dev-server.patch.apply` | `ApplyPatch` | Unified diff via `git apply`, else write `file_path` |
| `dev-server.git.create_commit` | `CreateCommit` | Denied on `main`/`master`; skipped denied paths |
| `dev-server.pr.create` | `CreatePullRequest` | `gh` + `GITHUB_TOKEN`, else manual instructions |
| `dev-server.git.revert_changes` | `RevertChanges` | `git restore` / `clean`, or `git revert --no-edit` |

### Explicitly Denied

| Action | Reason |
|--------|--------|
| Direct commit / push / merge to main | User is only merge authority |
| `git reset --hard` | Destructive; not exposed |
| Secrets (`.env`, keys, credentials) | Path denylist |
| Production deploy / docker.sock / package install | Not in the API |

## Language Auto-Detection

The server detects language from indicator files in the **target** directory
(`ai-server` by default, or repo root when `target=all`):

| Language | Indicators | Test Command | Lint Command |
|----------|-----------|-------------|-------------|
| Python | `pyproject.toml`, `setup.py` | `python -m pytest` | `ruff check .` |
| Kotlin | `build.gradle.kts` | `./gradlew test` | `./gradlew ktlintCheck` |
| TypeScript | `tsconfig.json` | `npm test` | `npx eslint .` |
| JavaScript | `package.json` | `npm test` | `npx eslint .` |
| Rust | `Cargo.toml` | `cargo test` | `cargo clippy` |

The default image includes git, Python, pytest, ruff, and `gh`. Node / JDK /
Rust are not bundled; those commands fail with `toolchain missing`.

## Safety Constraints

- All git/test/lint/gh calls use argv lists (`shell=False`)
- `extra_args` is `shlex`-split; shell metacharacters are rejected
- Paths must stay inside `AEGIS_REPO_PATH` (`/workspace` in Docker)
- Denied path fragments: `.env`, credentials, SSH keys, `.git/config`
- Docker socket is not mounted

## Runtime

- Compose service `dev-server` listens on `50056`
- Repo is mounted write-capable at `/workspace`
- Production overlay puts this service behind the `dev` profile and lists it
  in `AEGIS_DISABLED_SERVERS` by default. Start with:

```bash
docker compose --profile dev up -d --no-deps dev-server
```

## GitHub PR Integration

When `GITHUB_TOKEN` is set **and** `gh` is on PATH, `CreatePullRequest` runs
`gh pr create`. Otherwise the RPC returns the equivalent `gh` command for
manual use. Branch and commit still happen locally.

## Testing

```bash
cd dev-server
pytest tests/test_dev_server.py -q

# Live gRPC probe (server already running)
python ../scripts/e2e/dev-real-probe.py 127.0.0.1 50056
```
