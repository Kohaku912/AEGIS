"""No handler lists a broad exception alongside others -- the specific names are dead.

Measured 2026-10-06 (cycle 48)
-----------------------------
``except (json.JSONDecodeError, Exception):`` catches **exactly** what
``except Exception:`` catches: ``JSONDecodeError`` is a subclass of ``Exception``, so
naming it adds nothing. The tuple is not a narrower filter that someone forgot to
widen -- it is a filter that *reads* narrower and behaves identically, which is worse:
it suggests a specificity the handler does not have, and it survives review precisely
because it looks careful.

Cycle 43 found two of these in ``task/execution_engine.py`` (``(AttributeError,
Exception)``) and fixed them there. Six remained, in five modules:

- ``backup/import_restore.py`` ``DataImporter.dry_run`` / ``restore`` (2 sites)
- ``backup/integrity.py`` ``validate_manifest``
- ``llm/cost_tracker.py`` ``CostTracker._load``
- ``llm/factory.py`` ``create_multimodal_llm_provider``
- ``security/tokens.py`` ``TokenStore._load``

Three of the six were **also** silent (``pass`` / a bare ``self._tokens = {}``), so this
cycle names those too -- the type change is what makes them visible, and leaving them
silent after touching them would be the "fixed the symptom" failure:

- ``CostTracker._load``: the handler sits **outside** the read loop, so one malformed
  line aborts the whole file -- the ledger comes back *short*, and a short ledger is
  indistinguishable from one that was never written. ⚠️ The *behaviour* is unchanged
  (still aborts; still ``pass``-equivalent); only the record is new.
- ``create_multimodal_llm_provider``: a failed ``settings_resolver.resolve`` left the
  vision provider built from environment defaults with no trace.
- ``TokenStore._load``: ``self._tokens = {}`` on a corrupt file. ⚠️ This module is
  **UNWIRED** (``security/tokens.py`` docstring; ``DELEGATION.md`` §4;
  ``tests/test_security_package_stays_unwired.py``), so this record is **inert today** --
  it is here because the type was wrong, not because it helps. Recorded, not claimed.

The tuple change is **provably value-identical** at every one of the six sites: the
caught set of ``(X, Exception)`` is the caught set of ``Exception``. The three ``backup``
sites already reported through their return values and still do.

Scope
-----
Repo-wide, on the *type*: no ``ExceptHandler`` under ``ai-server/src`` may list
``Exception`` or ``BaseException`` in a tuple with other names. A single-name
``except Exception:`` is not the defect -- the tuple is.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from aegis_ai.backup.integrity import validate_manifest
from aegis_ai.llm.cost_tracker import CostTracker
from aegis_ai.llm.factory import create_multimodal_llm_provider

_SRC = Path(__file__).resolve().parents[1] / "src"
_COST = "aegis_ai.llm.cost_tracker"
_FACTORY = "aegis_ai.llm.factory"
_TOKENS = "aegis_ai.security.tokens"

_BROAD = {"Exception", "BaseException"}


# ── the detector, factored out so it can be tested on synthetic sources ─────


def redundant_broad_tuples(source: str) -> list[tuple[int, list[str]]]:
    """Return ``(lineno, names)`` for every handler whose type tuple is redundant."""
    found = []
    for handler in ast.walk(ast.parse(source)):
        if not isinstance(handler, ast.ExceptHandler) or handler.type is None:
            continue
        elts = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
        names = [ast.unparse(e) for e in elts]
        if len(names) > 1 and any(n in _BROAD for n in names):
            found.append((handler.lineno, names))
    return found


# ── structural: the rule, and proof the instrument is not empty ─────────────


def test_no_redundant_broad_except_tuple_in_the_tree():
    offenders = []
    for path in sorted(_SRC.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, names in redundant_broad_tuples(text):
            offenders.append(f"{path.relative_to(_SRC)}:{lineno} ({', '.join(names)})")
    assert offenders == [], f"redundant broad-except tuples remain: {offenders}"


def test_the_scan_covers_the_tree():
    """Non-vacuity: a wrong root or a rename would make the rule pass by scanning nothing."""
    files = 0
    handlers = 0
    for path in sorted(_SRC.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, SyntaxError):
            continue
        files += 1
        handlers += sum(1 for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler))
    assert files >= 350, f"only {files} modules scanned -- wrong root?"
    assert handlers >= 900, f"only {handlers} handlers seen -- the scanner is blind"


def test_the_detector_actually_fires():
    """Control: the instrument distinguishes a redundant tuple from a genuine one."""
    assert redundant_broad_tuples("try:\n    pass\nexcept (ValueError, Exception):\n    pass\n") == [
        (3, ["ValueError", "Exception"])
    ]
    # A genuine multi-exception filter must NOT be flagged.
    assert redundant_broad_tuples("try:\n    pass\nexcept (ValueError, TypeError):\n    pass\n") == []
    # A single broad name is fine -- it is honest about what it catches.
    assert redundant_broad_tuples("try:\n    pass\nexcept Exception:\n    pass\n") == []
    assert redundant_broad_tuples("try:\n    pass\nexcept (OSError, BaseException):\n    pass\n") == [
        (3, ["OSError", "BaseException"])
    ]


def test_import_restore_handlers_all_report_through_result_errors():
    """Every handler in ``import_restore`` reports via ``result.errors``; none is silent.

    ⚠️ The tuple scan found **two** redundant tuples here, but the file has **three**
    handlers -- the third (``Failed to restore {key}``) was already ``except Exception``.
    A count of *defects* is not a count of *sites*; this asserts the sites.
    """
    src = (_SRC / "aegis_ai" / "backup" / "import_restore.py").read_text(encoding="utf-8")
    handlers = [h for h in ast.walk(ast.parse(src)) if isinstance(h, ast.ExceptHandler)]
    assert len(handlers) == 3, f"expected 3 handlers, found {len(handlers)}"
    assert [ast.unparse(h.type) for h in handlers] == ["Exception"] * 3

    def _body(h: ast.ExceptHandler) -> str:
        return ast.unparse(ast.Module(body=h.body, type_ignores=[]))

    reporting = [h for h in handlers if "result.errors" in _body(h)]
    assert len(reporting) == 3, "a handler stopped reporting through result.errors"
    # The two this cycle changed are the pair that reports a bad data file.
    assert sum(1 for h in reporting if "Invalid data file" in _body(h)) == 2


def test_validate_manifest_still_reports_a_bad_manifest(tmp_path):
    bad = tmp_path / "manifest.json"
    bad.write_text("not json", encoding="utf-8")
    ok, errors = validate_manifest(str(bad))
    assert ok is False
    assert errors and "Invalid manifest JSON" in errors[0]


# ── behavioural: the three sites that were also silent are now named ───────


def test_cost_tracker_names_a_malformed_ledger(tmp_path, caplog):
    ledger = tmp_path / "cost.jsonl"
    # The malformed line comes FIRST, so the valid line after it is never read.
    ledger.write_text("NOT JSON\n{}\n", encoding="utf-8")
    with caplog.at_level(logging.DEBUG, logger=_COST):
        tracker = CostTracker(path=str(ledger))
    assert any("Failed to load cost entries" in r.getMessage() for r in caplog.records), (
        "a truncated ledger was still indistinguishable from an empty one"
    )
    assert any(r.exc_info for r in caplog.records), "the traceback was not attached"
    # Behaviour preserved: the whole read aborted, so the valid second line was dropped.
    assert tracker._entries == []


def test_cost_tracker_with_a_valid_ledger_is_quiet(tmp_path, caplog):
    """Control: the record must come from the failure, not from loading."""
    ledger = tmp_path / "cost.jsonl"
    ledger.write_text("{}\n{}\n", encoding="utf-8")
    with caplog.at_level(logging.DEBUG, logger=_COST):
        tracker = CostTracker(path=str(ledger))
    assert len(tracker._entries) == 2, "the control did not actually load anything"
    assert [r for r in caplog.records if r.name == _COST] == []


class _RaisingResolver:
    def resolve(self, **_kwargs):
        raise KeyError("vision_observation")


def test_multimodal_factory_names_a_failed_profile_resolution(caplog):
    with caplog.at_level(logging.DEBUG, logger=_FACTORY):
        create_multimodal_llm_provider(
            provider_name="mock", settings_resolver=_RaisingResolver()
        )
    assert any("Failed to resolve the vision profile" in r.getMessage() for r in caplog.records)


def test_multimodal_factory_without_a_resolver_is_quiet(caplog):
    """Control: no resolver configured is not a failure."""
    with caplog.at_level(logging.DEBUG, logger=_FACTORY):
        create_multimodal_llm_provider(provider_name="mock", settings_resolver=None)
    assert [r for r in caplog.records if r.name == _FACTORY] == []


def test_token_store_load_is_named_and_its_fallback_is_unchanged():
    """Measured on the *source*, not by driving it -- see the note below.

    ⚠️ This module is UNWIRED, and ``tests/test_security_package_stays_unwired.py`` asserts
    that nothing outside ``aegis_ai/security/`` **imports** the package or **names** its
    documented classes (``ast.Name`` / ``ast.Attribute``, so a docstring is fine but a call
    site is not). An ``import`` here fails *that* guard -- measured 2026-10-06: the first
    version of this pin did exactly that, and two of the guard's assertions went red. So the
    check reads the file instead. That also matches the module's status: a record in code
    nothing calls is **inert**, so driving it would prove nothing about the system.
    """
    src = (_SRC / "aegis_ai" / "security" / "tokens.py").read_text(encoding="utf-8")
    handlers = [h for h in ast.walk(ast.parse(src)) if isinstance(h, ast.ExceptHandler)]
    assert len(handlers) == 1, f"expected 1 handler, found {len(handlers)}"
    handler = handlers[0]
    assert ast.unparse(handler.type) == "Exception", "the redundant tuple came back"
    body = ast.unparse(ast.Module(body=handler.body, type_ignores=[]))
    assert "logger.debug" in body, "the failure is silent again"
    assert "self._tokens = {}" in body, "the fallback value moved"


def test_the_two_new_loggers_exist():
    for name, rel in ((_COST, "aegis_ai/llm/cost_tracker.py"),
                      (_TOKENS, "aegis_ai/security/tokens.py")):
        text = (_SRC / rel).read_text(encoding="utf-8")
        assert f'getLogger("{name}")' in text, f"{rel} lost its logger {name}"
