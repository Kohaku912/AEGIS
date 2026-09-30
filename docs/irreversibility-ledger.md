# Irreversibility Ledger — Post-hoc Visibility After the Approval Gate

> **Status**: Phase 3 implemented (2026-09-27)
> **Code**: `ai-server/src/aegis_ai/irreversibility.py`, `ai-server/src/aegis_schema/safety_vocab.py`
> **API**: `GET /api/audit/irreversible`, `GET /api/audit/irreversible/occurrences`
> **Tests**: `ai-server/tests/test_irreversibility_ledger.py`, `ai-server/tests/test_safety_vocabulary.py`
> **Related**: [`GOAL-CHANGE.md`](GOAL-CHANGE.md), [`egress-gate.md`](egress-gate.md), `IMPROVEMENT_PROPOSAL.md` §9.3 Phase 3

## Why this exists

Approval was retired as a constraint. The project has exactly one constraint left —
the user's information must never be sent outside **without the user's permission** — and it is
enforced by the egress gate. **Re-scoped 2026-09-30**: the gate no longer blocks all egress; it blocks
*unpermitted* egress, so the **voluntary ask** is now part of how that constraint is satisfied (see
[`GOAL-CHANGE.md`](GOAL-CHANGE.md)).

Removing a **pre-execution gate** only works if something replaces it. The
replacement is **post-hoc visibility**: AEGIS may do irreversible things, but
afterwards it must be possible to enumerate and trace them.

This ledger blocks nothing. It answers two questions:

| Question | Source | Why it cannot drift |
|---|---|---|
| Which capabilities *can* do something that cannot be taken back? | the manifests | derived, not hand-maintained — see the conformance test below |
| Which of those *actually ran*? | the audit log, joined on `capability_id` | the audit log already recorded the id, so nothing needed instrumenting |

## The vocabulary

Declared **once**, in `aegis_schema/safety_vocab.py`. Six manifest fields:

| Field | Vocabulary | Meaning |
|---|---|---|
| `ownership_scope` | `aegis` \| `user` \| `system` \| `external` \| `unknown` | whose state the operation touches |
| `reversibility` | `fully_reversible` \| `recoverable` \| `difficult` \| `irreversible` \| `unknown` | how hard it is to undo |
| `destructive_effects` | see below | *what* it destroys, as groupable buckets |
| `data_loss_risk` | `none` \| `low` \| `medium` \| `high` \| `unknown` | probability data is destroyed |
| `active_work_loss_risk` | `none` \| `low` \| `medium` \| `high` \| `unknown` | probability in-flight work is destroyed |
| `blast_radius` | `single` \| `bounded` \| `bulk` \| `system_wide` \| `unknown` | how far one operation reaches |

`destructive_effects` is a controlled vocabulary:
`file_delete`, `data_overwrite`, `message_send`, `purchase`, `account_change`,
`permission_change`, `process_terminate`, `device_state_change`, `memory_delete`,
`schedule_change`, `remote_transmit`, `unknown`.

It exists because the manifests' other prose field, `risk.side_effects`, is
free-form — 44 distinct values across the builtin set (`discord_voice_call_join`,
`sends HTTP request`, `ir_transmit`, …) — which cannot be grouped. The ledger's
headline view is "delete / send / purchase", and that needs buckets.

### `unknown` is not a safe-looking default

Every field defaults to `unknown` when unset. Previously the readers fell back to
`blast_radius="single"`, `data_loss_risk="none"`, `reversibility="reversible"` —
values that read as *positive claims of harmlessness* about a capability nobody
had described. `unknown` says only what is true.

For `destructive_effects`, an **absent key** maps to `["unknown"]` while a
**declared `[]`** means "destroys nothing". Collapsing those two would let an
unclassified capability read as harmless.

### Two vocabularies, one direction

`reversibility` is declared at two levels of precision, because it is consumed by
two different audiences:

* **manifests** use the precise 5-value set (`fully_reversible`, `recoverable`, …)
* **delegation rules** are written against a coarser 4-value set
  (`reversible`, `difficult`, `irreversible`, `unknown`)

`normalize_reversibility()` is the only permitted mapping between them, and it is
applied on **both** sides of the comparison in
`DelegationPolicyStore.evaluate()`.

> **This was a real bug.** The two sets used to be declared separately, as bare
> comments. The delegation policy matches dimensions by exact string equality, so
> a manifest declaring `recoverable` put `recoverable` into the delegation
> context, which never equalled a rule's `reversible` — and a `forbidden` rule
> silently stopped firing. No error, no log. Regression tests:
> `test_manifest_spelling_still_matches_a_rule_written_as_reversible`,
> `test_rule_written_with_the_manifest_spelling_also_matches`.

## Classification conventions

Applied to every builtin manifest, 2026-09-27; re-verified 2026-09-28:

1. If the declared operation has a deterministic effect, classify that effect.
2. If the effect depends on caller-supplied arguments, classify the **worst case
   reachable through the declared input schema**. `pc-server.shell.execute` takes
   an arbitrary `command`, so its worst case is `irreversible` / `system_wide` /
   `data_loss_risk=high`.
