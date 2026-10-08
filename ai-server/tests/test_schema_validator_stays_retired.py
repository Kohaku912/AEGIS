"""``aegis_schema.validation`` stays deleted, and the job it claimed is still covered.

Deleted 2026-09-29. The evidence, measured rather than assumed:

* **No caller, no test, no external consumer.** The three functions and the result
  type were re-exported from ``aegis_schema/__init__.py`` and referenced *only*
  there. A repo-wide search found no test touching them; the SDK imports
  ``aegis_schema.models`` (``Capability``, ``RiskLevel``, ``ServerType``, …) but
  never ``aegis_schema.validation``, and carries its own validator
  (``packages/aegis-sdk-python/aegis_sdk/safety.py::validate_capability_definition``) instead.
* **It had no work to do.** Built from all **128** live manifests via
  ``tool_broker._capability_from_manifest`` and run through
  ``validate_capabilities_batch``: **0 errors**, 133 warnings.
* **Its one universal warning had a false rationale.** 128 of those 133 warnings —
  one per capability — said the tags should include ``risk:<level>`` **"for Policy
  Engine filtering"**. Nothing filters capabilities by a risk tag: ``PolicyEngine``
  keys on ``RiskLevel`` through ``DEFAULT_RISK_MAP``, ``capability_catalog.list_for_llm``
  applies no filter at all (a manifest-declared feature flag used to gate it and was
  removed as never-supplied — ``PROJECT_STATUS_REVIEW.md`` row A-12), and ``tags`` is
  merely serialised into the LLM listing. No manifest carries a ``risk:`` tag
  either. So wiring it would have emitted 128 false warnings on every load.
* **Its distinctive checks encoded retired eras.** One warned that a high-risk
  capability declares ``requires_approval=false`` (approval era), and
  ``validate_capabilities_batch`` warned "No capabilities registered for Dev
  server" for the deleted ``dev-server``.

The checks that *own* manifest validation live in ``tests/test_manifest_schemas.py``
and run in CI. Wiring the validator instead would have made a second source of
truth for the same checks — the thing this repo keeps getting bitten by.

So the deletion is pinned here: if you want a schema validator back, add it
deliberately and revisit the false rationale above.
"""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
_VALIDATOR = _SRC / "aegis_schema" / "validation.py"
_PACKAGE_INIT = _SRC / "aegis_schema" / "__init__.py"

#: Names the deleted module provided. None may come back through the package.
_RETIRED_NAMES: tuple[str, ...] = (
    "ValidationResult",
    "validate_capability",
    "validate_capabilities_batch",
    "validate_capability_json",
)

#: Names that must still be exported, so the check below cannot pass vacuously by
#: looking at an empty or moved package.
_STILL_EXPORTED: tuple[str, ...] = ("Capability", "RiskLevel", "ServerType", "Event")


def test_the_validator_module_is_gone() -> None:
    assert not _VALIDATOR.exists(), (
        "aegis_schema/validation.py is back. Read this module's docstring first — the "
        "deleted version reported 0 errors on all 128 live capabilities, and its only "
        "universal warning claimed a risk-tag filter that does not exist."
    )


def test_the_package_does_not_re_export_a_validator() -> None:
    """The names must not be reachable as ``aegis_schema.validate_capability``."""
    import aegis_schema

    # Guard the guard: if this fails, the assertions below are looking at nothing.
    for name in _STILL_EXPORTED:
        assert hasattr(aegis_schema, name), f"aegis_schema no longer exports {name}"

    for name in _RETIRED_NAMES:
        assert not hasattr(aegis_schema, name), (
            f"aegis_schema.{name} is back; the validator was deleted on purpose "
            "(see this module's docstring)"
        )


def test_the_deleted_module_is_not_importable() -> None:
    assert importlib.util.find_spec("aegis_schema.validation") is None, (
        "aegis_schema.validation resolves to a module again"
    )


def test_nothing_in_src_imports_the_deleted_module() -> None:
    """A stale ``import aegis_schema.validation`` would fail at runtime, not at review."""
    offenders: list[str] = []
    for path in _SRC.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "aegis_schema.validation":
                offenders.append(str(path.relative_to(_SRC)))
            elif isinstance(node, ast.Import):
                offenders.extend(
                    str(path.relative_to(_SRC))
                    for alias in node.names
                    if alias.name == "aegis_schema.validation"
                )

    assert offenders == [], f"these modules still import the deleted validator: {offenders}"


def test_the_replacement_coverage_still_exists() -> None:
    """The deletion rests on another test owning this job.

    ``tests/test_manifest_schemas.py`` checks every manifest's safety-annotation
    vocabulary, risk-label registration, and schema shape — over the manifest
    *data*, which is the right place for it. If that file disappears, the coverage
    this deletion assumed goes with it, so say so here rather than discovering it
    later.
    """
    replacement = Path(__file__).resolve().parent / "test_manifest_schemas.py"

    assert replacement.is_file(), (
        "test_manifest_schemas.py is gone; the manifest-validation coverage that "
        "justified deleting aegis_schema/validation.py needs a new home"
    )
