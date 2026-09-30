# Egress Gate — Enforcement of the Single Constraint

> **Status**: Phase 1 implemented, Phase 4 test discipline in place (2026-09-27)
> **Code**: `ai-server/src/aegis_ai/egress/`
> **Tests**: `test_egress_gate.py` (53) · `test_egress_closure.py` (36) ·
> `test_egress_reliability.py` (10) · `test_ineffective_flags.py` (41) ·
> `test_local_llm_path.py` (25) — 165 marked `egress`
> **CI**: `scripts/test-ai-server.ps1`
> **Related**: [`GOAL-CHANGE.md`](GOAL-CHANGE.md), [`security.md`](security.md), `AGENTS.md` Security Policy

## Why this exists

AEGIS has exactly **one constraint**:

> **The user's information must never be sent outside without the user's permission.**

**Re-scoped 2026-09-30** (owner): this used to read "must never leave the local environment", with no
consent exception. Outbound **connections** are now allowed; what the gate still forbids is
**unpermitted** disclosure of user information. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

Everything else — approval, reversibility, policy, reliability-proof — is no longer a constraint.
That makes the constraint *load-bearing*: if egress is not checked, AEGIS has **no
constraint at all**. The egress gate is that check.

## Design

The gate is a single object through which **all** outbound transmission must pass. **Local**
destinations pass. **External** destinations pass when the request carries no user information, or when
the user has permitted that egress; otherwise they are denied.

```
component → EgressGate.require(request) → ALLOW (local)
                                        | ALLOW (external, no user data)
                                        | ALLOW (external, user-permitted)
                                        | DENY  (external, fail closed)
                     │
                     └── every decision → AuditManager (post-hoc verification)
```

### Five principles

1. **Deny by default.** External destinations are refused.
2. **Local is allowed.** AEGIS is a multi-device system; its own LAN *is* the local environment.
   Loopback, RFC1918, link-local, Tailscale CGNAT (`100.64.0.0/10`), IPv6 ULA (`fc00::/7`), loopback
   hostnames, `.local` mDNS names, single-label LAN hostnames, and unix sockets are local.
3. **Fail closed.** If a destination cannot be classified, the request is denied.
4. **Permission, not a wall** (re-scoped 2026-09-30). The constraint is now *unpermitted* egress, so
   the intended mechanism is the **voluntary ask**, not an absolute refusal. ⚠️ **The code still
   enforces the pre-re-scope form**: external egress requires **all three** — the master switch, the
   matching feature flag, **and** an allowlist entry. Wiring the permission check is open work; until
   it lands this list describes current behaviour, not the target.
5. **Auditable.** Every decision is recorded so the constraint can be verified after the fact.

### Three locks

An external destination is permitted only when **all** of these hold:

| Lock | Setting | Default |
|---|---|---|
| Master switch | `privacy.external_egress_allowed` | `False` |
| Feature flag | `privacy.external_llm_allowed` / `privacy.web_search_allowed` / `voice.external_voice_api_allowed` | `False` |
| Allowlist | `privacy.egress_allowed_hosts` | `[]` |

A flag alone never opens egress. This is deliberate: it prevents the "declared but ineffective"
class of bug that previously affected `web_search_allowed` (defined in settings, never read).

> **The allowlist lock was itself dead until Phase 4.** `EgressGate` only ever read the
> `allowed_hosts` constructor argument, and `runtime.py` passes only a settings store — so
> `privacy.egress_allowed_hosts` had **no reader anywhere in `src/`** and could not open egress
> from `settings.json`. `EgressGate._settings_allowed_hosts()` now reads it and unions it with the
> constructor value, so `_evaluate()` and `status()` both honour the configured lock.
> The ineffective-flag detector (`tests/test_ineffective_flags.py`) is what surfaced this.

### Purpose → flag mapping

| Purpose prefix | Flag |
|---|---|
| `llm.*` | `privacy.external_llm_allowed` |
| `web.*`, `search.*` | `privacy.web_search_allowed` |
| `voice.*` | `voice.external_voice_api_allowed` |
| anything else | denied even when the master switch is on |

## API

