"""The "are all layers live?" tool must not report OK over a call it never got.

``scripts/verify_llm_layers.py`` is the instrument an acceptance run goes through, so its
final line is a *claim about state*: "every layer resolves to a permitted, non-Mock provider
and answered live". A live call can come back ``success=True`` with an empty body --
measured 2026-10-06, intermittently and *not* a ``max_tokens`` effect (0/20 empty at
32/64/128/256) -- so the tool retries once and then reports a **WARN**, keeping exit 0: the
provider *was* reached, which is what proves the wiring, and failing on a model-side hiccup
would produce false "not operational" readings.

These two tests pin that contract together with its control: an empty body is loud but not
fatal, whereas a call that did not come from a real provider is fatal. Both drive the real
``main()`` and double only the provider call, so the settings store, the egress gate, the
``llm.yaml`` resolver and the provider factory all stay production code.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.router import LLMResponse

pytestmark = pytest.mark.egress

_TOOL_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify_llm_layers.py"


def _load_tool() -> Any:
    """Load the script by explicit path, never by bare name: a name can resolve elsewhere."""
    spec = importlib.util.spec_from_file_location("aegis_verify_llm_layers_under_test", _TOOL_PATH)
    assert spec is not None and spec.loader is not None, f"cannot load {_TOOL_PATH}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def tool() -> Any:
    return _load_tool()


def _run_live(tool: Any, monkeypatch: pytest.MonkeyPatch, response: LLMResponse) -> str:
    """Drive ``main() --live`` with the provider call doubled; return what it printed."""

    def _answer(self: LLMGateway, layer: str, prompt: str, **kwargs: Any) -> LLMResponse:
        return response

    monkeypatch.setattr(LLMGateway, "request", _answer)
    monkeypatch.setattr(sys, "argv", ["verify_llm_layers.py", "--live"])
    return tool.main()


def test_an_empty_body_is_a_warning_not_a_failure(
    tool: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """success=True with no content means the provider answered -- so: exit 0, and say so."""
    rc = _run_live(
        tool,
        monkeypatch,
        LLMResponse(content="", success=True, provider_used="openai", model_used="deepseek-v4-flash"),
    )
    out = capsys.readouterr().out
    assert out.count("WARN ") == 3, f"every layer must report the empty body, got:\n{out}"
    assert "FAIL" not in out, f"an empty body is not a wiring failure, got:\n{out}"
    assert "3 warning(s) above" in out, f"the OK line must not read as unqualified, got:\n{out}"
    assert rc == 0, (
        "an empty body must not fail the check: the destination is permitted and the provider is "
        "not Mock, so the wiring is proven and only the completion is missing"
    )


def test_a_call_that_never_reached_a_provider_is_a_failure(
    tool: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The control: the same driver, one field changed, must flip the verdict to failure."""
    rc = _run_live(
        tool,
        monkeypatch,
        LLMResponse(content="", success=False, provider_used="mock", error="no provider"),
    )
    out = capsys.readouterr().out
    assert out.count("FAIL ") == 3, f"every layer must report the dead call, got:\n{out}"
    assert "OK:" not in out, f"the tool must not claim OK when no real provider answered, got:\n{out}"
    assert rc == 1, "a call that did not come from a real provider must fail the check"
