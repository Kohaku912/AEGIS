"""Tests for Browser-Use Agent."""

from __future__ import annotations

from aegis_browser.browser_use_agent import BrowserUseAgent, SafetyStop
from aegis_browser.config import Config
from aegis_browser.main import get_runtime_health
from aegis_browser.session import BrowserSession
from aegis_browser.task_models import (
    BrowserTask,
    BrowserTaskResult,
    DRAFT_TASK,
    READONLY_TASK,
    SIGNUP_TASK,
    TaskStatus,
)
from aegis_browser.trace import BrowserTrace


# ═══════════════════════════════════════════════════════════════
# 1. BrowserTask Models
# ═══════════════════════════════════════════════════════════════


class TestBrowserTask:
    """BrowserTask data models."""

    def test_task_creation(self):
        """BrowserTask can be created."""
        task = BrowserTask(
            task_id="test_001",
            natural_language_goal="Read example.com",
        )
        assert task.task_id == "test_001"

    def test_readonly_task_template(self):
        """READONLY_TASK has correct defaults."""
        assert "read_page" in READONLY_TASK.allowed_actions
        assert "solve_captcha" in READONLY_TASK.forbidden_actions
        assert "publish" in READONLY_TASK.forbidden_actions

    def test_draft_task_template(self):
        """DRAFT_TASK allows draft actions."""
        assert "draft_text" in DRAFT_TASK.allowed_actions
        assert "save_draft" in DRAFT_TASK.allowed_actions
        assert "publish" in DRAFT_TASK.forbidden_actions

    def test_signup_task_template(self):
        """SIGNUP_TASK has stop conditions."""
        assert "captcha_detected" in SIGNUP_TASK.stop_conditions
        assert "payment_required" in SIGNUP_TASK.stop_conditions


# ═══════════════════════════════════════════════════════════════
# 2. Safety Boundary
# ═══════════════════════════════════════════════════════════════


class TestBrowserSafetyBoundary:
    """Safety boundary checks."""

    def test_captcha_detected(self):
        """CAPTCHA triggers stop."""
        from aegis_browser.safety_boundary import BrowserSafetyBoundary

        task = BrowserTask(
            task_id="test",
            natural_language_goal="Test",
            forbidden_actions=["solve_captcha"],
        )
        boundary = BrowserSafetyBoundary(task)
        result = boundary.check_page_content("Please solve the CAPTCHA to continue")
        assert result.should_stop is True

    def test_payment_detected(self):
        """Payment triggers stop."""
        from aegis_browser.safety_boundary import BrowserSafetyBoundary

        task = BrowserTask(
            task_id="test",
            natural_language_goal="Test",
            forbidden_actions=["purchase", "paid_subscription"],
        )
        boundary = BrowserSafetyBoundary(task)
        result = boundary.check_page_content("Payment required: $9.99/month")
        assert result.should_stop is True

    def test_identity_verification_detected(self):
        """Identity verification triggers stop."""
        from aegis_browser.safety_boundary import BrowserSafetyBoundary

        task = BrowserTask(
            task_id="test",
            natural_language_goal="Test",
            forbidden_actions=["upload_identity_document"],
        )
        boundary = BrowserSafetyBoundary(task)
        result = boundary.check_page_content("Please upload ID or passport for verification")
        assert result.should_stop is True

    def test_publish_detected(self):
        """Publish action needs approval."""
        from aegis_browser.safety_boundary import BrowserSafetyBoundary

        task = BrowserTask(
            task_id="test",
            natural_language_goal="Test",
            forbidden_actions=["publish"],
        )
        boundary = BrowserSafetyBoundary(task)
        result = boundary.check_page_content("Publish this post to your blog")
        assert result.needs_approval is True

    def test_password_detected(self):
        """Password field needs user input."""
        from aegis_browser.safety_boundary import BrowserSafetyBoundary

        task = BrowserTask(
            task_id="test",
            natural_language_goal="Test",
            forbidden_actions=["enter_password_without_user"],
        )
        boundary = BrowserSafetyBoundary(task)
        result = boundary.check_page_content("Enter your password to continue")
        assert result.needs_user_input is True

    def test_normal_content_allowed(self):
        """Normal content is allowed."""
        from aegis_browser.safety_boundary import BrowserSafetyBoundary

        task = BrowserTask(task_id="test", natural_language_goal="Test")
        boundary = BrowserSafetyBoundary(task)
        result = boundary.check_page_content("Welcome to example.com. This is a normal page.")
        assert result.allowed is True

    def test_forbidden_action_blocked(self):
        """Forbidden actions are blocked."""
        from aegis_browser.safety_boundary import BrowserSafetyBoundary

        task = BrowserTask(
            task_id="test",
            natural_language_goal="Test",
            forbidden_actions=["solve_captcha"],
        )
        boundary = BrowserSafetyBoundary(task)
        result = boundary.check_action("solve_captcha")
        assert result.allowed is False


