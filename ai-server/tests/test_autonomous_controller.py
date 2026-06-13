"""Tests for AutonomousController."""

from __future__ import annotations

import shutil
import tempfile
import time

import pytest

from aegis_ai.autonomous.autonomous_controller import AutonomousController, TickResult
from aegis_ai.autonomous.motivation_arbiter import ExternalTask, MotivationArbiter
from aegis_ai.desire.desire_action_evaluator import DesireActionEvaluator
from aegis_ai.desire.desire_system import DesireSystem
from aegis_ai.desire.intrinsic_task_generator import IntrinsicTaskGenerator, RiskLevel
from trigger_engine import TaskRequest


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _make_system(tmpdir: str, overrides: dict[str, float] | None = None) -> DesireSystem:
    return DesireSystem(data_dir=f"{tmpdir}/desires", initial_values=overrides or {})


class TestTickDecay:
    def test_tick_calls_decay(self, tmpdir):
        desire = _make_system(tmpdir)
        curiosity = desire.get_desire("curiosity")
        curiosity.last_updated_at = int(time.time() * 1000) - 3_600_000
        initial = curiosity.value
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0)
        ctrl = AutonomousController(desire_system=desire, task_generator=gen, data_dir=f"{tmpdir}/ctrl")
        ctrl.tick(now_ms=int(time.time() * 1000))
        assert curiosity.value < initial


class TestTickLowFrustration:
    def test_low_frustration_no_action(self, tmpdir):
        desire = _make_system(tmpdir, {n: 7.0 for n in [
            "user_helpfulness", "learning_progress", "curiosity", "system_safety",
            "reliability", "autonomy", "social_connection", "creativity",
            "purpose", "maintenance",
        ]})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0)
        ctrl = AutonomousController(desire_system=desire, task_generator=gen, data_dir=f"{tmpdir}/ctrl")
        result = ctrl.tick(now_ms=int(time.time() * 1000))
        assert result.task_request is None
        assert result.executed is False
        assert "threshold" in result.reason.lower() or result.decision is None


class TestTickHighFrustration:
    def test_high_frustration_generates_tasks(self, tmpdir):
        desire = _make_system(tmpdir, {"curiosity": 0.0, "system_safety": 0.0})
        gen = IntrinsicTaskGenerator(
            frustration_threshold=2.0,
            available_capabilities={"read_file", "run_command"},
        )
        arbiter = MotivationArbiter(available_capabilities={"read_file", "run_command"})
        ctrl = AutonomousController(
            desire_system=desire, task_generator=gen, arbiter=arbiter,
            data_dir=f"{tmpdir}/ctrl",
        )
        result = ctrl.tick(now_ms=int(time.time() * 1000))
        assert result.decision is not None
        assert result.decision.selected_task is not None


class TestDryRun:
    def test_dry_run_no_execution(self, tmpdir):
        desire = _make_system(tmpdir, {"curiosity": 0.0})
        gen = IntrinsicTaskGenerator(
            frustration_threshold=2.0, available_capabilities={"read_file"},
        )
        arbiter = MotivationArbiter(available_capabilities={"read_file"})
        ctrl = AutonomousController(
            desire_system=desire, task_generator=gen, arbiter=arbiter,
            data_dir=f"{tmpdir}/ctrl",
        )
        result = ctrl.tick(dry_run=True, now_ms=int(time.time() * 1000))
        assert result.dry_run is True
        assert result.executed is False
        assert result.task_request is None


class TestApprovalRequired:
    def test_approval_required_not_executed(self, tmpdir):
        desire = _make_system(tmpdir, {"maintenance": 0.0})
        gen = IntrinsicTaskGenerator(
            frustration_threshold=2.0, available_capabilities={"delete_file"},
        )
        arbiter = MotivationArbiter(available_capabilities={"delete_file"})
        ctrl = AutonomousController(
            desire_system=desire, task_generator=gen, arbiter=arbiter,
            data_dir=f"{tmpdir}/ctrl",
        )
        result = ctrl.tick(now_ms=int(time.time() * 1000))
        if result.decision and result.decision.requires_approval:
            assert result.executed is False
            assert result.task_request is None


class TestTaskRequestConversion:
    def test_intrinsic_to_task_request(self, tmpdir):
        desire = _make_system(tmpdir, {"reliability": 0.0})
        gen = IntrinsicTaskGenerator(
            frustration_threshold=2.0, available_capabilities={"run_command"},
        )
        ctrl = AutonomousController(
            desire_system=desire, task_generator=gen,
            data_dir=f"{tmpdir}/ctrl",
        )
        from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask
        now = int(time.time() * 1000)
        task = IntrinsicTask(
            task_id="test1", source_desire="reliability", title="Check tests",
            description="Run tests", priority=0.5,
            expected_desire_effects={"reliability": 2.0},
            required_capabilities=["run_command"], risk_level=RiskLevel.LOW,
            requires_user_approval=False, cooldown_seconds=3600,
            created_at=now, reason="", fingerprint="fp-test1",
        )
        tr = ctrl.build_task_request_from_intrinsic_task(task, now_ms=now)
        assert isinstance(tr, TaskRequest)
        assert "intrinsic_test1" in tr.task_id
        assert tr.triggered_by_event_type == "desire_driven"


class TestShouldTrigger:
    def test_high_frustration_should_trigger(self, tmpdir):
        desire = _make_system(tmpdir, {"curiosity": 0.0})
        ctrl = AutonomousController(desire_system=desire, data_dir=f"{tmpdir}/ctrl")
        assert ctrl.should_trigger_intrinsic_task(now_ms=int(time.time() * 1000)) is True

    def test_low_frustration_should_not_trigger(self, tmpdir):
        desire = _make_system(tmpdir, {n: 7.0 for n in [
            "user_helpfulness", "learning_progress", "curiosity", "system_safety",
            "reliability", "autonomy", "social_connection", "creativity",
            "purpose", "maintenance",
        ]})
        ctrl = AutonomousController(desire_system=desire, data_dir=f"{tmpdir}/ctrl")
        assert ctrl.should_trigger_intrinsic_task(now_ms=int(time.time() * 1000)) is False


class TestAuditLog:
    def test_audit_recorded(self, tmpdir):
        desire = _make_system(tmpdir)
        ctrl = AutonomousController(desire_system=desire, data_dir=f"{tmpdir}/ctrl")
        ctrl.tick(now_ms=int(time.time() * 1000))
        assert len(ctrl._audit_log) >= 1


class TestUserTaskPriority:
    def test_user_task_beats_desire(self, tmpdir):
        desire = _make_system(tmpdir, {"curiosity": 0.0})
        gen = IntrinsicTaskGenerator(
            frustration_threshold=2.0, available_capabilities={"read_file"},
        )
        arbiter = MotivationArbiter(available_capabilities={"read_file"})
        ctrl = AutonomousController(
            desire_system=desire, task_generator=gen, arbiter=arbiter,
            data_dir=f"{tmpdir}/ctrl",
        )
        user = ExternalTask(
            task_id="user1", title="User task", source="user",
            priority=1.0, risk_level=RiskLevel.LOW, requires_approval=False,
        )
        result = ctrl.tick(user_tasks=[user], now_ms=int(time.time() * 1000))
        if result.decision:
            assert result.decision.selected_task.task_id == "user1"
