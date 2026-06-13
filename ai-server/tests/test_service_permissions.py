"""Tests for Service Permission Scopes — types, store, policy, and browser inference."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from aegis_ai.permissions.service_permission_policy import (
    ServicePermissionPolicy,
    infer_service_operation_from_browser_action,
)
from aegis_ai.permissions.service_permission_store import (
    ServicePermissionStore,
)
from aegis_ai.permissions.service_scope_types import (
    Operation,
    OperationCategory,
    ServicePermissionScope,
    get_operation_category,
    infer_operation_from_element,
    infer_service_from_url,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def store(tmpdir):
    path = str(Path(tmpdir) / "perms.json")
    return ServicePermissionStore(path=path)


@pytest.fixture()
def policy(store):
    return ServicePermissionPolicy(store=store)


# ── Types ─────────────────────────────────────────────────────

class TestServicePermissionScope:
    def test_create(self):
        scope = ServicePermissionScope(
            scope_id="s1",
            service="gmail",
            operation="read",
            allowed=True,
        )
        assert scope.service == "gmail"
        assert scope.operation == "read"
        assert scope.allowed is True

    def test_is_expired_no_expiry(self):
        scope = ServicePermissionScope(expires_at=0)
        assert scope.is_expired() is False

    def test_is_expired_past(self):
        scope = ServicePermissionScope(expires_at=1000)
        assert scope.is_expired(now_ms=2000) is True

    def test_is_expired_future(self):
        scope = ServicePermissionScope(expires_at=9999999999999)
        assert scope.is_expired() is False

    def test_matches(self):
        scope = ServicePermissionScope(service="gmail", operation="read")
        assert scope.matches("gmail", "read") is True
        assert scope.matches("gmail", "send") is False
        assert scope.matches("calendar", "read") is False

    def test_matches_wildcard_op(self):
        scope = ServicePermissionScope(service="gmail", operation="*")
        assert scope.matches("gmail", "read") is True
        assert scope.matches("gmail", "send") is True

    def test_to_dict(self):
        scope = ServicePermissionScope(
            scope_id="s1", service="gmail", operation="read",
        )
        d = scope.to_dict()
        assert d["scope_id"] == "s1"
        assert d["service"] == "gmail"


class TestOperationCategory:
    def test_safe_read(self):
        assert get_operation_category(Operation.READ) == OperationCategory.SAFE_READ
        assert get_operation_category(Operation.SEARCH) == OperationCategory.SAFE_READ
        assert get_operation_category(Operation.SUMMARIZE) == OperationCategory.SAFE_READ

    def test_low_risk(self):
        assert get_operation_category(Operation.DRAFT) == OperationCategory.LOW_RISK_WRITE
        assert get_operation_category(Operation.EDIT_DRAFT) == OperationCategory.LOW_RISK_WRITE

    def test_medium_risk(self):
        assert get_operation_category(Operation.CREATE) == OperationCategory.MEDIUM_RISK_WRITE
        assert get_operation_category(Operation.UPDATE) == OperationCategory.MEDIUM_RISK_WRITE

    def test_high_risk(self):
        assert get_operation_category(Operation.SEND) == OperationCategory.HIGH_RISK_EXTERNAL_EFFECT
        assert get_operation_category(Operation.PUBLISH) == OperationCategory.HIGH_RISK_EXTERNAL_EFFECT
        assert get_operation_category(Operation.SHARE) == OperationCategory.HIGH_RISK_EXTERNAL_EFFECT

    def test_destructive(self):
        assert get_operation_category(Operation.DELETE) == OperationCategory.DESTRUCTIVE
        assert get_operation_category(Operation.CHANGE_PERMISSION) == OperationCategory.DESTRUCTIVE
        assert get_operation_category(Operation.CREDENTIAL_ACCESS) == OperationCategory.DESTRUCTIVE

    def test_financial(self):
        assert get_operation_category(Operation.PURCHASE) == OperationCategory.FINANCIAL_OR_LEGAL
        assert get_operation_category(Operation.PAYMENT) == OperationCategory.FINANCIAL_OR_LEGAL


class TestBrowserInference:
    def test_gmail_url(self):
        assert infer_service_from_url("https://mail.google.com/mail/u/0/") == "gmail"

    def test_calendar_url(self):
        assert infer_service_from_url("https://calendar.google.com/calendar") == "calendar"

    def test_github_url(self):
        assert infer_service_from_url("https://github.com/user/repo") == "github"

    def test_twitter_url(self):
        assert infer_service_from_url("https://x.com/user") == "x_twitter"
        assert infer_service_from_url("https://twitter.com/user") == "x_twitter"

    def test_unknown_url(self):
        assert infer_service_from_url("https://example.com") == "browser"

    def test_send_element(self):
        assert infer_operation_from_element("Send") == "send"
        assert infer_operation_from_element("送信") == "send"

    def test_post_element(self):
        assert infer_operation_from_element("Post") == "publish"
        assert infer_operation_from_element("投稿する") == "publish"

    def test_delete_element(self):
        assert infer_operation_from_element("Delete") == "delete"
        assert infer_operation_from_element("削除") == "delete"

    def test_share_element(self):
        assert infer_operation_from_element("Share") == "share"
        assert infer_operation_from_element("共有") == "share"

    def test_purchase_element(self):
        assert infer_operation_from_element("Purchase") == "purchase"
        assert infer_operation_from_element("Buy Now") == "purchase"
        assert infer_operation_from_element("購入する") == "purchase"

    def test_draft_element(self):
        assert infer_operation_from_element("Draft") == "draft"
        assert infer_operation_from_element("下書き") == "draft"

    def test_unknown_element(self):
        assert infer_operation_from_element("Click here") == "read"


class TestBrowserHighRiskKeywords:
    def test_infer_browser_action(self):
        result = infer_service_operation_from_browser_action(
            "https://mail.google.com", "Send"
        )
        assert result["service"] == "gmail"
        assert result["operation"] == "send"

    def test_infer_browser_purchase(self):
        result = infer_service_operation_from_browser_action(
            "https://example.com/shop", "Purchase"
        )
        assert result["service"] == "browser"
        assert result["operation"] == "purchase"


# ── Store ─────────────────────────────────────────────────────

class TestServicePermissionStore:
    def test_load_defaults(self, store):
        count = store.load_defaults()
        assert count > 50

    def test_gmail_read_allowed(self, store):
        store.load_defaults()
        assert store.is_allowed("gmail", "read") is True

    def test_gmail_send_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("gmail", "send") is True
        assert store.is_allowed("gmail", "send") is False

    def test_gmail_search_allowed(self, store):
        store.load_defaults()
        assert store.is_allowed("gmail", "search") is True

    def test_gmail_draft_allowed(self, store):
        store.load_defaults()
        assert store.is_allowed("gmail", "draft") is True

    def test_calendar_read_allowed(self, store):
        store.load_defaults()
        assert store.is_allowed("calendar", "read") is True

    def test_calendar_create_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("calendar", "create") is True

    def test_calendar_delete_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("calendar", "delete") is True

    def test_github_read_allowed(self, store):
        store.load_defaults()
        assert store.is_allowed("github", "read") is True

    def test_github_publish_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("github", "publish") is True

    def test_github_delete_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("github", "delete") is True

    def test_sns_send_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("sns", "send") is True

    def test_sns_publish_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("sns", "publish") is True

    def test_discord_send_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("discord", "send") is True

    def test_cloud_share_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("cloud_storage", "share") is True

    def test_cloud_delete_requires_approval(self, store):
        store.load_defaults()
        assert store.requires_approval("cloud_storage", "delete") is True

    def test_purchase_deny_or_approval(self, store):
        store.load_defaults()
        d = store.explain_decision("browser", "purchase")
        assert d.decision in ("deny", "ask_approval")

    def test_financial_universal_deny(self, store):
        store.load_defaults()
        d = store.explain_decision("*", "payment")
        assert d.decision == "deny"

    def test_unknown_service_category_default(self, store):
        store.load_defaults()
        d = store.explain_decision("custom_service", "read")
        assert d.decision == "allow"

    def test_unknown_operation_category_default(self, store):
        store.load_defaults()
        d = store.explain_decision("gmail", "unknown_op")
        assert d.decision in ("allow", "ask_approval", "deny")

    def test_set_scope(self, store):
        scope = ServicePermissionScope(
            service="test_svc",
            operation="read",
            allowed=True,
        )
        store.set_scope(scope)
        assert store.is_allowed("test_svc", "read") is True
        assert scope.scope_id

    def test_disable_scope(self, store):
        scope = ServicePermissionScope(
            scope_id="dis1",
            service="test_svc2",
            operation="read",
            allowed=True,
        )
        store.set_scope(scope)
        assert store.is_allowed("test_svc2", "read") is True
        store.disable_scope("dis1")
        assert store.is_allowed("test_svc2", "read") is False

    def test_disable_nonexistent(self, store):
        assert store.disable_scope("nonexistent") is False

    def test_list_scopes(self, store):
        store.load_defaults()
        gmail_scopes = store.list_scopes("gmail")
        assert len(gmail_scopes) > 0
        for s in gmail_scopes:
            assert s.service == "gmail"

    def test_list_all_scopes(self, store):
        store.load_defaults()
        all_scopes = store.list_scopes()
        assert len(all_scopes) > 50

    def test_desire_driven_external_send(self, store):
        store.load_defaults()
        assert store.requires_approval("gmail", "send", source="desire_driven") is True

    def test_desire_driven_high_risk(self, store):
        store.load_defaults()
        assert store.requires_approval("sns", "publish", source="desire_driven") is True

    def test_persistence(self, store):
        store.load_defaults()
        store2 = ServicePermissionStore(path=store._path)
        assert store2.is_allowed("gmail", "read") is True
        assert store2.requires_approval("gmail", "send") is True

    def test_explain_decision(self, store):
        store.load_defaults()
        d = store.explain_decision("gmail", "send")
        assert d.decision == "ask_approval"
        assert d.requires_approval is True
        assert "approval" in d.reason.lower()


# ── Policy ────────────────────────────────────────────────────

class TestServicePermissionPolicy:
    def test_evaluate_gmail_read(self, policy):
        result = policy.evaluate_service_operation("gmail", "read")
        assert result["decision"] == "allow"

    def test_evaluate_gmail_send(self, policy):
        result = policy.evaluate_service_operation("gmail", "send")
        assert result["decision"] == "ask_approval"
        assert result["requires_approval"] is True

    def test_evaluate_browser_send(self, policy):
        result = policy.evaluate_browser_action(
            "https://mail.google.com", "Send"
        )
        assert result["decision"] == "ask_approval"

    def test_evaluate_browser_purchase(self, policy):
        result = policy.evaluate_browser_action(
            "https://example.com/shop", "Purchase"
        )
        assert result["decision"] in ("deny", "ask_approval")

    def test_evaluate_browser_post(self, policy):
        result = policy.evaluate_browser_action(
            "https://x.com/compose", "Post"
        )
        assert result["decision"] == "ask_approval"

    def test_evaluate_browser_share(self, policy):
        result = policy.evaluate_browser_action(
            "https://drive.google.com", "Share"
        )
        assert result["decision"] == "ask_approval"

    def test_evaluate_browser_delete(self, policy):
        result = policy.evaluate_browser_action(
            "https://github.com/user/repo", "Delete"
        )
        assert result["decision"] == "ask_approval"

    def test_evaluate_browser_draft_allowed(self, policy):
        result = policy.evaluate_browser_action(
            "https://mail.google.com", "Draft"
        )
        assert result["decision"] == "allow"

    def test_evaluate_browser_read_allowed(self, policy):
        result = policy.evaluate_browser_action(
            "https://mail.google.com", "Read"
        )
        assert result["decision"] == "allow"

    def test_stale_world_state_blocks(self, policy):
        from aegis_ai.permissions import ServicePermissionScope
        policy.store.set_scope(ServicePermissionScope(
            service="gmail", operation="read", allowed=True,
            requires_fresh_world_state=True,
        ))
        class FakeWS:
            stale_sections = ["gmail"]
        result = policy.evaluate_service_operation(
            "gmail", "read", world_state=FakeWS()
        )
        assert result["decision"] == "ask_approval"
        assert "stale" in result["reason"].lower()

    def test_explain_decision(self, policy):
        result = policy.explain_decision("gmail", "send")
        assert result["decision"] == "ask_approval"
        assert "scope" in result

    def test_oauth_mappings(self, policy):
        mappings = policy.list_oauth_mappings()
        assert len(mappings) > 0

    def test_oauth_gmail_readonly(self, policy):
        result = policy.get_oauth_explanation(
            "gmail", "https://www.googleapis.com/auth/gmail.readonly"
        )
        assert result is not None
        assert "gmail:read" in result["internal_scopes"]

    def test_oauth_unknown(self, policy):
        result = policy.get_oauth_explanation("gmail", "unknown_scope")
        assert result is None

    def test_list_oauth_by_service(self, policy):
        gmail_mappings = policy.list_oauth_mappings("gmail")
        assert len(gmail_mappings) > 0
        for m in gmail_mappings:
            assert m["service"] == "gmail"

    def test_desire_driven_blocked(self, policy):
        result = policy.evaluate_service_operation(
            "gmail", "send", source="desire_driven"
        )
        assert result["decision"] == "ask_approval"


# ── Module exports ────────────────────────────────────────────

class TestModuleExports:
    def test_imports(self):
        from aegis_ai.permissions import (
            ServicePermissionPolicy,
            ServicePermissionScope,
            ServicePermissionStore,
        )
        assert ServicePermissionScope is not None
        assert ServicePermissionStore is not None
        assert ServicePermissionPolicy is not None


# ── Secret masking in context ─────────────────────────────────

class TestSecretNotInContext:
    def test_no_token_in_explain(self, policy):
        result = policy.explain_decision("gmail", "send")
        result_str = json.dumps(result)
        for keyword in ["token", "password", "secret", "cookie", "sk-", "Bearer"]:
            assert keyword not in result_str, f"Found '{keyword}' in explain result"

    def test_no_token_in_oauth(self, policy):
        mappings = policy.list_oauth_mappings()
        for m in mappings:
            m_str = json.dumps(m)
            for keyword in ["token", "password", "secret", "cookie"]:
                assert keyword not in m_str.lower(), f"Found '{keyword}' in OAuth mapping"
