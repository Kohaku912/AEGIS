"""The L1 gate failure record must carry the cause, not just the fact.

Measured 2026-10-04: `ai-server/data/audit.db` held **706** `llm.first_stage.*.failed` rows whose
`error` was the *fixed* string "exception during L1 tool gate" / "…satisfaction gate", while the
real exception went only to `logger.debug(..., exc_info=True)`. So the audit said *that* the gate
failed and never *why* — none of the 706 rows could be traced to anything, and the same record
also could not distinguish "the gate broke" from "the gate was never reachable".

These tests pin the repaired shape: the record carries the exception's **type and message**, the
failure reaches the **error** log (not only debug), and the gate's return value is unchanged.
"""

from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any

import pytest

from aegis_ai.web import chat_tools

# Tokens only the *raised exception* can supply — a fixed string cannot contain them. That is
# what makes these assertions non-vacuous: a record built from a literal fails them.
TOOL_TOKEN = "tool-gate-boom-9f3a"
SAT_TOKEN = "satisfaction-gate-boom-4c71"

_BARE_TOOL = "exception during L1 tool gate"
_BARE_SAT = "exception during L1 satisfaction gate"


class _RaisingLLM:
    """A gate LLM whose call raises — the branch the old record could not describe."""

    def __init__(self, exc: BaseException) -> None:
        self.exc = exc

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 0,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
        profile: str | None = None,
    ):
        raise self.exc


class _ContentLLM:
    """A gate LLM that answers, so the JSON-shape branches are reachable."""

    def __init__(self, content: str) -> None:
        self.content = content

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 0,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
        profile: str | None = None,
    ):
        return SimpleNamespace(success=True, content=self.content, error="")


@pytest.fixture()
def emitted(monkeypatch) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []

    def _capture(runtime, event_type, **kwargs):
        captured.append({"event_type": event_type, **kwargs})

    monkeypatch.setattr(chat_tools, "_emit_event", _capture)
    return captured


def _run_tool_gate(llm):
    return chat_tools._llm_wants_tools(
        llm,
        "open example.com and check it",
        system_prompt="You are AEGIS.",
        context_meta={"request_id": "req-1"},
        runtime=SimpleNamespace(),
    )


def _run_satisfaction_gate(llm):
    return chat_tools._llm_response_satisfies_without_tools(
        llm,
        "open example.com and check it",
        "I will check that for you.",
        context_meta={"request_id": "req-1"},
        runtime=SimpleNamespace(),
    )


# ── the exception branch: the cause must be in the record ──────────────────────────────


def test_tool_gate_exception_record_carries_the_cause(emitted) -> None:
    wants_tools, pending_tool_call = _run_tool_gate(_RaisingLLM(RuntimeError(TOOL_TOKEN)))

    assert (wants_tools, pending_tool_call) == (None, None)  # behaviour unchanged
    record = emitted[0]
    assert record["event_type"] == "llm.first_stage.tool_gate.failed"
    assert TOOL_TOKEN in record["error"], "the exception message must be in the record"
    assert "RuntimeError" in record["error"], "the exception type must be in the record"
    assert record["error"].startswith(_BARE_TOOL), "the old prefix is kept for existing greps"


def test_satisfaction_gate_exception_record_carries_the_cause(emitted) -> None:
    assert _run_satisfaction_gate(_RaisingLLM(KeyError(SAT_TOKEN))) is None

    record = emitted[0]
    assert record["event_type"] == "llm.first_stage.satisfaction_gate.failed"
    assert SAT_TOKEN in record["error"]
    assert "KeyError" in record["error"]
    assert record["error"].startswith(_BARE_SAT)


def test_the_record_is_not_the_bare_fixed_string(emitted) -> None:
    """The defect itself: a literal would pass every other assertion above."""

    _run_tool_gate(_RaisingLLM(RuntimeError(TOOL_TOKEN)))
    _run_satisfaction_gate(_RaisingLLM(RuntimeError(SAT_TOKEN)))

    assert emitted[0]["error"] != _BARE_TOOL
    assert emitted[1]["error"] != _BARE_SAT
    assert len(emitted[0]["error"]) > len(_BARE_TOOL)


# ── the traceback must reach a log operators actually capture ──────────────────────────
#
# `_emit_l1_gate_failure` already logs the *message* at ERROR, so "an ERROR record exists" is
# vacuous — it stays green even with the traceback demoted to DEBUG (measured: the first two
# versions of this pin survived exactly that mutation). The only record that can carry the
# traceback is the `except` branch's, via `exc_info`. Pin that, not the level alone.


def _error_records_with_traceback(caplog) -> list[logging.LogRecord]:
    return [
        r
        for r in caplog.records
        if r.name == "aegis_ai.web.chat_tools" and r.levelno >= logging.ERROR and r.exc_info
    ]


def test_the_tool_gate_traceback_reaches_the_error_log(caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.web.chat_tools"):
        _run_tool_gate(_RaisingLLM(RuntimeError(TOOL_TOKEN)))

    with_traceback = _error_records_with_traceback(caplog)
    assert with_traceback, "the traceback must attach to an ERROR record, not only a DEBUG one"
    assert any(TOOL_TOKEN in r.getMessage() for r in with_traceback)


def test_the_satisfaction_gate_traceback_reaches_the_error_log(caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.web.chat_tools"):
        _run_satisfaction_gate(_RaisingLLM(RuntimeError(SAT_TOKEN)))

    with_traceback = _error_records_with_traceback(caplog)
    assert with_traceback, "the traceback must attach to an ERROR record, not only a DEBUG one"
    assert any(SAT_TOKEN in r.getMessage() for r in with_traceback)


# ── the malformed-JSON branch had the same defect, one layer out ───────────────────────


def test_tool_gate_malformed_json_records_the_parse_cause(emitted) -> None:
    wants_tools, pending_tool_call = _run_tool_gate(_ContentLLM("{ not json }"))

    assert (wants_tools, pending_tool_call) == (None, None)
    error = emitted[0]["error"]
    assert error.startswith("L1 tool gate JSON parsing failed")
    assert "JSONDecodeError" in error, "the parse cause must survive into the record"


def test_satisfaction_gate_malformed_json_records_the_parse_cause(emitted) -> None:
    assert _run_satisfaction_gate(_ContentLLM("{ not json }")) is None

    error = emitted[0]["error"]
    assert error.startswith("L1 satisfaction gate JSON parsing failed")
    assert "JSONDecodeError" in error


# ── the renderer itself ────────────────────────────────────────────────────────────────


def test_describe_exception_keeps_type_and_message() -> None:
    assert chat_tools._describe_exception(ValueError("bad value")) == "ValueError: bad value"


def test_describe_exception_falls_back_to_the_type_when_messageless() -> None:
    assert chat_tools._describe_exception(ValueError()) == "ValueError: ValueError"
