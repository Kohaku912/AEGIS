"""The L1 dashboard metric ``event_driven_llm_calls_60s`` has a producer.

``web/routes/l1_routes.py`` counts an audit row as an *event-driven L1 LLM call*
only when it satisfies a two-part predicate (the reader is already queried with
``actor="llm"``, ``action="llm_call"``)::

    profile_id == "l1_default"  and  detail["source"] == "l1_router.observe"

``tests/test_l1_routes.py`` pins the *counting* — but with hand-written audit dicts
that already have that shape. Nothing proved the real L1 request path **emits** it,
so the two halves (producer / consumer) could drift apart silently: rename the L1
profile, move the ``source`` key, change the provider's ``actor`` — the route keeps
returning 0 while every existing test stays green.

This module drives the real chain and closes that gap:

    L1Router.observe -> LLMGateway.request_json(layer="L1")
      -> request -> generate -> _enrich_context_meta(profile="l1_default")
      -> a real TypeSafeProvider (the provider ``l1_default`` names)
      -> the real AuditLog -> the real AuditManager -> the real route.

Measured 2026-10-09 (cycle 125): one ``L1Router.observe`` produces exactly one
``actor="llm"`` ``llm_call`` row with ``profile_id="l1_default"`` and
``detail["source"]=="l1_router.observe"``, and ``/api/l1/events/stats`` counts it.

⚠️ What is stubbed, and why. ``LLMGateway._get_provider_for_profile`` is replaced
with one that returns a real ``TypeSafeProvider``. The real factory consults the
egress gate, whose answer depends on this machine's ``settings.json`` (and on
whether a local Ollama is listening); neither belongs in a pin about an audit
*shape*. The provider that IS built is the real one — the same class the shipped
``l1_default`` profile names (asserted below) — and it is given an empty API key so
``generate`` takes its ``_failure_response`` branch: the audit row is still written,
and no socket is opened.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from flask import Flask

from aegis_ai.audit.audit_log import AuditLog
from aegis_ai.audit.audit_manager import AuditManager
from aegis_ai.intake.l1_router import L1Router
from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.layer_profiles import layer_to_profile
from aegis_ai.llm.providers.typesafe_provider import TypeSafeProvider
from aegis_ai.llm.settings_resolver import LLMSettingsResolver
from aegis_ai.web.routes.l1_routes import init_l1_routes

# The shipped config — the same file the runtime loads.
_LLM_YAML = Path(__file__).resolve().parents[1] / "config" / "llm.yaml"


class _Runtime:
    """The two attributes ``l1_routes`` reads: ``event_manager`` / ``audit_manager``."""

    def __init__(self, audit_manager: Any) -> None:
        self.event_manager = None  # no persisted events -> only the audit half is exercised
        self.audit_manager = audit_manager


class _Owner:
    def __init__(self, runtime: _Runtime) -> None:
        self._runtime = runtime
        self.app = Flask(__name__)


class _Stack:
    """The real producer -> consumer chain, on a throwaway audit DB."""

    def __init__(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # Empty key -> TypeSafeProvider._failure_response: audited, no socket.
        monkeypatch.setenv("TYPESAFE_API_KEY", "")
        self.audit_log = AuditLog(path=str(tmp_path / "audit.jsonl"))
        self.audit_manager = AuditManager(
            audit_log=self.audit_log, data_dir=str(tmp_path / "data")
        )
        self.gateway = LLMGateway(
            router=None,
            settings_resolver=LLMSettingsResolver(str(_LLM_YAML)),
            audit_log=self.audit_log,
        )
        monkeypatch.setattr(
            self.gateway,
            "_get_provider_for_profile",
            lambda settings: TypeSafeProvider(api_key="", audit_log=self.audit_log),
        )
        self.router = L1Router(llm_gateway=self.gateway)

        owner = _Owner(_Runtime(self.audit_manager))
        init_l1_routes(owner)
        self.client = owner.app.test_client()

    def stats(self) -> dict[str, Any]:
        res = self.client.get("/api/l1/events/stats")
        assert res.status_code == 200
        return res.get_json()

    def llm_call_rows(self) -> list[dict[str, Any]]:
        return self.audit_manager.read_recent_for_dashboard(
            max_entries=200, action="llm_call", actor="llm"
        )


def test_the_shipped_l1_profile_is_the_one_the_metric_names() -> None:
    """The metric hard-codes ``"l1_default"``; the layer mapping must produce it.

    If this fails, every ``event_driven_llm_calls_60s`` reading silently becomes 0
    (the route compares against a name the L1 call no longer carries).
    """
    assert layer_to_profile("L1") == "l1_default"
    settings = LLMSettingsResolver(str(_LLM_YAML)).resolve(profile_id="l1_default")
    assert settings.provider == "typesafe", (
        "l1_default no longer names the typesafe provider — the stub in _Stack (and "
        "the metric's expectation) are stale"
    )


def test_one_observe_produces_the_row_the_metric_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = _Stack(tmp_path, monkeypatch)
    stack.router.observe({"event_type": "pc.user_activity.snapshot"}, event_id="e1")

    rows = stack.llm_call_rows()
    assert len(rows) == 1, rows
    row = rows[0]
    assert row["action"] == "llm_call"
    assert row["actor"] == "llm"
    assert row["profile_id"] == "l1_default"
    assert row["detail"]["source"] == "l1_router.observe"

    body = stack.stats()
    assert body["llm_calls_60s"] == 1
    assert body["event_driven_llm_calls_60s"] == 1


def test_the_route_counts_every_observe_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = _Stack(tmp_path, monkeypatch)
    for i in range(3):
        stack.router.observe({"event_type": "pc.user_activity.snapshot"}, event_id=f"e{i}")

    body = stack.stats()
    assert body["llm_calls_60s"] == 3
    assert body["event_driven_llm_calls_60s"] == 3


def test_the_source_half_of_the_predicate_is_load_bearing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An L1 call with no ``source`` is an llm_call, but not an *event-driven* one."""
    stack = _Stack(tmp_path, monkeypatch)
    stack.gateway.request_json(layer="L1", prompt="x", context_meta={"event_id": "e1"})

    body = stack.stats()
    assert body["llm_calls_60s"] == 1
    assert body["event_driven_llm_calls_60s"] == 0


def test_the_profile_half_of_the_predicate_is_load_bearing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An L2 call carrying the L1 ``source`` is not counted as an L1 call."""
    stack = _Stack(tmp_path, monkeypatch)
    stack.gateway.request_json(
        layer="L2", prompt="x", context_meta={"source": "l1_router.observe"}
    )

    body = stack.stats()
    assert body["llm_calls_60s"] == 1
    assert body["event_driven_llm_calls_60s"] == 0
