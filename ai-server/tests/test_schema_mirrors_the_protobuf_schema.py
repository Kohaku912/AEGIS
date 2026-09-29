"""``aegis_schema`` mirrors the protobuf schema — nothing extra, and nothing false.

Two defects in ``aegis_schema/models.py``, found 2026-09-29:

1. **``ApprovalRequirement``** described "what approval is needed before executing a
   capability", with ``requires_user_approval`` defaulting to **``True``**, an
   ``approval_message`` "to show in Approval UI", and a ``timeout_seconds`` that
   **auto-denies**. It had **zero consumers** — no Python, TypeScript, Kotlin, Rust,
   doc or SDK reference — and was the **only** class in the file with no protobuf
   counterpart, in a package whose docstring promises every model mirrors
   ``protos/aegis/``. Deleted.

2. **``RiskLevel``'s prose was false.** Its docstring said the Policy Engine "uses this
   to decide whether to allow, ask for approval, or deny an action", and
   ``APPROVAL_REQUIRED`` was commented "Needs explicit user confirmation". The engine
   never asks: ``DEFAULT_RISK_MAP`` maps ``APPROVAL_REQUIRED`` to ``ALLOW_WITH_AUDIT``.
   The *protobuf* counterpart (``SafetyLevel.LEVEL_2_APPROVAL``) had already been
   corrected in Phase 5b — the Python mirror had not. That asymmetry is the point.

Why the first test is shaped the way it is. The interesting failure was not the wrong
sentence; it was that **nothing linked the two halves of the schema**. So that test
discovers both sides — the classes in ``models.py`` and the messages/enums under
``protos/aegis/`` — and asserts every model has a counterpart. That is what would have
caught ``ApprovalRequirement`` without anyone reading its prose.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_MODELS = _REPO / "ai-server" / "src" / "aegis_schema" / "models.py"
_PROTO_DIR = _REPO / "protos" / "aegis"

#: Python class -> protobuf type, for the names that differ. Kept tiny and asserted
#: below, so a rename cannot quietly become a lie.
_RENAMES: dict[str, str] = {"RiskLevel": "SafetyLevel"}

#: The one class this file exists to keep deleted.
_RETIRED: str = "ApprovalRequirement"


def _schema_classes() -> list[str]:
    """Top-level classes in ``models.py``, discovered rather than listed."""
    tree = ast.parse(_MODELS.read_text(encoding="utf-8"))
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def _proto_types() -> set[str]:
    """Every ``message`` and ``enum`` declared under ``protos/aegis/``."""
    found: set[str] = set()
    for path in sorted(_PROTO_DIR.glob("*.proto")):
        found.update(
            re.findall(
                r"^(?:message|enum)\s+([A-Za-z_][A-Za-z0-9_]*)",
                path.read_text(encoding="utf-8"),
                re.M,
            )
        )
    return found


# ── The invariant the package claims ──────────────────────────────────────────


def test_every_schema_model_mirrors_a_protobuf_type() -> None:
    classes = _schema_classes()
    proto = _proto_types()

    # Guard the guard: a truncated scan on either side would pass vacuously.
    assert len(classes) >= 10, f"only {len(classes)} classes parsed from models.py"
    assert len(proto) >= 80, f"only {len(proto)} proto types discovered"

    unmapped = sorted({_RENAMES.get(name, name) for name in classes} - proto)
    assert unmapped == [], (
        f"these aegis_schema models mirror no protobuf type: {unmapped}. The package "
        "docstring says every model mirrors protos/aegis/ — either add the proto or "
        "delete the model."
    )


def test_the_rename_map_is_real() -> None:
    """``RiskLevel``/``SafetyLevel`` is the only rename, and it is genuinely one."""
    proto = _proto_types()
    for python_name, proto_name in _RENAMES.items():
        assert python_name in _schema_classes(), f"{python_name} is not a schema class"
        assert python_name not in proto, f"{python_name} is a proto name — drop the rename"
        assert proto_name in proto


# ── The deletion ──────────────────────────────────────────────────────────────


def test_approval_requirement_is_gone() -> None:
    assert _RETIRED not in _schema_classes(), (
        "ApprovalRequirement is back in aegis_schema/models.py. Read this module's "
        "docstring first: it had zero consumers and no protobuf counterpart."
    )


def test_the_package_does_not_re_export_approval_requirement() -> None:
    import aegis_schema

    # Non-vacuity: the package still exports the rest of the schema.
    assert len(aegis_schema.__all__) >= 9, "aegis_schema exports almost nothing"
    assert not hasattr(aegis_schema, _RETIRED), (
        f"aegis_schema.{_RETIRED} is reachable again — the model was deleted on purpose"
    )
    assert _RETIRED not in aegis_schema.__all__


def test_nothing_in_src_references_the_deleted_model() -> None:
    """A stale ``ApprovalRequirement`` would fail at runtime, not at review."""
    src = _REPO / "ai-server" / "src"
    offenders: list[str] = []
    for path in src.rglob("*.py"):
        if "__pycache__" in path.parts or "generated" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == _RETIRED:
                offenders.append(str(path.relative_to(src)))
            elif isinstance(node, ast.Attribute) and node.attr == _RETIRED:
                offenders.append(str(path.relative_to(src)))
            elif isinstance(node, ast.ImportFrom):
                offenders.extend(
                    str(path.relative_to(src)) for alias in node.names if alias.name == _RETIRED
                )
    assert offenders == [], f"these modules still reference the deleted model: {offenders}"


# ── The false prose ───────────────────────────────────────────────────────────


def _risk_level_block() -> str:
    text = _MODELS.read_text(encoding="utf-8")
    return text[text.index("class RiskLevel") : text.index("class ServerType")]


def test_the_risk_level_prose_does_not_claim_a_prompt() -> None:
    """The Python mirror must not re-assert the gate the proto already retired."""
    block = _risk_level_block()
    for claim in ("ask for approval", "Needs explicit user confirmation"):
        assert claim not in block, (
            f"RiskLevel's prose claims {claim!r} again. DEFAULT_RISK_MAP maps "
            "APPROVAL_REQUIRED to ALLOW_WITH_AUDIT — the engine never asks."
        )
    assert "not a gate" in block


def test_the_proto_keeps_the_annotation_the_python_side_was_aligned_to() -> None:
    """If the proto loses its correction, the alignment above points at nothing."""
    common = (_PROTO_DIR / "common.proto").read_text(encoding="utf-8")
    assert "LEVEL_2_APPROVAL" in common
    assert "no longer implies that anyone is asked" in common, (
        "SafetyLevel.LEVEL_2_APPROVAL lost its corrective annotation — the Python "
        "RiskLevel prose was aligned to it, so this is now a dangling reference"
    )
