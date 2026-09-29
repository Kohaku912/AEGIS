"""Validate the Phase 3 classification against the manifests and its vocabularies.

Read-only. Exits non-zero on any mismatch so it can gate the persist step.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPS = ROOT / "capabilities"
CLASSIFICATION = json.loads(
    (ROOT / "scripts" / "phase3_irreversibility.json").read_text(encoding="utf-8")
)
VOCAB = CLASSIFICATION["_vocabularies"]
FIELDS = tuple(VOCAB.keys())

entries = {k: v for k, v in CLASSIFICATION.items() if not k.startswith("_")}
manifest_paths = {p.relative_to(CAPS).as_posix() for p in CAPS.rglob("*.json")}

errors: list[str] = []

# 1. Coverage — exact set equality in both directions.
missing = sorted(manifest_paths - set(entries))
extra = sorted(set(entries) - manifest_paths)
if missing:
    errors.append(f"unclassified manifests ({len(missing)}): {missing}")
if extra:
    errors.append(f"classification entries with no manifest ({len(extra)}): {extra}")

# 2. Vocabulary conformance.
tallies: dict[str, Counter] = {f: Counter() for f in FIELDS}
for path, values in entries.items():
    if set(values) != set(FIELDS):
        errors.append(f"{path}: keys {sorted(values)} != {sorted(FIELDS)}")
        continue
    for field, value in values.items():
        allowed = VOCAB[field]
        if field == "destructive_effects":
            if not isinstance(value, list):
                errors.append(f"{path}.{field}: expected list, got {type(value).__name__}")
                continue
            for item in value:
                if item not in allowed:
                    errors.append(f"{path}.{field}: {item!r} not in vocabulary")
                tallies[field][item] += 1
        else:
            if value not in allowed:
                errors.append(f"{path}.{field}: {value!r} not in vocabulary {allowed}")
            tallies[field][value] += 1

# 3. Cross-field sanity: `irreversible` should not claim zero data-loss risk.
for path, values in entries.items():
    if values.get("reversibility") == "irreversible" and values.get("data_loss_risk") == "none":
        errors.append(
            f"{path}: reversibility=irreversible but data_loss_risk=none "
            "(irreversible ops must declare what is lost)"
        )

if errors:
    print("VALIDATION FAILED\n")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK — {len(entries)} manifests classified, {len(manifest_paths)} manifests on disk")
for field in FIELDS:
    rendered = ", ".join(f"{k}={v}" for k, v in tallies[field].most_common())
    print(f"\n  {field}:\n    {rendered}")

# Highlight the ledger's payload: what an owner would want to see post-hoc.
irreversible = sorted(p for p, v in entries.items() if v["reversibility"] == "irreversible")
difficult = sorted(p for p, v in entries.items() if v["reversibility"] == "difficult")
unknown = sorted(p for p, v in entries.items() if "unknown" in v.values())
print(f"\n  irreversible ({len(irreversible)}):")
for p in irreversible:
    print(f"    {p}")
print(f"\n  difficult ({len(difficult)}):")
for p in difficult:
    print(f"    {p}")
print(f"\n  declares unknown ({len(unknown)}):")
for p in unknown:
    print(f"    {p}")
