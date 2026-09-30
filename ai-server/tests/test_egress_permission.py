"""The user's permission is the second path for external egress (re-scope 2026-09-30).

**What this pins.** The constraint was re-scoped on 2026-09-30: *unpermitted* user
information must never leave the local environment, outbound connections are allowed, and
user information may be sent externally **with the user's permission**. Before the
re-scope, "permission" meant standing configuration only (master switch + feature flag +
host allowlist). These tests pin the path the re-scope added: a permission the user gave
about a **specific** destination, read out of the confirmation store.

**The boundary this must not cross.** The forced approval gate was retired on 2026-09-27
and stays retired (D4=(b)): the *forced* gate is gone, the *voluntary* ask remains. The
new path is therefore **read-only over decisions the user already made**. It cannot ask,
so wiring it in cannot reintroduce a prompt. ``test_the_gate_only_ever_reads_the_store``
is the pin that keeps it that way — it records every method the adapter calls and
requires the list to be exactly ``["all"]``.

**Fail-closed everywhere.** Every unreadable, unparseable, mismatched or raising input
denies. A test that only proved the happy path would leave the failure direction unstated,
so each denial case is pinned explicitly.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any

import pytest

from aegis_ai.egress import (
    EGRESS_PERMISSION_CAPABILITY,
    ConfirmationGrantSource,
    EgressDecision,
    EgressGate,
    EgressPermission,
    EgressRequest,
    format_scope,
    parse_scope,
)
from aegis_ai.settings.models import AEGISSettings, PrivacySettings

# Guards the single constraint, so the --require-egress-tests floor counts it.
pytestmark = pytest.mark.egress

_HOST = "api.example.com"
_PURPOSE = "llm.chat"
_DESTINATION = f"https://{_HOST}/v1/chat/completions"


class _SettingsStore:
    """Minimal SettingsStore stand-in. External egress is ON unless told otherwise."""

    def __init__(self, *, external_egress_allowed: bool = True, hosts: list[str] | None = None) -> None:
        self._settings = AEGISSettings(
            privacy=PrivacySettings(
                external_egress_allowed=external_egress_allowed,
                external_llm_allowed=True,
                egress_allowed_hosts=list(hosts or []),
            )
        )

    def get(self) -> AEGISSettings:
        return self._settings


@dataclass
class _Confirmation:
    """A confirmation as the store would return it."""

    approval_id: str = "c1"
    capability_id: str = EGRESS_PERMISSION_CAPABILITY
    status: str = "approved"
    target: str = field(default_factory=lambda: format_scope(_HOST, _PURPOSE))
    resolved_at: int | None = 1_000
    expires_at: int | None = None


class _Store:
    """A ConfirmationStore stand-in that records which methods were called on it."""

    def __init__(self, items: list[_Confirmation] | None = None) -> None:
        self._items = list(items or [])
        self.calls: list[str] = []

    def all(self, *, limit: int = 200) -> list[_Confirmation]:
        self.calls.append("all")
        return list(self._items[: max(0, int(limit))])

    def request(self, **fields: Any) -> Any:  # pragma: no cover - must never be reached
        self.calls.append("request")
        raise AssertionError("the egress gate asked the user a question — the forced gate is retired")

    def resolve(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        self.calls.append("resolve")
        raise AssertionError("the egress gate resolved a confirmation")

    def approve(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        self.calls.append("approve")
        raise AssertionError("the egress gate approved its own permission")

    def reject(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        self.calls.append("reject")
        raise AssertionError("the egress gate rejected a confirmation")


def _gate(store: _Store | None = None, **settings: Any) -> EgressGate:
    return EgressGate(
        settings_store=_SettingsStore(**settings),
        permission_source=ConfirmationGrantSource(store) if store is not None else None,
    )


def _request(**overrides: Any) -> EgressRequest:
    fields: dict[str, Any] = {"destination": _DESTINATION, "purpose": _PURPOSE, "component": "test"}
    fields.update(overrides)
    return EgressRequest(**fields)


# ── The default is the strict one ─────────────────────────────────────────────


def test_a_request_is_assumed_to_carry_user_information() -> None:
    """The fail-closed default, pinned as a *default* rather than as a call-site choice."""
    default = inspect.signature(EgressRequest).parameters["carries_user_information"].default
    assert default is True, (
        "carries_user_information no longer defaults to True — a caller that has not reasoned "
        "about it would silently get the un-gated path"
    )
    assert EgressRequest(destination=_DESTINATION, purpose=_PURPOSE).carries_user_information is True


# ── Path 1: standing configuration is unchanged ───────────────────────────────


def test_without_a_permission_source_an_external_host_is_still_denied() -> None:
    """No source means the pre-re-scope behaviour — this is what makes the change additive."""
    assert _gate().check(_request()) is EgressDecision.DENY


def test_an_allowlisted_host_needs_no_grant() -> None:
    """The standing path still works on its own, so the two paths are independent."""
    gate = _gate(hosts=[_HOST])
    assert gate.check(_request()) is EgressDecision.ALLOW


# ── Path 2: a permission the user gave ────────────────────────────────────────


def test_a_recorded_permission_allows_the_exact_destination() -> None:
    """The happy path — and the reason names the grant, so the audit says *why*."""
    gate = _gate(_Store([_Confirmation(approval_id="grant-7")]))
    assert gate.allow(_request()) is True
    # The reason is not returned by `allow`; read it through the evaluation directly.
    decision, reason = gate._evaluate(_request())
    assert decision is EgressDecision.ALLOW
    assert "grant-7" in reason, f"the reason must name the grant it relied on, got {reason!r}"


def test_a_permission_for_another_host_does_not_apply() -> None:
    """A grant is scoped, not blanket: the same purpose at a different host is denied."""
    gate = _gate(_Store([_Confirmation(target=format_scope("other.example.com", _PURPOSE))]))
    assert gate.check(_request()) is EgressDecision.DENY


def test_a_permission_for_another_purpose_does_not_apply() -> None:
    gate = _gate(_Store([_Confirmation(target=format_scope(_HOST, "web.search"))]))
    assert gate.check(_request()) is EgressDecision.DENY


def test_the_host_match_is_case_insensitive() -> None:
    """A hostname's case is not information; refusing `API.Example.com` would be noise."""
    gate = _gate(_Store([_Confirmation(target=format_scope(_HOST.upper(), _PURPOSE))]))
    assert gate.check(_request()) is EgressDecision.ALLOW


