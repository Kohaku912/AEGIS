"""Tests for Security — auth, tokens, CSRF, rate limiting, origin checking."""

from __future__ import annotations

import time

from aegis_ai.security.auth import LocalTokenAuth, generate_token, hash_token
from aegis_ai.security.csrf import CSRFProtection
from aegis_ai.security.origin import OriginChecker
from aegis_ai.security.rate_limit import RateLimiter
from aegis_ai.security.tokens import TokenStore

# ═══════════════════════════════════════════════════════════════
# 1. Local Token Auth
# ═══════════════════════════════════════════════════════════════


class TestLocalTokenAuth:
    """Token-based server authentication."""

    def test_valid_token_auth(self):
        """Valid token authenticates server."""
        auth = LocalTokenAuth(token="test-token-123")
        result = auth.validate_server("pc-server", "test-token-123")
        assert result.authenticated is True
        assert result.server_id == "pc-server"

    def test_invalid_token_denied(self):
        """Invalid token denies server."""
        auth = LocalTokenAuth(token="test-token-123")
        result = auth.validate_server("pc-server", "wrong-token")
        assert result.authenticated is False

    def test_empty_token_denied(self):
        """Empty token denies server."""
        auth = LocalTokenAuth(token="test-token-123")
        result = auth.validate_server("pc-server", "")
        assert result.authenticated is False

    def test_server_not_in_allowlist(self):
        """Server not in allowlist is denied."""
        auth = LocalTokenAuth(
            token="test-token",
            allowed_servers={"pc-server", "android-server"},
        )
        result = auth.validate_server("unknown-server", "test-token")
        assert result.authenticated is False

    def test_server_in_allowlist(self):
        """Server in allowlist is allowed."""
        auth = LocalTokenAuth(
            token="test-token",
            allowed_servers={"pc-server", "android-server"},
        )
        result = auth.validate_server("pc-server", "test-token")
        assert result.authenticated is True

    def test_failed_attempts_tracked(self):
        """Failed attempts are tracked."""
        auth = LocalTokenAuth(token="test-token")
        auth.validate_server("pc-server", "wrong")
        auth.validate_server("pc-server", "wrong")
        assert auth.get_failed_attempts("pc-server") == 2

    def test_generate_token(self):
        """generate_token creates a token."""
        token = generate_token()
        assert len(token) >= 32

    def test_hash_token(self):
        """hash_token creates a hash."""
        h = hash_token("test-token")
        assert len(h) == 64  # SHA-256 hex


# ═══════════════════════════════════════════════════════════════
# 2. Token Store
# ═══════════════════════════════════════════════════════════════


class TestTokenStore:
    """Token store persists and rotates tokens."""

    def test_get_or_create_token(self):
        """get_or_create_token creates and returns token."""
        import os
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)

        store = TokenStore(path=path)
        token = store.get_or_create_token("pc-server")
        assert len(token) >= 32

        # Same token on second call
        token2 = store.get_or_create_token("pc-server")
        assert token == token2

    def test_rotate_token(self):
        """rotate_token creates a new token."""
        import os
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)

        store = TokenStore(path=path)
        token1 = store.get_or_create_token("pc-server")
        token2 = store.rotate_token("pc-server")
        assert token1 != token2

    def test_validate_token(self):
        """validate_token checks token correctness."""
        import os
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)

        store = TokenStore(path=path)
        token = store.get_or_create_token("pc-server")
        assert store.validate_token("pc-server", token) is True
        assert store.validate_token("pc-server", "wrong") is False

    def test_remove_token(self):
        """remove_token removes the token."""
        import os
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)

        store = TokenStore(path=path)
        store.get_or_create_token("pc-server")
        store.remove_token("pc-server")
        assert store.validate_token("pc-server", "any") is False


# ═══════════════════════════════════════════════════════════════
# 3. CSRF Protection
# ═══════════════════════════════════════════════════════════════


class TestCSRFProtection:
    """CSRF token generation and validation."""

    def test_generate_and_validate(self):
        """Generate and validate CSRF token."""
        csrf = CSRFProtection()
        token = csrf.generate_token("session-1")
        assert csrf.validate_token("session-1", token) is True

    def test_invalid_token_rejected(self):
        """Invalid CSRF token is rejected."""
        csrf = CSRFProtection()
        csrf.generate_token("session-1")
        assert csrf.validate_token("session-1", "wrong") is False

    def test_invalidate_token(self):
        """Invalidated token is rejected."""
        csrf = CSRFProtection()
        token = csrf.generate_token("session-1")
        csrf.invalidate_token("session-1")
        assert csrf.validate_token("session-1", token) is False

    def test_expired_token_rejected(self):
        """Expired token is rejected."""
        csrf = CSRFProtection(token_lifetime_seconds=0)
        token = csrf.generate_token("session-1")
        time.sleep(0.01)
        assert csrf.validate_token("session-1", token) is False


# ═══════════════════════════════════════════════════════════════
# 4. Rate Limiter
# ═══════════════════════════════════════════════════════════════


class TestRateLimiter:
    """Rate limiter prevents abuse."""

    def test_within_limit(self):
        """Requests within limit are allowed."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            result = limiter.check("client-1")
            assert result.allowed is True

    def test_exceeds_limit(self):
        """Requests exceeding limit are denied."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("client-1")
        limiter.check("client-1")
        result = limiter.check("client-1")
        assert result.allowed is False

    def test_different_clients_independent(self):
        """Different clients have independent limits."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("client-1")
        limiter.check("client-1")
        result = limiter.check("client-2")
        assert result.allowed is True

    def test_reset(self):
        """Reset clears rate limit."""
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.check("client-1")
        limiter.reset("client-1")
        result = limiter.check("client-1")
        assert result.allowed is True


# ═══════════════════════════════════════════════════════════════
# 5. Origin Checker
# ═══════════════════════════════════════════════════════════════


class TestOriginChecker:
    """Origin checker validates request origins."""

    def test_localhost_allowed(self):
        """Localhost is allowed by default."""
        checker = OriginChecker()
        assert checker.is_allowed("http://localhost:8080", "127.0.0.1") is True

    def test_external_origin_denied(self):
        """External origin is denied by default."""
        checker = OriginChecker()
        assert checker.is_allowed("https://evil.com", "1.2.3.4") is False

    def test_custom_origin_allowed(self):
        """Custom allowed origin is accepted."""
        checker = OriginChecker(allowed_origins={"https://my-app.local"})
        assert checker.is_allowed("https://my-app.local", "192.168.1.1") is True

    def test_none_origin_with_localhost(self):
        """None origin with localhost IP is allowed."""
        checker = OriginChecker()
        assert checker.is_allowed(None, "127.0.0.1") is True
