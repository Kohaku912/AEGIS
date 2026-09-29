# Confirmation UI — Design & Usage

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

> **Status**: Verified against the current code snapshot — `aegis_ai/confirmation/` +
> `web/routes/approval.py`
> **Related**: [`architecture.md`](architecture.md) §7.3, [`GOAL-CHANGE.md`](GOAL-CHANGE.md),
> [`AGENTS.md`](../AGENTS.md) "LLM-Driven Operations"

## What this surface is now

**AEGIS-initiated confirmation.** AEGIS acts inside its delegated scope without asking. When it
judges that *the user* should decide — an irreversible step, an ambiguous goal, a genuinely new
kind of action — it raises a confirmation and the dashboard renders it. The same judgement decides
whether to speak at all, so a confirmation is the interactive half of the interruption design:
"when should I interrupt?" and "what do I need from you?" are one decision.

The user's standing rule, which this doc exists to serve:

> Removing the forced gate does not mean removing the ability to ask. It means deleting the
> mechanism that **forces** AEGIS to obtain approval before using certain capabilities. When
> **AEGIS voluntarily asks the user for confirmation**, the approval UI must remain usable.

So the UI stayed, and the *gate* did not.

## What was deleted (2026-09-27 → 2026-09-28)

| Removed | Was |
|---|---|
| `aegis_ai/approval/` package | `ApprovalManager`, `ApprovalFanout`, per-channel adapters |
| `RequestApproval` / `ResolveApproval` / `ListPendingApprovals` RPCs + their 5 messages | The forced gate's wire contract |
| `POLICY_DECISION_ASK_APPROVAL` | Now `reserved 2` in `protos/aegis/common.proto` |
| `ToolBroker.invoke_tool_approved()` | The "execute only with a valid approval" path |
| `ApprovalStore`, `ApprovalWebApp` | The old store and its standalone Flask app |
| The "Allow once / for session / Deny and remember" lifecycle | Timeout → auto-deny, permanent denial |

`invoke_tool_approved` survives only as a step name in the `evaluation/` scenario runner, where it
is inert. If you find it anywhere else, that reference is stale.

## Architecture

```
AEGIS decides to ask
  └── ai-server.confirmation.request        capability manifest
        └── ConfirmationStore.request()     aegis_ai/confirmation/store.py
              ├── JSONL history             data/…  (last write wins per id)
              ├── listeners ──► SSE         GET /api/approvals/events
              ├── dashboard queue           GET /api/approvals/pending
              └── capability surface        ai-server.confirmation.list

User answers ──► POST /api/approvals/<id>/<action>
                   └── ConfirmationStore.approve() / reject() / cancel() / modify_and_approve()
                         └── the answer informs what AEGIS does next.
                             Nothing was waiting on it. No capability is unblocked.
```

**Nothing in the execution path consults the store.** A capability runs because the LLM decided to
run it — never because a request was approved. The store has no reference to the policy engine,
the tool broker or a capability manifest, and it does no risk inference and no keyword matching.

## Endpoints

