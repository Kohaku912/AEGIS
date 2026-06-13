"""Tests for MotivationArbiter."""

from __future__ import annotations

import time

import pytest

from aegis_ai.autonomous.motivation_arbiter import (
    DecisionType,
    ExternalTask,
    MotivationArbiter,
    MotivationDecision,
)
from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask, RiskLevel


def _ext(task_id: str, source: str = "user", priority: float = 1.0,
         risk: RiskLevel = RiskLevel.LOW, approval: bool = False) -> ExternalTask:
    return ExternalTask(
        task_id=task_id, title=f"Task {task_id}", source=source,
        priority=priority, risk_level=risk, requires_approval=approval,
    )


def _intrinsic(task_id: str, desire: str, priority: float = 0.5,
               risk: RiskLevel = RiskLevel.LOW, approval: bool = False,
               caps: list[str] | None = None, fp: str = "") -> IntrinsicTask:
    now = int(time.time() * 1000)
    return IntrinsicTask(
        task_id=task_id, source_desire=desire, title=f"Desire {desire}",
        description="", priority=priority, expected_desire_effects={desire: 1.0},
        required_capabilities=caps or [], risk_level=risk,
        requires_user_approval=approval, cooldown_seconds=3600,
        created_at=now, reason="", fingerprint=fp or f"fp-{task_id}",
    )


class TestUserExplicitPriority:
    def test_user_task_beats_desire_task(self):
        user = [_ext("u1", priority=1.0)]
        desire = [_intrinsic("d1", "curiosity", priority=0.9, fp="fp-d1")]
        arb = MotivationArbiter()
        d = arb.decide(user_tasks=user, desire_tasks=desire)
        assert d.decision_type == DecisionType.USER_EXPLICIT
        assert d.selected_task.task_id == "u1"


class TestSafetyUrgent:
    def test_safety_desire_beats_regular_desire(self):
        desire = [
            _intrinsic("d-safe", "system_safety", priority=0.3, risk=RiskLevel.NONE, fp="fp-safe"),
            _intrinsic("d-cur", "curiosity", priority=0.9, fp="fp-cur"),
        ]
        arb = MotivationArbiter()
        d = arb.decide(desire_tasks=desire)
        assert d.decision_type == DecisionType.SAFETY_URGENT
        assert d.selected_task.task_id == "d-safe"


class TestCooldownSuppression:
    def test_cooldown_task_skipped(self):
        desire = [_intrinsic("d1", "social_connection", priority=0.5, fp="fp-d1")]
        arb = MotivationArbiter(cooldown_fingerprints={"fp-d1"})
        d = arb.decide(desire_tasks=desire)
        assert d.decision_type == DecisionType.SKIP
        assert any(s["reason"] == "cooldown" for s in d.skipped_tasks)


class TestHighRiskApproval:
    def test_high_risk_requires_approval(self):
        desire = [_intrinsic("d1", "maintenance", priority=0.5,
                             risk=RiskLevel.HIGH, approval=True, fp="fp-d1")]
        arb = MotivationArbiter(available_capabilities={"delete_file"})
        d = arb.decide(desire_tasks=desire)
        assert d.requires_approval is True


class TestCapabilityFilter:
    def test_missing_capability_skips(self):
        desire = [_intrinsic("d1", "curiosity", priority=0.5,
                             caps=["web_search"], fp="fp-d1")]
        arb = MotivationArbiter(available_capabilities=set())
        d = arb.decide(desire_tasks=desire)
        assert d.selected_task is None or d.requires_approval is True


class TestRecentFailureSuppression:
    def test_failed_task_not_selected(self):
        user = [_ext("u1")]
        arb = MotivationArbiter(recent_failures=["u1"])
        d = arb.decide(user_tasks=user)
        assert d.selected_task is None


class TestDesireDrivenSelection:
    def test_safe_desire_task_selected(self):
        desire = [_intrinsic("d1", "reliability", priority=0.6,
                             risk=RiskLevel.LOW, fp="fp-d1")]
        arb = MotivationArbiter(available_capabilities={"run_command"})
        d = arb.decide(desire_tasks=desire)
        assert d.selected_task is not None
        assert d.decision_type in (DecisionType.SAFETY_URGENT, DecisionType.DESIRE_DRIVEN)


class TestDeduplication:
    def test_already_executed_skipped(self):
        user = [_ext("u1")]
        arb = MotivationArbiter(recent_task_ids=["u1"])
        d = arb.decide(user_tasks=user)
        assert d.selected_task is None


class TestSkipDecision:
    def test_no_tasks_returns_skip(self):
        arb = MotivationArbiter()
        d = arb.decide()
        assert d.decision_type == DecisionType.SKIP
        assert d.selected_task is None
        assert d.reason


class TestDecisionFields:
    def test_decision_has_all_fields(self):
        user = [_ext("u1")]
        arb = MotivationArbiter()
        d = arb.decide(user_tasks=user)
        assert isinstance(d, MotivationDecision)
        assert d.decision_type
        assert isinstance(d.score, float)
        assert d.reason
        assert isinstance(d.skipped_tasks, list)
        assert isinstance(d.risk_level, RiskLevel)
        assert isinstance(d.requires_approval, bool)
        assert d.created_at > 0
