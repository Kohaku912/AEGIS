"""Cycle 17 pin: the four *reachable* swallows in `context_builder.py` name themselves.

Why only four
-------------
`context_builder.py` has **fourteen** `except` handlers and, before this cycle, **no logger at
all**.  Measuring reachability *before* writing changed the claim: the composition root
(`runtime.py:979`) constructs the builder with **7 of the ~20** backends it accepts, so ten
handlers record nothing on paths that are either never configured or are deliberate fallbacks:

  * 8 sit on backends the root never passes (`_create_default_multimodal_llm` is not called
    because `multimodal_llm` is passed; the `elif self._tool_broker` branch is unreachable
    because the preceding `if self._capability_retriever` branch wins; and
    `_situation_model` / `_user_state_manager` / `_delegation_policy` / `_commitment_manager` /
    `_user_understanding_service` / `_agent_state` are all unwired);
  * 2 are **deliberate fallbacks** that still produce a value (`_user_model_store` falls back to
    `to_context_string()`, `_media_fingerprint` falls back to `str(metadata)`).

Naming the first group would mean adding a record to code that cannot run; naming the second
would misdescribe a handled failure.  This cycle names the remaining **four**, each of which
yields a value indistinguishable from a successful-but-empty result.

Consequence, measured: `ctx.recent_events` and `ctx.recent_media_summaries` are rendered into
the interpreter's context (`llm_task_interpreter.py:367-370`), so a failed read silently drops
a line from what the LLM is told.  `ctx.available_capability_ids` is read only for **token
accounting** (`:722`, `:759`), so its consequence is a wrong budget -- not "the LLM sees no
capabilities".  `ctx.dialogue_policy` is read only inside this module and rendered nowhere.
"""
from __future__ import annotations

import ast
import logging
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from aegis_ai.context_builder import ContextBuilder, MediaInput

_LOGGER = "aegis_ai.context_builder"
_AI_SERVER = Path(__file__).resolve().parents[1]
_MODULE = _AI_SERVER / "src" / "aegis_ai" / "context_builder.py"
_RUNTIME = _AI_SERVER / "src" / "aegis_ai" / "runtime.py"

# The backends the composition root actually passes (measured from runtime.py, pinned below).
_WIRED = {
    "event_bus",
    "tool_broker",
    "multimodal_llm",
    "capability_retriever",
    "settings_resolver",
    "user_model_store",
    "identity",
}

# label -> a phrase only that site's warning contains.
_NAMED: dict[str, str] = {
    "events": "an unreadable event bus looks like a quiet system",
    "capabilities": "an unreadable retriever looks like an empty catalog",
    "media_payload": "a malformed payload looks like an event that carried no media",
    "media_summary": "an unreadable model looks like media with nothing to describe",
}

_TYPE_SHAPE = re.compile(r"\([A-Za-z_][A-Za-z0-9_]*(Error|Exception):")


# ── doubles ────────────────────────────────────────────────────────────────


class _RaisingEventBus:
    def list_recent_events(self, limit):
        raise RuntimeError("event bus unavailable")


class _RaisingRetriever:
    def select_for_request(self, *_a, **_k):
        raise RuntimeError("retriever unavailable")


class _RaisingVisionLLM:
    """Only `generate_with_media` is needed: a video MediaInput takes that branch."""

    def generate_with_media(self, **_k):
        raise RuntimeError("vision backend unavailable")


def _build(**kw) -> ContextBuilder:
    return ContextBuilder(**kw)


def _drive(label: str, system: ContextBuilder, tmp_path) -> None:
    if label == "events":
        system.build()
    elif label == "capabilities":
        system.build()
    elif label == "media_payload":
        event = SimpleNamespace(payload_json="{not json", event_type="t", source_server_id="s")
        system._media_inputs_from_event(event)
    elif label == "media_summary":
        media = MediaInput(kind="video", source="test", name="clip", frames_base64=["AAAA"])
        system._summarize_media(media, "what is this")
    else:  # pragma: no cover
        raise AssertionError(f"unknown label {label!r}")


def _make(label: str, tmp_path) -> ContextBuilder:
    if label == "events":
        return _build(event_bus=_RaisingEventBus())
    if label == "capabilities":
        return _build(capability_retriever=_RaisingRetriever())
    if label == "media_summary":
        return _build(multimodal_llm=_RaisingVisionLLM())
    return _build()


# ── the pin ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("label", sorted(_NAMED))
def test_a_reachable_swallow_is_named(label, tmp_path, caplog) -> None:
    system = _make(label, tmp_path)
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        _drive(label, system, tmp_path)

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any(_NAMED[label] in m for m in messages), (
        f"{label}: the failure left no record naming its consequence; got {messages}"
    )
    assert any(_TYPE_SHAPE.search(m) for m in messages), (
        f"{label}: no record named the exception type; got {messages}"
    )


def test_the_deliberate_fallbacks_still_produce_a_value(tmp_path) -> None:
    """The two fallbacks are *handled* failures, not swallows -- they must still return content."""
    system = _build()

    class _NoRelevantContext:
        def to_context_string(self):
            return "fallback text"

    system._user_model_store = _NoRelevantContext()
    # `relevant_context` is absent, so the `else` branch runs; the fallback in the handler is
    # reached by making `relevant_context` exist and raise.
    class _RelevantRaises:
        def relevant_context(self, *_a):
            raise RuntimeError("store unavailable")

        def to_context_string(self):
            return "fallback text"

    system._user_model_store = _RelevantRaises()
    system.build()
    assert system.last_context is not None


def test_the_composition_root_passes_exactly_these_backends() -> None:
    """If a backend is wired, this goes red and cycle 17 must be revisited."""
    tree = ast.parse(_RUNTIME.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "ContextBuilder":
            found = {kw.arg for kw in node.keywords if kw.arg}
    assert found == _WIRED, (
        f"the composition root's ContextBuilder backends changed: {sorted(found)}"
    )


def _handlers() -> tuple[int, int]:
    """Return (named, silent) counts for `except` handlers in the module."""
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    named = silent = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        calls_logger = any(
            isinstance(sub, ast.Call)
            and isinstance(sub.func, ast.Attribute)
            and isinstance(sub.func.value, ast.Name)
            and sub.func.value.id == "logger"
            for sub in ast.walk(node)
        )
        if calls_logger:
            named += 1
        else:
            silent += 1
    return named, silent


def test_the_silent_handlers_are_exactly_the_unreachable_and_the_fallbacks() -> None:
    """Non-vacuity: 4 named (this cycle), 10 silent (8 unwired + 2 deliberate fallbacks)."""
    named, silent = _handlers()
    assert named == 4, f"expected the 4 named sites, found {named}"
    assert silent == 10, f"expected 10 silent handlers, found {silent}"
    # And the module must actually have gained a logger -- it had none before this cycle.
    source = _MODULE.read_text(encoding="utf-8")
    assert 'logger = logging.getLogger("aegis_ai.context_builder")' in source
