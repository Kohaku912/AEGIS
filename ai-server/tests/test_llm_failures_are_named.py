"""The llm/ package names its failures.

Measured 2026-10-06 (cycle 50)
-----------------------------
Six handlers under ``llm/`` had a body that was exactly ``pass``, in five modules. One of
those modules (``json_utils``) had **no logger** -- the package gained one.

Two are the optional-dependency idiom:

- ``factory.py`` ``<module>`` and ``gateway.py::_get_provider_for_profile`` guard
  ``from dotenv import load_dotenv`` with ``except ImportError: pass``. These are named
  rather than allow-listed, so the package rule stays the simple one: **no handler's body
  is ``pass``**. A missing ``dotenv`` means the project ``.env`` is silently not loaded --
  which is worth a DEBUG record precisely because it is invisible otherwise.

Two are **audit** paths -- the same family cycle 45 found in ``personal_ai/``, and the same
argument applies: an audit trail that can fail silently is not an audit trail.

- ``gateway.py::_audit_call``: ``self._prompt_registry.get_metadata(prompt_id)`` raising
  ``KeyError`` dropped the prompt's version/hash from the audit entry, and the entry was
  written anyway with empty strings -- so the record looked complete and was not.
- ``providers/openai_provider.py::_audit_log``: the whole ``self._audit.append(...)`` was
  wrapped in ``except Exception: pass``, so a failed append left **no** record at all.

The remaining two:

- ``json_utils.py::extract_json_object``: the strict ``json.loads`` failure is **expected on
  the common path** -- the fallback below extracts the first ``{...}`` substring. It is
  named at DEBUG for that reason, and the function still raises when there is no object.
- ``prompt_registry.py::update_prompt``: the temp-file ``unlink()`` inside the save-failure
  path. The save failure itself is already reported (``logger.error("Failed to save
  prompts: %s", e)``); only the cleanup was silent. ⚠️ Measured: this handler fires *only*
  after the outer failure, so it is a secondary diagnostic -- naming it does not change what
  the caller sees.

All six now log at DEBUG (behaviour-preserving: a record only).

Scope
-----
Cycle 16's unit, applied to a package: **no handler under ``llm/`` has a body that is
exactly ``pass``**. Handlers that produce a value the caller receives stay out.
"""

from __future__ import annotations

import ast
import json
import logging
from pathlib import Path

import pytest

from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.json_utils import extract_json_object
from aegis_ai.llm.providers.openai_provider import OpenAIProvider

_PKG = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "llm"

_FACTORY = "aegis_ai.llm.factory"
_GATEWAY = "aegis_ai.llm.gateway"
_JSON_UTILS = "aegis_ai.llm.json_utils"
_PROMPT_REGISTRY = "aegis_ai.llm.prompt_registry"
_OPENAI = "aegis_ai.llm.providers.openai"

# (module path relative to the package, enclosing function) -> the logger that must name it.
_NAMED_SITES = {
    ("factory.py", "<module>"): _FACTORY,
    ("gateway.py", "_get_provider_for_profile"): _GATEWAY,
    ("gateway.py", "_audit_call"): _GATEWAY,
    ("json_utils.py", "extract_json_object"): _JSON_UTILS,
    ("prompt_registry.py", "update_prompt"): _PROMPT_REGISTRY,
    ("providers/openai_provider.py", "_audit_log"): _OPENAI,
}


# ── helpers ────────────────────────────────────────────────────────────────


def _modules() -> list[Path]:
    return sorted(_PKG.rglob("*.py"))


def _handlers(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            yield tree, node


def _body_without_docstring(handler: ast.ExceptHandler) -> list[ast.stmt]:
    return [
        s
        for s in handler.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                and isinstance(s.value.value, str))
    ]


def _is_bare_pass(handler: ast.ExceptHandler) -> bool:
    body = _body_without_docstring(handler)
    return len(body) == 1 and isinstance(body[0], ast.Pass)


def _enclosing_function(tree: ast.AST, target: ast.AST) -> str:
    best = "<module>"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if sub is target:
                    best = node.name
    return best


def _names_a_logger(handler: ast.ExceptHandler) -> bool:
    for stmt in _body_without_docstring(handler):
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Attribute) and sub.attr in (
                "debug", "info", "warning", "error", "exception", "critical", "log",
            ):
                if isinstance(sub.value, ast.Name) and "log" in sub.value.id:
                    return True
    return False


# ── structural ─────────────────────────────────────────────────────────────


def test_no_handler_in_llm_is_a_bare_pass():
    offenders = []
    for path in _modules():
        for _tree, handler in _handlers(path):
            if _is_bare_pass(handler):
                offenders.append(f"{path.name}:{handler.lineno}")
    assert offenders == [], f"bare `pass` handlers remain in llm/: {offenders}"


def test_the_census_is_not_vacuous():
    """Measured 2026-10-06: 21 modules, 72 handlers."""
    files = _modules()
    total = sum(1 for path in files for _ in _handlers(path))
    assert len(files) >= 18, f"only {len(files)} files under llm/ -- wrong root?"
    assert total >= 55, f"only {total} handlers found -- the scanner is not seeing them"


def test_each_named_site_calls_a_logger():
    seen = {}
    for path in _modules():
        for tree, handler in _handlers(path):
            key = (path.relative_to(_PKG).as_posix(), _enclosing_function(tree, handler))
            if key in _NAMED_SITES:
                seen[key] = _names_a_logger(handler)
    assert set(seen) == set(_NAMED_SITES), (
        f"missing sites: {sorted(set(_NAMED_SITES) - set(seen))}"
    )
    unnamed = sorted(k for k, ok in seen.items() if not ok)
    assert unnamed == [], f"these sites no longer log their failure: {unnamed}"


