"""Tests for DesireActionEvaluator."""

from __future__ import annotations

import time

import pytest

from aegis_ai.desire.desire_action_evaluator import DesireActionEvaluator, TaskEvaluation
from aegis_ai.desire.desire_system import DesireSnapshot
from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask, RiskLevel


def _make_snapshot(overrides: dict[str, float] | None = None) -> DesireSnapshot:
    now = int(time.time() * 1000)
    dims: dict[str, dict] = {}
    for name in [
        "user_helpfulness", "learning_progress", "curiosity", "system_safety",
        "reliability", "autonomy", "social_connection", "creativity",
        "purpose", "maintenance",
    ]:
        val = 5.0
        expected = 7.0
        if overrides and name in overrides:
            val = overrides[name]
        frust = max(0.0, expected - val)
        dims[name] = {
            "value": val, "expected_value": expected, "frustration": frust,
            "decay_rate_per_hour": 0.1, "recovery_rate": 0.2,
            "safety_category": "general", "visible": True, "hidden": False,
            "last_updated_at": now,
        }
    frusts = {n: d["frustration"] for n, d in dims.items()}
    top = sorted(frusts, key=lambda n: frusts[n], reverse=True)
    return DesireSnapshot(
        timestamp=now,
        average_frustration=sum(frusts.values()) / len(frusts),
        max_frustration=max(frustrations := frusts.values()) if frusts else 0.0,
        top_unsatisfied_desires=top,
        desires=dims,
    )


def _make_task(task_id: str, desire: str, risk: RiskLevel = RiskLevel.LOW,
               caps: list[str] | None = None, effects: dict[str, float] | None = None,
               fp: str = "") -> IntrinsicTask:
    now = int(time.time() * 1000)
    return IntrinsicTask(
        task_id=task_id, source_desire=desire, title=f"Task {task_id}",
        description="", priority=0.5, expected_desire_effects=effects or {desire: 1.5},
        required_capabilities=caps or [], risk_level=risk,
        requires_user_approval=False, cooldown_seconds=3600,
        created_at=now, reason="", fingerprint=fp or f"fp-{task_id}",
    )


class TestDesireGain:
    def test_high_frustration_high_gain(self):
        snap = _make_snapshot({"curiosity": 0.0})
        task = _make_task("t1", "curiosity", effects={"curiosity": 2.0})
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert ev[0].desire_gain_score > 0.5

    def test_low_frustration_low_gain(self):
        snap = _make_snapshot({"curiosity": 6.5})
        task = _make_task("t1", "curiosity", effects={"curiosity": 2.0})
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert ev[0].desire_gain_score < 0.3


class TestRiskScore:
    def test_high_risk_high_score(self):
        snap = _make_snapshot()
        task = _make_task("t1", "maintenance", risk=RiskLevel.HIGH)
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert ev[0].risk_score >= 0.7

    def test_no_risk_low_score(self):
        snap = _make_snapshot()
        task = _make_task("t1", "curiosity", risk=RiskLevel.NONE)
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert ev[0].risk_score == 0.0


class TestAnnoyance:
    def test_notify_high_annoyance(self):
        snap = _make_snapshot()
        task = _make_task("t1", "social_connection", caps=["notify_user"])
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert ev[0].annoyance_score >= 0.5

    def test_no_notify_low_annoyance(self):
        snap = _make_snapshot()
        task = _make_task("t1", "curiosity", caps=["read_file"])
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert ev[0].annoyance_score == 0.0


class TestCapabilityFit:
    def test_all_caps_available(self):
        snap = _make_snapshot()
        task = _make_task("t1", "curiosity", caps=["read_file"])
        ev = DesireActionEvaluator(available_capabilities={"read_file"}).score_candidates([task], snap)
        assert ev[0].capability_fit_score == 1.0

    def test_no_caps_available(self):
        snap = _make_snapshot()
        task = _make_task("t1", "curiosity", caps=["web_search"])
        ev = DesireActionEvaluator(available_capabilities=set()).score_candidates([task], snap)
        assert ev[0].capability_fit_score == 0.0

    def test_no_caps_needed(self):
        snap = _make_snapshot()
        task = _make_task("t1", "autonomy", caps=[])
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert ev[0].capability_fit_score == 1.0


class TestRepeatPenalty:
    def test_recent_fingerprint_penalized(self):
        snap = _make_snapshot()
        task = _make_task("t1", "curiosity", fp="fp-dup")
        ev = DesireActionEvaluator(recent_fingerprints=["fp-dup"]).score_candidates([task], snap)
        assert ev[0].repeat_penalty > 0.0

    def test_no_repeat_no_penalty(self):
        snap = _make_snapshot()
        task = _make_task("t1", "curiosity", fp="fp-new")
        ev = DesireActionEvaluator(recent_fingerprints=["fp-other"]).score_candidates([task], snap)
        assert ev[0].repeat_penalty == 0.0


class TestFinalScore:
    def test_low_risk_high_gain_wins(self):
        snap = _make_snapshot({"curiosity": 0.0, "maintenance": 0.0})
        safe = _make_task("safe", "curiosity", risk=RiskLevel.NONE, effects={"curiosity": 2.0})
        risky = _make_task("risky", "maintenance", risk=RiskLevel.HIGH, effects={"maintenance": 2.0})
        ev = DesireActionEvaluator().score_candidates([safe, risky], snap)
        assert ev[0].task_id == "safe"

    def test_forbidden_zero_success(self):
        snap = _make_snapshot()
        task = _make_task("t1", "curiosity", risk=RiskLevel.FORBIDDEN)
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert ev[0].success_probability == 0.0


class TestEvaluationFields:
    def test_all_fields_present(self):
        snap = _make_snapshot()
        task = _make_task("t1", "curiosity")
        ev = DesireActionEvaluator().score_candidates([task], snap)
        assert len(ev) == 1
        e = ev[0]
        assert isinstance(e, TaskEvaluation)
        assert 0.0 <= e.desire_gain_score <= 1.0
        assert 0.0 <= e.risk_score <= 1.0
        assert 0.0 <= e.annoyance_score <= 1.0
        assert 0.0 <= e.capability_fit_score <= 1.0
        assert 0.0 <= e.novelty_score <= 1.0
        assert 0.0 <= e.repeat_penalty <= 1.0
        assert 0.0 <= e.success_probability <= 1.0
        assert 0.0 <= e.final_score <= 1.0
        assert e.reason
        assert isinstance(e.predicted_desire_effects, dict)
