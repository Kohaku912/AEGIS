"""pass^k reliability for the egress gate.

A single passing test tells you the gate *can* deny. It does not tell you the gate
*always* denies — and for a constraint, "always" is the whole requirement. A block
that holds 19 times out of 20 is not a constraint; it is a coin flip with good PR.

This module applies the retired ``pass^k`` discipline (run the same task N times,
require **every** trial to succeed) to egress blocking:

* every external destination is denied on every trial;
* every local destination is still allowed on every trial (a gate that refuses
  everything would otherwise pass the first check);
* unclassifiable destinations fail closed on every trial;
* each of the "near miss" lock configurations still blocks on every trial;
* every denial is audited on every trial;
* repeated local traffic never erodes the block.

Trials use a **freshly constructed gate**, so nothing can be carried over between
them. The trial count is asserted at the end of each test, so a silently shrinking
destination list cannot turn a pass^k test into a pass^0 test.
"""

from __future__ import annotations

from typing import Any

import pytest

# Every test in this module guards the single constraint. The marker is counted by
# --require-egress-tests (see conftest.py) so this suite can never silently run empty.
pytestmark = pytest.mark.egress

#: Trials per destination. The retired P2-3 discipline: all of them, not most.
PASS_K = 20

#: Destinations that must be refused. Deliberately varied: schemes, ports, IPv4,
#: IPv6, credentials in the authority, punycode, trailing dots, case, and the
#: specific hosts AEGIS used to talk to before the gate existed.
_EXTERNAL_DESTINATIONS: tuple[str, ...] = (
    "https://api.deepseek.com/v1/chat/completions",
    "https://api.openai.com/v1",
    "http://api.openai.com/v1",
    "https://api.typesafe.ai/v1/systemone",
    "https://ws-nuimlupsvbr9m8x1.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
    "https://speech.platform.bing.com",
    "https://html.duckduckgo.com/html/",
    "duckduckgo.com",
    "https://api.telegram.org/bot123/sendMessage",
    "https://discord.com/api/webhooks/1/2",
    "https://hooks.slack.com/services/x",
    "https://api.open-meteo.com/v1/forecast",
    "https://otlp.external.example.com:4317",
    "https://agent.example.com/api",
    "smtp.external.example.com:587",
    "8.8.8.8",
    "https://8.8.8.8/dns-query",
    "https://[2001:4860:4860::8888]/dns-query",
    "https://user:pass@evil.example.com/hook",
    "https://evil.example.com:8443/x",
    "https://xn--fiqs8s.example.com/path",
    "https://example.com/path?q=secret",
    "https://EXAMPLE.COM",
    "sub.domain.co.jp",
)

#: Destinations inside the environment. The multi-device LAN *is* local.
_LOCAL_DESTINATIONS: tuple[str, ...] = (
    "http://localhost:11434/v1",
    "http://127.0.0.1:50051",
    "http://[::1]:8090",
    "http://192.168.1.10:50052",
    "http://10.0.0.5:50055",
    "http://172.16.4.2",
    "http://100.101.102.103:50051",
    "http://[fd7a:115c:a1e0::1]:50051",
    "orangepi",
    "room-server.local",
    "unix:/tmp/aegis.sock",
)

#: Destination that must be refused for the specific lock configuration.
_LOCK_PROBE = "https://api.deepseek.com/v1/chat/completions"

#: Configurations that look permissive but are still missing a lock. Each entry is
#: (label, privacy overrides, allowlist). None of these may open egress.
_NEAR_MISS_CONFIGS: tuple[tuple[str, dict[str, Any], list[str]], ...] = (
    ("master switch only", {"external_egress_allowed": True}, []),
    (
        "llm flag + allowlist, master switch off",
        {"external_llm_allowed": True},
        ["api.deepseek.com"],
    ),
    (
        "master + llm flag, allowlist names another host",
        {"external_egress_allowed": True, "external_llm_allowed": True},
        ["allowed.example.com"],
    ),
    (
        "web flag open but the purpose is llm.chat",
        {"external_egress_allowed": True, "web_search_allowed": True},
        ["api.deepseek.com"],
    ),
)

#: Destinations the gate cannot classify. Fail closed means deny, every time.
_UNCLASSIFIABLE_DESTINATIONS: tuple[str, ...] = (
    "",
    "   ",
    "not a url",
    "ftp://weird!!host",
    "://missing-scheme",
)


class _RecordingAudit:
    def __init__(self) -> None:
        self.entries: list[Any] = []

    def append(self, entry: Any) -> None:
        self.entries.append(entry)


def _fresh_gate(settings_store_factory, **privacy_overrides):
    """A brand-new gate per trial, so no state can survive between trials."""
    from aegis_ai.egress import EgressGate

    return EgressGate(settings_store=settings_store_factory(**privacy_overrides))


# ── pass^k on the deny path ───────────────────────────────────────────────────


def test_every_external_destination_is_denied_on_every_trial(settings_store_factory):
    from aegis_ai.egress import EgressDecision, EgressRequest

    trials = 0
    leaks: list[tuple[int, str]] = []

    for trial in range(PASS_K):
        gate = _fresh_gate(settings_store_factory)
        for destination in _EXTERNAL_DESTINATIONS:
            trials += 1
            decision = gate.check(
                EgressRequest(destination, purpose="llm.chat", component="pass^k")
            )
            if decision is not EgressDecision.DENY:
                leaks.append((trial, destination))

    assert trials == PASS_K * len(_EXTERNAL_DESTINATIONS), "the trial loop did not run in full"
    assert leaks == [], f"egress leaked on {len(leaks)} of {trials} trials: {leaks[:5]}"