def test_the_new_json_utils_logger_exists():
    text = (_PKG / "json_utils.py").read_text(encoding="utf-8")
    assert 'getLogger("aegis_ai.llm.json_utils")' in text


# ── behavioural: the strict JSON parse is named, and the fallback still works ──


def test_extract_json_object_names_a_strict_parse_failure(caplog):
    with caplog.at_level(logging.DEBUG, logger=_JSON_UTILS):
        got = extract_json_object('prose before {"a": 1} prose after')
    assert got == {"a": 1}, "the substring fallback stopped working"
    assert any("Whole-response JSON parse failed" in r.getMessage() for r in caplog.records), (
        "the common-path parse failure left no record"
    )


def test_extract_json_object_on_clean_json_is_quiet(caplog):
    """Control: a clean response must not be reported as a failure."""
    with caplog.at_level(logging.DEBUG, logger=_JSON_UTILS):
        got = extract_json_object('{"a": 1}')
    assert got == {"a": 1}
    assert [r for r in caplog.records if r.name == _JSON_UTILS] == []


def test_extract_json_object_still_raises_when_there_is_no_object(caplog):
    """The record must not replace the raise: a caller relies on it."""
    with caplog.at_level(logging.DEBUG, logger=_JSON_UTILS):
        with pytest.raises(json.JSONDecodeError):
            extract_json_object("no object here")
    assert any("Whole-response JSON parse failed" in r.getMessage() for r in caplog.records)


# ── behavioural: the two audit paths ──────────────────────────────────────


class _AuditSink:
    def __init__(self, *, raises: bool = False):
        self.entries = []
        self._raises = raises

    def append(self, entry):
        if self._raises:
            raise RuntimeError("audit sink down")
        self.entries.append(entry)


class _Registry:
    def __init__(self, *, raises: bool = False):
        self._raises = raises

    def get_metadata(self, prompt_id):
        if self._raises:
            raise KeyError(prompt_id)
        return {"version": "1", "hash": "abc"}


class _Settings:
    provider = "mock"
    model = "m"
    max_tokens = 16
    temperature = 0.0
    reasoning_level = "low"


class _Response:
    success = True
    tokens_used = 3


def _gateway(*, registry_raises: bool, audit=None) -> LLMGateway:
    gw = object.__new__(LLMGateway)
    gw._audit = audit if audit is not None else _AuditSink()
    gw._prompt_registry = _Registry(raises=registry_raises)
    return gw


def test_gateway_names_a_missing_prompt_metadata(caplog):
    gateway = _gateway(registry_raises=True)
    with caplog.at_level(logging.DEBUG, logger=_GATEWAY):
        gateway._audit_call(
            profile="p", prompt_id="pid", settings=_Settings(),
            response=_Response(), duration_ms=1,
        )
    assert any("No prompt metadata" in r.getMessage() for r in caplog.records), (
        "the audit entry was written with empty version/hash, silently"
    )
    # The entry itself is still written -- the behaviour is unchanged.
    assert len(gateway._audit.entries) == 1
    assert gateway._audit.entries[0].prompt_version == ""


def test_gateway_with_prompt_metadata_is_quiet(caplog):
    """Control: a registry that answers must not produce the KeyError record."""
    gateway = _gateway(registry_raises=False)
    with caplog.at_level(logging.DEBUG, logger=_GATEWAY):
        gateway._audit_call(
            profile="p", prompt_id="pid", settings=_Settings(),
            response=_Response(), duration_ms=1,
        )
    assert not any("No prompt metadata" in r.getMessage() for r in caplog.records)
    assert gateway._audit.entries[0].prompt_version == "1"


def test_gateway_without_a_registry_is_quiet(caplog):
    """Control: no registry configured is not a failure."""
    gateway = object.__new__(LLMGateway)
    gateway._audit = _AuditSink()
    gateway._prompt_registry = None
    with caplog.at_level(logging.DEBUG, logger=_GATEWAY):
        gateway._audit_call(
            profile="p", prompt_id="pid", settings=_Settings(),
            response=_Response(), duration_ms=1,
        )
    assert not any("No prompt metadata" in r.getMessage() for r in caplog.records)


def _provider(*, audit) -> OpenAIProvider:
    provider = object.__new__(OpenAIProvider)
    provider._model = "m"
    provider._audit = audit
    return provider


def test_openai_provider_names_a_failed_audit_append(caplog):
    provider = _provider(audit=_AuditSink(raises=True))
    with caplog.at_level(logging.DEBUG, logger=_OPENAI):
        provider._audit_log("llm_call", "EXECUTED", {})
    assert any("Failed to append the LLM audit entry" in r.getMessage() for r in caplog.records), (
        "a failed audit append left no record at all"
    )


def test_openai_provider_without_an_audit_sink_is_quiet(caplog):
    """Control: no audit sink configured is not a failure."""
    provider = _provider(audit=None)
    with caplog.at_level(logging.DEBUG, logger=_OPENAI):
        provider._audit_log("llm_call", "EXECUTED", {})
    assert [r for r in caplog.records if r.name == _OPENAI] == []


def test_openai_provider_with_a_working_sink_is_quiet(caplog):
    """Control: a successful append must not be reported."""
    sink = _AuditSink()
    provider = _provider(audit=sink)
    with caplog.at_level(logging.DEBUG, logger=_OPENAI):
        provider._audit_log("llm_call", "EXECUTED", {})
    assert len(sink.entries) == 1, "the control did not actually append"
    assert [r for r in caplog.records if r.name == _OPENAI] == []
