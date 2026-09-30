# AEGIS Risk Register

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Consequently:
> - **R-03 (Approval bypass) is retired** as a risk — replaced by **R-19 (Egress gate bypass)**.
> - **R-04 (External data leakage) is elevated to the single highest-priority risk** — it is now the
>   enforcement of the *only* constraint.
> - "Level 2 approval required" mitigations below become **risk annotations**, not gates.
> See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

## 2026-07-14 Deployment Truth

- Production auth is passkey-only with CSRF and fresh-auth gates; access tokens
  are bootstrap/recovery only.
- Docker services bind privately and rotate logs. Full acceptance still depends
  on all real E2E checks passing.
- gRPC TLS is not fully integrated. Plaintext gRPC is permitted only inside
  Tailscale/private network boundaries and must never be directly published.
- Room is `UNCONFIGURED/DISABLED` until Orange Pi uses a real provider; mock
  Room results are rejected as production success.
- Dashboard/Android/PC/OS notifications exist. LINE, Discord, SMTP, and voice
  external senders remain disabled and deferred from v1.

> **Last Updated**: 2026-09-27

## Risk Matrix

| Risk ID | Risk | Likelihood | Impact | Mitigation | Status |
|---------|------|-----------|--------|------------|--------|
| R-01 | Prompt injection via web pages | High | Critical | PolicyEngine structural safety, untrusted content wrapping | ✅ Mitigated |
| R-02 | Prompt injection via tool results | High | Critical | Tool results treated as data, not instructions | ✅ Mitigated |
| ~~R-03~~ | ~~Approval bypass~~ | — | — | **Retired** — approval is no longer a constraint. Replaced by R-19. | ⛔ N/A |
| R-04 | **Unpermitted external data leakage (THE single constraint)** | Medium | **Critical** | Egress gate (`aegis_ai/egress/`) — **re-scoped 2026-09-30**: it forbids *unpermitted* user-information egress, and outbound connections are allowed; `external_llm_allowed=false` by default, i.e. permission is required | 🔄 Phase 1 |
| R-05 | PC误操作 (mouse/keyboard) | Medium | High | Risk annotation (was "Level 2 approval"); mock only in CI | ✅ Mitigated |
| R-06 | Android误操作 (tap/swipe) | Medium | High | Risk annotation; password deny | ✅ Mitigated |
| R-07 | Room物理操作 (robot arm) | Low | Critical | FORBIDDEN pattern, emergency stop only | ✅ Mitigated |
| R-08 | Self-dev safety weakening | Medium | Critical | PolicyEngine DENY for modify_policy, main merge FORBIDDEN (dev-flow rule) | ✅ Mitigated |
| R-09 | Memory privacy (secrets stored) | Medium | High | Scrub before storage, secrets pattern detection | ✅ Mitigated |
| R-10 | External integrations misuse | Low | High | Real senders behind the **egress gate**, all locks closed by default | ✅ Mitigated |
| R-11 | Long-running autonomy cost | Medium | Medium | Cost tracker, daily/monthly budgets | ✅ Mitigated |
| R-12 | Real LLM hallucination | High | Medium | Mock for CI, prompt safety, untrusted content wrapping | ⚠️ Partial |
| R-13 | Docker misconfiguration | Medium | Medium | Compose/Dockerfiles exist, needs full validation | Partial |
| R-14 | gRPC plaintext | Low | Medium | TLS config helper exists; gRPC integration pending | Partial |
| R-15 | Single-user credential theft | Low | High | Token-based auth, localhost binding | ✅ Mitigated |
| R-16 | Real device damage (Room) | Low | Critical | FORBIDDEN patterns, emergency stop | ✅ Mitigated |
| R-17 | SNS/DM/email auto-send | Low | Critical | Egress-gate permission required before any send; note `send_dm`/`send_sns` are **not** in `EXPLICIT_DENY_PATTERNS` | ✅ Mitigated |
| R-18 | Purchase/payment | Low | Critical | FORBIDDEN patterns, no real payment integration | ✅ Mitigated |
| **R-19** | **Egress gate bypass** | Medium | **Critical** | Single gate + startup assertion + egress regression tests (`--fail-on-empty`, pass^k) | 🔄 Phase 1 |

## Detailed Risk Analysis

### R-04: External Data Leakage — the single constraint

**Threat**: Any code path transmits user data, context, or knowledge derived from them to an external
service (cloud LLM, web search, cloud STT/TTS, webhook, third-party API) **without the user's
permission**.

**Mitigation**:
- Single **egress gate** (`ai-server/src/aegis_ai/egress/`) — **re-scoped 2026-09-30**: it denies
  *unpermitted user-information* egress; outbound connections are allowed
- `external_llm_allowed` and `web_search_allowed` default to **False**, i.e. permission is required
- Startup assertion: if the gate is not structurally in place, AEGIS **refuses to start**
- Local LLM path (Ollama) must be functional so cloud is never a functional prerequisite
- **Unpermitted egress has no exception** — the old "explicitly configured" escape hatch is removed;
  the user's own permission is the one route out

**Residual Risk**: A new dependency may open a socket outside the gate. Egress regression tests and
the "ineffective flag" detector must be extended whenever a dependency is added.

### R-19: Egress Gate Bypass

**Threat**: A component (Agent, RemoteBackend, plugin, capability) opens an outbound connection
without going through the gate — e.g. direct `requests`/`httpx`/`socket`, `subprocess` with a network
tool, or a recomputed state flag.

**Mitigation**:
- Gate is the only permitted outbound path; ToolBroker routes through it
- Direct `subprocess.run(shell=True)`, direct capability invocation, and direct socket clients are denied
- Audit records every attempted transmission
- Egress regression tests must fail if any path leaks

**Residual Risk**: New capability registrations must follow the pattern.

### R-01/R-02: Prompt Injection

**Threat**: Malicious web pages or tool results contain instructions that try to manipulate AEGIS.

**Mitigation**:
- PolicyEngine is structural (deterministic rules), not LLM-based
- Web content is wrapped in `wrap_untrusted_content()` before LLM sees it
- Tool results are treated as data, never as instructions
- Prompt regression pack tests injection scenarios

**Residual Risk**: New injection patterns may emerge. Prompt regression pack must be updated.

### R-08: Self-Dev Safety Weakening

**Threat**: SelfDevAgent modifies PolicyEngine or the egress gate.

**Mitigation**:
- `dev.merge_to_main` is FORBIDDEN (explicit deny pattern)
- `dev.modify_policy.*` is FORBIDDEN
- SelfDevAgent can only create PRs, not merge
- All self-dev changes require human review via PR

**Residual Risk**: SelfDevAgent could create PRs that weaken safety. Human review is the gate.

### R-12: Real LLM Hallucination

**Threat**: Real LLM fabricates sources, makes incorrect claims, or follows injected instructions.

**Mitigation**:
- Mock LLM used for all CI tests
- `@pytest.mark.real_llm` marker for optional real LLM tests
- Prompt safety patterns detect common injection attempts
- Untrusted content wrapping for web/browser data

**Residual Risk**: Real LLM behavior is non-deterministic. Hallucination is inherent.

### R-14: gRPC Plaintext

**Threat**: gRPC traffic intercepted on network.

**Mitigation**: TLSConfig exists, but it is not fully integrated with all gRPC server/client paths.

**Action**: Implement TLS before any network-exposed deployment.

## Risk Review Schedule

| Review | Frequency |
|--------|-----------|
| Safety regression tests | Every CI run |
| Prompt regression tests | Every CI run |
| Risk register update | Monthly or after major changes |
| ADR review | Before any architectural change |
