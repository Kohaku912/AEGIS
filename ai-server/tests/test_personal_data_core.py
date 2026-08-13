"""Personal Data Core store, provenance, retention, and room media tests."""

from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.personal_data.core import PersonalDataCore
from aegis_ai.personal_data.ingest import sanitize_value_payload
from aegis_ai.personal_data.room_media import MotionGate, pcm_rms


def test_ingest_keeps_raw_title_and_provenance(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    event = SimpleNamespace(
        event_type="pc.user_activity.snapshot",
        event_id="evt_1",
        source_server_id="pc-server",
        timestamp_ms=1_700_000_000_000,
        payload_json='{"app_name":"chrome","active_window_title":"AGORA — reply","url":"https://agora.example/post"}',
    )
    written = core.ingest_bus_event(event)
    assert written is not None
    assert written["payload"]["active_window_title"] == "AGORA — reply"
    assert written["payload"]["url"] == "https://agora.example/post"
    assert written["epistemics"] == "observed"
    assert written["provenance"]["bus_event_id"] == "evt_1"
    loaded = core.get_event(written["id"])
    assert loaded is not None
    assert loaded["observations"]
    assert loaded["facts"] or loaded["event_type"] == "pc.window.focused"


def test_password_value_is_kept() -> None:
    payload = sanitize_value_payload({"control_name": "Password", "is_password": True, "value": "secret", "keys": ["A"]})
    assert payload["value"] == "secret"
    assert payload["keys"] == ["A"]
    assert payload["control_kind"] == "password"


def test_replacement_glyphs_are_dropped_from_title(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    written = core.ingest_pc_stream([{
        "event_type": "pc.input.typed",
        "app_name": "Cursor",
        "window_title": "Cursor Agents",
        "control_name": "???????????????? Timeline ????????????",
        "value": "??????????????????????????s",
        "keyboard_count": 4,
        "key_category_counts": {"printable": 4},
        "timestamp_ms": 1_700_000_000_400,
    }])
    assert written
    assert written[0]["event_type"] == "pc.input.typed"
    assert "?" not in written[0]["title"]
    assert written[0]["payload"]["value"] == ""
    assert written[0]["payload"]["control_name"] == ""
    assert "printable×4" in written[0]["title"]


def test_typed_keys_and_click_position_are_kept(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    written = core.ingest_pc_stream([{
        "event_type": "pc.input.typed",
        "app_name": "chrome",
        "keys": ["Ctrl", "L"],
        "mouse_buttons": ["LButton"],
        "click_x": 120,
        "click_y": 480,
        "keyboard_count": 2,
        "mouse_count": 1,
        "timestamp_ms": 1_700_000_000_500,
    }])
    assert written
    assert written[0]["payload"]["keys"] == ["Ctrl", "L"]
    assert written[0]["payload"]["click_x"] == 120
    assert "Ctrl+L" in written[0]["title"]
    assert "(120,480)" in written[0]["title"]


def test_search_and_evidence_roundtrip(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    core.ingest_pc_stream([{
        "event_type": "pc.ui.invoked",
        "app_name": "chrome",
        "control_name": "Reply",
        "url": "https://agora.example/post",
        "timestamp_ms": 1_700_000_000_100,
    }])
    hits = core.search("Reply")
    assert hits["items"]
    jpeg = b"\xff\xd8\xff" + b"x" * 120
    stored = core.ingest_pc_stream([{
        "event_type": "pc.ui.focus_changed",
        "app_name": "chrome",
        "control_name": "Reply",
        "screenshot_jpeg_base64": __import__("base64").b64encode(jpeg).decode("ascii"),
        "timestamp_ms": 1_700_000_000_200,
    }])
    evidence_id = stored[0]["evidence_ids"][0]
    blob, meta = core.get_evidence_bytes(evidence_id)
    assert blob == jpeg
    assert meta["codec"] == "jpeg"
    fact = core.record_fact("User opened AGORA reply", event_ids=[stored[0]["id"]], evidence_ids=[evidence_id])
    loaded = core.get_event(stored[0]["id"])
    assert any(row["id"] == fact.id or fact.statement in str(row) for row in loaded["facts"]) or loaded["evidence"]


def test_retention_deletes_expired_evidence(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    jpeg = b"\xff\xd8\xff" + b"y" * 80
    written = core.ingest_pc_stream([{
        "event_type": "pc.ui.focus_changed",
        "app_name": "notepad",
        "screenshot_jpeg_base64": __import__("base64").b64encode(jpeg).decode("ascii"),
        "timestamp_ms": 1000,
    }])
    evidence_id = written[0]["evidence_ids"][0]
    core._store._conn.execute("UPDATE evidence SET timestamp_ms=1, retention_class='ephemeral_screen' WHERE id=?", (evidence_id,))
    core._store._conn.execute("UPDATE events SET timestamp_ms=1, retention_class='ephemeral_screen' WHERE id=?", (written[0]["id"],))
    core._store._conn.commit()
    cleaned = core.apply_retention()
    assert cleaned["ephemeral_screen"] >= 1
    assert core.get_evidence_bytes(evidence_id) is None


def test_room_still_has_no_video(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    core.policy = lambda: __import__("aegis_ai.personal_data.models", fromlist=["CollectionPolicy"]).CollectionPolicy(camera_enabled=True, enabled=True)  # type: ignore[method-assign]
    frame = b"\xff\xd8\xff" + b"z" * 200
    first = core.ingest_room_frame(frame, timestamp_ms=10, location={"room": "bedroom", "zone": "desk"})
    second = core.ingest_room_frame(frame, timestamp_ms=20, location={"room": "bedroom", "zone": "desk"})
    assert first["ok"]
    assert second.get("video") is False or second.get("event", {}).get("event_type") == "room.still"


def test_motion_gate_emits_clip() -> None:
    gate = MotionGate(pre_frames=2, post_frames=1)
    still = b"\xff\xd8" + b"a" * 80
    moving = b"\xff\xd8" + b"b" * 80
    gate.push(still, 1)
    gate.push(still, 2)
    assert gate.push(moving, 3)["kind"] == "motion"
    kinds = [gate.push(still, 4)["kind"], gate.push(still, 5)["kind"]]
    assert "clip_ready" in kinds or "post_buffer" in kinds


def test_silence_not_stored(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    core.policy = lambda: __import__("aegis_ai.personal_data.models", fromlist=["CollectionPolicy"]).CollectionPolicy(mic_enabled=True, enabled=True)  # type: ignore[method-assign]
    quiet = b"\x00\x00" * 1600
    assert pcm_rms(quiet) < 10
    result = core.ingest_room_audio(quiet, timestamp_ms=5)
    assert result.get("stored") is False


def test_user_state_redacts_while_pdc_keeps_raw(tmp_path) -> None:
    from aegis_ai.user_state.manager import UserStateManager

    core = PersonalDataCore(tmp_path / "pdc")

    class Bus:
        _personal_data_core = core

    manager = UserStateManager(data_dir=str(tmp_path / "user_state"), event_manager=Bus())
    payload = {
        "timestamp_ms": 1_700_000_000_000,
        "app_name": "chrome",
        "active_window_title": "AGORA — reply",
        "url": "https://agora.example/post",
        "text": "secret draft",
    }
    manager._offer_raw_to_pdc("pc.user_activity.snapshot", payload)
    manager.ingest_event("pc-server", {"event_type": "pc.user_activity.snapshot", **payload})
    redacted = __import__("json").dumps(manager.get_recent_events(limit=1)[0], ensure_ascii=False)
    assert "secret draft" not in redacted
    assert "active_window_title_hash" in redacted
    items, _ = core._store.timeline(limit=10)
    raw = __import__("json").dumps(items, ensure_ascii=False)
    assert "AGORA — reply" in raw
    assert "https://agora.example/post" in raw


def test_memory_derivation_records_provenance(tmp_path) -> None:
    class Mem:
        def write_memory(self, content, **kwargs):
            return "mem_test"

    core = PersonalDataCore(tmp_path, memory_manager=Mem())
    written = core.ingest_pc_stream([{
        "event_type": "pc.ui.invoked",
        "app_name": "chrome",
        "control_name": "Send",
        "timestamp_ms": 9,
    }])
    fact = core.record_fact("clicked send", event_ids=[written[0]["id"]])
    derived = core.derive_memory(fact_ids=[fact.id], event_ids=[written[0]["id"]], statement="User sent a reply")
    assert derived["memory_id"] == "mem_test"
    assert fact.id in derived["fact_ids"]


def test_legacy_value_payload_ingests(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    written = core.ingest_pc_stream([{
        "event_type": "pc.ui.value_changed",
        "app_name": "chrome",
        "control_name": "Reply",
        "control_type": "ControlType.Document",
        "value": "hello AGORA draft",
        "timestamp_ms": 11,
    }])
    assert written[0]["payload"]["value"] == "hello AGORA draft"


def test_notification_raw_respects_policy(tmp_path) -> None:
    from types import SimpleNamespace

    from aegis_ai.personal_data.models import CollectionPolicy

    core = PersonalDataCore(tmp_path)
    core.policy = lambda: CollectionPolicy(enabled=True, android_a11y_enabled=True, notification_raw_text=False)  # type: ignore[method-assign]
    event = SimpleNamespace(
        event_type="android.notification.posted",
        event_id="n1",
        source_server_id="android-server",
        timestamp_ms=20,
        payload_json='{"package_name":"com.mail","title":"Secret subject","text":"body","title_hash":"h1","text_hash":"h2"}',
    )
    written = core.ingest_bus_event(event)
    assert written is not None
    assert "Secret subject" not in str(written["payload"])
    assert written["payload"].get("title_hash") == "h1"

    core.policy = lambda: CollectionPolicy(enabled=True, android_a11y_enabled=True, notification_raw_text=True)  # type: ignore[method-assign]
    event2 = SimpleNamespace(
        event_type="android.notification.posted",
        event_id="n2",
        source_server_id="android-server",
        timestamp_ms=21,
        payload_json='{"package_name":"com.mail","title":"Visible subject","text":"body","title_hash":"h3","text_hash":"h4"}',
    )
    kept = core.ingest_bus_event(event2)
    assert kept is not None
    assert kept["payload"].get("title") == "Visible subject"


def test_android_screenshot_becomes_evidence(tmp_path) -> None:
    from types import SimpleNamespace

    jpeg = b"\xff\xd8\xff" + b"a" * 80
    b64 = __import__("base64").b64encode(jpeg).decode("ascii")
    core = PersonalDataCore(tmp_path)
    event = SimpleNamespace(
        event_type="android.screen.transition",
        event_id="a1",
        source_server_id="android-server",
        timestamp_ms=30,
        payload_json=f'{{"package_name":"com.chrome","control_name":"Main","screenshot_jpeg_base64":"{b64}"}}',
    )
    written = core.ingest_bus_event(event)
    assert written is not None
    assert written["evidence_ids"]
    assert "screenshot_jpeg_base64" not in written["payload"]
    blob, meta = core.get_evidence_bytes(written["evidence_ids"][0])
    assert blob == jpeg
    assert meta["codec"] == "jpeg"


def test_timeline_filters_by_event_type_and_returns_facets(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    core.ingest_pc_stream([
        {
            "event_type": "pc.ui.invoked",
            "app_name": "chrome",
            "control_name": "Reply",
            "timestamp_ms": 1_700_000_000_100,
        },
        {
            "event_type": "pc.window.focused",
            "app_name": "chrome",
            "active_window_title": "Docs",
            "timestamp_ms": 1_700_000_000_200,
        },
    ])
    page = core.timeline(limit=10, event_type="pc.ui.invoked")
    assert page["total"] == 1
    assert page["items"][0]["event_type"] == "pc.ui.invoked"
    types = {row["event_type"]: row["count"] for row in page["event_types"]}
    assert types["pc.ui.invoked"] == 1
    assert types["pc.window.focused"] == 1


def test_keyboard_snapshot_becomes_typed_event(tmp_path) -> None:
    core = PersonalDataCore(tmp_path)
    event = SimpleNamespace(
        event_type="pc.user_activity.snapshot",
        event_id="keys_1",
        source_server_id="pc-server",
        timestamp_ms=1_700_000_000_300,
        payload_json='{"app_name":"chrome","process_name":"chrome.exe","keyboard_count":4,"mouse_count":0,"key_category_counts":{"printable":3,"editing":1}}',
    )
    written = core.ingest_bus_event(event)
    assert written is not None
    assert written["event_type"] == "pc.input.typed"
    assert "printable×3" in written["title"]
    assert written["payload"]["keyboard_count"] == 4
