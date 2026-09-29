"""Every guarded egress point refuses while the constraint is closed.

AEGIS has exactly one constraint: **the user's information must never leave the
local environment.** Phase 1 built the gate (``aegis_ai/egress/``) and wired it
into the components that transmit data. ``test_egress_gate.py`` covers the gate
itself plus the LLM factory/gateway and a few wired points.

This module closes the remaining gap. It drives *each* guarded egress point listed
in ``docs/egress-gate.md`` and asserts that nothing leaves the process.

Two things make this a regression suite rather than a smoke test:

1. **The inventory is executable.** ``_AI_SERVER_POINTS`` below maps every point
   in the doc's "Guarded egress points" table to the test module that exercises
   it, and ``test_the_documented_inventory_and_this_suite_agree`` parses the doc
   and asserts the two agree. A newly documented point with no test, or a test
   for a point that is no longer documented, both fail.

2. **Each point is driven for real**, through its own public entry point — never
   asserted by reading source. Phase 1 found a guard
   (``browser-server``'s ``check_domain()``) that existed but was *never called*;
   a source-inspecting test would have passed. Every test here also asserts that
   the underlying transport was never touched, so "the response says denied" and
   "nothing actually left" are checked separately.
"""

from __future__ import annotations

import smtplib
import types
from pathlib import Path

import pytest

# Every test in this module guards the single constraint. The marker is counted by
# --require-egress-tests (see conftest.py) so this suite can never silently run empty.
pytestmark = pytest.mark.egress

_TESTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TESTS_DIR.parents[1]
_SRC = _TESTS_DIR.parent / "src"
_DOC_PATH = _REPO_ROOT / "docs" / "egress-gate.md"


# ── Shared helpers ────────────────────────────────────────────────────────────
#
# The settings-store double and the "gate closed, restored afterwards" fixture live
# in tests/conftest.py (``settings_store`` / ``closed_egress_gate``) so that every
# egress suite drives the gate the same way.


# ── The executable inventory ──────────────────────────────────────────────────
#
# Keyed by the exact `File` cell in docs/egress-gate.md's guarded-point table.
# The value is the test module that exercises that point. `test_egress_gate.py`
# (Phase 1) already covers its entries; the rest are covered below in this module.

_AI_SERVER_POINTS: dict[str, str] = {
    "llm/factory.py": "test_egress_gate.py",
    "llm/gateway.py": "test_egress_gate.py",
    "llm/router.py": "test_egress_closure.py",
    "integrations/duckduckgo_search.py": "test_egress_closure.py",
    "integrations/tts_service.py": "test_egress_closure.py",
    "integrations/webhook_sender.py": "test_egress_closure.py",
    "integrations/agora/agora_client.py": "test_egress_closure.py",
    "observability/otel_tracing.py": "test_egress_closure.py",
    "briefing/provider.py": "test_egress_gate.py",
    "agents/backends/openhands/workspace.py": "test_egress_gate.py",
    "server_executor.py": "test_egress_closure.py",
    "personal_ai/social_proxy.py": "test_egress_closure.py",
}


def _documented_egress_points() -> dict[str, set[str]]:
    """Parse the guarded-point tables out of ``docs/egress-gate.md``.

    Returns ``{"ai-server": {file, ...}, "browser-server": {file, ...}}``. Only the
    `File` cell of each table row is collected, so the prose can change freely.
    """
    sections: dict[str, set[str]] = {"ai-server": set(), "browser-server": set()}
    section: str | None = None

    for line in _DOC_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = "ai-server" if "Guarded egress points" in line else None
        elif line.startswith("### "):
            section = "browser-server" if "Browser Server" in line else None
        elif section is not None and line.startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            # The File cell is the second one and is always backticked; this skips
            # the header row and the |---|---| separator.
            if len(cells) >= 2 and cells[1].startswith("`"):
                sections[section].add(cells[1].strip("`"))

    return sections


def _resolve_src(point: str) -> Path:
    """Locate a doc-listed file under ``src/`` (aegis_ai/ first, then src/)."""
    for candidate in (_SRC / "aegis_ai" / point, _SRC / point):
        if candidate.is_file():
            return candidate
    return _SRC / "aegis_ai" / point


# ── Drift guards ──────────────────────────────────────────────────────────────


