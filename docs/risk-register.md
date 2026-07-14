# AEGIS Risk Register

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

> **Last Updated**: 2026-06-12

## Risk Matrix

| Risk ID | Risk | Likelihood | Impact | Mitigation | Status |
|---------|------|-----------|--------|------------|--------|
| R-01 | Prompt injection via web pages | High | Critical | PolicyEngine structural safety, untrusted content wrapping | ✅ Mitigated |
| R-02 | Prompt injection via tool results | High | Critical | Tool results treated as data, not instructions | ✅ Mitigated |
| R-03 | Approval bypass | Medium | Critical | ApprovalStore with one-time tokens, audit logging | ✅ Mitigated |
| R-04 | External data leakage | Medium | High | External integrations default disabled, redaction | ✅ Mitigated |
| R-05 | PC误操作 (mouse/keyboard) | Medium | High | Level 2 approval required, mock only in CI | ✅ Mitigated |
| R-06 | Android误操作 (tap/swipe) | Medium | High | Level 2 approval required, password deny | ✅ Mitigated |
| R-07 | Room物理操作 (robot arm) | Low | Critical | FORBIDDEN pattern, emergency stop only | ✅ Mitigated |
| R-08 | Self-dev safety weakening | Medium | Critical | PolicyEngine DENY for modify_policy, main merge FORBIDDEN | ✅ Mitigated |
| R-09 | Memory privacy (secrets stored) | Medium | High | Scrub before storage, secrets pattern detection | ✅ Mitigated |
| R-10 | External integrations misuse | Low | High | All stubs, default disabled, approval required | ✅ Mitigated |
| R-11 | Long-running autonomy cost | Medium | Medium | Cost tracker, daily/monthly budgets | ✅ Mitigated |
| R-12 | Real LLM hallucination | High | Medium | Mock for CI, prompt safety, untrusted content wrapping | ⚠️ Partial |
| R-13 | Docker misconfiguration | Medium | Medium | Compose/Dockerfiles exist, needs full validation | Partial |
| R-14 | gRPC plaintext | Low | Medium | TLS config helper exists; gRPC integration pending | Partial |
| R-15 | Single-user credential theft | Low | High | Token-based auth, localhost binding | ✅ Mitigated |
| R-16 | Real device damage (Room) | Low | Critical | FORBIDDEN patterns, approval gates, emergency stop | ✅ Mitigated |
| R-17 | SNS/DM/email auto-send | Low | Critical | FORBIDDEN patterns, all stubs | ✅ Mitigated |
| R-18 | Purchase/payment | Low | Critical | FORBIDDEN patterns, no real payment integration | ✅ Mitigated |

## Detailed Risk Analysis

### R-01/R-02: Prompt Injection

**Threat**: Malicious web pages or tool results contain instructions that try to manipulate AEGIS.

**Mitigation**:
- PolicyEngine is structural (deterministic rules), not LLM-based
- Web content is wrapped in `wrap_untrusted_content()` before LLM sees it
- Tool results are treated as data, never as instructions
- Prompt regression pack tests injection scenarios

**Residual Risk**: New injection patterns may emerge. Prompt regression pack must be updated.

### R-03: Approval Bypass

**Threat**: Code path exists that executes Level 2+ actions without approval.

**Mitigation**:
- ToolBroker structurally enforces PolicyEngine check on ALL invocation paths
- ApprovalStore uses one-time tokens with expiration
- All approval decisions logged to audit
- No public method exists to execute without policy check

**Residual Risk**: New capability registrations must follow the pattern.

### R-08: Self-Dev Safety Weakening

**Threat**: SelfDevAgent modifies PolicyEngine or safety rules.

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