3. Use `unknown` when even the worst case cannot be bounded from the manifest —
   i.e. the manifest itself declares its intent ambiguous. Exactly one capability
   qualifies: `browser-server.page.browse` ("Legacy unspecialized browser
   automation… because intent is ambiguous").
4. `irreversible` must not be paired with `data_loss_risk="none"`: an
   irreversible operation has to say what is lost. Enforced by
   `test_irreversible_manifests_declare_what_is_lost`.
5. A read that *consumes* what it reads is not `read_only` and not
   `fully_reversible`. `pc-server.personal_data.drain` is the case that forced this
   rule to be written down; see "Resolved 2026-09-28" below.

### What the builtin set looks like

| Reversibility | Count |
|---|---|
| `fully_reversible` | 65 |
| `recoverable` | 38 |
| `difficult` | 21 |
| `irreversible` | 3 |
| `unknown` | 1 |

128 manifests, as of 2026-09-28. Two arrived with Phase 5a
(`ai-server.confirmation.request` / `.list`, both `fully_reversible`), and
`pc-server.personal_data.drain` moved `fully_reversible` → `recoverable` once the
Rust implementation was actually checked.

The three irreversible capabilities:

* `pc-server.shell.execute`
* `pc-server.shell.powershell`
* `pc-server.system.empty_recycle_bin`

Note `purchase` appears in the vocabulary but **no capability declares it**.
Purchases are a structural `DENY` in the policy engine, not a callable
capability — so there is nothing to classify.

## Reading the ledger

```bash
# Inventory (worst first), with tallies and the delete/send/overwrite buckets
curl -s 'http://localhost:8090/api/audit/irreversible' | jq '.by_destructive_effect'

# Only the three that cannot be undone, excluding anything unspecified
curl -s 'http://localhost:8090/api/audit/irreversible?threshold=irreversible&include_unknown=false'

# What actually ran, joined against the audit log
curl -s 'http://localhost:8090/api/audit/irreversible/occurrences?limit=50' | jq '.entries'
```

Both endpoints are **GET-only** — pinned by `test_the_ledger_api_is_read_only`.
The ledger observes; it cannot change a decision.

The same annotations are also attached to `PolicyResult` in `ToolBroker.execute()`
(via `annotate_policy_result`), so an audit entry describes *why* an action was
risky without having to re-resolve the manifest later, and are exposed on the
existing `CapabilityCatalog.risk_details()` surface.

## Guard against drift

`test_every_manifest_declares_the_safety_annotation_vocabulary` fails if any
manifest omits one of the six keys or uses an out-of-vocabulary value. A newly
added capability therefore cannot silently escape the ledger — it has to be
classified.

## Known behaviour change

Because `ownership_scope`, `reversibility` and — since 2026-09-28 —
`content_sensitivity` now read `unknown` when undeclared instead of
`aegis` / `reversible` / `normal`, a **dimension-scoped delegation rule no longer
fires for an operation whose dimension is unknown**. `DelegationPolicyStore.evaluate()`
falls through to `auto_allowed` when no rule matches.

In practice this only affects operations whose manifest the catalog cannot
resolve: all 128 builtin manifests declare the other five fields, and
`content_sensitivity` is undeclared *always*, because it is not a manifest field
at all (see below). It is pinned by
`test_undeclared_reversibility_no_longer_matches_a_reversible_rule` and
`test_undeclared_content_sensitivity_no_longer_matches_a_normal_rule`, so the
behaviour cannot drift unnoticed.

`audience` is deliberately left out of that list: its default is `private`, which
is the *conservative* end of its range rather than a claim of harmlessness.

## Deferred

* The dashboard UI for the ledger (Phase 5).
* The five delegation *matching* dimensions are barely reachable from the
  capability surface: `ai-server.delegation_policy.upsert` exposes only
  `operation_category` in its `input_schema`. A rule scoped by `scope`,
  `audience`, `content_sensitivity` or `reversibility` can only be created through
  `DelegationPolicyStore.upsert_rule()` directly. Worth revisiting together with
  the forced-gate rule removal (Phase 5b), since those rules are the thing being
  removed.

### Resolved 2026-09-28

Both items that used to sit here were verified against the implementation, then
fixed:

* **`content_sensitivity` was fabricated, not read.** `autonomous_loop` did
  `getattr(manifest, "content_sensitivity", "") or "normal"`, but
  `CapabilityManifest` has no such field — it is a *delegation* dimension, so that
  read could never return anything and the expression always produced `"normal"`.
  That is an unfounded claim of non-sensitivity: the same class as the
  `unknown`-is-not-a-safe-default rule above. `autonomous_loop`,
  `DelegationContext` and `DelegationPolicyStore._normalize_context` now all read
  `unknown` when nothing declares a value. Pinned by
  `test_delegation_context_never_fabricates_a_content_sensitivity`,
  `test_undeclared_content_sensitivity_is_unknown_not_normal` and
  `test_undeclared_content_sensitivity_no_longer_matches_a_normal_rule`.
* **`pc-server.personal_data.drain` did consume its buffer.**
  `pc-server/src/personal_data.rs` implements `drain()` as
  `guard.buffer.drain(..).collect()`, so the returned events are the only copy.
  The manifest moved from `read_only` / `fully_reversible` / no side effects to
  `operation_category="personal_data"`, `reversibility="recoverable"`,
  `data_loss_risk="low"`, `destructive_effects=["data_overwrite"]` — the same shape
  as `pc-server.clipboard.set`, where content leaves and the previous contents are
  gone. The new `operation_category` was kept outside the delegation category
  vocabulary on purpose, so no delegation rule changes which capabilities it
  matches. Pinned by `test_drain_does_not_claim_to_be_read_only` and
  `test_drain_classification_still_matches_the_rust_implementation`.
