"""Egress gate tests for the Browser Server.

The only constraint is user-information egress — **re-scoped 2026-09-30** to
*unpermitted* disclosure, with outbound connections and user-permitted disclosure
allowed. The browser server drives a real browser, so it is the most egress-prone
component in AEGIS. These tests exist so no future change can silently bypass the check.

Mirrors ``ai-server/tests/test_egress_gate.py`` — see ``docs/egress-gate.md``.
"""

from __future__ import annotations

import pytest

from aegis_browser.egress import (
    EgressDenied,
    EgressRequest,
    classify_destination,
    egress_allowed,
    external_egress_enabled,
    is_local_destination,
    require_egress,
)

# Every test in this module guards the single constraint. The marker is counted by
# --require-egress-tests (see conftest.py) so this suite can never silently run empty.
pytestmark = pytest.mark.egress


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Every test starts from the shipped default: external egress closed."""
    monkeypatch.delenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", raising=False)
    monkeypatch.delenv("AEGIS_EGRESS_ALLOWED_HOSTS", raising=False)


# ── Defaults ──────────────────────────────────────────────────────────────────


def test_external_egress_is_disabled_by_default():
    assert external_egress_enabled() is False


# ── Classification ────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "destination",
    [
        "http://localhost:11434/v1",
        "http://127.0.0.1:50053",
        "http://192.168.1.10:50053",
        "http://10.0.0.5/x",
        "http://172.16.4.4:8080",
        "http://100.64.0.5:8080",  # Tailscale CGNAT
        "http://[::1]:50051",
        "http://nas.local/x",
        "http://aegis-box:50051",  # single-label LAN host
    ],
)
def test_local_destinations_are_local(destination):
    assert classify_destination(destination) == "local"
    assert is_local_destination(destination) is True


@pytest.mark.parametrize(
    "destination",
    [
        "https://api.deepseek.com",
        "https://example.com/a",
        "https://api.open-meteo.com/v1/forecast",
        "http://8.8.8.8/",
    ],
)
def test_external_destinations_are_external(destination):
    assert classify_destination(destination) == "external"


@pytest.mark.parametrize("destination", ["", "   "])
def test_empty_destination_is_unknown(destination):
    assert classify_destination(destination) == "unknown"


@pytest.mark.parametrize("destination", ["not a url", "ftp://weird!!host"])
def test_malformed_destination_fails_closed(destination):
    """Malformed input must not be mistaken for a single-label LAN hostname."""
    assert classify_destination(destination) == "external"
    assert egress_allowed(EgressRequest(destination, purpose="web.navigate", component="t")) is False


# ── Deny by default ───────────────────────────────────────────────────────────


def test_external_is_denied_by_default():
    request = EgressRequest("https://example.com", purpose="web.navigate", component="t")
    assert egress_allowed(request) is False
    with pytest.raises(EgressDenied):
        require_egress(request)


def test_local_is_always_allowed():
    request = EgressRequest("http://localhost:11434/v1", purpose="llm.chat", component="t")
    assert egress_allowed(request) is True


def test_unknown_is_denied():
    request = EgressRequest("", purpose="web.navigate", component="t")
    assert egress_allowed(request) is False


# ── Two locks ─────────────────────────────────────────────────────────────────


def test_switch_alone_does_not_open_egress(monkeypatch):
    """The master switch without an allowlist entry must not permit egress."""
    monkeypatch.setenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "1")
    request = EgressRequest("https://example.com", purpose="web.navigate", component="t")
    assert egress_allowed(request) is False


def test_allowlist_alone_does_not_open_egress(monkeypatch):
    """An allowlist entry without the master switch must not permit egress."""
    monkeypatch.setenv("AEGIS_EGRESS_ALLOWED_HOSTS", "example.com")
    request = EgressRequest("https://example.com", purpose="web.navigate", component="t")
    assert egress_allowed(request) is False


def test_switch_and_allowlist_together_permit_egress(monkeypatch):
    monkeypatch.setenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "1")
    monkeypatch.setenv("AEGIS_EGRESS_ALLOWED_HOSTS", "example.com")
    request = EgressRequest("https://example.com", purpose="web.navigate", component="t")
    assert egress_allowed(request) is True


def test_allowlisted_host_does_not_permit_other_hosts(monkeypatch):
    monkeypatch.setenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "1")
    monkeypatch.setenv("AEGIS_EGRESS_ALLOWED_HOSTS", "example.com")
    request = EgressRequest("https://evil.example.net", purpose="web.navigate", component="t")
    assert egress_allowed(request) is False


# ── Navigation guards ─────────────────────────────────────────────────────────


def _task(**overrides):
    from aegis_browser.task_models import BrowserTask

    base = {"task_id": "t1", "natural_language_goal": "Read the news"}
    base.update(overrides)
    return BrowserTask(**base)


def test_check_domain_denies_external_url_by_default():
    """The domain check must consult the gate — it previously was never called."""
    from aegis_browser.safety_boundary import BrowserSafetyBoundary

    boundary = BrowserSafetyBoundary(_task(target_domains=["example.com"]))
    result = boundary.check_domain("https://example.com/page")
    assert result.allowed is False
    assert "Egress denied" in result.reason


def test_check_domain_allows_local_url():
    from aegis_browser.safety_boundary import BrowserSafetyBoundary

    boundary = BrowserSafetyBoundary(_task())
    result = boundary.check_domain("http://localhost:8000/index.html")
    assert result.allowed is True


def test_check_domain_still_enforces_target_scope_when_egress_open(monkeypatch):
    """Opening egress must not disable the task-scope check."""
    monkeypatch.setenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "1")
    monkeypatch.setenv("AEGIS_EGRESS_ALLOWED_HOSTS", "example.com,other.com")
    from aegis_browser.safety_boundary import BrowserSafetyBoundary

    boundary = BrowserSafetyBoundary(_task(target_domains=["example.com"]))
    assert boundary.check_domain("https://example.com/a").allowed is True
    assert boundary.check_domain("https://other.com/a").allowed is False


def test_navigation_guard_refuses_external_task_by_default():
    from aegis_browser.browser_use_agent import _navigation_egress_denied

    reason = _navigation_egress_denied(
        _task(natural_language_goal="Open https://example.com and summarize it")
    )
    assert reason != ""
    assert "Egress denied" in reason or "disabled" in reason


def test_navigation_guard_refuses_when_no_local_target_can_be_proven():
    """Fail closed: an unclassifiable task must not browse blind."""
    from aegis_browser.browser_use_agent import _navigation_egress_denied

    assert _navigation_egress_denied(_task(natural_language_goal="Read the news")) != ""


def test_navigation_guard_allows_local_task():
    from aegis_browser.browser_use_agent import _navigation_egress_denied

    assert _navigation_egress_denied(
        _task(natural_language_goal="Open http://localhost:8000/index.html and summarize")
    ) == ""


def test_navigation_guard_allows_allowlisted_external_task(monkeypatch):
    monkeypatch.setenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "1")
    monkeypatch.setenv("AEGIS_EGRESS_ALLOWED_HOSTS", "example.com")
    from aegis_browser.browser_use_agent import _navigation_egress_denied

    assert _navigation_egress_denied(
        _task(natural_language_goal="Open https://example.com and summarize it")
    ) == ""