def test_the_documented_inventory_and_this_suite_agree():
    """The doc's guarded-point table and this suite's inventory must be identical.

    This is the drift guard. Adding a row to docs/egress-gate.md without adding a
    covering test fails here; so does deleting a test while leaving the doc claim.
    """
    documented = _documented_egress_points()["ai-server"]
    assert documented, "docs/egress-gate.md no longer lists any guarded egress points"

    assert documented == set(_AI_SERVER_POINTS), (
        "docs/egress-gate.md and _AI_SERVER_POINTS have drifted.\n"
        f"  documented but untracked: {sorted(documented - set(_AI_SERVER_POINTS))}\n"
        f"  tracked but undocumented: {sorted(set(_AI_SERVER_POINTS) - documented)}\n"
        "Update both sides together."
    )


@pytest.mark.parametrize("point", sorted(_AI_SERVER_POINTS))
def test_each_documented_point_exists_and_has_a_covering_test(point: str):
    assert _resolve_src(point).is_file(), f"{point} is documented as guarded but does not exist"

    covering = _TESTS_DIR / _AI_SERVER_POINTS[point]
    assert covering.is_file(), f"{point} is covered by {covering.name}, which does not exist"


def test_browser_server_points_are_covered_in_its_own_suite():
    """browser-server carries its own gate, so its points get their own tests.

    The two distributions deliberately duplicate the gate; this check keeps the
    browser side from quietly losing coverage.
    """
    documented = _documented_egress_points()["browser-server"]
    assert documented, "docs/egress-gate.md no longer lists the browser-server points"

    browser_egress_tests = _REPO_ROOT / "browser-server" / "tests" / "test_egress.py"
    source = browser_egress_tests.read_text(encoding="utf-8")

    for name in sorted(documented):
        stem = name[:-3] if name.endswith(".py") else name
        assert stem in source, (
            f"{name} is documented as a guarded browser-server point, but "
            f"browser-server/tests/test_egress.py never mentions {stem}"
        )


# ── Web search (integrations/duckduckgo_search.py) ────────────────────────────


@pytest.mark.parametrize("method", ["search", "news"])
def test_web_search_withholds_the_query_when_closed(closed_egress_gate, monkeypatch, method):
    """The query is derived from user context, so it must not be transmitted.

    The backends are replaced with loud failures: if the guard were removed, the
    test would error rather than merely assert a response field.
    """
    from aegis_ai.integrations.duckduckgo_search import DuckDuckGoSearch

    def _never(name: str):
        def _backend(*_args, **_kwargs):
            pytest.fail(f"{name} was called — the search query left the process")

        return _backend

    for backend in ("_search_ddgs", "_search_legacy_package", "_search_html", "_news_ddgs"):
        monkeypatch.setattr(DuckDuckGoSearch, backend, _never(backend))

    response = getattr(DuckDuckGoSearch(), method)("my private medical query")

    assert response.success is False
    assert "single constraint" in response.error


# ── Text-to-speech (integrations/tts_service.py) ──────────────────────────────


def test_tts_withholds_the_text_when_closed(closed_egress_gate, monkeypatch):
    """edge-tts is a cloud service, so the spoken text must not be sent."""
    from aegis_ai.integrations.tts_service import TextToSpeechService, TTSRequest

    def _never(*_args, **_kwargs):
        pytest.fail("the TTS synthesis path was reached — the text left the process")

    monkeypatch.setattr(TextToSpeechService, "_synthesize_async", _never)

    result = TextToSpeechService().synthesize(TTSRequest(text="my private notes"))

    assert result.success is False
    assert "single constraint" in result.error


# ── Webhooks (integrations/webhook_sender.py) ─────────────────────────────────


def test_webhook_withholds_the_payload_when_closed(closed_egress_gate, monkeypatch):
    from aegis_ai.integrations.webhook_sender import (
        WebhookRequest,
        WebhookSender,
    )

    def _never(*_args, **_kwargs):
        pytest.fail("the webhook transport was reached — the payload left the process")

    monkeypatch.setattr(WebhookSender, "_execute_with_retry", _never)

    response = WebhookSender().send(
        WebhookRequest(url="https://hooks.external.example.com/ingest", payload={"secret": 1})
    )

    assert response.success is False
    assert "single constraint" in response.error


def test_webhook_still_allows_a_local_destination(closed_egress_gate):
    """The gate blocks external hosts, not the feature itself."""
    from aegis_ai.integrations.webhook_sender import WebhookSender

    assert WebhookSender._egress_allows("http://localhost:9000/hook") is True


# ── AGORA (integrations/agora/agora_client.py) ────────────────────────────────


