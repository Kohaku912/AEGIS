"""E2E lifecycle test — full approval lifecycle through Managers."""

from __future__ import annotations

import os
import tempfile
import threading
import time
from types import SimpleNamespace

import pytest

from event_bus import EventBus
from aegis_ai.audit import AuditLog
from aegis_ai.event.event_manager import EventManager
from aegis_ai.audit.audit_manager import AuditManager
from aegis_ai.status.status_manager import StatusManager
from aegis_ai.task.task_manager import TaskManager, TaskStatus
from aegis_ai.notification.notification_manager import NotificationManager
from aegis_ai.memory.memory_manager import MemoryManager
from aegis_ai.memory.sleep import SleepManager


@pytest.fixture
def managers(tmp_path):
    data_dir = str(tmp_path / "data")
    os.makedirs(data_dir, exist_ok=True)

    event_bus = EventBus()
    audit_log = AuditLog(path=os.path.join(data_dir, "audit.jsonl"))

    event_manager = EventManager(event_bus=event_bus, data_dir=data_dir)
    audit_manager = AuditManager(audit_log=audit_log, data_dir=data_dir)
    status_manager = StatusManager(event_manager=event_manager)
    task_manager = TaskManager(event_manager=event_manager, audit_manager=audit_manager, data_dir=data_dir)
    notification_manager = NotificationManager(event_manager=event_manager)
    memory_manager = MemoryManager(event_manager=event_manager)
    sleep_manager = SleepManager(
        memory_manager=memory_manager,
        event_manager=event_manager,
        audit_manager=audit_manager,
    )

    return SimpleNamespace(
        event_manager=event_manager,
        audit_manager=audit_manager,
        status_manager=status_manager,
        task_manager=task_manager,
        notification_manager=notification_manager,
        memory_manager=memory_manager,
        sleep_manager=sleep_manager,
    )


class TestE2ELifecycle:

    def test_full_approval_lifecycle(self, managers):
        tm = managers.task_manager
        am = managers.audit_manager

        task = tm.create_task(title="Deploy new feature", source="user", priority=5)
        task_id = task["task_id"]
        assert task["status"] == "created"

        tm.start_task(task_id)
        assert tm.get_task(task_id)["status"] == "running"

        tm.wait_for_approval(task_id, "appr_e2e_001")
        assert tm.get_task(task_id)["status"] == "waiting_approval"
        assert tm.get_task(task_id)["related_approval_id"] == "appr_e2e_001"

        waiting = tm.list_waiting_approval()
        assert len(waiting) == 1
        assert waiting[0]["task_id"] == task_id

        tm.resume_after_approval(task_id)
        assert tm.get_task(task_id)["status"] == "running"

        tm.complete_task(task_id, result_summary="Feature deployed successfully")
        assert tm.get_task(task_id)["status"] == "completed"
        assert tm.get_task(task_id)["result_summary"] == "Feature deployed successfully"

        audit_result = am.list_recent(limit=20)
        actions = [e["action"] for e in audit_result["entries"]]
        assert "task_created" in actions
        assert "task_completed" in actions

    def test_approval_reject_cancels_task(self, managers):
        tm = managers.task_manager

        task = tm.create_task(title="Delete production data", source="user")
        task_id = task["task_id"]
        tm.start_task(task_id)
        tm.wait_for_approval(task_id, "appr_e2e_002")

        tm.cancel_task(task_id, reason="approval rejected")
        assert tm.get_task(task_id)["status"] == "cancelled"

    def test_autonomous_task_lifecycle(self, managers):
        tm = managers.task_manager

        task = tm.create_task(title="Check server health", source="autonomous")
        task_id = task["task_id"]
        tm.start_task(task_id)
        tm.update_step(task_id, 1, step_name="ping_servers")
        tm.update_step(task_id, 2, step_name="analyze_results")
        tm.complete_task(task_id, result_summary="All servers healthy")

        result = tm.get_task(task_id)
        assert result["status"] == "completed"
        assert result["current_step"] == 2
        assert len(result["steps"]) == 2

    def test_status_manager_snapshot(self, managers):
        sm = managers.status_manager
        snapshot = sm.get_snapshot()
        assert "dashboard" in snapshot
        assert "pc-server" in snapshot

        sm.mark_online("pc-server")
        assert sm.get_server_status("pc-server")["status"] == "online"

        sm.mark_offline("pc-server", error="connection refused")
        assert sm.get_server_status("pc-server")["status"] == "offline"

    def test_memory_sleep_lifecycle(self, managers):
        sm = managers.sleep_manager
        am = managers.audit_manager

        status = sm.get_status()
        assert status["state"] == "idle"

        sm.start_sleep(reason="test")
        import time as t
        t.sleep(0.5)

        status = sm.get_status()
        assert status["state"] in ("running", "completed")

        audit_result = am.list_recent(limit=10)
        actions = [e["action"] for e in audit_result["entries"]]
        assert "sleep_started" in actions

    def test_notification_lifecycle(self, managers):
        nm = managers.notification_manager

        notif = nm.create_notification(title="Server Alert", body="CPU usage high")
        assert notif["status"] == "created"

        nm.mark_read(notif["notification_id"])
        assert nm.get_notification(notif["notification_id"])["status"] == "read"

    def test_event_persistence(self, managers):
        em = managers.event_manager
        from aegis_schema.models import Event, ServerType

        event = Event(
            event_id="evt_e2e_test",
            event_type="task.created",
            source="e2e_test",
            source_server_type=ServerType.AI,
            source_server_id="ai-server",
        )
        em.publish(event)

        events = em.list_recent(limit=10)
        assert len(events["events"]) >= 1

    def test_concurrent_task_operations(self, managers):
        tm = managers.task_manager
        errors = []

        def create_and_complete(i):
            try:
                task = tm.create_task(title=f"Concurrent task {i}", source="system")
                tm.start_task(task["task_id"])
                tm.complete_task(task["task_id"], result_summary=f"Done {i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_and_complete, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert len(errors) == 0
        completed = tm.list_tasks(status="completed")
        assert len(completed) == 10
