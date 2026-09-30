# Security — Local Network Authentication & Protection

> ⚠️ **Goal change (2026-09-27), re-scoped 2026-09-30**: the only constraint is now **"the user's
> information is not sent outside without the user's permission."** Outbound connections are allowed;
> *unpermitted* disclosure is not. Approval, reversibility, policy, and reliability-proof are no
> longer constraints. The enforcement point is the **egress gate**
> (`ai-server/src/aegis_ai/egress/`), which denies unpermitted user-information egress.
> See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

> **Status**: ⚠️ **Corrected 2026-10-01.** This page used to document six classes as if they were
> wired. **Measured: nothing outside `aegis_ai/security/` imports that package** — the whole
> package is a dead end. `tests/test_security_package_stays_unwired.py` pins the measurement.
> **Related**: `docs/local-network-security.md`, `docs/architecture.md` §7

## What is actually enforced

The live authentication system is **`aegis_ai/auth/`** (passkey-based; it has its own `csrf.py`),
installed by `aegis_ai/web/auth.py` via `install_passkey_auth`. The egress gate
(`aegis_ai/egress/`) is the constraint enforcement point.

| Property | Enforced by | Status |
|---|---|---|
| Passkey authentication / session middleware | `aegis_ai/auth/` | ✅ live |
| CSRF protection for web routes | `aegis_ai/auth/csrf.py` (`csrf_valid`) | ✅ live |
| Unpermitted user-information egress | `aegis_ai/egress/` | ✅ live |
| Token auth for server-to-server calls | — | ❌ not wired (see below) |
| Rate limiting | — | ❌ not wired |
| Origin checking | — | ❌ not wired |
| gRPC TLS | — | ❌ not wired (Tailscale boundary instead) |

## `aegis_ai/security/` — declared but not effective

`aegis_ai/security/` defines six classes and one helper. **No file outside the package imports it,
and none of these names is used outside it** (measured 2026-10-01 across ai-server, pc-server,
browser-server, room-server, android-server, the Python SDK, scripts and web-ui). The only non-self
references anywhere are `logging.getLogger("aegis_ai.security.…")` strings inside the package, its
own `__init__.py` re-exports, and this page.

| Module | Provides | Importers outside the package |
|---|---|---|
| `auth.py` | `LocalTokenAuth`, `generate_token`, `hash_token` | none |
| `tokens.py` | `TokenStore` | none |
| `csrf.py` | `CSRFProtection` | none (superseded by `aegis_ai/auth/csrf.py`) |
| `rate_limit.py` | `RateLimiter` | none |
| `origin.py` | `OriginChecker` | none |
| `tls.py` | `TLSConfig`, `generate_self_signed_cert` | none |
| `tls_config.py` | `TLSConfig` (`from_env` / `configure_server` / `configure_channel`) | none |

Two further notes on TLS specifically:

- **Two `TLSConfig` classes** exist, with incompatible APIs. `security/__init__.py` re-exports only
  `tls.py`'s; `tls_config.py` is imported by nothing at all — yet it is the one whose
  `configure_server` actually calls `add_secure_port`.
- **No live server binds a secure port.** `add_secure_port` is called only inside
  `tls_config.configure_server`; `grpc_server.serve` and `room-server` both use
  `add_insecure_port`. So gRPC stays plaintext, and the local hop is protected by the Tailscale /
  private-network boundary instead (see `docs/status.md`).

**Recorded, not wired, not deleted.** Wiring `security/` would re-introduce a *second* auth/CSRF
implementation alongside the live `aegis_ai/auth/`; deleting a whole documented package is an owner
judgement. The decision is carried in `DELEGATION.md` §4.

## Security Principles

- **Localhost only** by default — no external access
- **Passkey auth** for the web UI (`aegis_ai/auth/`)
- **CSRF protection** for web routes (`aegis_ai/auth/csrf.py`)
- **Secrets never logged** — tokens are redacted in audit
- **Unpermitted egress denied** by the egress gate
- **Local network trust is the default for MVP** — gRPC is plaintext inside a Tailscale boundary,
  not TLS
