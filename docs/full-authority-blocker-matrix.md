# Full-Authority Blocker Matrix

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Rows below that reference approval/argument-tampering are **historical** —
> see [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

This document tracks the current implementation boundaries that prevent
"full-authority" operation, the code that enforces those boundaries, and the
surfaces where the user can inspect them.

## Current Matrix

| Blocker | Current behavior | Enforced in code | Verified by tests | Visible in UI |
|---|---|---|---|---|
| **Egress (the single constraint)** | **Explicitly denied** — deny by default | `ai-server/src/aegis_ai/egress/` | `ai-server/tests/test_egress_gate.py` | audit / status |
| Purchases / payments | Explicitly denied | `ai-server/src/policy_engine.py` | `ai-server/tests/test_full_authority_policy.py` | `ControlHubPage`, `PersonalAiPage` blocked categories |
| Egress gate / audit bypass | Explicitly denied | `ai-server/src/policy_engine.py`, `ai-server/src/tool_broker.py` | `ai-server/tests/test_egress_gate.py` | audit / status |
| Browser verification / CAPTCHA / credential walls | Stops and requires user input | `browser-server/src/aegis_browser/safety_boundary.py` | browser safety tests | waiting surfaces, session timeline |
| ~~Approval argument tampering~~ | **Historical** — approval is no longer a constraint | ~~`execution_engine.py`~~ | — | — |
| ~~Permanent approval~~ | **Historical** — approval is no longer a constraint | — | — | — |

## Runtime Boundaries

- All capability execution must enter through `ToolBroker.execute()`.
- **All outbound transmission must enter through the egress gate.** No component may open an
  outbound connection outside it.
- `AegisRuntime` remains the only composition root.
- Autonomous follow-up goals can expand backlog, but they do not bypass the
  egress gate or audit.

## Implementation-Adjacent Notes

- "Allow with audit" is the default for capabilities that stay local. The main
  blockers are the **egress gate** and the explicit deny patterns, not a blanket
  approval-first model.
- `user_understanding` exposes blocked categories to the dashboard, so the
  authority ceiling is visible even when it cannot yet be removed.
- `ControlHubPage` and `PersonalAiPage` show the current authority summary and
  paused follow-up backlog; these are the primary operator surfaces.

## Safe Next Steps

1. Add richer task-detail surfaces for paused follow-up goals.
2. Replace remaining keyword-ish incident classification with structured evidence.
3. Keep blocker documentation synced whenever the **egress gate** or browser safety
   boundaries change.

## Sources

- `AGENTS.md`
- `ai-server/AGENTS.md`
- `docs/agent-runtime-patterns.md`
- `.trae/documents/aegis_full_authority_user_understanding_plan.md`
