"""Production stops when L1 cannot authenticate -- the audit alone is not enough
(DELEGATION.md section 4 item 46).

Measured 2026-10-05 (the record): with ``TYPESAFE_API_KEY`` unset, ``llm/gateway.py`` still
constructs ``TypeSafeProvider`` with an empty key, every call fails, and
``intake/l1_router._l1_unavailable_observation`` returns ``required_intelligence=HIGH``, so
**every** event escalates -- the process runs and looks alive while L1 classifies nothing.

That degradation is not *silent*: ``_audit_llm_profile_health`` logs ``issue=missing_api_key``
at ERROR. So the item was not "make it visible" but "decide whether it is fatal". Branch (1)
was selected, and the gate is the production-mode fail-fast that already exists in
``_build_runtime`` ("cannot start with MockLLMProvider") and in ``docker_entrypoint.main``
(auth mode / session secret) -- extended to the misconfiguration it did not cover.

Two things this file measures rather than asserts by description:

1. **Why CI stays safe.** The gate keys on ``is_production_mode()``, i.e. ``AEGIS_RUNTIME_MODE``
   (default ``development``). No CI job and no test sets it; its only occurrence outside the
   package is ``.env.production.example``. The premise is pinned (first test) instead of trusted.
2. **Why the scope is one profile.** The other cloud profiles in ``config/llm.yaml`` are
   legitimately unconfigured -- the shipped allowlist names ``api.typesafe.ai`` and nothing
   else, so the gate denies them and they degrade to Mock on purpose. A fail-fast over *every*
   profile would therefore refuse to start a correct production deployment, so the gate resolves
   exactly the profile L1 uses, discovered from ``layer_profiles`` rather than hardcoded.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

import aegis_ai.runtime as runtime_module
from aegis_ai.llm.layer_profiles import LAYER_L1, layer_to_profile
from aegis_ai.production_readiness import is_production_mode

_RUNTIME = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "runtime.py"

_ABSENT_KEY_ENV = "AEGIS_TEST_L1_KEY_THAT_IS_NOT_SET"


class _Settings:
    def __init__(
        self,
        *,
        api_key_env: str,
        provider: str = "typesafe",
        base_url: str = "https://api.typesafe.ai/v1",
    ) -> None:
        self.api_key_env = api_key_env
        self.provider = provider
        self.base_url = base_url


class _Resolver:
    """Records which profile ids were asked for, so scope is measurable."""

    def __init__(self, settings: Any, *, raises: Exception | None = None) -> None:
        self.settings = settings
        self.raises = raises
        self.requested: list[str] = []

    def resolve(self, *, profile_id: str) -> Any:
        self.requested.append(profile_id)
        if self.raises is not None:
            raise self.raises
        return self.settings


@pytest.fixture(autouse=True)
def _no_absent_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_ABSENT_KEY_ENV, raising=False)
    monkeypatch.delenv("AEGIS_RUNTIME_MODE", raising=False)


def test_the_gate_is_off_outside_production_and_asks_for_nothing(monkeypatch) -> None:
    """The CI-safety control: with no production mode the gate must not even resolve."""
    monkeypatch.setattr(runtime_module, "is_production_mode", lambda: False)
    resolver = _Resolver(_Settings(api_key_env=_ABSENT_KEY_ENV))

    runtime_module._require_l1_api_key_in_production(resolver)

    assert resolver.requested == [], (
        "the gate resolved a profile outside production -- it must return before it reads "
        "anything, or a misconfigured profile would be fatal in development too"
    )


def test_production_mode_defaults_off(monkeypatch) -> None:
    """The premise the CI-safety claim rests on, measured rather than trusted."""
    monkeypatch.delenv("AEGIS_RUNTIME_MODE", raising=False)
    assert is_production_mode() is False, (
        "AEGIS_RUNTIME_MODE no longer defaults to development -- every CI run would now hit "
        "the production fail-fast paths in _build_runtime"
    )


def test_production_without_the_key_stops_the_start(monkeypatch) -> None:
    monkeypatch.setattr(runtime_module, "is_production_mode", lambda: True)
    resolver = _Resolver(_Settings(api_key_env=_ABSENT_KEY_ENV))

    with pytest.raises(RuntimeError) as excinfo:
        runtime_module._require_l1_api_key_in_production(resolver)

    message = str(excinfo.value)
    assert _ABSENT_KEY_ENV in message, "the failure must name the env var to set"
    assert layer_to_profile(LAYER_L1) in message, "the failure must name the L1 profile"
    assert "AEGIS_RUNTIME_MODE=development" in message, (
        "the failure must name the way out (run in development) so the operator is not stuck"
    )


def test_production_with_the_key_starts(monkeypatch) -> None:
    monkeypatch.setattr(runtime_module, "is_production_mode", lambda: True)
    monkeypatch.setenv(_ABSENT_KEY_ENV, "present")
    resolver = _Resolver(_Settings(api_key_env=_ABSENT_KEY_ENV))

    runtime_module._require_l1_api_key_in_production(resolver)


def test_production_tolerates_a_local_profile_without_a_key(monkeypatch) -> None:
    """A localhost profile needs no key -- the same rule the health audit already applies."""
    monkeypatch.setattr(runtime_module, "is_production_mode", lambda: True)
    resolver = _Resolver(
        _Settings(api_key_env=_ABSENT_KEY_ENV, base_url="http://localhost:11434/v1")
    )

    runtime_module._require_l1_api_key_in_production(resolver)


def test_production_tolerates_a_profile_that_declares_no_key_env(monkeypatch) -> None:
    monkeypatch.setattr(runtime_module, "is_production_mode", lambda: True)
    resolver = _Resolver(_Settings(api_key_env=""))

    runtime_module._require_l1_api_key_in_production(resolver)


def test_the_scope_is_exactly_the_profile_l1_uses(monkeypatch) -> None:
    """Scope by discovery, not by a list -- and one profile, so unconfigured cloud profiles
    (denied by the allowlist and degraded to Mock by design) can never stop the start."""
    monkeypatch.setattr(runtime_module, "is_production_mode", lambda: True)
    resolver = _Resolver(_Settings(api_key_env=_ABSENT_KEY_ENV))

    with pytest.raises(RuntimeError):
        runtime_module._require_l1_api_key_in_production(resolver)

    assert resolver.requested == [layer_to_profile(LAYER_L1)], (
        f"the gate resolved {resolver.requested}; it must resolve exactly the L1 profile "
        f"({layer_to_profile(LAYER_L1)!r}) and nothing else"
    )


def test_an_unresolvable_l1_profile_stops_the_start(monkeypatch) -> None:
    monkeypatch.setattr(runtime_module, "is_production_mode", lambda: True)
    resolver = _Resolver(None, raises=KeyError("l1_default"))

    with pytest.raises(RuntimeError) as excinfo:
        runtime_module._require_l1_api_key_in_production(resolver)

    assert layer_to_profile(LAYER_L1) in str(excinfo.value)


def test_the_composition_root_calls_the_gate_after_the_audit() -> None:
    """Wiring, and order: the audit must keep running first (it covers every profile)."""
    tree = ast.parse(_RUNTIME.read_text(encoding="utf-8"), filename=str(_RUNTIME))
    builders = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_build_runtime"
    ]
    assert len(builders) == 1, f"expected one _build_runtime, found {len(builders)}"

    def _lines_of(name: str) -> list[int]:
        return sorted(
            node.lineno
            for node in ast.walk(builders[0])
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == name
        )

    gate = _lines_of("_require_l1_api_key_in_production")
    audit = _lines_of("_audit_llm_profile_health")

    assert gate, (
        "_build_runtime does not call _require_l1_api_key_in_production -- the gate is dead "
        "code; update DELEGATION.md section 4 item 46"
    )
    assert audit, (
        "_build_runtime no longer calls _audit_llm_profile_health -- the gate replaced the "
        "audit instead of complementing it; the audit covers every profile, the gate one"
    )
    assert min(gate) > min(audit), (
        "the gate runs before the audit; the audit is what makes the non-production "
        "degradation visible and must not be skipped"
    )


def test_the_gate_does_not_read_a_hardcoded_profile_name() -> None:
    """The scope claim: the profile id comes from ``layer_profiles``, not a literal.

    A hardcoded ``"l1_default"`` would silently stop matching if the layer map were
    re-pointed, and the gate would then resolve nothing -- passing while checking nothing.
    """
    source = _RUNTIME.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_RUNTIME))
    gate = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_require_l1_api_key_in_production"
    ]
    assert len(gate) == 1

    literals = [
        node.value
        for node in ast.walk(gate[0])
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    assert "l1_default" not in literals, (
        "the gate hardcodes the profile id instead of reading layer_profiles.LAYER_TO_PROFILE"
    )
