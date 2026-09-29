"""Phase 3 / Task #28 — persist the irreversibility classification into manifests.

Design notes
------------
* Textual insertion, not re-serialisation. Re-dumping the parsed object with
  ``json.dumps`` would reformat every file (e.g. collapse ``{"level": "low"}``
  one-liners into multi-line blocks) and bury the real change in noise.
* Fail-atomic: every file's new text is computed and verified in memory first.
  Nothing is written unless all 126 pass.
* The verification is a real round-trip, not a tautology: after insertion we
  re-strip the classification keys from the new text and assert it is byte-equal
  to the original text with the same keys stripped. That proves no other byte
  moved.

Run with::

    CODEBUDDY_SAFE_DELETE_ENABLED=0 ../.venv/Scripts/python.exe \
        scripts/_phase3_persist.py [--apply]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPS = ROOT / "capabilities"
CLASSIFICATION = json.loads(
    (ROOT / "scripts" / "phase3_irreversibility.json").read_text(encoding="utf-8")
)
FIELDS = tuple(CLASSIFICATION["_vocabularies"].keys())
ENTRIES = {k: v for k, v in CLASSIFICATION.items() if not k.startswith("_")}
APPLY = "--apply" in sys.argv


# ── JSON-aware text scanning ────────────────────────────────────────────────

def _scan_value_end(text: str, start: int) -> int:
    """Return the index just past the JSON value beginning at ``start``."""
    i = start
    n = len(text)
    while i < n and text[i] in " \t\r\n":
        i += 1
    if i >= n:
        return i
    opener = text[i]
    if opener in "{[":
        closer = "}" if opener == "{" else "]"
        depth = 0
        in_str = False
        esc = False
        while i < n:
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        raise ValueError("unbalanced brackets while scanning value")
    if opener == '"':
        i += 1
        esc = False
        while i < n:
            ch = text[i]
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                return i + 1
            i += 1
        raise ValueError("unterminated string while scanning value")
    # scalar: number / true / false / null
    while i < n and text[i] not in ",\r\n":
        i += 1
    return i


def find_key_span(text: str, key: str) -> tuple[int, int] | None:
    """Span of a ``"key": value`` entry, trailing comma and newline included.

    Works for both pretty-printed manifests (key alone at the head of its line)
    and single-line minified ones (key mid-line). When the key heads a line the
    leading indentation is included so removing the span leaves no blank line.

    Returns ``(start, end)`` or ``None``.
    """
    pattern = re.compile(r'"' + re.escape(key) + r'"\s*:')
    match = pattern.search(text)
    if match is None:
        return None
    start = match.start()
    line_start = text.rfind("\n", 0, start) + 1
    if text[line_start:start].strip() == "":
        start = line_start
    end = _scan_value_end(text, match.end())
    while end < len(text) and text[end] in " \t":
        end += 1
    if end < len(text) and text[end] == ",":
        end += 1
    if end < len(text) and text[end] == "\r":
        end += 1
    if end < len(text) and text[end] == "\n":
        end += 1
    return start, end


def strip_classification_keys(text: str) -> str:
    """Remove every classification key so two texts can be compared."""
    out = text
    for key in FIELDS:
        span = find_key_span(out, key)
        if span is None:
            continue
        out = out[: span[0]] + out[span[1] :]
    return out


def detect_indent(text: str) -> str:
    match = re.search(r'(?m)^([ \t]+)"', text)
    return match.group(1) if match else "  "


def _render_value(value) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(json.dumps(v) for v in value) + "]" if value else "[]"
    return json.dumps(value)


def render_block(values: dict, indent: str) -> str:
    return "".join(f'{indent}"{field}": {_render_value(values[field])},\n' for field in FIELDS)


def render_compact_block(values: dict) -> str:
    return "".join(f'"{field}":{_render_value(values[field])},' for field in FIELDS)


def insertion_index(text: str) -> tuple[int, str]:
    """Where to insert, and which anchor was used."""
    for anchor in ("risk", "operation_category", "server_id", "title"):
        span = find_key_span(text, anchor)
        if span is not None:
            return span[1], anchor
    # No anchor found — insert immediately after the opening brace.
    brace = text.index("{")
    return brace + 1, "root"


def build(original: str, values: dict) -> tuple[str, str]:
    stripped = strip_classification_keys(original)
    index, anchor = insertion_index(stripped)
    if "\n" not in stripped.rstrip("\n"):
        # Single-line minified manifest (a lone trailing newline doesn't count):
        # keep it minified, insert in place.
        return stripped[:index] + render_compact_block(values) + stripped[index:], f"{anchor}/minified"
    indent = detect_indent(stripped)
    prefix, suffix = stripped[:index], stripped[index:]
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    return prefix + render_block(values, indent) + suffix, f"{anchor}/pretty"


# ── Main ───────────────────────────────────────────────────────────────────

errors: list[str] = []
planned: list[tuple[Path, str, str, str]] = []
anchors: dict[str, int] = {}

for rel, values in sorted(ENTRIES.items()):
    path = CAPS / rel
    if not path.is_file():
        errors.append(f"{rel}: manifest not found")
        continue
    original = path.read_text(encoding="utf-8")
    try:
        new_text, anchor = build(original, values)
    except Exception as exc:  # noqa: BLE001 - reported below
        errors.append(f"{rel}: {type(exc).__name__}: {exc}")
        continue

    anchors[anchor] = anchors.get(anchor, 0) + 1

    # Structural check: parsed result must equal original + classification.
    try:
        merged = json.loads(new_text)
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: produced invalid JSON: {exc}")
        continue
    expected = {**json.loads(original), **values}
    if merged != expected:
        errors.append(f"{rel}: structural mismatch after merge")
        continue

    # Round-trip check: stripping the keys from both texts must be identical.
    if strip_classification_keys(new_text) != strip_classification_keys(original):
        errors.append(f"{rel}: bytes outside the classification keys changed")
        continue

    if new_text != original:
        planned.append((path, rel, original, new_text))

print(f"manifests classified : {len(ENTRIES)}")
print(f"files to change      : {len(planned)}")
print(f"anchors used         : {anchors}")

if errors:
    print(f"\nFAILED ({len(errors)}) — nothing written\n")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

if not APPLY:
    print("\nDry run OK. Re-run with --apply to write.")
    for _, rel, _, _ in planned[:3]:
        print(f"  would update {rel}")
    sys.exit(0)

for path, rel, original, new_text in planned:
    path.write_text(new_text, encoding="utf-8")

print(f"\nWrote {len(planned)} manifests.")
