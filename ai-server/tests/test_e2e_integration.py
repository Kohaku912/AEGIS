"""E2E integration tests for TaskManager and SleepManager integration.

These tests verify that the integration between managers is properly wired.
"""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from aegis_ai.web import dashboard_routes


def _runtime(tmp_path):
    """Create a mock runtime for testing."""
    from approval import ApprovalStore
    from event_bus import EventBus
    from policy_engine import PolicyEngine
    from tool_broker import ToolBroker
    from tool_registry import ToolRegistry

    from aegis_ai.approval import ApprovalQueue
    from aegis_ai.audit import AuditLog
    from aegis_ai.audit.audit_manager import AuditManager
    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai.event.event_manager import EventManager
    from aegis_ai.memory.memory_manager import MemoryManager
    from aegis_ai.memory.sleep import SleepManager
    from aegis_ai.settings.store import SettingsStore
    from aegis_ai.status.status_manager import StatusManager
    from aegis_ai.task.task_manager import TaskManager

    data_dir = tmp_path / "data"
    catalog = CapabilityCatalog(
        capabilities_dir=str(data_dir / "capabilities"),
        apps_dir=str(data_dir / "apps"),
    )
    registry = ToolRegistry()
    audit_log = AuditLog(path=str(data_dir / "audit.jsonl"))
    approval_store = ApprovalStore()
    policy_engine = PolicyEngine(approval_store=approval_store, data_dir=str(data_dir))
    broker = ToolBroker(registry=registry, policy_engine=policy_engine, audit_log=audit_log, catalog=catalog)
    event_bus = EventBus()
    event_manager = EventManager(event_bus=event_bus, data_dir=str(data_dir))
    audit_manager = AuditManager(audit_log=audit_log, data_dir=str(data_dir))
    status_manager = StatusManager(event_manager=event_manager)
    memory_manager = MemoryManager(event_manager=event_manager)
    task_manager = TaskManager(event_manager=event_manager, audit_manager=audit_manager, data_dir=str(data_dir))
    sleep_manager = SleepManager(memory_manager=memory_manager, event_manager=event_manager, audit_manager=audit_manager)

    return SimpleNamespace(
        settings_store=SettingsStore(
            path=str(tmp_path / "config" / "settings.json"),
            audit_path=str(data_dir / "settings_audit.jsonl"),
        ),
        audit_log=audit_log,
        capability_catalog=catalog,
        folder_registry=catalog.get_folder_registry(),
        tool_registry=registry,
        event_bus=event_bus,
        approval_store=approval_store,
        approval_queue=ApprovalQueue(data_dir=str(data_dir / "approvals"), audit_log=audit_log),
        policy_engine=policy_engine,
        tool_broker=broker,
        llm_gateway=object(),
        autonomous_loop=None,
        start_autonomous_if_enabled=lambda: None,
        status_manager=status_manager,
        event_manager=event_manager,
        audit_manager=audit_manager,
        memory_manager=memory_manager,
        task_manager=task_manager,
        sleep_manager=sleep_manager,
    )


class TestTaskManagerIntegration:
    """Tests for TaskManager integration."""

    def test_task_manager_exists(self, tmp_path):
        """Verify runtime has task_manager attribute."""
        rt = _runtime(tmp_path)
        assert hasattr(rt, 'task_manager')
        assert rt.task_manager is not None

    def test_task_manager_can_create_task(self, tmp_path):
        """Verify TaskManager can create tasks."""
        rt = _runtime(tmp_path)
        task = rt.task_manager.create_task(
            title="Test task",
            source="test",
            goal="Test goal",
        )
        assert task is not None
        assert "task_id" in task

    def test_task_manager_can_complete_task(self, tmp_path):
        """Verify TaskManager can complete tasks."""
        rt = _runtime(tmp_path)
        task = rt.task_manager.create_task(
            title="Test task",
            source="test",
            goal="Test goal",
        )
        task_id = task["task_id"]
        rt.task_manager.start_task(task_id)
        rt.task_manager.complete_task(task_id, result_summary="done")

    def test_task_manager_can_fail_task(self, tmp_path):
        """Verify TaskManager can fail tasks."""
        rt = _runtime(tmp_path)
        task = rt.task_manager.create_task(
            title="Test task",
            source="test",
            goal="Test goal",
        )
        task_id = task["task_id"]
        rt.task_manager.start_task(task_id)
        rt.task_manager.fail_task(task_id, error="Test error")


class TestSleepManagerIntegration:
    """Tests for SleepManager integration."""

    def test_sleep_manager_exists(self, tmp_path):
        """Verify runtime has sleep_manager attribute."""
        rt = _runtime(tmp_path)
        assert hasattr(rt, 'sleep_manager')
        assert rt.sleep_manager is not None

    def test_sleep_manager_has_consolidation_system_attr(self, tmp_path):
        """Verify SleepManager has consolidation_system attribute."""
        rt = _runtime(tmp_path)
        assert hasattr(rt.sleep_manager, '_consolidation_system')

    def test_sleep_manager_can_start_sleep(self, tmp_path):
        """Verify SleepManager can start sleep."""
        rt = _runtime(tmp_path)
        result = rt.sleep_manager.start_sleep(reason="test")
        assert result is True

    def test_sleep_manager_status(self, tmp_path):
        """Verify SleepManager returns status."""
        rt = _runtime(tmp_path)
        status = rt.sleep_manager.get_status()
        assert "state" in status


class TestStatusManagerIntegration:
    """Tests for StatusManager integration."""

    def test_status_manager_exists(self, tmp_path):
        """Verify runtime has status_manager attribute."""
        rt = _runtime(tmp_path)
        assert hasattr(rt, 'status_manager')
        assert rt.status_manager is not None

    def test_status_manager_returns_snapshot(self, tmp_path):
        """Verify StatusManager returns snapshot."""
        rt = _runtime(tmp_path)
        snapshot = rt.status_manager.get_snapshot()
        assert isinstance(snapshot, dict)


class TestApprovalManagerIntegration:
    """Tests for ApprovalManager integration with TaskManager."""

    def test_approval_manager_has_task_manager_callback(self, tmp_path):
        """Verify ApprovalManager has task_manager_callback method."""
        from aegis_ai.approval.approval_manager import ApprovalManager
        assert hasattr(ApprovalManager, '_task_manager_callback')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