```python
from aegis_ai.egress import EgressGate, EgressRequest, EgressDenied, get_egress_gate

gate = get_egress_gate()

# Raise on denial:
gate.require(EgressRequest(
    destination="https://api.deepseek.com/v1/chat/completions",
    purpose="llm.chat",
    component="llm.router",
    data_summary="chat prompt + memory context",
))  # raises EgressDenied while egress is closed

# Or check without raising:
if gate.allow(EgressRequest(destination=url, purpose="web.search", component="x")):
    ...
```

Helpers: `is_local_destination(dest) -> bool`, `classify_destination(dest) -> "local"|"external"|"unknown"`.

## Startup assertion

`verify_egress_configuration()` runs at composition-root startup (before any network-capable object
is built):

- **Violations** (fatal in `fail` mode): a flag or the allowlist is open. AEGIS refuses to start.
- **Readiness warnings** (non-fatal by default): the local LLM path is incomplete (`llm.yaml` is not
  `mode: local`, or vision has no local profile). Nothing is transmitted, but AEGIS would degrade to
  Mock. Escalate with `require_local_llm=True`.

Control with `AEGIS_EGRESS_STRICT=fail|warn` (default `fail`).

## Guarded egress points

| Point | File | Guard |
|---|---|---|
| LLM (factory) | `llm/factory.py` | refuses to construct a cloud provider; falls back to local Ollama, then Mock |
| LLM (gateway — L1/L2/L3) | `llm/gateway.py` | `_get_provider_for_profile` consults the gate before constructing; degrades to local/Mock |
| LLM (routing) | `llm/router.py` | `_select_provider` consults the gate before choosing a cloud provider |
| Web search | `integrations/duckduckgo_search.py` | `search()` / `news()` return a denied response |
| Text-to-speech | `integrations/tts_service.py` | `synthesize()` refuses (edge-tts is a cloud service) |
| Webhooks | `integrations/webhook_sender.py` | `send()` refuses and audits |
| AGORA | `integrations/agora/agora_client.py` | `_request()` returns `egress_denied` |
| OpenTelemetry | `observability/otel_tracing.py` | non-local OTLP endpoint is refused; Console fallback |
| Weather / briefing | `briefing/provider.py` | `_weather_egress_allowed()` — coordinates are not sent when closed |
| OpenHands remote | `agents/backends/openhands/workspace.py` | `_default_http_post()` raises `RemoteAPIError` when denied |
| Server executor (HTTP) | `server_executor.py` | `_execute_http()` returns `EGRESS_DENIED` for a non-local endpoint |
| Server executor (PC TCP) | `server_executor.py` | `_execute_pc_tcp()` refuses a non-local PC Server host |
| Email (SMTP) | `personal_ai/social_proxy.py` | `_send_email()` returns `EGRESS_DENIED` |

### Browser Server (separate distribution)

`browser-server` does not depend on `aegis_ai`, so it carries its own gate at
`browser-server/src/aegis_browser/egress.py`. **The two copies are meant to agree — and
they had drifted.** The browser copy was missing the IPv6 handling in `_extract_host`
and the `":" not in host` guard on the single-label rule, so it called `::1` external
while `http://[::1]/` was local: one host, two answers. Ported 2026-09-28. If you change
one, change the other.

| Point | File | Guard |
|---|---|---|
| Browser LLM | `browser_use_agent.py` | refuses a non-local LLM `base_url` before constructing the model |
| Navigation, *declared* targets | `browser_use_agent.py` | `_navigation_egress_denied()` refuses the task before a browser is launched |
| Navigation, *followed* links and redirects | `browser_use_agent.py` | `BrowserProfile.allowed_domains`, built by `egress.navigation_allowlist()`; browser-use's `SecurityWatchdog` vetoes `NavigateToUrlEvent`, re-checks on `NavigationCompleteEvent` and closes offending tabs |
| Domain check | `safety_boundary.py` | `check_domain()` consults the gate — but **nothing calls it**; the row above is what actually runs |

> **The per-navigation gate is pattern-based, and coarse on purpose.** browser-use matches
> with `fnmatch`, so the obvious `192.168.*` would also admit the publicly resolvable
> `192.168.evil.com`. Private-IP destinations are therefore admitted only when the task
> *declares* them, which appends the literal as an exact pattern.
> `browser-server/tests/test_navigation_allowlist.py` pins the direction: no pattern may
> admit a host the predicate calls external, and the allowlist is never empty (browser-use
> reads an empty list as "allow everything").

