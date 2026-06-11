# Self-Development — Design & Workflow

> **Status**: Phase 5 — Full workflow implementation
> **Related**: `docs/dev-server.md`, `docs/architecture.md` §5.7, §8

## Overview

AEGIS can improve its own codebase through a strictly gated workflow.
The SelfDevAgent orchestrates the entire process, from analyzing reflections
to creating pull requests. **Main merge is always user-only.**

## Workflow

```
┌──────────────┐
│   ANALYZE    │ ← Read ReflectionLog, find improvement opportunities
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   PROPOSE    │ ← Create improvement proposal with risk assessment
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   BRANCH     │ ← Create git branch (Level 1, auto-allowed)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   PATCH      │ ← Apply code changes (Level 2, approval required)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   TEST       │ ← Run test suite (Level 1, auto-allowed)
└──────┬───────┘
       │
       ├── FAIL → REVERT → FAILED
       │
       ▼
┌──────────────┐
│   LINT       │ ← Run linter (Level 1, auto-allowed)
└──────┬───────┘
       │
       ├── FAIL → REVERT → FAILED
       │
       ▼
┌──────────────┐
│   COMMIT     │ ← Create git commit (Level 2, approval required)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   PR         │ ← Create GitHub PR (Level 2, approval required)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   REFLECT    │ ← Write reflection to ReflectionLog
└──────────────┘
```

## Safety Gates

| Step | Gate | Behavior |
|------|------|---------|
| BRANCH | Level 1 | Auto-allowed, audited |
| PATCH | Level 2 | Approval required (auto-approved in self-dev flow) |
| TEST | Level 1 | Auto-allowed, audited |
| LINT | Level 1 | Auto-allowed, audited |
| COMMIT | Level 2 | Approval required (auto-approved in self-dev flow) |
| PR | Level 2 | Approval required |
| MERGE | **FORBIDDEN** | User-only, no API exists |

## SelfDevAgent Integration

### With ReflectionLog

```python
from aegis_ai.memory.reflection import ReflectionLog
from aegis_ai.agents.self_dev import SelfDevAgent

reflection = ReflectionLog()
reflection.add(Reflection(
    summary="Test failure in EventBus",
    what_failed=["event_bus.publish"],
    improvement_ideas=["Add retry logic to EventBus"],
))

agent = SelfDevAgent(reflection_log=reflection)
result = agent.run()  # Analyzes reflections automatically
```

### With ToolBroker + ApprovalStore

```python
from approval import ApprovalStore
from aegis_ai.agents.self_dev import SelfDevAgent

approval_store = ApprovalStore()
agent = SelfDevAgent(
    tool_broker=broker,
    audit_log=audit,
    reflection_log=reflection,
    approval_store=approval_store,
)

# Full workflow: analyze → propose → branch → patch → test → lint → commit → PR
result = agent.run(
    improvement_description="Add error handling to EventBus",
    file_path="src/event_bus.py",
    patch_content="--- a/src/event_bus.py\n+++ b/src/event_bus.py\n...",
)
```

## Failure Handling

| Failure | Behavior |
|---------|---------|
| Patch fails | Error recorded, workflow stops |
| Tests fail | Changes reverted, workflow stops |
| Lint fails | Changes reverted, workflow stops |
| Commit fails | Error recorded, workflow stops |
| PR fails | Error recorded, workflow stops |

All failures are:
1. Recorded in AuditLog
2. Written to ReflectionLog (for future learning)
3. Changes reverted (if possible)

## What SelfDevAgent NEVER Does

- ❌ Merge to main
- ❌ Push to main
- ❌ Deploy to production
- ❌ Access secrets
- ❌ Install system packages
- ❌ Bypass PolicyEngine
- ❌ Auto-approve its own operations
- ❌ Delete the repository
