# Goal Change — 2026-09-27, re-scoped 2026-09-30

> **Read this before trusting any approval / policy / reversibility / reliability statement in `docs/`.**

---

## 2026-09-30 — the constraint is re-scoped: permission-gated, not deny-all

**Read this section first. It supersedes the 2026-09-27 statement of the constraint.**

The owner re-scoped the single constraint. Outbound **connections** are allowed; what stays forbidden is
**unpermitted** disclosure of the user's information.

| | 2026-09-27 | **2026-09-30 (current)** |
|---|---|---|
| Outbound connections | denied by default | **allowed** |
| User information sent externally | never, no exception | **allowed with the user's permission** |
| User information sent externally *without* permission | forbidden | **still forbidden** (unchanged) |

Consequences that the rest of this document predates:

- **The egress gate changes meaning.** It stops being a deny-all wall and becomes the **permission
  check** on user-information egress. Plain outbound traffic passes.
- **The permission mechanism already exists** and is not new work: the confirmation store, the Android
  streamed approval, and the PC overlay. The constraint now rests on the **voluntary ask**.
- **D4=(b) still holds.** The *forced* approval gate stays retired; the *voluntary* ask is what carries
  this constraint. Satisfying only one half is still the failure mode.
- **This reopens features that egress had closed:** external messaging, cloud STT/TTS, external vision
  and external LLM calls are now implementable **through the permission check**. The owner has put
  **voice I/O and external messaging into v1**.
- **"No local LLM" is unchanged** — it is a decision about *which* model runs, not about egress. The
  owner confirmed it covers LLMs only, so **local STT/TTS is in scope**.

> **The 2026-09-27 section below is kept as the record of that change.** Where it says there is "no
> consent exception", it is now **wrong** — see the table above. Everything else in it still holds.

---

## What changed

The Long-Term Objective in `AGENTS.md` was narrowed to a **single constraint**.

| | Before | After |
|---|---|---|
| Constraints | approval, privacy, reversibility, policy boundaries, reliability proof, user control | **Privacy only** — the user's information must never leave the local environment |
| Posture | honest about uncertainty | honest about uncertainty (**unchanged**) |
| Condition for expanding authority | "wherever the system can prove reliability and preserve user control" | **none** — within capability and the user's delegation |

**Removed as constraints:** approval, reversibility, policy, reliability proof, user control.
**Kept:** "being honest about uncertainty" — as a **posture of the response**, not a constraint on action.

## What this means for the docs

Many documents in `docs/` describe approval gates, policy levels, reversibility, and reliability
gates as **mandatory requirements**. Those statements are now **historical**. They describe the
system as it was, not as it must be.

When you read a doc and see:

| You see | It now means |
|---|---|
| "requires approval" | Describes a mechanism that is **being retired** (Phase 2). Not a requirement. |
| "Level 2 / Level 3" | A **risk annotation**. Useful as metadata; not a gate. |
| "hard deny" | Only **egress** and **purchases/payments** are hard-denied (see `AGENTS.md` Security Policy). |
| "must be approved", "without approval" | Historical. Approval is not a constraint. |
| "never leaves the local network without explicit consent" | **Correct again as of 2026-09-30** — see the re-scope section at the top. From 2026-09-27 to 2026-09-30 this row read "**Wrong now.** There is no consent exception." |
| "reversibility", "rollback required" | A useful **tool**, not a constraint. |
| "reliability proof", "verified success only" | A useful **quality practice**, not a constraint. |

## The single constraint

> **Superseded 2026-09-30 — see the re-scope section at the top of this file.** The text below is the
> 2026-09-27 statement, kept as the record of that change. Read it with the re-scope in mind: the
> "no consent exception" half no longer holds.

**The user's information must never leave the local environment.**

All outbound transmission goes through the **egress gate** (`ai-server/src/aegis_ai/egress/`) and is
**denied by default**. There is no consent exception, no "explicitly configured" exception.

## Migration plan

The full phase-by-phase plan (Phase 0 documentation → Phase 1 egress gate → Phase 2 removal →
Phase 3 alternative safety → Phase 4 tests/CI → Phase 5 UI) is in
[`IMPROVEMENT_PROPOSAL.md`](../IMPROVEMENT_PROPOSAL.md) §9. **§9 supersedes §1–8 of that document.**

Ordering rule: **Phase 1 must precede Phase 2.** Removing approval increases autonomous execution;
if egress is not structurally blocked first, AEGIS ends up with *no constraint at all* and *more*
autonomy — the worst combination.

## Documents already aligned

- `AGENTS.md` — goal, Technology Decision Gate, architecture table, Security Policy, status tables, key files
- `docs/GOAL-CHANGE.md` — this file
- `docs/architecture.md` — key design constraint line, security design section, consent line
- `docs/security.md`, `docs/permissions.md`, `docs/risk-register.md` — constraint-defining docs
- `docs/adr/permissive-autonomy-policy.md` — autonomy policy

## Documents still describing the old model

The remaining docs in `docs/` (safety tables, UI checklists, runbooks, testing docs) still use
approval-centric language. They are being updated in Phase 0 on a rolling basis. Until then, treat
their approval/policy/reversibility statements as **historical descriptions**.
