# Security — Local Network Authentication & Protection

> **Status**: Verified against current code snapshot
> **Related**: `docs/local-network-security.md`, `docs/architecture.md` §7

## Overview

AEGIS Security provides authentication, CSRF protection, rate limiting,
and origin checking for local network operation.

## Components

### LocalTokenAuth (`auth.py`)

Token-based authentication for server-to-server communication.

```python
from aegis_ai.security import LocalTokenAuth, generate_token

auth = LocalTokenAuth(token="my-secret-token")
result = auth.validate_server("pc-server", token)
if result.authenticated:
    # Server is authorized
```

### TokenStore (`tokens.py`)

Persists and rotates authentication tokens.

```python
from aegis_ai.security import TokenStore

store = TokenStore(path="data/tokens.json")
token = store.get_or_create_token("pc-server")
store.rotate_token("pc-server")
```

### CSRFProtection (`csrf.py`)

Cross-site request forgery prevention for web routes.

```python
from aegis_ai.security import CSRFProtection

csrf = CSRFProtection()
token = csrf.generate_token(session_id)
# ... later ...
csrf.validate_token(session_id, token)
```

### RateLimiter (`rate_limit.py`)

Token bucket rate limiter to prevent abuse.

```python
from aegis_ai.security import RateLimiter

limiter = RateLimiter(max_requests=60, window_seconds=60)
result = limiter.check("client_id")
if result.allowed:
    # Process request
```

### OriginChecker (`origin.py`)

Validates request origins (localhost only by default).

```python
from aegis_ai.security import OriginChecker

checker = OriginChecker()
if checker.is_allowed(origin, remote_addr):
    # Allow request
```

### TLSConfig (`tls.py`)

Optional TLS configuration for local network.

```python
from aegis_ai.security import TLSConfig

config = TLSConfig(enabled=True, cert_file="certs/server.crt", key_file="certs/server.key")
```

## Security Principles

- **Localhost only** by default — no external access
- **Token auth** for server-to-server communication
- **CSRF protection** for all web forms
- **Rate limiting** to prevent abuse
- **Origin checking** to block unauthorized access
- **Secrets never logged** — tokens are redacted in audit
- **TLS optional** — local network trust is default for MVP
