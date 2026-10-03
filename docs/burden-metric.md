# Burden Metric — the instrument for the north star

> **Owner definition (2026-10-03).** The burden metric is **judged by the judgment LLM**, and the
> user is **asked to confirm or correct it periodically**. It is not a formula over the decision
> log, and no new instrumentation is required. This closes **`PROJECT_STATUS_REVIEW.md` §3.1 hole
> 3** — the last open north-star hole. Recorded in `DELEGATION.md` §4 item 8.
>
> ⚠️ **Measured 2026-10-03 — implemented but *not wired*.** `aegis_ai/burden/metric.py` exists and
> is pinned by `tests/test_burden_metric_is_judged.py`, but **nothing in `src/` constructs
> `BurdenMetric`** (the only mentions are the package's own two modules). So the metric is
> *definable and testable* today and *not yet produced* at runtime — the same shape as the egress
> grant source (`docs/permissions.md`, item 22). Wiring it into the composition root and giving it
> the loop's cadence hook is the remaining step.

> **Status**: Implemented (module), **not wired**
> **Related**: `docs/GOAL-CHANGE.md`, `PROJECT_STATUS_REVIEW.md` §3.1, `DELEGATION.md` §4 item 8

## Why it is a judgement, not a formula

§3.1 hole 3 was the last north-star hole: *"how much lighter did AEGIS make the user's life?"*
`DECISION_DRAFTS.md` §B-5 answered it with *"derive it from the existing decision log; no new
instrumentation is needed"*. Measured 2026-10-01, that premise holds for **one of the three**
sub-metrics it proposed and fails for the other two:

| Sub-metric | Computable? | Why |
|---|---|---|
| interruptions per day | ✅ | `AuditEntry.timestamp_ms` + the `interruption_decision` action |
| **the fraction the user responded to** | ❌ | the response lives in `NotificationManager._notifications`, an **in-memory dict**; nothing persists it, and `dismiss(notification_id)` cannot tell the user's dismissal from the system's own |
| median cost of accepted interruptions | ⚠️ 1 of 5 | computable only over the subset whose `_decision(...)` path carries a `utility` breakdown |

Those structural facts are still true and still pinned by
`tests/test_burden_metric_has_no_instrument.py` — that file is a *measurement*, and the owner's
decision did not invalidate it. What changed is the **conclusion**: rather than persist a response
and instrument four hard gates, put the judgement where AEGIS already puts judgements — **the LLM**
— and make **the user the check on it**.

## The judgement

`BurdenMetric(llm).assess(window_start_ms=…, window_end_ms=…, activity=[…])` returns a
`BurdenAssessment`:

- `score` — `0.0` (removed nothing the user would have had to do) … `1.0` (removed essentially all
  of it), or `None` when the judgement failed outright;
- `summary` — one sentence the user will read;
- `evidence` — short strings, each naming one concrete thing AEGIS did and the burden it stood in for;
- `judged_by_profile` / `judged_by_provider` / `judged_by_model` — see below;
- `error` — non-empty when the judgement failed.

The **activity is given, never gathered here**: the caller assembles the period and passes it in.
So there is no arithmetic over the decision log inside the module to go stale, and the module
imports **neither `aegis_ai.audit` nor `aegis_ai.confirmation`** (both absences are pinned).

The profile is **`decision`** (`config/llm.yaml`), the same profile the autonomous loop already
passes at its own judgement call sites — the burden metric is judged by the same mind that decides
what AEGIS should do, rather than by a second, private one.

### A failed judgement is recorded, not raised

`assess()` never raises for an LLM failure: a provider that throws, reports failure, or returns
non-JSON yields an assessment with `error` set and `score=None`. **A metric that throws is a metric
nobody can aggregate.**

### The label names the request; the fields name the resolution

Under the shipped allowlist (`privacy.egress_allowed_hosts: ["api.typesafe.ai"]`), a `decision`-profile
call to any other declared destination is **denied by the gate and degrades to Mock**. A judgement
from Mock is canned text and says **nothing** about the user's life. So the assessment carries the
**resolved** `judged_by_provider` / `judged_by_model` (read from `provider_used` / `model_used`),
and:

```python
@property
def is_trustworthy(self) -> bool:
    return not self.error and self.judged_by_provider not in ("", "mock")
```

**Callers must not ask the user about an assessment that is not trustworthy.**

## The periodic check on the judgement

The LLM's number is the *machine's* view; **the user's answer is the ground truth**. The two are
kept apart on purpose.

- **Cadence** — `due_for_user_check(last_ask_ms=…, now_ms=…)`, with `DEFAULT_ASK_INTERVAL_MS = 7 days`.
  A week is long enough that the answer is about a *period* rather than a moment, and short enough
  that a wrong judgement cannot stand for a month. The north star is **not asking too much**, so the
  interval is a **floor** on how often, not a target. `last_ask_ms=None` (a first run) is **not** due
  — the first judgement should exist before the user is asked about one.
- **The ask belongs to the asker.** `build_user_question(assessment)` returns a **dict of fields**
  for `ConfirmationStore.request(...)`; it does **not** raise the confirmation itself. `CoreCapabilities`
  is the only caller of `ConfirmationStore.request`, and the burden module must not become a second
  approval surface. `test_burden_metric_is_judged.py` asserts every returned key is one
  `ConfirmationRequest` actually declares, so the two cannot drift apart.
- **The answer never overwrites the number.** `apply_user_verdict(assessment, verdict=…, note=…)`
  records `confirmed` / `corrected` **beside** the LLM's `score`, never over it. The **gap between
  the two is the signal worth watching**; overwriting one with the other would destroy exactly that.
  An unknown verdict raises `ValueError`.

Verdict vocabulary: `unasked` (every fresh assessment) · `confirmed` · `corrected`.

## What remains

1. **Wire it.** Construct `BurdenMetric` in the composition root (`runtime.py`) and drive it from
   the autonomous loop, reusing the loop's existing periodic-hook pattern
   (`_health_check_interval_ms` / `_last_health_check_ms`) for the ask cadence.
2. **Persist `last_ask_ms`** so the cadence survives a restart, and so `due_for_user_check` is not
   always `False`.
3. **Feed `activity`** from the period's real work — the loop is where that is known.
