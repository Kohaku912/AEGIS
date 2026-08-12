"""INMP441 I2S MEMS microphone on Orange Pi Zero3.

Wiring for hardware I2S3 (H618 Port H — Port C cannot mux I2S):
  L/R → GND (left channel select)
  SCK → PH6 (board pin 23, BCLK)
  WS  → PH7 (board pin 19, LRCLK / WS)
  SD  → PH9 (board pin 24, DIN0 / mic DOUT)
  VDD → 3.3V, GND → GND

Enable with Armbian overlay ``overlays=i2s3`` built from
``room-server/overlays/sun50i-h616-i2s3-inmp441.dts`` (ALSA card ``ahubi2s3``).

Capture uses ALSA (`arecord`) when AEGIS_ROOM_SOUND_PROVIDER=alsa.
"""

from __future__ import annotations

import json
import math
import os
import struct
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any


def now_ms() -> int:
    return int(time.time() * 1000)


INMP441_WIRING: dict[str, str] = {
    "sensor": "INMP441",
    "L/R": "GND",
    # H618 I2S3 mux (Port C has no I2S function — do not use PC6/PC8/PC9).
    "SCK": "PH6",
    "WS": "PH7",
    "SD": "PH9",
    "board_SCK": "23",
    "board_WS": "19",
    "board_SD": "24",
    "alsa_card": "ahubi2s3",
}


DEFAULT_SOUND_DEVICE_ID = "sound-inmp441"


@dataclass
class SoundSample:
    device_id: str = DEFAULT_SOUND_DEVICE_ID
    sensor: str = "INMP441"
    rms: float = 0.0
    peak: float = 0.0
    db_fs: float | None = None
    sample_rate: int = 16000
    duration_ms: int = 0
    channels: int = 1
    provider: str = "mock"
    available: bool = True
    warning: str = ""
    wiring: dict[str, str] = field(default_factory=lambda: dict(INMP441_WIRING))
    updated_at_ms: int = field(default_factory=now_ms)

    def to_json(self) -> str:
        return json.dumps(
            {
                "sensor": self.sensor,
                "rms": self.rms,
                "peak": self.peak,
                "db_fs": self.db_fs,
                "sample_rate": self.sample_rate,
                "duration_ms": self.duration_ms,
                "channels": self.channels,
                "provider": self.provider,
                "available": self.available,
                "warning": self.warning,
                "wiring": self.wiring,
                "updated_at_ms": self.updated_at_ms,
            },
            ensure_ascii=True,
        )


def _rms_peak_from_s32le(raw: bytes, *, channels: int = 1, channel_index: int = 0) -> tuple[float, float]:
    if len(raw) < 4:
        return 0.0, 0.0
    n = len(raw) // 4
    samples = struct.unpack(f"<{n}i", raw[: n * 4])
    if not samples:
        return 0.0, 0.0
    ch = max(1, int(channels))
    idx = max(0, min(ch - 1, int(channel_index)))
    if ch > 1:
        samples = samples[idx::ch]
        if not samples:
            return 0.0, 0.0
    # Normalize to ±1.0 using 24-bit useful range inside 32-bit slots.
    scale = float(1 << 23)
    vals = [s / scale for s in samples]
    peak = max(abs(v) for v in vals)
    mean_sq = sum(v * v for v in vals) / len(vals)
    return math.sqrt(mean_sq), peak


def _db_fs(rms: float) -> float | None:
    if rms <= 1e-12:
        return None
    return 20.0 * math.log10(rms)


class MockSoundProvider:
    """Deterministic sound sample for CI / development."""

    provider_name = "mock"
    device_id = DEFAULT_SOUND_DEVICE_ID

    def sample(self, duration_ms: int = 250) -> SoundSample:
        # Quiet room baseline so callers see a stable non-zero level.
        rms = 0.01
        return SoundSample(
            rms=rms,
            peak=0.02,
            db_fs=_db_fs(rms),
            duration_ms=max(1, int(duration_ms)),
            provider=self.provider_name,
            available=True,
        )


class AlsaInmp441Provider:
    """Capture a short PCM burst via arecord and report RMS / dBFS."""

    provider_name = "alsa"
    device_id = DEFAULT_SOUND_DEVICE_ID

    def __init__(self) -> None:
        self._alsa_device = (
            os.environ.get("AEGIS_ROOM_SOUND_ALSA_DEVICE", "hw:ahubi2s3,0").strip() or "hw:ahubi2s3,0"
        )
        self._rate = int(os.environ.get("AEGIS_ROOM_SOUND_RATE", "16000") or "16000")
        self._arecord = os.environ.get("AEGIS_ROOM_SOUND_ARECORD", "arecord").strip() or "arecord"
        channels = int(os.environ.get("AEGIS_ROOM_SOUND_CHANNELS", "2") or "2")
        self._channels = channels if channels in {1, 2} else 2

    def sample(self, duration_ms: int = 250) -> SoundSample:
        duration_ms = max(50, min(5000, int(duration_ms)))
        # Older arecord rejects fractional -d; use whole seconds (ceil).
        duration_s = max(1, (duration_ms + 999) // 1000)
        cmd = [
            self._arecord,
            "-q",
            "-D",
            self._alsa_device,
            "-f",
            "S32_LE",
            "-r",
            str(self._rate),
            "-c",
            str(self._channels),
            "-d",
            str(duration_s),
            "-t",
            "raw",
        ]
        try:
            completed = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                timeout=max(3.0, float(duration_s) + 2.0),
            )
        except FileNotFoundError:
            return SoundSample(
                provider=self.provider_name,
                available=False,
                duration_ms=duration_ms,
                sample_rate=self._rate,
                channels=self._channels,
                warning="arecord not found; install alsa-utils and configure I2S capture",
            )
        except subprocess.TimeoutExpired:
            return SoundSample(
                provider=self.provider_name,
                available=False,
                duration_ms=duration_ms,
                sample_rate=self._rate,
                channels=self._channels,
                warning=f"arecord timed out on {self._alsa_device}",
            )

        if completed.returncode != 0 or not completed.stdout:
            err = (completed.stderr or b"").decode("utf-8", errors="replace").strip()
            hint = (
                f"{err}; INMP441 needs I2S3 ALSA card ahubi2s3 on "
                f"SCK=PH6 WS=PH7 SD=PH9 (device={self._alsa_device})"
            )
            return SoundSample(
                provider=self.provider_name,
                available=False,
                duration_ms=duration_ms,
                sample_rate=self._rate,
                channels=self._channels,
                warning=hint,
            )

        # L/R=GND → left slot (channel 0).
        rms, peak = _rms_peak_from_s32le(
            completed.stdout, channels=self._channels, channel_index=0
        )
        return SoundSample(
            rms=rms,
            peak=peak,
            db_fs=_db_fs(rms),
            sample_rate=self._rate,
            duration_ms=duration_ms,
            channels=self._channels,
            provider=self.provider_name,
            available=True,
            warning="",
        )


def create_sound_provider() -> MockSoundProvider | AlsaInmp441Provider | None:
    """Return sound provider, or None when sound is disabled."""
    provider = os.environ.get("AEGIS_ROOM_SOUND_PROVIDER", "mock").strip().lower()
    if provider in {"", "off", "none", "disabled"}:
        return None
    if provider == "alsa":
        return AlsaInmp441Provider()
    return MockSoundProvider()