def test_a_wildcard_scope_is_not_a_permission() -> None:
    """A blanket grant is deliberately not representable — it is a wall with a hole in it."""
    gate = _gate(_Store([_Confirmation(target=format_scope("*", _PURPOSE))]))
    assert gate.check(_request()) is EgressDecision.DENY


# ── Only a decision the user actually made counts ─────────────────────────────


@pytest.mark.parametrize("status", ["pending", "rejected", "expired", "cancelled", "failed", "superseded"])
def test_a_confirmation_the_user_did_not_approve_is_not_a_permission(status: str) -> None:
    gate = _gate(_Store([_Confirmation(status=status)]))
    assert gate.check(_request()) is EgressDecision.DENY, (
        f"a {status!r} confirmation was treated as permission"
    )


def test_an_expired_permission_is_not_a_permission() -> None:
    """A grant given for one task must not silently become a standing one."""
    gate = _gate(_Store([_Confirmation(expires_at=1)]))
    assert gate.check(_request()) is EgressDecision.DENY


def test_a_permission_that_has_not_expired_is_honoured() -> None:
    """Non-vacuous counterpart to the expiry test: a far-future expiry still allows."""
    gate = _gate(_Store([_Confirmation(expires_at=2**62)]))
    assert gate.check(_request()) is EgressDecision.ALLOW


def test_another_capabilitys_confirmation_is_not_an_egress_permission() -> None:
    """Status alone is not enough — the record must be an egress grant."""
    gate = _gate(_Store([_Confirmation(capability_id="browser.navigate")]))
    assert gate.check(_request()) is EgressDecision.DENY


@pytest.mark.parametrize("target", ["", "api.example.com", "|llm.chat", "api.example.com|", "|"])
def test_a_malformed_scope_is_not_a_permission(target: str) -> None:
    """An unparseable permission is not a permission."""
    gate = _gate(_Store([_Confirmation(target=target)]))
    assert gate.check(_request()) is EgressDecision.DENY


# ── Fail closed ───────────────────────────────────────────────────────────────


