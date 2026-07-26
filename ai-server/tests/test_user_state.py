from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone

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
            "key": "A",
            "raw_key": "B",
            "vk_codes": [65, 66],
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
    assert "\"A\"" not in raw
    assert "\"B\"" not in raw
    assert "vk_codes_redacted" in raw
    assert "private/path" not in raw
    assert "AA:BB:CC" not in raw
    assert "url_hash" in raw
    assert "wifi_bssid_hash" in raw


def test_event_ingest_preserves_safe_activity_detail_fields(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    manager.ingest_event(
        "android-server",
        {
            "event_type": "android.user_activity.changed",
            "app_name": "YouTube",
            "screen_title_summary": "Example video title",
            "screen_title_hash": "abc123",
            "content_kind": "video",
            "input_target_category": "none",
            "key_category_counts": {"printable": 3, "navigation": 1},
        },
    )

    payload = manager.get_recent_events(limit=1)[0]["payload"]

    assert payload["app_name"] == "YouTube"
    assert payload["screen_title_summary"] == "Example video title"
    assert payload["content_kind"] == "video"
    assert payload["input_target_category"] == "none"
    assert payload["key_category_counts"] == {"printable": 3, "navigation": 1}


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


def test_pc_game_fullscreen_low_idle_stays_pc_attention_and_gaming(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    manager.ingest_event(
        "pc-server",
        {
            "event_type": "pc.user_activity.snapshot",
            "app_name": "Steam Game",
            "process_name": "eldenring.exe",
            "active_window_title": "ELDEN RING",
            "keyboard_count": 0,
            "mouse_count": 0,
            "key_event_count": 0,
            "idle_ms": 25_000,
            "fullscreen": True,
            "locked": False,
            "input_target_category": "game",
        },
    )

    state = manager.get_current_user_state()

    assert state["attention"]["device"] == "pc"
    assert state["activity"]["label"] == "gaming"
    assert state["activity"]["app_name"] == "Steam Game"


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


def test_recent_query_does_not_scan_days_older_than_since(
    tmp_path,
    monkeypatch,
) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))
    current_ms = int(time.time() * 1000)
    manager.ingest_event(
        "pc-server",
        {
            "event_type": "pc.user_activity.snapshot",
            "timestamp_ms": current_ms,
            "process_name": "Code.exe",
        },
    )
    old_day = datetime.fromtimestamp(
        (current_ms - 3 * 24 * 3_600_000) / 1000,
        tz=timezone(timedelta(hours=9)),
    ).strftime("%Y-%m-%d")
    old_path = tmp_path / "user_state" / "timeline" / f"{old_day}.jsonl"
    old_path.write_text('{"timestamp_ms": 1}\n', encoding="utf-8")

    original = old_path.__class__.open

    def guarded_open(path, *args, **kwargs):
        if path == old_path:
            raise AssertionError("out-of-range daily file was scanned")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(old_path.__class__, "open", guarded_open)

    events = manager._store.query_recent(
        limit=10,
        since_ms=current_ms - 24 * 3_600_000,
    )

    assert len(events) == 1
    assert events[0]["timestamp_ms"] == current_ms


def test_pc_poller_keeps_active_fullscreen_snapshots_every_ten_seconds(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))
    snapshot = {"process_name": "eldenring.exe", "idle_ms": 20_000, "fullscreen": True}

    assert manager._should_save_pc_snapshot(snapshot) is True
    assert manager._should_save_pc_snapshot(snapshot) is False
    manager._last_pc_saved_ms -= 10_001
    assert manager._should_save_pc_snapshot(snapshot) is True


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


def test_android_touch_beats_repeated_passive_pc_idle_snapshots(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    for index in range(5):
        manager.ingest_event(
            "pc-server",
            {
                "event_type": "pc.user_activity.snapshot",
                "process_name": "Code.exe",
                "keyboard_count": 0,
                "mouse_count": 0,
                "key_event_count": 0,
                "idle_ms": 2_000,
                "locked": False,
                "timestamp_ms": int(time.time() * 1000) - (5 - index) * 4_000,
            },
        )
    manager.ingest_event(
        "android-server",
        {
            "event_type": "android.user_activity.changed",
            "screen_on": True,
            "locked": False,
            "touch_count": 4,
            "app_name": "YouTube",
            "package_name": "com.google.android.youtube",
            "layout_category": "video",
        },
    )

    state = manager.get_current_user_state()
    assert state["attention"]["device"] == "android"
    assert state["activity"]["label"] == "watching_video"


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


def test_android_youtube_and_browser_details_drive_activity(tmp_path) -> None:
    manager = UserStateManager(data_dir=str(tmp_path / "user_state"))

    manager.ingest_event(
        "android-server",
        {
            "event_type": "android.user_activity.changed",
            "screen_on": True,
            "locked": False,
            "touch_count": 2,
            "package_name": "com.google.android.youtube",
            "app_name": "YouTube",
            "layout_category": "video",
            "content_kind": "video",
            "screen_title_summary": "A useful video title",
        },
    )
    state = manager.get_current_user_state()
    assert state["activity"]["label"] == "watching_video"
    assert state["activity"]["app_name"] == "YouTube"
    assert state["activity"]["screen_title_summary"] == "A useful video title"
    assert state["activity"]["evidence"][-1]["screen_title_summary"] == "A useful video title"

    manager = UserStateManager(data_dir=str(tmp_path / "browser_state"))
    manager.ingest_event(
        "android-server",
        {
            "event_type": "android.user_activity.changed",
            "screen_on": True,
            "locked": False,
            "touch_count": 2,
            "package_name": "com.android.chrome",
            "app_name": "Chrome",
            "layout_category": "browser",
            "content_kind": "browser",
            "screen_title_summary": "Example page title",
        },
    )
    assert manager.get_current_user_state()["activity"]["label"] == "browsing"


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
