#!/usr/bin/env python3
"""Capture USB camera frame brightness on AI server host/container."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def find_video_devices() -> list[str]:
    return sorted(str(p) for p in Path("/dev").glob("video*") if p.exists())


def capture_with_ffmpeg(device: str, out_path: Path) -> bool:
    # Warm up auto-exposure; first frames from many USB cams are near-black.
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "v4l2",
        "-video_size",
        "640x480",
        "-i",
        device,
        "-vf",
        "fps=5",
        "-update",
        "1",
        "-frames:v",
        "15",
        str(out_path),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        return r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0
    except Exception as exc:
        print("ffmpeg_fail", exc)
        return False


def mean_brightness(path: Path) -> float:
    try:
        import cv2  # type: ignore

        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError("cv2 failed to read image")
        return float(img.mean())
    except Exception:
        # fallback via ffmpeg signalstats
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-f",
            "lavfi",
            f"movie={path},signalstats",
            "-show_entries",
            "frame_tags=lavfi.signalstats.YAVG",
            "-of",
            "json",
        ]
        # simpler: use python stdlib ppm via ffmpeg raw
        raw = path.with_suffix(".pgm")
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(path), "-vf", "scale=160:120,format=gray", str(raw)],
            capture_output=True,
            timeout=20,
        )
        data = raw.read_bytes()
        # skip pgm header
        parts = data.split(b"\n", 3)
        pixels = parts[-1]
        if not pixels:
            return -1.0
        return sum(pixels) / max(1, len(pixels))


def main() -> None:
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/aegis-cam")
    label = sys.argv[2] if len(sys.argv) > 2 else "shot"
    out_dir.mkdir(parents=True, exist_ok=True)
    devices = find_video_devices()
    print(json.dumps({"devices": devices}, ensure_ascii=False))
    if not devices:
        raise SystemExit(2)
    # prefer first capture-capable node; try each
    shot = out_dir / f"{label}.jpg"
    used = None
    for dev in devices:
        if capture_with_ffmpeg(dev, shot):
            used = dev
            break
    if not used:
        raise SystemExit(3)
    brightness = mean_brightness(shot)
    print(
        json.dumps(
            {
                "device": used,
                "path": str(shot),
                "bytes": shot.stat().st_size,
                "brightness": round(brightness, 2),
                "label": label,
                "ts": int(time.time() * 1000),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