def test_a_raising_permission_source_denies_rather_than_allows() -> None:
    """The failure direction is the whole point: a broken source must not open the gate."""

    class _Broken:
        def grant_for(self, **_: Any) -> Any:
            raise RuntimeError("store unavailable")

    gate = EgressGate(settings_store=_SettingsStore(), permission_source=_Broken())
    assert gate.check(_request()) is EgressDecision.DENY


def test_a_source_without_grant_for_denies() -> None:
    gate = EgressGate(settings_store=_SettingsStore(), permission_source=object())
    assert gate.check(_request()) is EgressDecision.DENY


def test_the_master_switch_still_bounds_everything() -> None:
    """A per-request grant must not make the user's global switch ineffective."""
    gate = _gate(_Store([_Confirmation()]), external_egress_allowed=False)
    assert gate.check(_request()) is EgressDecision.DENY, (
        "a recorded grant overrode the master switch — the global switch would become an "
        "ineffective flag"
    )


def test_an_unclassifiable_destination_is_still_denied_even_with_a_grant() -> None:
    """Permission is about *external* destinations; fail-closed classification is unchanged."""
    gate = _gate(_Store([_Confirmation(target=format_scope("", _PURPOSE))]))
    assert gate.check(_request(destination="")) is EgressDecision.DENY


# ── The constraint is about user information, not connectivity ────────────────


def test_a_request_carrying_no_user_information_needs_no_permission() -> None:
    """The re-scoped reading: connecting out is not itself the thing being constrained."""
    gate = _gate()
    assert gate.check(_request(carries_user_information=False)) is EgressDecision.ALLOW


def test_even_a_non_user_information_request_respects_the_master_switch() -> None:
    """Connectivity is not gated by permission, but the user's global switch still applies."""
    gate = _gate(external_egress_allowed=False)
    assert gate.check(_request(carries_user_information=False)) is EgressDecision.DENY


def test_local_destinations_are_unaffected() -> None:
    gate = _gate(external_egress_allowed=False)
    assert gate.check(_request(destination="http://192.168.1.10:50052")) is EgressDecision.ALLOW


# ── The retired forced gate stays retired ─────────────────────────────────────


def test_the_gate_only_ever_reads_the_store() -> None:
    """**The D4=(b) boundary.** The gate consults decided permissions; it never asks.

    A source that could be asked would put the retired forced gate back — the failure mode
    the owner named in both directions. The store stub raises on every mutating method, so
    any attempt to ask, resolve or self-approve fails loudly rather than quietly.
    """
    store = _Store([_Confirmation()])
    gate = _gate(store)

    assert gate.check(_request()) is EgressDecision.ALLOW
    assert store.calls == ["all"], (
        f"the permission source called {store.calls} on the store — only the read surface "
        "('all') is allowed, or the gate has started asking the user again"
    )


def test_the_adapter_exposes_no_way_to_ask() -> None:
    """Structural, not behavioural: the adapter's own surface has no ask on it."""
    public = {name for name in dir(ConfirmationGrantSource) if not name.startswith("_")}
    assert public == {"grants", "grant_for"}, (
        f"ConfirmationGrantSource grew a public member: {sorted(public)} — if it can ask, the "
        "forced gate is back"
    )


# ── Scope parsing, directly ───────────────────────────────────────────────────


def test_scope_round_trips() -> None:
    scope = format_scope("API.Example.com", "llm.chat")
    assert scope == "api.example.com|llm.chat"
    assert parse_scope(scope) == ("api.example.com", "llm.chat")


def test_an_expired_grant_is_not_returned_by_the_source() -> None:
    source = ConfirmationGrantSource(_Store([_Confirmation(expires_at=1_000)]))
    assert source.grant_for(host=_HOST, purpose=_PURPOSE, moment_ms=2_000) is None
    assert source.grant_for(host=_HOST, purpose=_PURPOSE, moment_ms=500) is not None


def test_a_grant_with_no_expiry_never_lapses() -> None:
    source = ConfirmationGrantSource(_Store([_Confirmation(expires_at=None)]))
    grant = source.grant_for(host=_HOST, purpose=_PURPOSE, moment_ms=2**62)
    assert isinstance(grant, EgressPermission)
    assert grant.grant_id == "c1"
