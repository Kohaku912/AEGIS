"""Assert-based check for INMP441 sound helper."""

from aegis_room.sound_inmp441 import INMP441_WIRING, MockSoundProvider, _db_fs, _rms_peak_from_s32le
import struct


def test_wiring_matches_fixture() -> None:
    assert INMP441_WIRING["SCK"] == "PH6"
    assert INMP441_WIRING["WS"] == "PH7"
    assert INMP441_WIRING["SD"] == "PH9"
    assert INMP441_WIRING["L/R"] == "GND"


def test_mock_sample_has_level() -> None:
    sample = MockSoundProvider().sample(100)
    assert sample.available is True
    assert sample.sensor == "INMP441"
    assert sample.db_fs is not None


def test_rms_from_s32() -> None:
    # One full-scale-ish 24-bit sample in a 32-bit slot.
    raw = struct.pack("<i", 1 << 22)
    rms, peak = _rms_peak_from_s32le(raw)
    assert peak > 0.4
    assert rms > 0.4
    assert _db_fs(rms) is not None


def test_stereo_left_channel() -> None:
    # left=1<<22, right=0
    raw = struct.pack("<ii", 1 << 22, 0)
    rms, peak = _rms_peak_from_s32le(raw, channels=2, channel_index=0)
    assert peak > 0.4
    rms_r, peak_r = _rms_peak_from_s32le(raw, channels=2, channel_index=1)
    assert peak_r == 0.0
    assert rms_r == 0.0
