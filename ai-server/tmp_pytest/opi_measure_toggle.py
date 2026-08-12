#!/usr/bin/env python3
"""Measure PC9 mmap toggle rate (carrier feasibility)."""
from __future__ import annotations

import mmap
import struct
import time

PIO = 0x0300B000
STRIDE = 0x24
bank, bit = 2, 9
bank_off = bank * STRIDE
cfg_off = bank_off + (bit // 8) * 4
cfg_shift = (bit % 8) * 4
dat_off = bank_off + 0x10

with open("/dev/mem", "r+b", buffering=0) as f:
    m = mmap.mmap(f.fileno(), 0x1000, offset=PIO)
    cfg = struct.unpack_from("<I", m, cfg_off)[0]
    struct.pack_into("<I", m, cfg_off, (cfg & ~(0xF << cfg_shift)) | (0x1 << cfg_shift))
    dat = struct.unpack_from("<I", m, dat_off)[0]
    n = 20000
    t0 = time.perf_counter()
    for i in range(n):
        if i & 1:
            dat |= 1 << bit
        else:
            dat &= ~(1 << bit)
        struct.pack_into("<I", m, dat_off, dat)
    t1 = time.perf_counter()
    hz = n / (t1 - t0)
    print(f"toggles={n} sec={t1 - t0:.4f} toggle_hz={hz:.0f} carrier_est_hz={hz / 2:.0f}")
    dat &= ~(1 << bit)
    struct.pack_into("<I", m, dat_off, dat)
    m.close()
