# AEGIS Status

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language in this repo is a **risk
> annotation**, not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

**This file is structure and intent, not a measurement.** Test totals and capability counts are
deliberately *not* repeated here — a quantity written in two places goes stale in one of them
(`PROJECT_STATUS_REVIEW.md` §4.3 class 9). For numbers, run the commands below or read the live report.

## Where the truth lives

| Question | Source |
|---|---|
| Assessed state, open findings, prioritised actions | `PROJECT_STATUS_REVIEW.md` |
| Migration progress, per-commit detail | `AGENT_PROGRESS.md` |
| Plan and owner decisions D1–D7 | `IMPROVEMENT_PROPOSAL.md` §9 |
| Agent-facing counts (**re-measure before trusting**) | `AGENTS.md` |
| Generated evidence | `data/reports/` |
| Run everything | `scripts/test-all-suites.ps1` (constraint gate + SDK / room / browser) |
| ai-server alone | `cd ai-server && pytest` |

## Servers

| Server | Language | Port | Role |
|---|---|---|---|
| AI Server | Python | 50051 | Central brain — LLM, memory, desires, capability catalog |
| PC Server | Rust | 50052 | Windows operations (screenshot, mouse, keyboard, overlay, shell) |
| Browser Server | Python | 50053 | Web browsing via browser-use |
| Android Server | Kotlin | 50054 (contract; the app connects **outbound** to 50051) | Mobile companion |
| Room Server | Python | 50055 | IoT / sensor data |
| Dashboard | Flask | 8090 | Web UI, chat, monitoring |

Android builds are **not compile-verified on the dev machine** (no JDK). Static checks only.

## Retired — do not go looking for it

| Gone | Note |
|---|---|
| Approval subsystem — `ApprovalManager`, `ApprovalFanout`, `ApprovalStore` (`aegis_ai/approval/`, `src/approval.py`) | Deleted. The forced gate is retired; a **voluntary** ask remains (confirmation store + streamed approval on Android + PC overlay). |
| `dev-server` | Deleted. A few id literals survive only as deny-list entries. |
| `AutonomyProfile` | Deleted — its ladder *was* Phase-5b approval semantics. |
| Research Agent (`aegis_ai/research/`) | Deleted. |
| SelfDev Agent (`agents/self_dev.py`) | Deleted — and `SelfDevAgent` was never a class. |

Pins that keep this true: `ai-server/tests/test_goal_change_guard.py` (the deleted subsystem stays
deleted) and `ai-server/tests/test_forced_gate_stays_retired.py` (no live path can reach a gate — this
also covers the unwired `aegis_ai/permissions/` service-permission gate).

## Not started

- **Real external messaging**: LINE, Discord, SMTP, webhook — represented at the interface level only.
- **Voice**: push-to-talk STT, TTS.
- **Multi-user** and multi-tenant isolation.
- **Cross-device context sharing**.
- **Graceful device-offline handling**.
- **Room real sensor provider** — Room stays `UNCONFIGURED/DISABLED` until a real Orange Pi provider
  replaces the development mock.

## Partial / in progress

- **gRPC TLS**: `security/tls_config.py` exists; server/client integration is incomplete, so v1 gRPC
  must stay inside Tailscale / a private network boundary.
- **Docker Compose**: compose file and Dockerfiles exist; full multi-service validation is pending.
- **Completion verification**: manifests may declare `completion`; ToolBroker verifies and retries for
  manifest-backed checks.

## Out of scope (deliberate)

| Not doing | Why |
|---|---|
| Cloud / SaaS deployment | Local-first architecture |
| Always-listening voice | Privacy |
| Plugin marketplace | Premature — needs real usage first |
| Multi-tenant isolation | Single-user |
| Real purchase / payment | `EXPLICIT_DENY_PATTERNS` denies payment capabilities outright — a product decision, **not** an egress rule |

**Obsolete rather than out of scope**: the old "auto-approve dangerous ops" item only had meaning while
a forced approval gate existed. With the gate retired the question no longer arises — what remains is
the single constraint (no egress) plus AEGIS's own judgement about when to ask.

## Acceptance is evidence-gated, not "done"

Code can be complete and still not accepted. The acceptance checks are **Ubuntu reboot recovery, PC real
actions, Android reconnect, and the soak** — each gated on its own current-host report. Regenerate with:

`scripts/audit-production-readiness.py` · `scripts/audit-v1-completion.py` ·
`scripts/audit-capability-coverage.py` · `scripts/audit-dead-code.py` · `scripts/audit-mocks.py` ·
`scripts/audit-secrets.py` · `scripts/audit-ui-completeness.py`

Outputs land in `data/reports/` (`readiness_summary.json`, `production_blockers.json`,
`v1_completion.json`, `capability_coverage.json`, `ui_completeness.json`, `secret_inventory.json`,
`mock_inventory.json`, and `e2e/latest/summary.json`).

## History

The June-era `docs/roadmap.md`, `docs/backlog.md` and `docs/implementation-status.md` — plus an earlier
revision of this file — were consolidated here on **2026-09-28**. They had stopped in June and
described the approval era: a total of **157 tests**, **53 capabilities**, and several modules as
"✅ Done" that no longer exist (`ApprovalManager`, `ApprovalFanout`, `ApprovalStore`, `Research Agent`,
`SelfDev Agent`). They also cited `data/reports/production_readiness.json`, which was never the real
filename (the audit writes `readiness_summary.json`). Git history keeps all of it; this file is the
live one.