### Deliberate differences between the two gate copies

Not drift, and not to be "aligned" by accident. **Do not add tables to the two sections
above:** `tests/test_egress_closure.py` reads the second cell of every table row inside a
guarded-point section, so any table placed there is parsed as a guarded point. That is how
this section came to exist.

| Aspect | ai-server | browser-server | Why |
|---|---|---|---|
| Local suffixes | `.local` | `.local`, `.localhost`, `.internal`, `.lan`, `.home` | a browser meets RFC 6762/8375 private-use names far more often |
| IP literal test | `is_unspecified` plus explicit RFC1918/CGNAT networks | `is_private` plus CGNAT | `is_private` also covers reserved blocks (`198.18/15`, `240/4`), which likewise never leave the environment |

### Not yet guarded (tracked)

- LINE / Discord senders (currently stubs)
- internal health checks (`status/status_manager.py`) and LAN discovery
  (`net/endpoint_resolver.py`) — loopback/LAN only, inside the environment by construction
- `llm/providers/typesafe_provider.py` — reachable only via the factory/gateway, both guarded

## Verifying the constraint

```bash
# Everything: the full suite + the egress floor + the mutation check.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/test-ai-server.ps1

# Just the egress suite, with the --fail-on-empty floor:
cd ai-server
../.venv/Scripts/python.exe -m pytest -m egress --require-egress-tests=160 -q

# Prove the suite fails when the gate is deliberately broken:
../.venv/Scripts/python.exe scripts/verify_egress_tests_catch_regression.py

cd ../browser-server
../.venv/Scripts/python.exe -m pytest -m egress --require-egress-tests=65 -q
```

### The five test layers

| Layer | File | What it establishes |
|---|---|---|
| Gate semantics | `test_egress_gate.py` | local/external classification, deny-by-default, the three-lock requirement, fail-closed on unknown destinations, audit recording, the startup assertion, the LLM factory **and gateway** refusing cloud providers, dead-local-endpoint degradation |
| Closure | `test_egress_closure.py` | **every** point in the guarded table above is driven through its own entry point and refuses — plus a drift guard that keeps this table and the tests in sync |
| Reliability (pass^k) | `test_egress_reliability.py` | the block holds on **every** trial, not merely once; repeated local traffic never erodes it |
| Ineffective flags | `test_ineffective_flags.py` | every settings flag has a reader; every lock is read by the enforcement point; flipping a lock changes a decision |
| Local LLM path | `test_local_llm_path.py` | local mode resolves locally for every profile, a dead endpoint degrades to Mock, and the generation path consults the gate about **no** external host |

### Three disciplines that keep those tests honest

1. **`--fail-on-empty`.** `pytest -m egress --require-egress-tests=N` fails the session when fewer
   than N `egress`-marked tests were collected (implemented in `ai-server/tests/conftest.py`, and
   mirrored in `browser-server/tests/conftest.py`). Without it, a rename, a marker typo, or a
   narrowed `-k` can leave the selection empty while pytest reports the rest of the suite as
   passing — the constraint would silently stop being checked.
2. **pass^k.** A block that holds 19 times out of 20 is not a constraint. `test_egress_reliability.py`
   runs 24 external destinations × 20 trials and requires zero leaks, and it asserts the trial count
   so a shrinking destination list cannot quietly turn pass^k into pass^0.
3. **Mutation check.** `scripts/verify_egress_tests_catch_regression.py` runs the suite twice — once
   normally (must pass), once with `EgressGate._evaluate` forced to ALLOW (must fail, currently
   38 tests). A suite that has never been observed failing is an assumption, not a control. The
   mutation is a process-local monkeypatch, so nothing on disk is modified.

Each closure test also asserts that the underlying transport was never touched (the transports are
replaced with loud failures), because "the response says denied" and "nothing actually left" are
different claims — and Phase 1 found a guard (`browser-server`'s `check_domain()`) that existed but
was never called, which only a behavioural test can catch.
