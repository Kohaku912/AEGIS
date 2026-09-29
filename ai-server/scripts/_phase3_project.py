"""Phase 3 recon: project the irreversibility-relevant fields from every manifest.

Read-only. Emits a compact JSON projection plus vocabulary tallies so the
classification can be done against the real canonical vocabularies.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPS = ROOT / "capabilities"

FIELDS = (
    "ownership_scope",
    "reversibility",
    "destructive_effects",
    "data_loss_risk",
    "active_work_loss_risk",
    "blast_radius",
)

paths = sorted(CAPS.rglob("*.json"))
print(f"manifests: {len(paths)}")

rows = []
missing = Counter()
side_effects = Counter()
op_cats = Counter()

for path in paths:
    data = json.loads(path.read_text(encoding="utf-8"))
    rel = path.relative_to(CAPS).as_posix()
    row = {
        "path": rel,
        "capability_id": ".".join(
            str(data.get(k, "")) for k in ("server_id", "app_id", "action")
        ),
        "title": data.get("title", ""),
        "description": (data.get("description", "") or "")[:400],
        "operation_category": data.get("operation_category", ""),
        "risk_level": (data.get("risk") or {}).get("level", ""),
        "side_effects": (data.get("risk") or {}).get("side_effects", []) or [],
    }
    for f in FIELDS:
        if f not in data:
            missing[f] += 1
        row[f] = data.get(f)
    rows.append(row)
    for se in row["side_effects"]:
        side_effects[str(se)] += 1
    op_cats[str(row["operation_category"])] += 1

out = ROOT / ".tmp-phase3-projection.json"
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n=== missing classification keys (of {len(paths)}) ===")
for f in FIELDS:
    print(f"  {f:26s} missing in {missing[f]:3d}")

print("\n=== operation_category ===")
for k, v in op_cats.most_common():
    print(f"  {v:3d}  {k}")

print(f"\n=== side_effects (distinct: {len(side_effects)}) ===")
for k, v in side_effects.most_common():
    print(f"  {v:3d}  {k}")

print(f"\nprojection written: {out}")