# ═══════════════════════════════════════════════════════════════
# 3. Trace
# ═══════════════════════════════════════════════════════════════


class TestBrowserTrace:
    """Trace recording works correctly."""

    def test_trace_creation(self):
        """Trace can be created."""
        trace = BrowserTrace(task_id="test_001")
        assert trace.task_id == "test_001"

    def test_record_entry(self):
        """Entries are recorded."""
        trace = BrowserTrace(task_id="test")
        trace.record("navigate", "Opened example.com")
        assert len(trace.get_entries()) == 1
        assert trace.get_entries()[0].action == "navigate"

    def test_trace_summary(self):
        """Summary is generated."""
        trace = BrowserTrace(task_id="test")
        trace.record("action1", "Test 1")
        trace.record("action2", "Test 2")
        summary = trace.get_summary()
        assert summary["total_entries"] == 2


# ═══════════════════════════════════════════════════════════════
# 4. BrowserUseAgent
# ═══════════════════════════════════════════════════════════════


class TestBrowserUseAgent:
    """BrowserUseAgent execution."""

    def test_agent_creation(self):
        """Agent can be created."""
        agent = BrowserUseAgent()
        assert agent.is_running() is False

    def test_build_task_with_safety(self):
        """Task is built with safety instructions."""
        agent = BrowserUseAgent()
        task = BrowserTask(
            task_id="test",
            natural_language_goal="Read example.com",
            forbidden_actions=["solve_captcha"],
        )
        full_task = agent._build_task_with_safety(task)
        assert "FORBIDDEN" in full_task
        assert "captcha" in full_task.lower()
        assert "Read example.com" in full_task

    def test_stop_sets_running_false(self):
        """Stop sets running to False."""
        agent = BrowserUseAgent()
        agent._running = True
        agent.stop()
        assert agent.is_running() is False


class TestBrowserRuntimeHealth:
    """Runtime health exposes dependency and profile state."""

    def test_runtime_health_reports_profile_and_dependency_mode(self, tmp_path, monkeypatch):
        config = Config(
            browser_profile_root=str(tmp_path / "profiles"),
            browser_session_root=str(tmp_path / "sessions"),
            browser_profile_name="owner",
        )

        monkeypatch.setattr("aegis_browser.main._module_available", lambda name: name == "playwright")

        health = get_runtime_health(config)

        assert health["status"] == "degraded"
        assert health["mode"] == "fallback"
        assert health["browser_use_available"] is False
        assert health["playwright_available"] is True
        assert health["profile_root"] == str(tmp_path / "profiles")
        assert health["profile_name"] == "owner"
        assert health["profile_dir"].endswith("owner")
        assert "browser-use" in health["degraded_reason"]

    def test_browser_session_profile_directory_is_stable(self, tmp_path):
        session = BrowserSession(
            session_id="owner",
            profile_dir=str(tmp_path / "profiles"),
            session_dir=str(tmp_path / "sessions"),
        )

        session.ensure_dirs()
        first_path = session.profile_dir
        session.record_page_visit("https://example.com")
        session.save_state()

        reloaded = BrowserSession(
            session_id="owner",
            profile_dir=str(tmp_path / "profiles"),
            session_dir=str(tmp_path / "sessions"),
        )

        assert reloaded.profile_dir == first_path
        assert reloaded.load_state() is True