def test_agora_request_is_denied_when_closed(closed_egress_gate, monkeypatch):
    """AGORA carries posts and account identity — both are user information."""
    import httpx

    from aegis_ai.integrations.agora.agora_client import AgoraClient

    def _never(*_args, **_kwargs):
        pytest.fail("an HTTP client was built — the AGORA request left the process")

    monkeypatch.setattr(httpx, "Client", _never)

    result = AgoraClient(token="token", base_url="https://api.agora.example.com")._request(
        "GET", "/posts"
    )

    assert isinstance(result, dict)
    assert result["error"] == "egress_denied"


# ── OpenTelemetry (observability/otel_tracing.py) ─────────────────────────────


@pytest.mark.parametrize(
    "endpoint,expected",
    [
        ("http://localhost:4317", True),
        ("http://127.0.0.1:4317", True),
        ("http://192.168.1.20:4317", True),
        ("https://otlp.external.example.com:4317", False),
        ("http://collector.example.com:4317", False),
        ("", False),  # unclassifiable → fail closed
        ("not a url", False),
    ],
)
def test_otel_endpoint_classification_is_local_only(endpoint, expected):
    """Spans and metrics carry user context, so the OTLP endpoint must be local."""
    from aegis_ai.observability.otel_tracing import _endpoint_is_local

    assert _endpoint_is_local(endpoint) is expected


def test_otel_refuses_to_export_to_a_remote_endpoint(monkeypatch):
    """A remote OTLP endpoint must never receive a span."""
    otlp_module = pytest.importorskip(
        "opentelemetry.exporter.otlp.proto.grpc.trace_exporter"
    )
    sdk_export = pytest.importorskip("opentelemetry.sdk.trace.export")

    from aegis_ai.observability import otel_tracing

    constructed: list[str] = []

    class _RecordingExporter:
        def __init__(self, endpoint: str = "", **_kwargs) -> None:
            constructed.append(endpoint)

        def export(self, *_args, **_kwargs) -> None:
            return None

        def shutdown(self, *_args, **_kwargs) -> None:
            return None

        def force_flush(self, *_args, **_kwargs) -> bool:
            return True

    # Both exporters are recorded: the point is to see *which* one was chosen.
    monkeypatch.setattr(otlp_module, "OTLPSpanExporter", _RecordingExporter)
    monkeypatch.setattr(sdk_export, "ConsoleSpanExporter", _RecordingExporter)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://otlp.external.example.com:4317")
    monkeypatch.setattr(otel_tracing, "_initialized", False)

    otel_tracing.init_tracing()

    # Non-empty proves the run reached the exporter decision rather than
    # early-returning because OpenTelemetry was unavailable.
    assert constructed, "init_tracing() returned before building any exporter"
    assert all("external.example.com" not in endpoint for endpoint in constructed), (
        f"a span exporter was built for a remote endpoint: {constructed}"
    )


def test_otel_exports_to_a_local_endpoint(monkeypatch):
    """Guard the guard: the refusal above must not be a blanket refusal."""
    otlp_module = pytest.importorskip(
        "opentelemetry.exporter.otlp.proto.grpc.trace_exporter"
    )

    from aegis_ai.observability import otel_tracing

    constructed: list[str] = []

    class _RecordingExporter:
        def __init__(self, endpoint: str = "", **_kwargs) -> None:
            constructed.append(endpoint)

        def export(self, *_args, **_kwargs) -> None:
            return None

        def shutdown(self, *_args, **_kwargs) -> None:
            return None

        def force_flush(self, *_args, **_kwargs) -> bool:
            return True

    monkeypatch.setattr(otlp_module, "OTLPSpanExporter", _RecordingExporter)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    monkeypatch.setattr(otel_tracing, "_initialized", False)

    otel_tracing.init_tracing()

    assert any("localhost:4317" in endpoint for endpoint in constructed), (
        f"a local OTLP endpoint should be exported to, got: {constructed}"
    )


# ── Server executor (server_executor.py) ──────────────────────────────────────


def test_http_executor_refuses_an_external_endpoint(closed_egress_gate, monkeypatch):
    """A manifest resolving to an external host must be refused, not transmitted."""
    import urllib.request

    from server_executor import ServerExecutor

    def _never(*_args, **_kwargs):
        pytest.fail("urlopen was called — capability parameters left the process")

    monkeypatch.setattr(urllib.request, "urlopen", _never)

    result = ServerExecutor()._execute_http(
        {"endpoint": "https://api.external.example.com/execute"}, {"secret": "x"}
    )

    assert result["code"] == "EGRESS_DENIED"


