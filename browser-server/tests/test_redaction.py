"""Tests for redaction module."""

from aegis_browser.redaction import redact, redact_headers


class TestRedaction:
    def test_redact_authorization_header(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        result = redact(text)
        assert "Authorization: [REDACTED]" in result
        assert "eyJhbGci" not in result

    def test_redact_cookie(self):
        text = "Set-Cookie: session_id=abc123; Path=/; HttpOnly"
        result = redact(text)
        assert "Set-Cookie: [REDACTED]" in result
        assert "abc123" not in result

    def test_redact_api_key(self):
        text = 'x-api-key=sk-1234567890abcdef'
        result = redact(text)
        assert "[REDACTED]" in result
        assert "sk-1234567890abcdef" not in result

    def test_redact_headers_dict(self):
        headers = {"Content-Type": "text/html", "Authorization": "Bearer secret", "Cookie": "session=xyz"}
        result = redact_headers(headers)
        assert result["Content-Type"] == "text/html"
        assert result["Authorization"] == "[REDACTED]"
        assert result["Cookie"] == "[REDACTED]"

    def test_safe_text_passes_through(self):
        text = "Hello, this is normal text without secrets."
        assert redact(text) == text
