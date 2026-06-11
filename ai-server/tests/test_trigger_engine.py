"""Tests for TriggerEngine — rule matching, cooldown, TaskRequest generation."""

from __future__ import annotations

import json
from pathlib import Path

from aegis_schema.models import Event, EventPriority, ServerType
from event_bus import EventBus
from trigger_engine import (
    ActionType,
    TriggerEngine,
    TriggerRule,
    create_default_rules,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def _make_event(
    event_id: str = "evt-001",
    event_type: str = "pc.screen_changed",
    server_type: ServerType = ServerType.PC,
    priority: EventPriority = EventPriority.NORMAL,
    severity: int = 5,
) -> Event:
    return Event(
        event_id=event_id,
        event_type=event_type,
        source_server_type=server_type,
        source_server_id="test-server",
        priority=priority,
        severity=severity,
    )


# ═══════════════════════════════════════════════════════════════
# Rule Matching
# ═══════════════════════════════════════════════════════════════

class TestRuleMatching:
    def test_exact_event_type_match(self):
        rule = TriggerRule(
            rule_id="test-rule",
            event_type_pattern="pc.screen_changed",
            action_type=ActionType.OBSERVE,
        )
        event = _make_event(event_type="pc.screen_changed")
        assert rule.matches(event) is True

    def test_event_type_mismatch(self):
        rule = TriggerRule(
            rule_id="test-rule",
            event_type_pattern="pc.screen_changed",
        )
        event = _make_event(event_type="android.notification_received")
        assert rule.matches(event) is False

    def test_wildcard_match(self):
        rule = TriggerRule(
            rule_id="catch-all",
            event_type_pattern="*",
        )
        assert rule.matches(_make_event(event_type="anything.here")) is True

    def test_prefix_wildcard_match(self):
        rule = TriggerRule(
            rule_id="dev-events",
            event_type_pattern="dev.*",
        )
        assert rule.matches(_make_event(event_type="dev.test_failed")) is True
        assert rule.matches(_make_event(event_type="dev.ci_error")) is True
        assert rule.matches(_make_event(event_type="pc.screen_changed")) is False

    def test_server_type_filter(self):
        rule = TriggerRule(
            rule_id="pc-only",
            event_type_pattern="*",
            source_type=ServerType.PC,
        )
        assert rule.matches(_make_event(server_type=ServerType.PC)) is True
        assert rule.matches(_make_event(server_type=ServerType.ANDROID)) is False

    def test_severity_filter(self):
        rule = TriggerRule(
            rule_id="high-severity",
            event_type_pattern="*",
            min_severity=7,
        )
        assert rule.matches(_make_event(severity=8)) is True
        assert rule.matches(_make_event(severity=3)) is False
        assert rule.matches(_make_event(severity=7)) is True  # boundary

    def test_priority_filter(self):
        rule = TriggerRule(
            rule_id="urgent-only",
            event_type_pattern="*",
            min_priority=EventPriority.URGENT,
        )
        assert rule.matches(_make_event(priority=EventPriority.URGENT)) is True
        assert rule.matches(_make_event(priority=EventPriority.NORMAL)) is False

    def test_disabled_rule_never_matches(self):
        rule = TriggerRule(
            rule_id="disabled",
            event_type_pattern="*",
            enabled=False,
        )
        assert rule.matches(_make_event()) is False

    def test_combined_filters(self):
        """All filters must match (AND logic)."""
        rule = TriggerRule(
            rule_id="specific",
            event_type_pattern="dev.test_*",
            source_type=ServerType.DEV,
            min_severity=6,
            min_priority=EventPriority.NORMAL,
        )
        # All match
        assert rule.matches(Event(
            event_id="e1", event_type="dev.test_failed",
            source_server_type=ServerType.DEV, source_server_id="dev-1",
            severity=7, priority=EventPriority.URGENT,
        )) is True
        # Wrong server type
        assert rule.matches(Event(
            event_id="e2", event_type="dev.test_failed",
            source_server_type=ServerType.PC, source_server_id="pc-1",
            severity=7, priority=EventPriority.URGENT,
        )) is False


# ═══════════════════════════════════════════════════════════════
# Trigger Engine
# ═══════════════════════════════════════════════════════════════

class TestTriggerEngine:
    def test_matching_event_generates_task(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test",
            event_type_pattern="pc.screen_changed",
            action_type=ActionType.OBSERVE,
            cooldown_seconds=0,  # no cooldown for test
        ))

        event = _make_event(event_type="pc.screen_changed")
        task = engine.on_event(event)

        assert task is not None
        assert task.action_type == ActionType.OBSERVE
        assert task.triggered_by_event_id == "evt-001"
        assert task.triggered_by_rule_id == "test"

    def test_non_matching_event_returns_none(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test",
            event_type_pattern="dev.test_*",
            action_type=ActionType.SELF_DEV,
            cooldown_seconds=0,
        ))

        event = _make_event(event_type="pc.screen_changed")
        task = engine.on_event(event)
        assert task is None

    def test_multiple_rules_first_wins(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="rule-a",
            event_type_pattern="*",
            action_type=ActionType.NOTIFY,
            cooldown_seconds=0,
        ))
        engine.add_rule(TriggerRule(
            rule_id="rule-b",
            event_type_pattern="*",
            action_type=ActionType.ALERT,
            cooldown_seconds=0,
        ))

        task = engine.on_event(_make_event())
        assert task is not None
        assert task.triggered_by_rule_id == "rule-a"  # first registered


