from __future__ import annotations

import logging

from aegis_ai.intake.l1_models import RequiredIntelligence
from aegis_ai.intake.l1_router import L1Router


class _ErrorGateway:
    def request_json(self, *args, **kwargs):
        return {"error": "TypeSafe API key is not configured"}


class _GenericErrorGateway:
    def request_json(self, *args, **kwargs):
        return {"error": "temporary provider outage"}


class _ExceptionGateway:
    def request_json(self, *args, **kwargs):
        raise RuntimeError("generic llm failure")


class _RaisingGateway:
    """Raise a *chosen* exception type so two types can be compared."""

    def __init__(self, exc: BaseException) -> None:
        self._exc = exc

    def request_json(self, *args, **kwargs):
        raise self._exc


def test_l1_router_surfaces_typesafe_unavailability_as_anomaly() -> None:
    router = L1Router(llm_gateway=_ErrorGateway())  # type: ignore[arg-type]

    observation = router.observe({"event_id": "evt-ts-down", "type": "social.inbox.received"})
    assert observation.value == 1.0
    assert observation.priority == 1.0
    assert observation.raw["summary_bucket"] == "anomaly"


def test_l1_router_surfaces_generic_error_result_as_anomaly() -> None:
    router = L1Router(llm_gateway=_GenericErrorGateway())  # type: ignore[arg-type]
    observation = router.observe({"event_id": "evt-generic-down", "type": "memory.written"})
    assert observation.meaning == "<l1 unavailable>"
    assert observation.required_intelligence == RequiredIntelligence.HIGH
    assert observation.raw["summary_bucket"] == "anomaly"
    assert "temporary provider outage" in observation.raw["error"]


def test_l1_router_surfaces_generic_exception_as_anomaly() -> None:
    router = L1Router(llm_gateway=_ExceptionGateway())  # type: ignore[arg-type]
    observation = router.observe({"event_id": "evt-generic-exc", "type": "memory.written"})
    assert observation.meaning == "<l1 unavailable>"
    assert observation.required_intelligence == RequiredIntelligence.HIGH
    assert observation.raw["summary_bucket"] == "anomaly"
    assert "generic llm failure" in observation.raw["error"]


# ── the failure record must carry the exception *type* (cycles 119/120) ──────
#
# ``observe``'s sentinel observation is the only record the caller gets of *why*
# L1 went unavailable, and ``raw["error"]`` used to be ``str(exc)`` alone -- so
# ``KeyError("payload")`` and ``ValueError("payload")`` produced the identical
# record. These pin the type in both the record and the log line.


def test_the_unavailable_record_carries_the_exception_type() -> None:
    router = L1Router(llm_gateway=_RaisingGateway(KeyError("payload")))  # type: ignore[arg-type]

    observation = router.observe({"event_id": "evt-typed", "type": "memory.written"})
    assert "KeyError" in observation.raw["error"]
    assert "payload" in observation.raw["error"]


def test_two_exception_types_leave_two_different_records() -> None:
    # ValueError and TypeError both render ``str(exc)`` as ``"payload"``, so
    # ``str(exc)`` alone would leave the identical record -- only the *type*
    # distinguishes them. (KeyError is deliberately *not* used here: its
    # ``str`` is ``"'payload'"``, which would differ even without the fix.)
    value_router = L1Router(llm_gateway=_RaisingGateway(ValueError("payload")))  # type: ignore[arg-type]
    type_router = L1Router(llm_gateway=_RaisingGateway(TypeError("payload")))  # type: ignore[arg-type]

    value_error = value_router.observe({"event_id": "e", "type": "t"}).raw["error"]
    type_error = type_router.observe({"event_id": "e", "type": "t"}).raw["error"]

    assert str(ValueError("payload")) == str(TypeError("payload"))
    assert value_error != type_error
    assert value_error == "ValueError: payload"
    assert type_error == "TypeError: payload"


def test_a_raising_llm_is_logged_at_error_with_a_traceback(caplog) -> None:
    router = L1Router(llm_gateway=_RaisingGateway(RuntimeError("boom")))  # type: ignore[arg-type]

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.intake.l1_router"):
        router.observe({"event_id": "evt-log", "type": "memory.written"})

    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert errors, "the failure must be recorded at ERROR"
    assert "RuntimeError" in errors[0].getMessage()
    # ``LogRecord.exc_info`` is ``False`` -- not ``None`` -- when it is unset, so
    # test truthiness rather than ``is not None``.
    assert errors[0].exc_info
    assert errors[0].exc_info[0] is RuntimeError
