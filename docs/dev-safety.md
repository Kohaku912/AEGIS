# Dev Server — Safety & Privacy

> **Status**: Phase 5 — Self-development scaffold
> **Related**: `docs/dev-server.md`, `docs/self-development.md`, `docs/architecture.md` §7, §8

## Safety Level Classification

### Level 0 — READ_ONLY (auto-allowed)

| Capability | Side Effects | Notes |
|-----------|-------------|-------|
| `dev.get_repo_status` | None | Git branch, commit, modified files |
| `dev.get_diff` | None | Diff between branches |
| `dev.read_file` | None | Denied for secrets (.env, .pem, etc.) |
| `dev.search_code` | None | Code search in workspace |

### Level 1 — SAFE_ACTION (auto-allowed, audited)

| Capability | Notes |
|-----------|-------|
| `dev.create_branch` | Creates git branch, audited |
| `dev.run_tests` | Auto-detects language, runs test suite |
| `dev.run_lint` | Auto-detects language, runs linter |

### Level 2 — APPROVAL_REQUIRED

| Capability | Approval Flow |
|-----------|---------------|
| `dev.apply_patch` | Approval UI → execute |
| `dev.create_commit` | Approval UI → execute |
| `dev.create_pull_request` | Approval UI → execute (requires GITHUB_TOKEN) |
| `dev.revert_changes` | Approval UI → execute |

### Explicitly Denied (always DENY)

| Capability | Reason |
|-----------|--------|
| `dev.push_main` | Direct push to main forbidden |
| `dev.merge_to_main` | User is only merge authority |
| `dev.deploy_production` | Production deploy forbidden |
| `dev.read_secrets` | Secrets access forbidden |
| `dev.delete_repo` | Repository deletion forbidden |
| `dev.disable_policy_engine` | Policy bypass forbidden |
| `dev.modify_approval_bypass` | Approval bypass forbidden |
| `dev.install_system_package` | System modification forbidden |
| `dev.mount_docker_socket` | Docker socket access forbidden |

## File Safety

### Denied Paths

Files matching these patterns are NEVER readable:

| Pattern | Category |
|---------|----------|
| `.env`, `.env.local`, `.env.production` | Environment secrets |
| `credentials.json`, `credentials.xml` | Credentials |
| `.pem`, `.key`, `.crt`, `.p12` | Certificates |
| `id_rsa`, `id_ed25519`, `id_ecdsa` | SSH keys |
| `token`, `secret`, `password` | Generic secrets |

## Sandbox Design

### Workspace Isolation (OpenHands/SWE-agent inspired)

- All operations run within a designated workspace directory
- No access to parent directories or system files
- Git operations are scoped to the workspace
- Test/lint commands run in the workspace context

### What the Sandbox Prevents

- ❌ Access to files outside the workspace
- ❌ System-level operations (package install, service management)
- ❌ Docker daemon access
- ❌ Network access to external services (except GitHub API for PRs)
- ❌ Access to secrets or credentials

## Self-Development Safety

### Workflow Constraints

1. **main merge is FORBIDDEN** — `dev.merge_to_main` is in PolicyEngine deny patterns
2. **PR creation requires approval** — Level 2, goes through Approval UI
3. **Test failure → revert** — Changes are automatically reverted
4. **Lint failure → revert** — Changes are automatically reverted
5. **All attempts audited** — Every step logged to AuditLog
6. **Reflection written** — Success/failure recorded for learning

### Approval Flow

When SelfDevAgent encounters a Level 2 capability:

1. Calls `ToolBroker.invoke_tool(capability_id, params)`
2. PolicyEngine returns `ASK_APPROVAL`
3. SelfDevAgent auto-approves via ApprovalStore (self-dev is pre-authorized)
4. Calls `ToolBroker.invoke_tool_approved(capability_id, params)`
5. Execution proceeds
6. Result logged to AuditLog

### What SelfDevAgent NEVER Does

- ❌ Merge to main
- ❌ Push to main
- ❌ Deploy to production
- ❌ Access secrets
- ❌ Install system packages
- ❌ Bypass PolicyEngine
- ❌ Auto-approve its own operations (except in self-dev workflow)
- ❌ Delete the repository
- ❌ Modify PolicyEngine or Approval UI

## Data Flow

```
ReflectionLog
  ↓ (analysis)
SelfDevAgent
  ├── ANALYZE → find improvement opportunities
  ├── PROPOSE → create proposal
  ├── BRANCH → ToolBroker → PolicyEngine (Level 1, auto-allow)
  ├── PATCH → ToolBroker → PolicyEngine (Level 2, auto-approve)
  ├── TEST → ToolBroker → PolicyEngine (Level 1, auto-allow)
  ├── LINT → ToolBroker → PolicyEngine (Level 1, auto-allow)
  ├── COMMIT → ToolBroker → PolicyEngine (Level 2, auto-approve)
  ├── PR → ToolBroker → PolicyEngine (Level 2, approval required)
  └── REFLECT → write to ReflectionLog
        ↓
AuditLog (every step recorded)
```