# ═══════════════════════════════════════════════════════════════
# Cooldown
# ═══════════════════════════════════════════════════════════════

class TestCooldown:
    def test_cooldown_blocks_rapid_activation(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test",
            event_type_pattern="*",
            cooldown_seconds=10.0,
        ))

        # First activation — allowed
        task1 = engine.on_event(_make_event("evt-1"))
        assert task1 is not None

        # Second activation within cooldown — blocked
        task2 = engine.on_event(_make_event("evt-2"))
        assert task2 is None

    def test_cooldown_allows_after_reset(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test",
            event_type_pattern="*",
            cooldown_seconds=10.0,
        ))

        engine.on_event(_make_event("evt-1"))
        engine.reset_cooldown("test")

        task2 = engine.on_event(_make_event("evt-2"))
        assert task2 is not None

    def test_cooldown_zero_allows_all(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test",
            event_type_pattern="*",
            cooldown_seconds=0,
        ))

        assert engine.on_event(_make_event("e1")) is not None
        assert engine.on_event(_make_event("e2")) is not None
        assert engine.on_event(_make_event("e3")) is not None

    def test_cooldown_key_scoping(self):
        """Rules with different cooldown_keys have independent cooldowns."""
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="rule-a",
            event_type_pattern="pc.*",
            cooldown_seconds=10.0,
            cooldown_key="scope-pc",
        ))
        engine.add_rule(TriggerRule(
            rule_id="rule-b",
            event_type_pattern="android.*",
            cooldown_seconds=10.0,
            cooldown_key="scope-android",
        ))

        # Trigger rule-a
        task = engine.on_event(_make_event("pc-1", event_type="pc.screen_changed"))
        assert task is not None

        # Same rule-a should be blocked
        task = engine.on_event(_make_event("pc-2", event_type="pc.screen_changed"))
        assert task is None

        # But rule-b should still fire (different cooldown scope)
        task = engine.on_event(
            _make_event("android-1", event_type="android.notification_received",
                       server_type=ServerType.ANDROID)
        )
        assert task is not None


# ═══════════════════════════════════════════════════════════════
# Task Queue
# ═══════════════════════════════════════════════════════════════

class TestTaskQueue:
    def test_drain_tasks_returns_all(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test", event_type_pattern="*", cooldown_seconds=0,
        ))

        engine.on_event(_make_event("e1"))
        engine.on_event(_make_event("e2"))

        tasks = engine.drain_tasks()
        assert len(tasks) == 2

    def test_drain_clears_queue(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test", event_type_pattern="*", cooldown_seconds=0,
        ))

        engine.on_event(_make_event("e1"))
        engine.drain_tasks()
        assert engine.pending_task_count() == 0

    def test_task_queue_size_limit(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test", event_type_pattern="*", cooldown_seconds=0,
        ))

        for i in range(150):
            engine.on_event(_make_event(f"evt-{i}"))

        tasks = engine.drain_tasks()
        assert len(tasks) <= 100  # MAX_TASK_QUEUE


# ═══════════════════════════════════════════════════════════════
# TaskRequest
# ═══════════════════════════════════════════════════════════════

class TestTaskRequest:
    def test_task_request_has_all_fields(self):
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test",
            event_type_pattern="*",
            action_type=ActionType.RESEARCH,
            cooldown_seconds=0,
        ))

        event = Event(
            event_id="evt-special",
            event_type="web.rss_updated",
            source_server_type=ServerType.BROWSER,
            source_server_id="browser-1",
            severity=6,
            priority=EventPriority.NORMAL,
            payload_json='{"feed":"test"}',
        )
        task = engine.on_event(event)

        assert task is not None
        assert task.task_id.startswith("task_")
        assert task.action_type == ActionType.RESEARCH
        assert task.triggered_by_event_id == "evt-special"
        assert task.source_server_type == ServerType.BROWSER
        assert task.source_server_id == "browser-1"
        assert task.payload_snapshot == '{"feed":"test"}'
        assert "web.rss_updated" in task.context_summary
        assert task.created_at_ms > 0


