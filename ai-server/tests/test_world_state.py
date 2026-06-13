"""Tests for World State module."""

from __future__ import annotations

import shutil
import tempfile
import time

import pytest

from aegis_ai.world.world_state_store import WorldStateStore
from aegis_ai.world.world_state_types import (
    AndroidState,
    ApprovalState,
    BrowserState,
    DesireStateSummary,
    DevState,
    PCState,
    Staleness,
    StateEntry,
    TaskPhase,
    TaskState,
    WorldState,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestStateEntry:
    def test_create_entry(self):
        entry = StateEntry(key="url", value="https://example.com", source="observation")
        assert entry.key == "url"
        assert entry.staleness == Staleness.FRESH

    def test_is_stale_expired(self):
        entry = StateEntry(
            key="test", value="v", expires_at=int(time.time() * 1000) - 1000,
        )
        assert entry.is_stale() is True

    def test_is_stale_fresh(self):
        entry = StateEntry(key="test", value="v")
        assert entry.is_stale() is False

    def test_to_context_string_masks_secret(self):
        entry = StateEntry(key="api_key", value="sk-abcdef1234567890", sensitivity="secret")
        ctx = entry.to_context_string()
        assert "sk-abcdef" not in ctx
        assert "***MASKED***" in ctx

    def test_to_dict(self):
        entry = StateEntry(key="url", value="https://example.com", confidence=0.9)
        d = entry.to_dict()
        assert d["key"] == "url"
        assert d["confidence"] == 0.9


class TestDeviceStates:
    def test_pc_state_to_context(self):
        state = PCState(active_window_title="Chrome", active_process="chrome.exe")
        ctx = state.to_context_string()
        assert "Chrome" in ctx
        assert "chrome.exe" in ctx

    def test_browser_state_to_context(self):
        state = BrowserState(current_url="https://example.com", page_title="Example")
        ctx = state.to_context_string()
        assert "example.com" in ctx

    def test_browser_login_detected(self):
        state = BrowserState(visible_text_summary="Please sign in to continue")
        assert "sign in" in state.visible_text_summary.lower()

    def test_android_state_to_context(self):
        state = AndroidState(current_package="com.example.app", permission_dialog_detected=True)
        ctx = state.to_context_string()
        assert "com.example.app" in ctx
        assert "PERMISSION_DIALOG" in ctx

    def test_dev_state_to_context(self):
        state = DevState(active_repo="aegis", active_branch="main", test_status="passing")
        ctx = state.to_context_string()
        assert "aegis" in ctx
        assert "passing" in ctx


class TestTaskAndApprovalState:
    def test_task_state_idle(self):
        state = TaskState()
        ctx = state.to_context_string()
        assert "idle" in ctx.lower() or "No active" in ctx

    def test_task_state_executing(self):
        state = TaskState(
            active_task_id="t1", status=TaskPhase.EXECUTING,
            blocked_reason="", current_step="step_2",
        )
        ctx = state.to_context_string()
        assert "t1" in ctx
        assert "executing" in ctx

    def test_approval_state_none(self):
        state = ApprovalState()
        ctx = state.to_context_string()
        assert "No pending" in ctx

    def test_approval_state_pending(self):
        state = ApprovalState(pending_count=3, highest_risk_pending="high")
        ctx = state.to_context_string()
        assert "3" in ctx

    def test_desire_state_summary(self):
        state = DesireStateSummary(
            top_unsatisfied_desires=["curiosity", "autonomy"],
            average_frustration=4.5,
        )
        ctx = state.to_context_string()
        assert "curiosity" in ctx


class TestWorldState:
    def test_create_state(self):
        state = WorldState(world_state_id="ws1", version=1)
        assert state.world_state_id == "ws1"
        assert state.version == 1

    def test_mark_stale(self):
        state = WorldState()
        state.mark_stale("browser_state", "url changed")
        assert state.is_section_stale("browser_state") is True

    def test_to_context_string(self):
        state = WorldState()
        state.task_state = TaskState(active_task_id="t1", status=TaskPhase.EXECUTING)
        ctx = state.to_context_string()
        assert "t1" in ctx

    def test_to_context_masks_secrets(self):
        state = WorldState()
        state.memory_state_summary = "api_key=sk-abcdef1234567890abcdef1234567890"
        ctx = state.to_context_string()
        assert "sk-abcdef" not in ctx

    def test_to_dict(self):
        state = WorldState(world_state_id="ws1")
        d = state.to_dict()
        assert d["world_state_id"] == "ws1"


class TestWorldStateStore:
    def test_create_store(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        assert store.state.world_state_id

    def test_update_from_browser_observation(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.update_from_observation({
            "target": "browser",
            "current_url": "https://example.com",
            "page_title": "Example",
            "visible_text_summary": "Hello world",
            "status": "success",
            "observation_id": "obs1",
        })
        assert store.state.browser_state.current_url == "https://example.com"
        assert store.state.browser_state.page_title == "Example"
        assert store.state.version > 1

    def test_update_from_pc_observation(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.update_from_observation({
            "target": "pc",
            "active_window": "Chrome",
            "active_app": "chrome.exe",
            "status": "success",
            "observation_id": "obs2",
        })
        assert store.state.pc_state.active_window_title == "Chrome"

    def test_update_from_android_observation(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.update_from_observation({
            "target": "android",
            "active_app": "com.example",
            "visible_text_summary": "Main screen",
            "status": "success",
            "observation_id": "obs3",
        })
        assert store.state.android_state.current_package == "com.example"

    def test_update_desire_snapshot(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        snap = type("Snap", (), {
            "top_unsatisfied_desires": ["curiosity", "autonomy"],
            "average_frustration": 4.5,
            "max_frustration": 6.0,
        })()
        store.update_from_desire_snapshot(snap)
        assert store.state.desire_state.average_frustration == 4.5
        assert "curiosity" in store.state.desire_state.top_unsatisfied_desires

    def test_update_approval_state(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.update_approval_state(
            pending_count=2, highest_risk="high",
            pending_summaries=["delete file", "send email"],
        )
        assert store.state.approval_state.pending_count == 2

    def test_update_task_state(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.update_task_state(task_id="t1", source="desire_driven", status="executing")
        assert store.state.task_state.active_task_id == "t1"
        assert store.state.task_state.status == TaskPhase.EXECUTING

    def test_mark_stale(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.mark_stale("browser_state", "observation failed")
        assert store.state.is_section_stale("browser_state") is True

    def test_expire_old_entries(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.state.pc_state.last_verified_at = int(time.time() * 1000) - 300_000
        count = store.expire_old_entries()
        assert count >= 1

    def test_diff_states(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        before = WorldState(
            world_state_id="ws1",
            browser_state=BrowserState(current_url="https://old.com"),
            task_state=TaskState(status=TaskPhase.IDLE),
        )
        after = WorldState(
            world_state_id="ws2",
            browser_state=BrowserState(current_url="https://new.com"),
            task_state=TaskState(status=TaskPhase.EXECUTING),
        )
        diff = store.diff_states(before, after)
        assert diff.browser_url_changed is True
        assert diff.task_status_changed is True
        assert diff.changed is True

    def test_summarize_for_context(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        summary = store.summarize_for_context()
        assert "WorldState" in summary

    def test_persistence(self, tmpdir):
        store1 = WorldStateStore(data_dir=tmpdir)
        store1.update_task_state(task_id="t1", status="executing")
        store2 = WorldStateStore(data_dir=tmpdir)
        assert store2.state.task_state.active_task_id == "t1"

    def test_browser_login_detected(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.update_from_observation({
            "target": "browser",
            "visible_text_summary": "Please sign in to your account",
            "status": "success",
        })
        assert store.state.browser_state.login_required is True

    def test_browser_captcha_detected(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.update_from_observation({
            "target": "browser",
            "visible_text_summary": "Please complete the captcha",
            "status": "success",
        })
        assert store.state.browser_state.captcha_or_2fa_detected is True

    def test_secret_not_in_context(self, tmpdir):
        store = WorldStateStore(data_dir=tmpdir)
        store.state.memory_state_summary = "password=secret123 token=abc123"
        ctx = store.summarize_for_context()
        assert "secret123" not in ctx
