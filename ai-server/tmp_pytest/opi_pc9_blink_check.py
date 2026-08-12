#!/usr/bin/env python3
"""Calibrate H618 PIO DAT map and blink-test PC9 for IR wiring check."""

from __future__ import annotations

import mmap
import struct
import time

import gpiod
from gpiod.line import Direction, Value

PIO = 0x0300B000


def read_word(m: mmap.mmap, off: int) -> int:
    return struct.unpack_from("<I", m, off)[0]


def write_word(m: mmap.mmap, off: int, value: int) -> None:
    struct.pack_into("<I", m, off, value)


def main() -> None:
    print("=== Naming ===")
    print("PC9 = SoC pin name (Port C, bit 9)")
    print("On Orange Pi Zero3 26-pin header, PC9 is PHYSICAL PIN 7")
    print("Counting: pin1=3.3V, pin2=5V, ... pin7=PC9 (next to GND pin9)")
    print("Board silkscreen often does NOT say 'PC9'; count pins from the 3.3V end.")
    print()
    print("26-pin header (top view, pin1 near 3.3V):")
    print("  1:3.3V   2:5V")
    print("  3:PH5    4:5V")
    print("  5:PH4    6:GND")
    print("  7:PC9 <<<< IR signal should be HERE")
    print("  8:PH2")
    print("  9:GND   10:PH3")
    print("Also: 13-pin audio/USB header has CIR-RX=PH10 (IR receive only), not PC9.")
    print()

    with open("/dev/mem", "r+b", buffering=0) as f:
        m = mmap.mmap(f.fileno(), 0x1000, offset=PIO)

        print("=== Calibrate DAT using gpiod on PC8 (line 72) ===")
        req = gpiod.request_lines(
            "/dev/gpiochip1",
            consumer="cal-pc8",
            config={72: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)},
        )
        found = None
        for stride in (0x24, 0x30):
            for dat_rel in (0x10, 0x14, 0x0C, 0x08):
                off = 2 * stride + dat_rel
                low_vals = []
                high_vals = []
                for level in (0, 1, 0, 1):
                    req.set_value(72, Value.ACTIVE if level else Value.INACTIVE)
                    time.sleep(0.005)
                    val = read_word(m, off)
                    (high_vals if level else low_vals).append(val)
                # bit 8 must follow PC8
                if all(((v >> 8) & 1) == 0 for v in low_vals) and all(((v >> 8) & 1) == 1 for v in high_vals):
                    found = (stride, dat_rel, off)
                    print(f"FOUND stride=0x{stride:x} dat_rel=0x{dat_rel:x} off=0x{off:x}")
                    print(f"  low={low_vals[0]:08x} high={high_vals[0]:08x}")
                    break
            if found:
                break
        req.release()
        if not found:
            print("FAILED to calibrate DAT offset; dumping bank2 region")
            for off in range(0x40, 0xB0, 4):
                print(f"  {off:03x}: {read_word(m, off):08x}")
            m.close()
            raise SystemExit(2)

        stride, dat_rel, dat_off = found
        cfg1_off = 2 * stride + 0x04
        print(f"Using CFG1 off=0x{cfg1_off:x} DAT off=0x{dat_off:x}")

        # Force PC9 to GPIO output and blink 1Hz for 10 seconds
        print()
        print("=== PC9 1Hz blink for 10s ===")
        print("Check IR LED with phone camera (front camera often sees IR purple flicker).")
        print("If no flicker, signal wire is probably NOT on physical pin 7 / PC9.")
        cfg1 = read_word(m, cfg1_off)
        shift = (9 - 8) * 4
        old_func = (cfg1 >> shift) & 0xF
        cfg1 = (cfg1 & ~(0xF << shift)) | (0x1 << shift)
        write_word(m, cfg1_off, cfg1)
        print(f"PC9 mux {old_func} -> 1 (GPIO out), CFG1={read_word(m, cfg1_off):08x}")

        def set_pc9(high: bool) -> int:
            dat = read_word(m, dat_off)
            if high:
                dat |= 1 << 9
            else:
                dat &= ~(1 << 9)
            write_word(m, dat_off, dat)
            return (read_word(m, dat_off) >> 9) & 1

        for i in range(10):
            rb = set_pc9(True)
            print(f"{i:02d} HIGH readback={rb} dat={read_word(m, dat_off):08x}", flush=True)
            time.sleep(0.5)
            rb = set_pc9(False)
            print(f"{i:02d} LOW  readback={rb} dat={read_word(m, dat_off):08x}", flush=True)
            time.sleep(0.5)
        set_pc9(False)
        print("blink_done")
        m.close()


if __name__ == "__main__":
    main()