# ═══════════════════════════════════════════════════════════════
# Default Rules
# ═══════════════════════════════════════════════════════════════

class TestDefaultRules:
    def test_default_rules_exist(self):
        rules = create_default_rules()
        assert len(rules) > 5

    def test_default_rules_all_enabled(self):
        rules = create_default_rules()
        for rule in rules:
            assert rule.enabled is True

    def test_default_rules_all_have_ids(self):
        rules = create_default_rules()
        for rule in rules:
            assert rule.rule_id != ""

    def test_default_rules_match_sample_events(self):
        """All sample events should match at least one default rule."""
        engine = TriggerEngine()
        for rule in create_default_rules():
            engine.add_rule(rule)

        with open(SAMPLES_DIR / "events.json", encoding="utf-8") as f:
            data = json.load(f)

        matched_count = 0
        for item in data:
            event = Event.model_validate(item)
            task = engine.on_event(event)
            if task is not None:
                matched_count += 1

        # Most sample events should trigger at least one rule
        assert matched_count >= 5, f"Only {matched_count}/10 events triggered a rule"

    def test_test_failure_triggers_self_dev(self):
        engine = TriggerEngine()
        for rule in create_default_rules():
            engine.add_rule(rule)

        event = Event(
            event_id="evt-fail",
            event_type="dev.test_failed",
            source_server_type=ServerType.DEV,
            source_server_id="dev-1",
            severity=8,
            priority=EventPriority.URGENT,
        )
        task = engine.on_event(event)
        assert task is not None
        assert task.action_type == ActionType.SELF_DEV

    def test_security_event_triggers_alert(self):
        engine = TriggerEngine()
        for rule in create_default_rules():
            engine.add_rule(rule)

        event = Event(
            event_id="evt-sec",
            event_type="pc.security_unauthorized_access",
            source_server_type=ServerType.PC,
            source_server_id="pc-1",
            severity=10,
            priority=EventPriority.URGENT,
        )
        task = engine.on_event(event)
        assert task is not None
        assert task.action_type == ActionType.ALERT


# ═══════════════════════════════════════════════════════════════
# Integration: EventBus + TriggerEngine
# ═══════════════════════════════════════════════════════════════

class TestIntegration:
    def test_eventbus_to_triggerengine_flow(self):
        """Full flow: publish event → subscriber → rule match → TaskRequest."""
        bus = EventBus()
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test",
            event_type_pattern="pc.*",
            action_type=ActionType.OBSERVE,
            cooldown_seconds=0,
        ))

        # Subscribe TriggerEngine to EventBus
        bus.subscribe(engine.on_event)

        # Publish event
        event = _make_event(event_type="pc.screen_changed")
        bus.publish(event)

        # TriggerEngine should have generated a task
        tasks = engine.drain_tasks()
        assert len(tasks) == 1
        assert tasks[0].triggered_by_event_id == "evt-001"

    def test_cooldown_integration(self):
        """Cooldown suppresses rapid repeated activations in the full flow."""
        bus = EventBus()
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="test",
            event_type_pattern="*",
            cooldown_seconds=10.0,
        ))
        bus.subscribe(engine.on_event)

        # First event — triggers
        bus.publish(_make_event("e1"))
        # Second event — suppressed by cooldown
        bus.publish(_make_event("e2"))
        # Third event — also suppressed
        bus.publish(_make_event("e3"))

        tasks = engine.drain_tasks()
        assert len(tasks) == 1

    def test_high_severity_events_not_throttled_by_low_rules(self):
        """Each rule has its own cooldown. High-severity rule can fire independently."""
        bus = EventBus()
        engine = TriggerEngine()
        engine.add_rule(TriggerRule(
            rule_id="low",
            event_type_pattern="*",
            min_severity=0,
            cooldown_seconds=9999,  # Long cooldown
        ))
        engine.add_rule(TriggerRule(
            rule_id="high",
            event_type_pattern="*",
            min_severity=9,
            cooldown_seconds=0,  # No cooldown for critical
        ))
        bus.subscribe(engine.on_event)

        # A normal event — hits low rule, starts cooldown
        bus.publish(_make_event("e1", severity=3))
        # Another normal event — blocked by low rule cooldown, doesn't match high
        bus.publish(_make_event("e2", severity=3))
        # Critical event — matches high rule (cooldown=0), fires
        bus.publish(_make_event("e3", severity=9))

        tasks = engine.drain_tasks()
        # e1 matches both low+high (low wins), e2 suppressed, e3 matches high
        assert len(tasks) == 2
        assert tasks[1].triggered_by_event_id == "e3"
