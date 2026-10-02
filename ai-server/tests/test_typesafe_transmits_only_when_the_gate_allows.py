"""The TypeSafe provider transmits only when the egress gate allows it.

``docs/improvement-review.md`` §S-4: ``llm/providers/typesafe_provider.py`` attaches an
``Authorization: Bearer`` header and calls ``request.urlopen`` **directly**, with no gate call in
the method. The safety argument rested on the *construction path* — ``TypeSafeProvider(`` is built
in exactly two places (``llm/factory.py``, ``llm/gateway.py``), and both consult
``egress_allows_llm`` first — which made "the construction path is the only entrance" a
**convention rather than an invariant**.

Two things are pinned here:

* the **behaviour** — with the gate closed, ``_system_one`` transmits **nothing**; with it open, it
  does (so the probe can actually observe a transmission rather than passing vacuously);
* the **structure** — the construction sites are exactly the two gated modules, so a third,
  ungated entrance cannot be added silently.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import aegis_ai
import aegis_ai.llm.factory as factory_module
import aegis_ai.llm.providers.typesafe_provider as provider_module

_BASE_URL = "https://api.typesafe.example/v1/systemone"


class _FakeResponse:
    """Minimal stand-in for ``http.client.HTTPResponse`` — a context manager with ``read``."""

    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False

    def read(self) -> bytes:
        return self._body


def _provider() -> provider_module.TypeSafeProvider:
    return provider_module.TypeSafeProvider(
        model="jev-probe", api_key="probe-key", base_url=_BASE_URL
    )


def _record_transmissions(monkeypatch, calls: list[str]) -> None:
    def fake_urlopen(req, timeout=None):  # noqa: ANN001, ANN202
        calls.append(str(getattr(req, "full_url", "")))
        return _FakeResponse(json.dumps({"answers": {}, "usage": {}}).encode("utf-8"))

    # ``_system_one`` reaches urlopen through the module-level ``request`` alias.
    monkeypatch.setattr(provider_module.request, "urlopen", fake_urlopen)


def test_a_closed_gate_transmits_nothing(monkeypatch) -> None:
    """The method itself must refuse, not merely rely on how it was constructed."""
    calls: list[str] = []
    _record_transmissions(monkeypatch, calls)
    monkeypatch.setattr(factory_module, "egress_allows_llm", lambda base_url, **kw: False)

    raised: Exception | None = None
    try:
        _provider()._system_one(state={}, questions={})
    except Exception as exc:  # noqa: BLE001 - the point is that *something* is raised
        raised = exc

    # Asserted first: this is the defect. A missing or mis-ordered gate shows up here, whereas a
    # ``pytest.raises`` wrapper would report "DID NOT RAISE" — which names the exception, not the
    # transmission that actually happened.
    assert calls == [], (
        "the provider opened an outbound connection with the egress gate closed — "
        "the in-method check is missing or ordered after the request (§S-4)"
    )
    assert raised is not None, "a closed gate must raise rather than return a result"
    assert "Egress gate denied" in str(raised), f"unexpected error: {raised!r}"


def test_an_open_gate_transmits(monkeypatch) -> None:
    """The control: the probe *can* see a transmission, so the test above is not vacuous."""
    calls: list[str] = []
    _record_transmissions(monkeypatch, calls)
    monkeypatch.setattr(factory_module, "egress_allows_llm", lambda base_url, **kw: True)

    result = _provider()._system_one(state={}, questions={})

    assert calls == [_BASE_URL], "the allowed path must reach the network exactly once"
    assert result == {"answers": {}, "usage": {}}


def _calls_named(tree: ast.AST, name: str) -> bool:
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
        for node in ast.walk(tree)
    )


def test_the_only_construction_sites_are_the_gated_ones() -> None:
    """The convention §S-4 relied on, turned into an assertion."""
    root = Path(aegis_ai.__file__).resolve().parent
    sources = sorted(root.rglob("*.py"))

    # Non-vacuity floor: the scan must actually have walked the package.
    assert len(sources) >= 300, f"the scan is blind — only {len(sources)} modules seen"

    constructors: set[str] = set()
    for path in sources:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if _calls_named(tree, "TypeSafeProvider"):
            constructors.add(path.relative_to(root).as_posix())

    assert constructors == {"llm/factory.py", "llm/gateway.py"}, (
        f"the TypeSafe provider's construction sites changed: {sorted(constructors)}. "
        "A new site must consult the egress gate before constructing (§S-4)."
    )

    for rel in sorted(constructors):
        tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        assert _calls_named(tree, "egress_allows_llm"), (
            f"{rel} constructs the provider without consulting the egress gate (§S-4)"
        )
