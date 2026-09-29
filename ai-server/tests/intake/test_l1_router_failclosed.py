from __future__ import annotations

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
