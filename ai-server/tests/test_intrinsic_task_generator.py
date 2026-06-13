"""Tests for IntrinsicTaskGenerator."""

from __future__ import annotations

import time

import pytest

from aegis_ai.desire.desire_system import DesireSnapshot
from aegis_ai.desire.intrinsic_task_generator import (
    IntrinsicTask,
    IntrinsicTaskGenerator,
    RiskLevel,
    _fingerprint,
)


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
        max_frustration=max(frusts.values()),
        top_unsatisfied_desires=top,
        desires=dims,
    )


class TestIntrinsicTaskGeneration:
    def test_high_frustration_generates_tasks(self):
        snap = _make_snapshot({"learning_progress": 1.0})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={"read_file"})
        tasks = gen.generate(snap)
        lp = [t for t in tasks if t.source_desire == "learning_progress"]
        assert len(lp) >= 1

    def test_low_frustration_generates_no_tasks(self):
        snap = _make_snapshot({"learning_progress": 6.5})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={"read_file"})
        tasks = gen.generate(snap)
        assert not any(t.source_desire == "learning_progress" for t in tasks)

    def test_cooldown_prevents_duplicate(self):
        snap = _make_snapshot({"learning_progress": 1.0})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={"read_file"})
        tasks = gen.generate(snap)
        assert len(tasks) > 0
        first = tasks[0]
        gen.record_execution(first)
        tasks2 = gen.generate(snap)
        assert not any(t.fingerprint == first.fingerprint for t in tasks2)

    def test_high_risk_requires_approval(self):
        snap = _make_snapshot({"maintenance": 1.0})
        gen = IntrinsicTaskGenerator(
            frustration_threshold=2.0,
            available_capabilities={"read_file", "delete_file"},
        )
        tasks = gen.generate(snap)
        high = [t for t in tasks if t.risk_level in (RiskLevel.HIGH, RiskLevel.FORBIDDEN)]
        for t in high:
            assert t.requires_user_approval is True

    def test_missing_capability_upgrades_to_approval(self):
        snap = _make_snapshot({"curiosity": 1.0})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities=set())
        tasks = gen.generate(snap)
        for t in tasks:
            if t.required_capabilities:
                assert t.requires_user_approval is True

    def test_social_connection_has_cooldown(self):
        snap = _make_snapshot({"social_connection": 1.0})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={"notify_user"})
        tasks = gen.generate(snap)
        sc = [t for t in tasks if t.source_desire == "social_connection"]
        for t in sc:
            assert t.cooldown_seconds > 0

    def test_fingerprint_deterministic(self):
        fp1 = _fingerprint("curiosity", "Research topic")
        fp2 = _fingerprint("curiosity", "Research topic")
        assert fp1 == fp2

    def test_task_has_all_fields(self):
        snap = _make_snapshot({"reliability": 1.0})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={"run_command"})
        tasks = gen.generate(snap)
        assert len(tasks) > 0
        t = tasks[0]
        assert t.task_id
        assert t.source_desire
        assert t.title
        assert t.description
        assert t.priority >= 0
        assert isinstance(t.expected_desire_effects, dict)
        assert isinstance(t.required_capabilities, list)
        assert isinstance(t.risk_level, RiskLevel)
        assert isinstance(t.requires_user_approval, bool)
        assert t.cooldown_seconds > 0
        assert t.created_at > 0
        assert t.reason
        assert t.fingerprint

    def test_tasks_sorted_by_priority(self):
        snap = _make_snapshot({"system_safety": 0.5, "reliability": 1.0, "curiosity": 2.0})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={"read_file", "run_command"})
        tasks = gen.generate(snap)
        priorities = [t.priority for t in tasks]
        assert priorities == sorted(priorities, reverse=True)

    def test_all_desires_can_generate(self):
        for name in [
            "user_helpfulness", "learning_progress", "curiosity", "system_safety",
            "reliability", "autonomy", "social_connection", "creativity",
            "purpose", "maintenance",
        ]:
            snap = _make_snapshot({name: 0.0})
            gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={
                "read_file", "run_command", "web_search", "notify_user", "delete_file",
            })
            tasks = gen.generate(snap)
            matching = [t for t in tasks if t.source_desire == name]
            assert len(matching) >= 1, f"No tasks generated for {name}"

    def test_cooldown_map_persists_across_generate_calls(self):
        snap = _make_snapshot({"reliability": 0.0})
        gen = IntrinsicTaskGenerator(frustration_threshold=2.0, available_capabilities={"run_command", "read_file"})
        tasks = gen.generate(snap)
        assert len(tasks) >= 1
        gen.record_execution(tasks[0])
        assert gen.is_cooling_down(tasks[0])
