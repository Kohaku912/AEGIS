"""Tests for User Model and Dialogue system."""

from __future__ import annotations

import shutil
import tempfile

import pytest

from aegis_ai.dialogue import (
    DialogueStyleController,
    InteractionContext,
    InteractionDecisionType,
    InteractionPolicy,
    NotificationRecord,
    NotificationUrgency,
    ProactiveNotificationController,
)
from aegis_ai.user_model import (
    ApprovalStrictness,
    AutonomyLevel,
    DetailLevel,
    NotificationPreference,
    UserModel,
    UserModelStore,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestUserModel:
    def test_default_values(self):
        m = UserModel()
        assert m.preferred_language == "ja"
        assert m.detail_level == DetailLevel.NORMAL
        assert m.autonomy_level == AutonomyLevel.MEDIUM

    def test_quiet_hours_night(self):
        m = UserModel()
        m.quiet_hours.enabled = True
        m.quiet_hours.start_hour = 22
        m.quiet_hours.end_hour = 8
        assert m.is_quiet_now(23) is True
        assert m.is_quiet_now(3) is True
        assert m.is_quiet_now(12) is False

    def test_quiet_hours_disabled(self):
        m = UserModel()
        m.quiet_hours.enabled = False
        assert m.is_quiet_now(3) is False

    def test_allows_proactive_normal(self):
        m = UserModel()
        assert m.allows_proactive("approval_required") is True
        assert m.allows_proactive("social_check_in") is False

    def test_allows_proactive_minimal(self):
        m = UserModel()
        m.notification_preference = NotificationPreference.MINIMAL
        assert m.allows_proactive("approval_required") is True
        assert m.allows_proactive("task_completed") is False

    def test_disallowed_category(self):
        m = UserModel()
        m.disallowed_proactive_categories = ["social_check_in"]
        assert m.allows_proactive("social_check_in") is False

    def test_to_dict(self):
        m = UserModel()
        d = m.to_dict()
        assert "user_id" in d
        assert "detail_level" in d


class TestUserModelStore:
    def test_save_and_load(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        store.update({"detail_level": "brief"}, reason="user said short")
        store2 = UserModelStore(data_dir=tmpdir)
        assert store2.model.detail_level == DetailLevel.BRIEF
        assert store2.model.last_user_feedback == "user said short"

    def test_adjust_trust(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        initial = store.model.trust_score
        store.adjust_trust(0.1, "good job")
        assert store.model.trust_score > initial

    def test_adjust_annoyance(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        store.adjust_annoyance(0.3, "annoying")
        assert store.model.annoyance_score > 0.0

    def test_to_context_string(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        ctx = store.to_context_string()
        assert "lang=" in ctx
        assert "Detail:" in ctx


class TestInteractionPolicy:
    def test_safety_warning_always_speaks(self):
        policy = InteractionPolicy()
        ctx = InteractionContext(
            category="safety_warning",
            is_safety_related=True,
            urgency="critical",
        )
        d = policy.evaluate(ctx)
        assert d.decision == InteractionDecisionType.SPEAK_NOW
        assert d.urgency == NotificationUrgency.CRITICAL

    def test_focus_mode_queues(self):
        user = UserModel()
        user.focus_mode = True
        policy = InteractionPolicy()
        ctx = InteractionContext(
            user_model=user,
            category="task_completed",
        )
        d = policy.evaluate(ctx)
        assert d.decision == InteractionDecisionType.QUEUE_FOR_LATER

    def test_quiet_hours_queues(self):
        user = UserModel()
        user.quiet_hours.enabled = True
        user.quiet_hours.start_hour = 0
        user.quiet_hours.end_hour = 23
        policy = InteractionPolicy()
        ctx = InteractionContext(
            user_model=user,
            category="task_completed",
        )
        d = policy.evaluate(ctx)
        assert d.decision == InteractionDecisionType.QUEUE_FOR_LATER

    def test_social_checkin_cooldown(self):
        user = UserModel()
        user.notification_preference = NotificationPreference.PROACTIVE
        policy = InteractionPolicy()
        ctx = InteractionContext(
            user_model=user,
            category="social_check_in",
            last_notification_ago_seconds=100,
        )
        d = policy.evaluate(ctx)
        assert d.decision == InteractionDecisionType.SUPPRESS

    def test_approval_required_notify(self):
        policy = InteractionPolicy()
        ctx = InteractionContext(
            category="approval_required",
            is_approval_required=True,
            pending_approval_count=1,
        )
        d = policy.evaluate(ctx)
        assert d.decision == InteractionDecisionType.NOTIFY_NOW

    def test_too_many_approvals_summarize(self):
        policy = InteractionPolicy()
        ctx = InteractionContext(
            category="approval_required",
            is_approval_required=True,
            pending_approval_count=10,
        )
        d = policy.evaluate(ctx)
        assert d.decision == InteractionDecisionType.SUMMARIZE_LATER

    def test_rejection_suppresses(self):
        policy = InteractionPolicy()
        policy.record_rejection("social_check_in")
        user = UserModel()
        user.notification_preference = NotificationPreference.PROACTIVE
        ctx = InteractionContext(
            user_model=user,
            category="social_check_in",
            last_notification_ago_seconds=99999,
        )
        d = policy.evaluate(ctx)
        assert d.decision == InteractionDecisionType.SUPPRESS


class TestProactiveNotificationController:
    def test_safety_warning_always_passes(self, tmpdir):
        ctrl = ProactiveNotificationController(data_dir=tmpdir)
        ok, reason = ctrl.should_notify("safety_warning")
        assert ok is True

    def test_cooldown_blocks(self, tmpdir):
        ctrl = ProactiveNotificationController(data_dir=tmpdir)
        rec = NotificationRecord(
            category="task_completed",
            message_summary="done",
        )
        ctrl.record_notification(rec)
        ok, reason = ctrl.should_notify("task_completed")
        assert ok is False

    def test_rejection_extends_cooldown(self, tmpdir):
        ctrl = ProactiveNotificationController(data_dir=tmpdir)
        rec = NotificationRecord(
            notification_id="n1",
            category="social_check_in",
            message_summary="hello",
        )
        ctrl.record_notification(rec)
        ctrl.record_user_response("n1", "rejected")
        ok, reason = ctrl.should_notify("social_check_in")
        assert ok is False

    def test_record_persists(self, tmpdir):
        ctrl = ProactiveNotificationController(data_dir=tmpdir)
        rec = NotificationRecord(category="task_failed", message_summary="error")
        ctrl.record_notification(rec)
        ctrl2 = ProactiveNotificationController(data_dir=tmpdir)
        assert len(ctrl2.get_recent_records()) == 1


class TestDialogueStyleController:
    def test_format_approval_request(self):
        ctrl = DialogueStyleController()
        msg = ctrl.format_approval_request(
            what="ファイル削除",
            why="外部送信にあたるため",
            impact="データが失われます",
        )
        assert "承認が必要です" in msg
        assert "理由" in msg

    def test_format_success_brief(self):
        user = UserModel()
        user.detail_level = DetailLevel.BRIEF
        ctrl = DialogueStyleController(user_model=user)
        msg = ctrl.format_success("テスト実行", "100 passed")
        assert "完了" in msg
        assert "100 passed" not in msg

    def test_format_error_masks_secrets(self):
        ctrl = DialogueStyleController()
        msg = ctrl.format_error("API call", "Error: api_key=secret123 failed")
        assert "secret123" not in msg
        assert "***" in msg

    def test_format_safety_warning(self):
        ctrl = DialogueStyleController()
        msg = ctrl.format_safety_warning("危険な操作です")
        assert "⚠️" in msg

    def test_format_daily_summary(self):
        ctrl = DialogueStyleController()
        msg = ctrl.format_daily_summary(completed=5, failed=1, pending=2)
        assert "完了: 5" in msg


class TestSummaryDigest:
    def test_to_text(self):
        from aegis_ai.dialogue import SummaryDigest
        d = SummaryDigest(
            period="daily",
            completed_tasks=10,
            failed_tasks=2,
            pending_approvals=1,
            important_warnings=["disk low"],
            recommendations=["run cleanup"],
        )
        text = d.to_text()
        assert "完了: 10" in text
        assert "disk low" in text
        assert "run cleanup" in text

    def test_to_dict(self):
        from aegis_ai.dialogue import SummaryDigest
        d = SummaryDigest(digest_id="d1", period="session", completed_tasks=3)
        data = d.to_dict()
        assert data["digest_id"] == "d1"
        assert data["completed_tasks"] == 3


class TestUserModelStoreFeedback:
    def test_brief_feedback(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        store.record_user_feedback("短くして")
        assert store.model.detail_level == DetailLevel.BRIEF

    def test_detailed_feedback(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        store.record_user_feedback("詳しく説明して")
        assert store.model.detail_level == DetailLevel.DETAILED

    def test_stop_feedback(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        store.record_user_feedback("勝手にやらないで")
        assert store.model.autonomy_level == AutonomyLevel.LOW
        assert store.model.approval_strictness == ApprovalStrictness.STRICT

    def test_automate_feedback(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        store.record_user_feedback("もっと自動でやって")
        assert store.model.autonomy_level == AutonomyLevel.HIGH

    def test_noisy_feedback(self, tmpdir):
        store = UserModelStore(data_dir=tmpdir)
        store.record_user_feedback("うるさい")
        assert store.model.notification_preference == NotificationPreference.MINIMAL


class TestUserModelDict:
    def test_to_dict_has_all_fields(self):
        m = UserModel()
        d = m.to_dict()
        assert "preferred_report_format" in d
        assert "allowed_proactive_categories" in d
        assert "disallowed_proactive_categories" in d