def test_every_local_destination_is_allowed_on_every_trial(settings_store_factory):
    """The positive control: a gate that refused everything would pass the test above."""
    from aegis_ai.egress import EgressDecision, EgressRequest

    trials = 0
    refusals: list[tuple[int, str]] = []

    for trial in range(PASS_K):
        gate = _fresh_gate(settings_store_factory)
        for destination in _LOCAL_DESTINATIONS:
            trials += 1
            decision = gate.check(
                EgressRequest(destination, purpose="llm.chat", component="pass^k")
            )
            if decision is not EgressDecision.ALLOW:
                refusals.append((trial, destination))

    assert trials == PASS_K * len(_LOCAL_DESTINATIONS), "the trial loop did not run in full"
    assert refusals == [], f"local traffic was refused on {len(refusals)} of {trials} trials: {refusals[:5]}"


def test_unclassifiable_destinations_fail_closed_on_every_trial(settings_store_factory):
    from aegis_ai.egress import EgressDecision, EgressRequest

    trials = 0
    leaks: list[tuple[int, str]] = []

    for trial in range(PASS_K):
        gate = _fresh_gate(settings_store_factory)
        for destination in _UNCLASSIFIABLE_DESTINATIONS:
            trials += 1
            decision = gate.check(
                EgressRequest(destination, purpose="llm.chat", component="pass^k")
            )
            if decision is not EgressDecision.DENY:
                leaks.append((trial, destination))

    assert trials == PASS_K * len(_UNCLASSIFIABLE_DESTINATIONS), "the trial loop did not run in full"
    assert leaks == [], f"an unclassifiable destination was not refused: {leaks[:5]}"


@pytest.mark.parametrize(
    "label,overrides,allowed_hosts",
    _NEAR_MISS_CONFIGS,
    ids=[config[0] for config in _NEAR_MISS_CONFIGS],
)
def test_the_three_locks_hold_on_every_trial(
    settings_store_factory, label, overrides, allowed_hosts
):
    """Every lock configuration that is *missing one lock* must still deny, every trial."""
    from aegis_ai.egress import EgressDecision, EgressGate, EgressRequest

    leaks: list[int] = []

    for trial in range(PASS_K):
        gate = EgressGate(
            settings_store=settings_store_factory(**overrides),
            allowed_hosts=allowed_hosts,
        )
        decision = gate.check(
            EgressRequest(_LOCK_PROBE, purpose="llm.chat", component="pass^k")
        )
        if decision is not EgressDecision.DENY:
            leaks.append(trial)

    assert len(leaks) == 0, f"[{label}] egress opened on trials {leaks}"


def test_all_locks_open_allows_only_the_allowlisted_host(settings_store_factory):
    """Guard the guard: the near-miss configurations above must not be blanket refusals.

    With every lock open, an allowlisted host is permitted — which proves the
    refusals above come from the missing lock, not from the gate refusing
    unconditionally. A host outside the allowlist is still denied.
    """
    from aegis_ai.egress import EgressDecision, EgressGate, EgressRequest

    gate = EgressGate(
        settings_store=settings_store_factory(
            external_egress_allowed=True, external_llm_allowed=True
        ),
        allowed_hosts=["api.deepseek.com"],
    )

    assert (
        gate.check(EgressRequest(_LOCK_PROBE, purpose="llm.chat", component="pass^k"))
        is EgressDecision.ALLOW
    )
    assert (
        gate.check(
            EgressRequest(
                "https://api.openai.com/v1", purpose="llm.chat", component="pass^k"
            )
        )
        is EgressDecision.DENY
    )


# ── pass^k on the audit trail ─────────────────────────────────────────────────


def test_every_denial_is_audited_on_every_trial(settings_store_factory):
    """A constraint you cannot verify after the fact is not verifiable at all."""
    from aegis_ai.egress import EgressGate, EgressRequest

    for trial in range(PASS_K):
        audit = _RecordingAudit()
        gate = EgressGate(settings_store=settings_store_factory(), audit=audit)

        for destination in _EXTERNAL_DESTINATIONS:
            gate.check(EgressRequest(destination, purpose="llm.chat", component="pass^k"))

        assert len(audit.entries) == len(_EXTERNAL_DESTINATIONS), (
            f"trial {trial}: {len(audit.entries)} audit entries for "
            f"{len(_EXTERNAL_DESTINATIONS)} denials"
        )
        assert all(entry.decision == "deny" for entry in audit.entries)
        assert all(entry.action == "egress_decision" for entry in audit.entries)


# ── pass^k on the absence of state ────────────────────────────────────────────


def test_repeated_local_traffic_never_erodes_the_block(settings_store_factory):
    """The decision must be a function of the request, not of how many came before.

    A gate that counted requests, cached a verdict, or leaked state between checks
    would eventually allow an external destination after enough local traffic.
    """
    from aegis_ai.egress import EgressDecision, EgressGate, EgressRequest

    gate = EgressGate(settings_store=settings_store_factory())

    for _ in range(PASS_K * 10):
        assert (
            gate.check(
                EgressRequest("http://localhost:11434/v1", purpose="llm.chat", component="pass^k")
            )
            is EgressDecision.ALLOW
        )

    for trial in range(PASS_K):
        assert (
            gate.check(
                EgressRequest(_LOCK_PROBE, purpose="llm.chat", component="pass^k")
            )
            is EgressDecision.DENY
        ), f"an external destination was allowed after {PASS_K * 10} local checks (trial {trial})"
