"""Motion-gated room camera / VAD microphone ingest. ffmpeg optional."""

from __future__ import annotations

import hashlib
import logging
import math
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.personal_data.room_media")

# ponytail: JPEG byte fingerprint, not decoded pixels. Upgrade to ffmpeg/OpenCV scene-detect.
_STILL_HAMMING = 12
_VAD_RMS = 500.0


def jpeg_fingerprint(data: bytes) -> bytes:
    if len(data) < 64:
        return hashlib.blake2s(data, digest_size=8).digest()
    step = max(1, len(data) // 64)
    sample = bytes(data[i] for i in range(0, len(data), step)[:64])
    return hashlib.blake2s(sample, digest_size=8).digest()


def hamming(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b, strict=False))


def pcm_rms(pcm: bytes, sample_width: int = 2) -> float:
    if not pcm or sample_width != 2:
        return 0.0
    count = len(pcm) // 2
    if count <= 0:
        return 0.0
    total = 0.0
    for i in range(count):
        sample = struct.unpack_from("<h", pcm, i * 2)[0]
        total += float(sample * sample)
    return math.sqrt(total / count)


def encode_opus(pcm: bytes, *, sample_rate: int = 16000) -> tuple[bytes, str]:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return pcm, "pcm_s16le"
    src = tempfile.NamedTemporaryFile(suffix=".s16le", delete=False)
    dst = src.name + ".opus"
    try:
        src.write(pcm)
        src.close()
        subprocess.run(
            [ffmpeg, "-y", "-f", "s16le", "-ar", str(sample_rate), "-ac", "1", "-i", src.name, "-c:a", "libopus", dst],
            check=True,
            capture_output=True,
            timeout=20,
        )
        return Path(dst).read_bytes(), "opus"
    except Exception:
        logger.debug("ffmpeg opus encode unavailable", exc_info=True)
        return pcm, "pcm_s16le"
    finally:
        for path in (src.name, dst):
            try:
                os.unlink(path)
            except OSError:
                pass


def encode_h265(frames: list[bytes]) -> tuple[bytes, str]:
    """Encode JPEG keyframes to H.265 when ffmpeg exists; else keep first JPEG."""
    if not frames:
        return b"", "jpeg"
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return frames[0], "jpeg"
    work = Path(tempfile.mkdtemp(prefix="aegis-pdc-"))
    try:
        for index, frame in enumerate(frames):
            (work / f"f{index:04d}.jpg").write_bytes(frame)
        out = work / "clip.hevc"
        subprocess.run(
            [
                ffmpeg, "-y", "-framerate", "5", "-i", str(work / "f%04d.jpg"),
                "-c:v", "libx265", "-preset", "veryfast", "-crf", "28", str(out),
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )
        return out.read_bytes(), "h265"
    except Exception:
        logger.debug("ffmpeg h265 encode unavailable", exc_info=True)
        return frames[0], "jpeg"
    finally:
        for path in work.glob("*"):
            try:
                path.unlink()
            except OSError:
                pass
        try:
            work.rmdir()
        except OSError:
            pass


class MotionGate:
    def __init__(self, *, pre_frames: int = 10, post_frames: int = 30) -> None:
        self.pre_frames = pre_frames
        self.post_frames = post_frames
        self._prev: bytes | None = None
        self._pre: list[bytes] = []
        self._active: list[bytes] = []
        self._post_left = 0
        self._still_since_ms: int | None = None

    def push(self, jpeg: bytes, timestamp_ms: int) -> dict[str, Any]:
        fp = jpeg_fingerprint(jpeg)
        motion = self._prev is not None and hamming(self._prev, fp) > _STILL_HAMMING
        self._prev = fp
        self._pre.append(jpeg)
        if len(self._pre) > self.pre_frames:
            self._pre.pop(0)
        if motion:
            if not self._active:
                self._active.extend(self._pre)
            self._active.append(jpeg)
            self._post_left = self.post_frames
            self._still_since_ms = None
            return {"kind": "motion", "timestamp_ms": timestamp_ms, "fingerprint": fp.hex()}
        if self._post_left > 0:
            self._active.append(jpeg)
            self._post_left -= 1
            if self._post_left == 0 and self._active:
                clip = list(self._active)
                self._active = []
                return {"kind": "clip_ready", "timestamp_ms": timestamp_ms, "frames": clip}
            return {"kind": "post_buffer", "timestamp_ms": timestamp_ms}
        if self._still_since_ms is None:
            self._still_since_ms = timestamp_ms
        return {
            "kind": "still",
            "timestamp_ms": timestamp_ms,
            "still_since_ms": self._still_since_ms,
            "video": False,
        }
