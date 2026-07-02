from __future__ import annotations

import json
import time
from types import SimpleNamespace

from aegis_ai.context_builder import ContextBuilder
from aegis_ai.personal_ai.hooks import Hook, HookEngine
from aegis_ai.personal_ai.interruption import InterruptionController
from aegis_ai.personal_ai.situation import SituationModel
from aegis_ai.user_state import UserStateManager


def test_event_ingest_redacts_sensitive_fields(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    manager.ingest_event(
        "android-server",
        {
            "event_type": "android.user_activity.changed",
            "text": "secret dm body",
            "password": "hunter2",
            "input_text": "123456",
            "layout_tree": {"raw": "full ui"},
            "url": "https://example.com/private/path?token=abc",
            "wifi_bssid": "AA:BB:CC:DD:EE:FF",
            "notification_title": "認証コード 123456",
        },
    )

    saved = manager.get_recent_events(limit=1)[0]
    raw = json.dumps(saved, ensure_ascii=False)

    assert "secret dm body" not in raw
    assert "hunter2" not in raw
    assert "123456" not in raw
    assert "full ui" not in raw
    assert "private/path" not in raw
    assert "AA:BB:CC" not in raw
    assert "url_hash" in raw
    assert "wifi_bssid_hash" in raw


def test_pc_activity_sets_attention_and_activity(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    manager.ingest_event(
        "pc-server",
        {
            "event_type": "pc.user_activity.snapshot",
            "process_name": "Code.exe",
            "active_window_title": "AEGIS repo",
            "keyboard_count": 4,
            "mouse_count": 3,
            "idle_ms": 1000,
            "locked": False,
        },
    )

    state = manager.get_current_user_state()
    assert state["attention"]["device"] == "pc"
    assert state["activity"]["label"] == "coding"
    assert state["where"]["label"] == "home_pc_desk"


def test_pc_window_title_is_not_stored_raw(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    manager.ingest_event(
        "pc-server",
        {
            "event_type": "pc.user_activity.snapshot",
            "active_window_title": "Private DM 987654",
            "process_name": "Code.exe",
        },
    )

    saved = manager.get_recent_events(limit=1)[0]
    raw = json.dumps(saved, ensure_ascii=False)

    assert "987654" not in raw
    assert "active_window_title_hash" in raw


def test_pc_poller_skips_unchanged_idle_snapshots_but_keeps_input(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    idle = {"process_name": "Code.exe", "keyboard_count": 0, "mouse_count": 0, "idle_ms": 5000}
    assert manager._should_save_pc_snapshot(idle) is True
    assert manager._should_save_pc_snapshot(idle) is False
    assert manager._should_save_pc_snapshot({**idle, "keyboard_count": 1}) is True
    assert manager._should_save_pc_snapshot({**idle, "mouse_count": 1}) is True


def test_recent_pc_input_beats_android_presence_noise(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    for index in range(5):
        manager.ingest_event(
            "android-server",
            {
                "event_type": "android.heartbeat" if index % 2 else "android.foreground_app.changed",
                "screen_on": True,
                "locked": False,
                "package_name": "com.aegis.android",
            },
        )
    manager.ingest_event(
        "pc-server",
        {
            "event_type": "pc.user_activity.snapshot",
            "process_name": "Code.exe",
            "keyboard_count": 0,
            "mouse_count": 0,
            "idle_ms": 0,
            "locked": False,
        },
    )

    assert manager.get_current_user_state()["attention"]["device"] == "pc"


def test_android_activity_and_home_wifi(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AEGIS_HOME_WIFI_BSSIDS", "aa:bb:cc:dd:ee:ff")
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    manager.ingest_event(
        "android-server",
        {
            "event_type": "android.user_activity.changed",
            "screen_on": True,
            "locked": False,
            "touch_count": 5,
            "foreground_app": "com.discord",
            "layout_category": "chat",
            "wifi_connected": True,
            "wifi_bssid": "AA:BB:CC:DD:EE:FF",
        },
    )

    state = manager.get_current_user_state()
    assert state["where"]["label"] == "home"
    assert state["attention"]["device"] == "android"
    assert state["activity"]["label"] == "chatting"


def test_android_away_when_no_home_wifi_and_location_signal(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AEGIS_HOME_WIFI_BSSIDS", "11:22:33:44:55:66")
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    manager.ingest_event(
        "android-server",
        {
            "event_type": "android.presence.changed",
            "screen_on": True,
            "wifi_connected": False,
            "gps_available": True,
            "latitude_bucket": 35.68,
            "longitude_bucket": 139.76,
            "location_accuracy_m": 50,
        },
    )

    assert manager.get_current_user_state()["where"]["label"] == "away"


def test_archive_manager_encrypts_old_daily_log(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))
    old_ms = int((time.time() - 2 * 24 * 3600) * 1000)
    manager.ingest_event("pc-server", {"event_type": "pc.user_activity.snapshot", "timestamp_ms": old_ms, "process_name": "Code.exe"})

    result = manager.archive_due_logs()
    archives = result["archived"]

    assert len(archives) == 1
    archive_path = tmp_path / "user_state" / "archive" / f"{archives[0]['day']}.jsonl.gz.aesgcm"
    assert archive_path.exists()
    assert not (tmp_path / "user_state" / "timeline" / f"{archives[0]['day']}.jsonl").exists()
    assert b"Code.exe" not in archive_path.read_bytes()


def test_situation_context_interruption_and_hook_use_user_state(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))
    manager.ingest_event(
        "pc-server",
        {
            "event_type": "pc.user_activity.snapshot",
            "process_name": "Steam",
            "keyboard_count": 2,
            "mouse_count": 2,
            "idle_ms": 1000,
            "fullscreen": True,
        },
    )
    situation = SituationModel(data_dir=str(tmp_path / "personal"), user_state_manager=manager)
    state = situation.get_state()
    assert state["activity"]["label"] == "gaming"

    ctx = ContextBuilder(user_state_manager=manager, situation_model=situation).build(triggering_query="status")
    assert "User state:" in ctx.dialogue_policy

    controller = InterruptionController(data_dir=str(tmp_path / "personal"), situation_model=situation)
    decision = controller.decide({"category": "general", "severity": "info"})
    assert decision["decision"] == "batch_later"
    assert controller.decide({"category": "approval_required", "severity": "info"})["decision"] == "send_now"

    hook_engine = HookEngine(data_dir=str(tmp_path / "personal"), user_state_manager=manager)
    hook = Hook(hook_id="h1", name="PC attention", condition={"path": "user_state.attention.device", "op": "eq", "value": "pc"})
    assert hook_engine._condition_matches(hook, {}) is True
