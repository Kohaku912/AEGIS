#!/usr/bin/env python3
"""Nudge the desktop session back to the kiosk window after login."""

from __future__ import annotations

import ctypes
import subprocess
import time


def main() -> int:
    subprocess.run(
        [
            "busctl",
            "--user",
            "set-property",
            "org.gnome.Shell",
            "/org/gnome/Shell",
            "org.gnome.Shell",
            "OverviewActive",
            "b",
            "false",
        ],
        check=False,
        timeout=5,
    )
    time.sleep(0.5)

    x11 = ctypes.cdll.LoadLibrary("libX11.so.6")
    xtst = ctypes.cdll.LoadLibrary("libXtst.so.6")
    x11.XOpenDisplay.restype = ctypes.c_void_p
    display = x11.XOpenDisplay(None)
    if not display:
        return 0

    # Escape twice closes the GNOME initial overview and returns to the kiosk window.
    for keysym in (0xFF1B, 0xFF1B):
        code = x11.XKeysymToKeycode(ctypes.c_void_p(display), ctypes.c_ulong(keysym))
        xtst.XTestFakeKeyEvent(ctypes.c_void_p(display), code, True, 0)
        xtst.XTestFakeKeyEvent(ctypes.c_void_p(display), code, False, 0)
        x11.XFlush(ctypes.c_void_p(display))
        time.sleep(0.35)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
