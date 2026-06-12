"""Beta E2E: Browser Stop Conditions — CAPTCHA/payment/identity detection.

Scenario:
  browser-use encounters CAPTCHA/payment/identity verification
  → Safety boundary detects condition
  → Task stops immediately
  → No bypass attempted
"""

from __future__ import annotations

from aegis_browser.safety_boundary import BrowserSafetyBoundary
from aegis_browser.task_models import BrowserTask, READONLY_TASK, SIGNUP_TASK


# ═══════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════


class TestBetaBrowserStopConditions:
    """Browser stop conditions E2E test."""

    def test_captcha_detected_stops(self):
        """CAPTCHA detection stops task."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        result = boundary.check_page_content("Please solve the CAPTCHA to continue")
        assert result.should_stop is True

    def test_recaptcha_detected_stops(self):
        """reCAPTCHA detection stops task."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        result = boundary.check_page_content("reCAPTCHA verification required")
        assert result.should_stop is True

    def test_payment_required_stops(self):
        """Payment requirement stops task."""
        boundary = BrowserSafetyBoundary(SIGNUP_TASK)
        result = boundary.check_page_content("Payment required: $9.99/month")
        assert result.should_stop is True

    def test_identity_verification_stops(self):
        """Identity verification stops task."""
        boundary = BrowserSafetyBoundary(SIGNUP_TASK)
        result = boundary.check_page_content("Please upload ID or passport for verification")
        assert result.should_stop is True

    def test_age_verification_stops(self):
        """Age verification stops task."""
        boundary = BrowserSafetyBoundary(SIGNUP_TASK)
        result = boundary.check_page_content("Age verification required")
        assert result.should_stop is True

    def test_publish_requires_approval(self):
        """Publish action requires approval."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        result = boundary.check_page_content("Publish this post to your blog")
        assert result.needs_approval is True

    def test_send_requires_approval(self):
        """Send action requires approval."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        result = boundary.check_page_content("Send message to all followers")
        assert result.needs_approval is True

    def test_password_needs_user_input(self):
        """Password field needs user input."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        result = boundary.check_page_content("Enter your password to continue")
        assert result.needs_user_input is True

    def test_2fa_needs_user_input(self):
        """2FA field needs user input."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        result = boundary.check_page_content("Enter 2FA code from authenticator")
        assert result.needs_user_input is True

    def test_normal_content_allowed(self):
        """Normal content is allowed."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        result = boundary.check_page_content("Welcome to example.com. This is a normal page.")
        assert result.allowed is True
        assert result.should_stop is False

    def test_forbidden_action_blocked(self):
        """Forbidden actions are blocked."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        result = boundary.check_action("solve_captcha")
        assert result.allowed is False

    def test_no_bypass_attempted(self):
        """No bypass is attempted (safety boundary blocks)."""
        boundary = BrowserSafetyBoundary(READONLY_TASK)
        # Even if content mentions bypass, it should be blocked
        result = boundary.check_action("bypass_bot_detection")
        assert result.allowed is False
