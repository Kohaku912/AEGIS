# Dev Server — Safety & Privacy

> **REMOVED (Phase 9).** The Dev Server (`dev-server/`, port 50056) has been **deleted**, along with
> its AI Server client (`ai-server/src/aegis_ai/integrations/dev/grpc_client.py`). Self-development now
> runs through the separate **Agent Server** (`aegis-openhands-agent.service`), whose AI Server side is
> `ai-server/src/aegis_ai/agents/backends/openhands/`. See
> [`dev-server.md`](dev-server.md) and [`self-development.md`](self-development.md).
>
> ⚠️ **This document described a server that no longer exists.** It is kept for historical reference.
> Do not follow the capability or workflow sections below. Rewritten 2026-09-28 to say so plainly and
> to separate what is *still true* from what was never true.

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

> **Status**: server removed; document retained for history
> **Related**: [`dev-server.md`](dev-server.md), [`self-development.md`](self-development.md)

## What is still true

### The deny list was deleted; the ids remain unbuildable

The `dev.*` ids below used to be listed in
`ai-server/src/aegis_ai/settings/validation.py`'s `FORBIDDEN_CAPABILITIES`, which was **deleted on
2026-09-29** (B-12 / A-1). They were **deny-list strings, not manifests** — no `dev-server`
capability manifest exists (the catalog holds only `ai-server`, `android-server`, `browser-server`,
`pc-server` and `room-server`), and `_PREFIX_MAP` still carries a `dev-server → dev` entry that can
never resolve. **The list itself never denied them** — it was written in a dialect its gate never
read (B-12, measured 2026-09-29; see
[`permissions.md`](permissions.md#the-forbidden-capability-list-was-deleted-b-12--a-1)). They are
never buildable:

| Id | Reason |
|-----------|--------|
| `dev.merge_to_main` | The user is the only merge authority |
| `dev.push_main` | Direct push to main forbidden |
| `dev.deploy_production` | Production deploy forbidden |
| `dev.production_deploy` | Production deploy forbidden |
| `dev.read_secrets` | Secrets access forbidden |
| `dev.delete_repo` | Repository deletion forbidden |
| `dev.disable_policy_engine` | Policy bypass forbidden |
| `dev.modify_approval_bypass` | Approval bypass forbidden |
| `dev.install_system_package` | System modification forbidden |
| `dev.mount_docker_socket` | Docker socket access forbidden |

> An earlier revision listed only **nine** of these — it omitted `dev.production_deploy`.

## What was never true

These sections described a server that either did not exist as documented or has since been deleted.
They are retained only so the old text is not mistaken for current behaviour.

- **The capability tables.** `dev.get_repo_status`, `dev.get_diff`, `dev.read_file`, `dev.search_code`,
  `dev.create_branch`, `dev.run_tests`, `dev.run_lint`, `dev.apply_patch`, `dev.create_commit`,
  `dev.create_pull_request`, `dev.revert_changes` — none of these exist in the catalog, and the
  `dev-server` that would have served them is gone. `dev.run_tests` also appears in
  `ai-server/samples/capabilities.json` and `MockLLMClient`, both inert.
- **The `Level 2` / "Approval UI → execute" column.** There is no approval gate.
- **The "Approval Flow" section.** It described `PolicyEngine` returning `ASK_APPROVAL`, then
  `SelfDevAgent` auto-approving via `ApprovalStore` and calling `ToolBroker.invoke_tool_approved()`.
  `ASK_APPROVAL`, `ApprovalStore` and the approval method were deleted on 2026-09-28
  (`invoke_tool_approved` survives only as an `evaluation/` scenario step name).
- **`SelfDevAgent`.** No such class exists. The only trace is an untyped optional
  `self_dev_agent: Any = None` parameter in `aegis_ai/interaction/router.py` (and, until it was
  deleted on 2026-10-08, a docstring mention in `reflection_loop.py`), so the workflow diagram
  described an agent that was never written.
- **"PR creation requires approval — Level 2."** No approval step exists anywhere in the pipeline.
- **The file deny list** (`dev.read_file` denied for `.env`, `.pem`, `id_rsa`, …). That check belonged
  to the deleted server; nothing enforces it now.
- **The sandbox claims** (workspace isolation, no access to parent directories or system files, no
  Docker daemon access, no external network except the GitHub API). Those described the deleted
  `dev-server`. The current agent backend is `agents/backends/openhands/`, which has its own
  `workspace.py`; consult that and [`self-development.md`](self-development.md) for the live model
  rather than the text below.

## Historical text (do not follow)

The following was the body of this document before the server was removed. It is preserved verbatim
only to explain references you may find in older commits.

### Historical — Safety Level Classification

- *Level 0 (READ_ONLY)*: `dev.get_repo_status`, `dev.get_diff`, `dev.read_file`, `dev.search_code`
- *Level 1 (SAFE_ACTION)*: `dev.create_branch`, `dev.run_tests`, `dev.run_lint`
- *Level 2 (APPROVAL_REQUIRED)*: `dev.apply_patch`, `dev.create_commit`, `dev.create_pull_request`,
  `dev.revert_changes`
- *Explicitly denied*: the ten `dev.*` ids listed above

### Historical — Data Flow

```
ReflectionLog → SelfDevAgent
  ├── ANALYZE → find improvement opportunities
  ├── PROPOSE → create proposal
  ├── BRANCH  → ToolBroker → PolicyEngine (Level 1, auto-allow)
  ├── PATCH   → ToolBroker → PolicyEngine (Level 2, auto-approve)
  ├── TEST    → ToolBroker → PolicyEngine (Level 1, auto-allow)
  ├── LINT    → ToolBroker → PolicyEngine (Level 1, auto-allow)
  ├── COMMIT  → ToolBroker → PolicyEngine (Level 2, auto-approve)
  ├── PR      → ToolBroker → PolicyEngine (Level 2, approval required)
  └── REFLECT → write to ReflectionLog
        ↓
AuditLog (every step recorded)
```

Both the `SelfDevAgent` and the `Level 1/2` decisions in that diagram are fictional as of 2026-09-28.
