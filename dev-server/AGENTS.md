# Dev Server — AGENTS.md

## Purpose

The Dev Server is AEGIS's sandboxed self-development gRPC service:
- Git status, diff, branch, patch, commit, revert
- Test and lint (language auto-detect)
- GitHub PR creation (`gh` + `GITHUB_TOKEN`)

Main merge and direct commits to `main`/`master` are forbidden.

## Technology Stack

- **Language**: Python 3.12
- **Framework**: gRPC (`protos/aegis/dev_server.proto`)
- **Port**: 50056
- **Workspace**: `AEGIS_REPO_PATH` (Docker: `/workspace`)

## Directory Structure

```
dev-server/
├── src/
│   ├── dev_server.py          # Service + gRPC adapter + serve()
│   └── generated/aegis/       # Generated protobuf stubs
├── tests/
│   └── test_dev_server.py
├── pyproject.toml
└── AGENTS.md
```

AI Server calls this via `DevServerGrpcClient`
(`ai-server/src/aegis_ai/integrations/dev/grpc_client.py`).

## RPCs

| RPC | Capability ID |
|-----|---------------|
| `GetRepoStatus` | `dev-server.repo.status` |
| `GetDiff` | `dev-server.diff.get_diff` |
| `GetTestResults` | `dev-server.test.get_results` |
| `CreateBranch` | `dev-server.branch.create` |
| `ApplyPatch` | `dev-server.patch.apply` |
| `RunTests` | `dev-server.test.run_tests` |
| `RunLint` | `dev-server.lint.run_lint` |
| `CreateCommit` | `dev-server.git.create_commit` |
| `CreatePullRequest` | `dev-server.pr.create` |
| `RevertChanges` | `dev-server.git.revert_changes` |
| `HealthCheck` | `dev-server.system.health_check` |

## Safety

- argv subprocess only (`shell=False`)
- Workspace path confinement; `.env` / keys / credentials denied
- No docker.sock, no package-install API, no production deploy API
- `git reset --hard` is not exposed

## Running

```bash
cd dev-server
PYTHONPATH=src python -m dev_server

# Docker
docker compose up -d --no-deps dev-server
# Production overlay: docker compose --profile dev up -d --no-deps dev-server
```

## Tests

```bash
cd dev-server
pytest tests/test_dev_server.py -q
```