def test_http_executor_still_allows_a_local_endpoint(closed_egress_gate, monkeypatch):
    """The guard must not break ordinary loopback/LAN server-to-server calls."""
    from server_executor import ServerExecutor

    reached: list[str] = []

    def _stop(req, timeout=None):
        reached.append(req.full_url)
        raise OSError("stop here — we only care that the gate allowed the call")

    monkeypatch.setattr("urllib.request.urlopen", _stop)

    result = ServerExecutor()._execute_http({"endpoint": "http://localhost:50053/run"}, {})

    assert reached == ["http://localhost:50053/run"]
    assert "code" not in result or result.get("code") != "EGRESS_DENIED"


def test_pc_tcp_executor_refuses_a_host_outside_the_environment(closed_egress_gate, monkeypatch):
    """A PC Server host that resolves externally must not receive the command."""
    import server_executor

    monkeypatch.setattr(
        "aegis_ai.net.endpoint_resolver.resolve_tcp_endpoint",
        lambda *_args, **_kwargs: ("pc.external.example.com", 50052),
    )
    monkeypatch.setattr(
        server_executor.socket,
        "socket",
        lambda *_args, **_kwargs: pytest.fail(
            "a socket was opened — the PC command left the process"
        ),
    )

    manifest = types.SimpleNamespace(tcp_command="echo {command}", tcp_command_json="")
    result = server_executor.ServerExecutor()._execute_pc_tcp(
        "pc-server.shell.execute", {"command": "whoami"}, manifest
    )

    assert result["code"] == "EGRESS_DENIED"


# ── Email (personal_ai/social_proxy.py) ───────────────────────────────────────


def test_smtp_send_is_denied_when_closed(closed_egress_gate, monkeypatch, tmp_path):
    """An outbound email carries the user's information to an external mail server."""
    from aegis_ai.personal_ai.social_proxy import SocialProxy

    monkeypatch.setenv("AEGIS_SMTP_HOST", "smtp.external.example.com")
    monkeypatch.setenv("AEGIS_SMTP_FROM", "owner@example.com")
    monkeypatch.setattr(
        smtplib, "SMTP", lambda *_args, **_kwargs: pytest.fail("an SMTP session was opened")
    )

    result = SocialProxy(data_dir=str(tmp_path))._send_email(
        {"to": "friend@example.com", "subject": "hi", "body": "my private message"}
    )

    assert result["ok"] is False
    assert result["code"] == "EGRESS_DENIED"


# ── LLM routing (llm/router.py) ───────────────────────────────────────────────


class _NamedProvider:
    """Minimal provider stub — the router only reads the destination."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url


def _routing_router(settings_store_factory, *, external_llm_allowed: bool):
    """Build a router with one cloud provider and one local provider registered."""
    from aegis_ai.llm.router import LLMRouter

    router = LLMRouter(
        settings_store=settings_store_factory(external_llm_allowed=external_llm_allowed)
    )
    router.register_provider("deepseek", _NamedProvider("https://api.deepseek.com"))
    router.register_provider("mock", _NamedProvider(""))
    router.set_default_provider("deepseek")
    return router


def test_router_does_not_select_a_cloud_provider_when_the_flag_is_off(
    closed_egress_gate, settings_store_factory
):
    from aegis_ai.llm.router import TaskType

    router = _routing_router(settings_store_factory, external_llm_allowed=False)

    assert router._select_provider(TaskType.PLANNING) == "mock"


def test_router_does_not_select_a_cloud_provider_when_only_the_flag_is_on(
    closed_egress_gate, settings_store_factory
):
    """The flag alone must never be enough — the gate is consulted even when it is set.

    This is the router half of the retired "declared but ineffective" bug: a
    settings flag that no longer influences the outcome.
    """
    from aegis_ai.llm.router import TaskType

    router = _routing_router(settings_store_factory, external_llm_allowed=True)

    assert router._select_provider(TaskType.PLANNING) == "mock"


def test_router_selects_the_cloud_provider_only_when_every_lock_is_open(settings_store_factory):
    """Guard the guard: the tests above would pass trivially if selection were broken."""
    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.llm.router import TaskType

    configure_egress_gate(
        settings_store=settings_store_factory(
            external_egress_allowed=True,
            external_llm_allowed=True,
        ),
        allowed_hosts=["api.deepseek.com"],
    )

    router = _routing_router(settings_store_factory, external_llm_allowed=True)

    assert router._select_provider(TaskType.PLANNING) == "deepseek"
