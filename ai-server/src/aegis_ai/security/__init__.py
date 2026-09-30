"""Security — authentication, authorization, and network security for AEGIS.

⚠️ **UNWIRED (measured 2026-10-01).** Nothing outside this package imports it, and none of the
names below is used outside it. The live authentication system is ``aegis_ai.auth/`` (passkey,
with its own ``csrf.py``), installed by ``aegis_ai/web/auth.py``. This package is **superseded**,
not missing: wiring it would create a *second* auth/CSRF implementation. Do not wire it without a
decision — ``DELEGATION.md`` §4 carries it, and ``tests/test_security_package_stays_unwired.py``
pins the measurement.

Provides:
- LocalTokenAuth: Server-to-server token authentication
- TokenStore: Token persistence and rotation
- CSRFProtection: Cross-site request forgery prevention
- RateLimiter: Request rate limiting
- OriginChecker: Origin validation for web requests
- TLSConfig: Optional TLS configuration
"""

from aegis_ai.security.auth import LocalTokenAuth, generate_token, hash_token  # noqa: F401
from aegis_ai.security.csrf import CSRFProtection  # noqa: F401
from aegis_ai.security.origin import OriginChecker  # noqa: F401
from aegis_ai.security.rate_limit import RateLimiter  # noqa: F401
from aegis_ai.security.tls import TLSConfig  # noqa: F401
from aegis_ai.security.tokens import TokenStore  # noqa: F401
