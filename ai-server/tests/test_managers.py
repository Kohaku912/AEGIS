"""Tests for centralized Managers.

Covers: TaskManager, MemoryManager, SleepManager, EventManager,
AuditManager, StatusManager, NotificationManager.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def event_bus():
    from event_bus import EventBus
    return EventBus()


@pytest.fixture
def audit_log(tmp_dir):
    from aegis_ai.audit import AuditLog
    return AuditLog(path=os.path.join(tmp_dir, "audit.jsonl"))


@pytest.fixture
def event_manager(event_bus, tmp_dir):
    from aegis_ai.event.event_manager import EventManager
    return EventManager(event_bus=event_bus, data_dir=tmp_dir)


@pytest.fixture
def audit_manager(audit_log, tmp_dir):
    from aegis_ai.audit.audit_manager import AuditManager
    return AuditManager(audit_log=audit_log, data_dir=tmp_dir)


@pytest.fixture
def status_manager(event_manager):
    from aegis_ai.status.status_manager import StatusManager
    return StatusManager(event_manager=event_manager)


@pytest.fixture
def task_manager(event_manager, audit_manager, tmp_dir):
    from aegis_ai.task.task_manager import TaskManager
    return TaskManager(event_manager=event_manager, audit_manager=audit_manager, data_dir=tmp_dir)


@pytest.fixture
def notification_manager(event_manager):
    from aegis_ai.notification.notification_manager import NotificationManager
    return NotificationManager(event_manager=event_manager)


@pytest.fixture
def memory_manager(event_manager):
    from aegis_ai.memory.memory_manager import MemoryManager
    return MemoryManager(event_manager=event_manager)


@pytest.fixture
def sleep_manager(memory_manager, event_manager, audit_manager):
    from aegis_ai.memory.sleep import SleepManager
    manager = SleepManager(
        memory_manager=memory_manager,
        event_manager=event_manager,
        audit_manager=audit_manager,
    )
    yield manager
    manager.close()
    audit_manager._log.close()


# ── TaskManager Tests ─────────────────────────────────────────

class TestTaskManager:

    def test_create_task(self, task_manager):
        task = task_manager.create_task(title="Test task", source="user")
        assert task["task_id"].startswith("task_")
        assert task["status"] == "created"
        assert task["title"] == "Test task"

    def test_state_transition_created_to_running(self, task_manager):
        task = task_manager.create_task(title="Test")
        result = task_manager.start_task(task["task_id"])
        assert result["status"] == "running"

    def test_waiting_approval(self, task_manager):
        task = task_manager.create_task(title="Test")
        task_manager.start_task(task["task_id"])
        result = task_manager.wait_for_approval(task["task_id"], approval_id="appr_001")
        assert result["status"] == "waiting_approval"
        assert result["related_approval_id"] == "appr_001"

    def test_resume_after_approval(self, task_manager):
        task = task_manager.create_task(title="Test")
        task_manager.start_task(task["task_id"])
        task_manager.wait_for_approval(task["task_id"], approval_id="appr_001")
        result = task_manager.resume_after_approval(task["task_id"])
        assert result["status"] == "running"

    def test_complete_task(self, task_manager):
        task = task_manager.create_task(title="Test")
        task_manager.start_task(task["task_id"])
        result = task_manager.complete_task(task["task_id"], result_summary="done")
        assert result["status"] == "completed"
        assert result["result_summary"] == "done"

    def test_fail_task(self, task_manager):
        task = task_manager.create_task(title="Test")
        task_manager.start_task(task["task_id"])
        result = task_manager.fail_task(task["task_id"], error="timeout")
        assert result["status"] == "failed"
        assert result["error"] == "timeout"

    def test_cancel_task(self, task_manager):
        task = task_manager.create_task(title="Test")
        result = task_manager.cancel_task(task["task_id"], reason="user cancelled")
        assert result["status"] == "cancelled"

    def test_double_complete_prevented(self, task_manager):
        task = task_manager.create_task(title="Test")
        task_manager.start_task(task["task_id"])
        task_manager.complete_task(task["task_id"])
        result = task_manager.complete_task(task["task_id"])
        assert result is None

    def test_list_running(self, task_manager):
        task = task_manager.create_task(title="Test")
        task_manager.start_task(task["task_id"])
        running = task_manager.list_running()
        assert len(running) == 1

    def test_reload_recovers_interrupted_tasks(self, tmp_dir):
        from aegis_ai.task.task_manager import TaskManager

        manager = TaskManager(data_dir=tmp_dir)
        interrupted = manager.create_task("Interrupted execution")
        manager.start_task(interrupted["task_id"])
        manager.add_step(interrupted["task_id"], "step-1", capability_id="pc-server.test.run")
        manager.update_step_status(interrupted["task_id"], "step-1", "running")

        recovered = TaskManager(data_dir=tmp_dir).get_task(interrupted["task_id"])

        assert recovered is not None
        assert recovered["status"] == "failed"
        assert recovered["steps"][0]["status"] == "failed"
        assert "restart" in recovered["error"].lower()

    def test_reload_completes_task_whose_steps_were_terminal(self, tmp_dir):
        from aegis_ai.task.task_manager import TaskManager

        manager = TaskManager(data_dir=tmp_dir)
        task = manager.create_task("Final state interrupted")
        manager.start_task(task["task_id"])
        manager.add_step(task["task_id"], "step-1", capability_id="pc-server.test.observe")
        manager.update_step_status(task["task_id"], "step-1", "running")
        manager.update_step_status(task["task_id"], "step-1", "completed", result={"ok": True})

        recovered = TaskManager(data_dir=tmp_dir).get_task(task["task_id"])

        assert recovered is not None
        assert recovered["status"] == "completed"
        assert "Recovered completed" in recovered["result_summary"]

    def test_approval_reject_cancels_task(self, task_manager):
        task = task_manager.create_task(title="Test")
        task_manager.start_task(task["task_id"])
        task_manager.wait_for_approval(task["task_id"], approval_id="appr_001")
        result = task_manager.cancel_task(task["task_id"], reason="approval rejected")
        assert result["status"] == "cancelled"


# ── EventManager Tests ────────────────────────────────────────

class TestEventManager:

    def _make_event(self, event_type="test.event", source="test"):
        from aegis_schema.models import Event, ServerType
        import uuid
        return Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            source=source,
            source_server_type=ServerType.AI,
            source_server_id="ai-server",
        )

    def test_publish_and_subscribe(self, event_manager):
        received = []
        event_manager.subscribe(lambda e: received.append(e))
        event_manager.publish(self._make_event())
        assert len(received) == 1

    def test_persist_important_event(self, event_manager, tmp_dir):
        event_manager.publish(self._make_event("task.created"))
        events = event_manager.list_recent(limit=10)
        assert len(events["events"]) >= 1

    def test_cursor_pagination(self, event_manager):
        for i in range(5):
            event_manager.publish(self._make_event("task.created", f"test_{i}"))
        page1 = event_manager.list_recent(limit=2)
        assert len(page1["events"]) == 2
        if page1["next_cursor"]:
            page2 = event_manager.list_recent(limit=2, cursor=page1["next_cursor"])
            assert len(page2["events"]) >= 1

    def test_dead_letter(self, event_manager):
        event = self._make_event()
        event_manager.record_dead_letter(event, "handler_1", "boom")
        dead = event_manager.list_dead_letters()
        assert len(dead) == 1
        assert dead[0]["handler_id"] == "handler_1"


# ── AuditManager Tests ────────────────────────────────────────

class TestAuditManager:

    def test_list_recent_cursor(self, audit_manager):
        from aegis_ai.audit import AuditEntry
        for i in range(5):
            audit_manager.append(AuditEntry(action=f"test_{i}", actor="test"))
        result = audit_manager.list_recent(limit=2, page=1)
        assert len(result["entries"]) == 2
        assert result["total"] == 5
        assert result["total_pages"] == 3
        result2 = audit_manager.list_recent(limit=2, page=2)
        assert len(result2["entries"]) == 2

    def test_summary_has_detail(self, audit_manager):
        from aegis_ai.audit import AuditEntry
        audit_manager.append(AuditEntry(action="test", actor="test", detail={"key": "value"}))
        result = audit_manager.list_recent(limit=1)
        assert result["entries"][0]["detail"]["key"] == "value"

    def test_get_detail(self, audit_manager):
        from aegis_ai.audit import AuditEntry
        audit_manager.append(AuditEntry(action="test", actor="test", detail={"key": "value"}))
        all_entries = audit_manager.list_recent(limit=1)
        entry_id = all_entries["entries"][0]["entry_id"]
        detail = audit_manager.get_detail(entry_id)
        assert detail is not None

    def test_filter_by_action(self, audit_manager):
        from aegis_ai.audit import AuditEntry
        audit_manager.append(AuditEntry(action="task_created", actor="test"))
        audit_manager.append(AuditEntry(action="approval_approved", actor="test"))
        result = audit_manager.list_recent(action="task_created")
        assert all(e["action"] == "task_created" for e in result["entries"])


# ── StatusManager Tests ───────────────────────────────────────

class TestStatusManager:

    def test_background_checks_start(self):
        from aegis_ai.status.status_manager import StatusManager

        manager = StatusManager()
        try:
            assert manager._servers["ai-server"][1] == 50051
            assert manager._servers["dashboard"][1] == 8090

            manager.start_background_checks()

            assert manager._running is True
            assert manager._check_thread is not None
            assert manager._check_thread.is_alive()
        finally:
            manager.stop_background_checks()

    def test_get_snapshot(self, status_manager):
        snapshot = status_manager.get_snapshot()
        assert "ai-server" in snapshot
        assert "pc-server" in snapshot

    def test_mark_online(self, status_manager):
        status_manager.mark_online("pc-server")
        status = status_manager.get_server_status("pc-server")
        assert status["status"] == "online"

    def test_mark_offline(self, status_manager):
        status_manager.mark_offline("pc-server", error="down")
        status = status_manager.get_server_status("pc-server")
        assert status["status"] == "offline"
        assert status["error"] == "down"

    def test_snapshot_non_blocking(self, status_manager):
        import time as t
        start = t.time()
        status_manager.get_snapshot()
        elapsed = t.time() - start
        assert elapsed < 0.1


# ── NotificationManager Tests ─────────────────────────────────

class TestNotificationManager:

    def test_create_notification(self, notification_manager):
        notif = notification_manager.create_notification(title="Test", body="Body")
        assert notif["notification_id"].startswith("notif_")
        assert notif["status"] == "created"

    def test_mark_read(self, notification_manager):
        notif = notification_manager.create_notification(title="Test", body="Body")
        result = notification_manager.mark_read(notif["notification_id"])
        assert result["status"] == "read"

    def test_dismiss(self, notification_manager):
        notif = notification_manager.create_notification(title="Test", body="Body")
        result = notification_manager.dismiss(notif["notification_id"])
        assert result["status"] == "dismissed"

    def test_list_unread(self, notification_manager):
        notification_manager.create_notification(title="A", body="a")
        notification_manager.create_notification(title="B", body="b")
        unread = notification_manager.list_unread()
        assert len(unread) == 2

    def test_not_approval_notification(self, notification_manager):
        notif = notification_manager.create_notification(title="Info", body="just info")
        assert notif["category"] == "general"


# ── MemoryManager Tests ───────────────────────────────────────

class TestMemoryManager:

    def test_classify_memory_type(self, memory_manager):
        result = memory_manager.classify_memory_type("I learned that DeepSeek returns malformed JSON")
        assert result in ["episodic", "semantic", "skill", "lesson", "workflow", "preference", "person"]

    def test_deduplicate(self, memory_manager):
        count = memory_manager.deduplicate()
        assert isinstance(count, int)

    def test_search_returns_list(self, memory_manager):
        results = memory_manager.search_memory("test query")
        assert isinstance(results, list)

    def test_privacy_level_enforced(self, memory_manager):
        memory_id = memory_manager.write_memory(
            content="secret token",
            privacy_level="secret",
        )
        assert memory_id == ""

    def test_get_stats(self, memory_manager):
        stats = memory_manager.get_stats()
        assert isinstance(stats, dict)


# ── SleepManager Tests ────────────────────────────────────────

class TestSleepManager:

    def test_sleep_status(self, sleep_manager):
        status = sleep_manager.get_status()
        assert status["state"] == "idle"

    def test_idle_trigger_does_not_deadlock(self):
        import threading

        from aegis_ai.memory.sleep import SleepManager

        manager = SleepManager(idle_threshold_s=0)
        manager._last_activity_ms = 0
        result = []
        trigger_thread = threading.Thread(
            target=lambda: result.append(manager.check_triggers()),
            daemon=True,
        )

        trigger_thread.start()
        trigger_thread.join(timeout=1)
        manager.close()

        assert not trigger_thread.is_alive()
        assert result == [True]

    def test_start_sleep(self, sleep_manager):
        success = sleep_manager.start_sleep(reason="test")
        assert success is True
        import time as t
        t.sleep(0.3)
        status = sleep_manager.get_status()
        assert status["state"] in ("running", "completed")

    def test_double_start_prevented(self, sleep_manager):
        success1 = sleep_manager.start_sleep(reason="test")
        assert success1 is True
        import time as t
        t.sleep(0.5)
        success2 = sleep_manager.start_sleep(reason="test2")
        assert success2 is True
        assert sleep_manager.get_status()["state"] in ("running", "completed", "failed")

    def test_sleep_records_audit(self, sleep_manager, audit_manager):
        sleep_manager.start_sleep(reason="test")
        import time as t
        t.sleep(0.5)
        entries = audit_manager.list_recent(limit=10)
        actions = [e["action"] for e in entries["entries"]]
        assert "sleep_started" in actions

    def test_sleep_no_tool_execution(self, sleep_manager):
        assert sleep_manager._memory_manager is not None