`web/routes/approval.py` owns the blueprint; `web/resource_routes.py` serves the generic resource
listing the dashboard's table reads.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/approvals` | **History** — every confirmation, newest first (limit 200) |
| GET | `/api/approvals/pending` | Open confirmations only, oldest first, with `pending_count` |
| GET | `/api/approvals/<id>` | Detail for one confirmation |
| GET | `/api/approvals/events` | SSE: `connected`, then live `approval.created` / `approval.resolved` |
| POST | `/api/approvals/<id>/approve` | Record "yes" |
| POST | `/api/approvals/<id>/modify-and-approve` | Record "yes, but like this" — body may carry `edits` |
| POST | `/api/approvals/<id>/reject` | Record "no" |
| POST | `/api/approvals/<id>/cancel` | Withdraw the question (AEGIS's side, not a refusal) |

POST bodies: `{"decided_by": "user", "note": "…"}`, plus `{"edits": {…}}` for
`modify-and-approve`. `edits` may only narrow the **descriptive** fields — `summary`, `target`,
`preview`, `expected_effect`, `side_effects`. `capability_id` / `tool_name` are AEGIS's statement
of what it intends to do; letting them be rewritten would turn the confirmation into a way to
direct a different action than the one AEGIS reasoned about.

### Response codes

| Code | Error | Meaning |
|---|---|---|
| 404 | `unknown_confirmation` | No such confirmation |
| 409 | `confirmation_not_open` | It exists but is no longer pending — "you are too late" |
| 503 | `confirmation_store_unavailable` | The store is unreachable — "the server is unwell" |

404 and 409 are deliberately distinct from 503 so a client can tell the two apart. The 503 comes
from the blueprint's single `ConfirmationUnavailable` handler, which covers reads as well as
decisions.

### Surfaces

| Surface | How |
|---|---|
| Dashboard | `/dashboard/approvals` — buckets by status client-side from `fetchResourceEntities("approvals")` |
| SSE | `GET /api/approvals/events`; 30 s heartbeat, 100-frame per-client queue cap |
| PC overlay | `pc-server.approval.overlay` → TCP `overlay_approval {action}` (`pc-server/src/overlay_approval.rs`) |
| Android overlay | `AndroidApprovalCommand` / `AndroidApprovalDecision` in `protos/aegis/android_server.proto` |
| Capability surface | `ai-server.confirmation.request` (raise), `ai-server.confirmation.list` (read) |

There is **no** room-server confirmation channel and no `RoomChannel`. The retired fanout had one;
nothing replaced it.

## Capabilities AEGIS uses

| Capability | Risk label | Purpose |
|---|---|---|
| `ai-server.confirmation.request` | `low` | Raise a confirmation. Only `summary` is required. |
| `ai-server.confirmation.list` | `low` | Read the queue — by id, or filtered by `status` (default `pending`, limit 20, max 100) |

`ai-server.confirmation.request`'s own description is the contract: *"Use this when you judge that
the user should decide for themselves… This is your own initiative, not a permission check: it
blocks nothing, nothing waits for the answer, and no other capability depends on it. **Never call
this because a manifest, a risk level or a rule says approval is required**, and never call it for
work the user has already delegated to you."*

The `risk` and `side_effects` fields on a confirmation are **descriptions AEGIS supplies about its
own intended action**. They are shown to the user and are never consulted to decide anything.

## Lifecycle

```
pending ──approve──► approved
   ├──reject──────────► rejected
   ├──cancel──────────► cancelled
   └──expire_stale()──► expired          (default TTL: 30 minutes)
```

`DEFAULT_TTL_MS` is 30 minutes. An unanswered confirmation lapses so a stale question cannot sit in
the queue looking like a decision the user still owes — AEGIS re-raises if it still matters. This
is a judgement call, not a policy.

`ConfirmationStatus` also declares `executed`, `failed` and `superseded`, and the store declares
`mark_executed()` / `mark_failed()`. **None of them is reachable today:** nothing calls those two
methods, and `core_capabilities._confirmation()` dispatches only `.request` and `.list` (the
docstring there claims AEGIS may "report an outcome" — no branch implements it). Treat `executed`
and `failed` as declared-but-unproduced. This is a known gap, not a behaviour to rely on.

## Security

Authentication and CSRF are **not** implemented in the approval blueprint. `aegis_ai.auth.session_middleware`
enforces them centrally for every `POST` (`X-CSRF-Token`) and additionally requires a **fresh
passkey** for `/approve`, `/modify-and-approve` and `/cancel`. Re-checking them per route would
duplicate — and eventually contradict — that one implementation.

| Concern | Mitigation |
|---------|-----------|
| CSRF | Per-request `X-CSRF-Token`, enforced centrally in `auth/session_middleware.py` |
| Identity | Fresh passkey required for `/approve`, `/modify-and-approve`, `/cancel` |
| ID guessing | `new_confirmation_id()` → `cfm_<uuid>` |
| Secret exposure | AEGIS supplies `preview`; the retired payload-masking layer is gone |
| External access | Dashboard binds locally; the single constraint forbids egress regardless |
| Expiry | `expire_stale()` on the 30-minute TTL; the UI disables buttons on a closed item |

> The passkey requirement is **proportionality, not a gate**: it protects the *decision surface*,
> and answering a question cannot start or block an action. See the open question in
> `IMPROVEMENT_PROPOSAL.md` about whether `reject` (the "no" answer) should require it too.

## What AEGIS cannot do

- AEGIS has **no** access to the decision endpoints. It can raise a question
  (`ai-server.confirmation.request`) and read the queue (`ai-server.confirmation.list`); it cannot
  answer one. `core_capabilities._confirmation()` dispatches only those two suffixes, and
  `tests/test_forced_gate_stays_retired.py` pins that `approve` / `reject` / `cancel` / `resolve`
  are not reachable from there.
- AEGIS cannot create a fake *decision*. The store records `decided_by`, and only
  `web/routes/approval.py` writes a terminal status — through the four decision endpoints, each
  requiring a fresh passkey.
- AEGIS cannot mark its own confirmation `executed` or `failed` either: `mark_executed()` /
  `mark_failed()` exist on the store but nothing calls them (see Lifecycle).
- AEGIS cannot use a confirmation to unblock anything. No capability depends on one.
- `PolicyEngine`'s denies are structural (`EXPLICIT_DENY_PATTERNS`), not prompt-based.
- The Support Agent does not bypass `PolicyEngine`.
