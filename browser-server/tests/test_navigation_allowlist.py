"""The per-navigation egress gate: ``BrowserProfile.allowed_domains``.

``_navigation_egress_denied`` in ``browser_use_agent`` only vets the targets a task
*declares*, and it runs once, before the browser launches. Once the browser is
running the agent can follow a link or a redirect anywhere — a hole in the single
constraint that no pre-flight check can close.

browser-use's ``SecurityWatchdog`` closes it. It vetoes ``NavigateToUrlEvent`` before
navigation starts, re-checks on ``NavigationCompleteEvent`` (catching redirects) and
closes offending tabs — but it enforces ``BrowserProfile.allowed_domains`` and
nothing else. So the patterns handed to ``allowed_domains`` *are* the gate, and this
module is where their safety is pinned.

The safety direction is one-way. ``is_local_destination`` is the authority; the
patterns must not contradict it by being **looser**:

* a pattern that admits a host the predicate calls *external* is a constraint breach
  — the traffic leaves the environment;
* a pattern that blocks a host the predicate calls *local* is merely coarse — the
  agent cannot reach something it was allowed to reach.

Only the first is a defect, and it is the first that
``test_no_pattern_can_admit_an_external_host`` and
``test_the_pattern_shapes_are_ones_this_module_can_model`` enforce together.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aegis_browser.egress import (
    _LOCAL_NAVIGATION_PATTERNS,
    EgressRequest,
    _admissible_host,
    _extract_host,
    egress_allowed,
    is_local_destination,
    navigation_allowlist,
)

# Every test in this module guards the single constraint. The marker is counted by
# --require-egress-tests (see conftest.py) so this suite can never silently run empty.
pytestmark = pytest.mark.egress

_SRC = Path(__file__).resolve().parents[1] / "src"

#: browser-use converts ``allowed_domains`` to a set at this size, and pattern
#: matching silently stops working — ``*.local`` would stop matching. Mirrors
#: ``browser_use.browser.profile.DOMAIN_OPTIMIZATION_THRESHOLD`` (0.13.1); not
#: imported because ``browser-use`` is not installed in the test environment.
_DOMAIN_OPTIMIZATION_THRESHOLD = 100


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Every test starts from the shipped default: external egress closed."""
    monkeypatch.delenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", raising=False)
    monkeypatch.delenv("AEGIS_EGRESS_ALLOWED_HOSTS", raising=False)


# ── The safety direction ──────────────────────────────────────────────────────

#: Hosts the predicate calls external. Includes names built to look local: a
#: numeric-range glob such as ``192.168.*`` would admit the four ``*.evil.com``
#: entries below.
_EXTERNAL_PROBES = (
    "example.com",
    "8.8.8.8",
    "172.32.0.1",  # one step outside the RFC1918 172.16/12 block
    "::2",  # IPv6, but not the loopback literal
    "127.0.0.1.evil.com",
    "10.evil.com",
    "192.168.evil.com",
    "172.16.evil.com",
    "169.254.evil.com",
    "localhost.evil.com",
    "evil.localhost.attacker.com",
    "local.evil.com",
    "internal.evil.com",
    "lan.evil.com",
    "home.evil.com",
)


def _admits(host: str, pattern: str) -> bool:
    """Model the two pattern shapes this module permits.

    Deliberately **not** a reimplementation of browser-use's ``_is_url_match``: that
    would be a second source of truth, and the copy is always the one nobody
    re-reads. Instead, ``test_the_pattern_shapes_are_ones_this_module_can_model``
    proves the real list only contains these two shapes — which is what makes this
    model faithful. Weaken that test and this one becomes a lie.
    """
    if pattern.startswith("*."):
        return host.endswith(pattern[1:])
    return host == pattern


def _admitted_by(host: str) -> str | None:
    """Return the pattern that admits ``host``, or None."""
    for pattern in _LOCAL_NAVIGATION_PATTERNS:
        if _admits(host, pattern):
            return pattern
    return None


def _predicate_probe(pattern: str) -> str:
    """Build a destination the predicate can parse for ``pattern``.

    browser-use compares patterns against ``urlparse(url).hostname``; the predicate
    takes a destination *string*. For an IPv6 literal the two forms differ —
    browser-use sees ``::1``, the predicate needs ``http://[::1]/`` — so the probe is
    bracketed. See ``test_the_ipv6_literal_parser_gap_is_recorded``.
    """
    if pattern.startswith("*."):
        return f"http://probe{pattern[1:]}/"
    if ":" in pattern:
        return f"http://[{pattern}]/"
    return f"http://{pattern}/"


def test_the_pattern_shapes_are_ones_this_module_can_model():
    """Only exact hosts and ``*.suffix`` are allowed.

    This is the test that catches a numeric-range glob. ``192.168.*`` looks
    reasonable and is not: browser-use matches with ``fnmatch``, so it also admits the
    publicly resolvable ``192.168.evil.com``. Rejecting the shape is what makes
    ``_admits`` above a faithful model of the real matching, and
    ``test_private_ip_targets_must_be_declared`` records what rejecting it costs.
    """
    for pattern in _LOCAL_NAVIGATION_PATTERNS:
        if pattern.startswith("*."):
            rest = pattern[1:]
            assert "*" not in rest and "?" not in rest, (
                f"{pattern!r} is a glob that is not of the form '*.suffix'. This "
                "module's model of matching cannot describe it, so its safety is "
                "unproven. Use an exact host, or let the task declare the target."
            )
        else:
            assert "*" not in pattern and "?" not in pattern, (
                f"{pattern!r} contains a wildcard but is not of the form '*.suffix'. "
                "A wildcard that is not a whole leading label — '192.168.*', '10.*', "
                "'127.*' — also matches hosts the predicate calls external (e.g. "
                "192.168.evil.com). That is a breach of the single constraint."
            )


def test_no_pattern_can_admit_an_external_host():
    """The load-bearing assertion: no pattern is looser than the predicate."""
    for host in _EXTERNAL_PROBES:
        assert is_local_destination(host) is False, (
            f"{host!r} is in _EXTERNAL_PROBES but the predicate calls it local. The "
            "probe list is wrong, so this test is not testing what it claims."
        )
        admitted = _admitted_by(host)
        assert admitted is None, (
            f"pattern {admitted!r} admits {host!r}, which is_local_destination() calls "
            "external. The per-navigation gate would let the browser reach it."
        )


@pytest.mark.parametrize("pattern", _LOCAL_NAVIGATION_PATTERNS)
def test_every_pattern_actually_matches_a_local_host(pattern):
    """Each pattern must be reachable and local — no dead or loosening entry."""
    probe = _predicate_probe(pattern)
    assert is_local_destination(probe) is True, (
        f"{pattern!r} would admit {probe!r}, which the predicate does not call local. "
        "Coarse is acceptable; loose is not."
    )


# ── Recorded asymmetries ──────────────────────────────────────────────────────


def test_ipv6_literals_are_classified_the_same_however_they_are_written():
    """Regression: ``_extract_host`` could not parse a bare IPv6 literal.

    ``urlsplit("//::1")`` yields no hostname, so ``is_local_destination("::1")`` was
    False while ``is_local_destination("http://[::1]:50051")`` was True — the same
    host, two answers, depending on how it was written. That is what made
    ``_admissible_host`` disagree with ``egress_allowed``; the fix was to port the
    IPv6 handling the ai-server copy already had.

    ``::2`` and ``ff02::1`` are why the single-label rule is guarded with
    ``":" not in host``: neither contains a dot, so without the guard the bare-literal
    fix would have reclassified a globally routable address as local — fail-open,
    the one direction the constraint forbids.
    """
    for form in ("::1", "[::1]", "http://[::1]/", "http://[::1]:50051/"):
        assert is_local_destination(form) is True, f"{form!r} should be local"
    for form in ("::2", "ff02::1", "http://[::2]/", "2001:4860:4860::8888"):
        assert is_local_destination(form) is False, f"{form!r} should be external"

    assert _extract_host("::1") == "::1"
    assert _extract_host("[::1]") == "::1"
    assert _extract_host("[::1]:50051") == "::1"
    assert _extract_host("http://[::1]:50051/") == "::1"
    assert "::1" in _LOCAL_NAVIGATION_PATTERNS


def test_single_label_hosts_are_coarse_not_loose():
    """The predicate calls any dotless host local; the patterns do not admit them.

    ``notlocalhost`` and ``aegis-box`` are LAN-local by the predicate's single-label
    rule. The patterns admit them only when the task declares them, which appends the
    literal as an exact pattern. That is the coarse direction, and it is deliberate:
    a bare ``*`` entry would admit every dotless host in existence.
    """
    for host in ("notlocalhost", "aegis-box"):
        assert is_local_destination(host) is True
        assert _admitted_by(host) is None
        assert _extract_host(host) in navigation_allowlist([f"http://{host}:8080/"])


def test_private_ip_targets_must_be_declared():
    """The recorded cost of banning numeric-range globs.

    ``192.168.*`` is the obvious pattern for a home-LAN service and is unsafe, so a
    private-IP destination reaches the browser only when the task declares it.
    """
    assert "192.168.1.10" not in navigation_allowlist()
    assert "192.168.1.10" in navigation_allowlist(["http://192.168.1.10:8080/dashboard"])


# ── Two locks, fail closed ────────────────────────────────────────────────────


def test_undeclared_external_target_is_not_admitted():
    """Declaring an external target does not admit it while the gate is closed."""
    assert "example.com" not in navigation_allowlist(["https://example.com/"])


def test_external_target_needs_both_locks(monkeypatch):
    """The master switch and an allowlist entry, same as ``egress_allowed``."""
    declared = ["https://example.com/"]

    monkeypatch.setenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "1")
    assert "example.com" not in navigation_allowlist(declared), "switch alone admitted it"

    monkeypatch.delenv("AEGIS_EXTERNAL_EGRESS_ALLOWED")
    monkeypatch.setenv("AEGIS_EGRESS_ALLOWED_HOSTS", "example.com")
    assert "example.com" not in navigation_allowlist(declared), "allowlist alone admitted it"

    monkeypatch.setenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "1")
    assert "example.com" in navigation_allowlist(declared)


@pytest.mark.parametrize(
    "destination",
    [
        "http://localhost:11434/v1",
        "http://127.0.0.1:50053",
        "http://192.168.1.10:50053",
        "http://[::1]:50051",
        "http://nas.local/x",
        "http://aegis-box:50051",
        "https://example.com/a",
        "http://8.8.8.8/",
        "",
        "not a url",
    ],
)
def test_admissibility_agrees_with_the_gate(destination, monkeypatch):
    """The allowlist must admit exactly what the gate admits.

    Two halves of one gate disagreeing about the same host is how a constraint gets
    bypassed by whichever half is asked.
    """
    for env in ({}, {"AEGIS_EXTERNAL_EGRESS_ALLOWED": "1", "AEGIS_EGRESS_ALLOWED_HOSTS": "example.com"}):
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        host = _extract_host(destination)
        expected = egress_allowed(
            EgressRequest(destination, purpose="web.navigate", component="test")
        )
        assert _admissible_host(host) is expected, (
            f"{destination!r} (host={host!r}) env={env}: the allowlist says "
            f"{_admissible_host(host)} but the gate says {expected}."
        )
        for key in env:
            monkeypatch.delenv(key)


def test_the_allowlist_is_never_empty():
    """browser-use treats an empty ``allowed_domains`` as "allow every URL".

    An empty list would therefore *open* the gate instead of closing it. The failure
    mode is fail-open, which is the one thing the single constraint forbids.
    """
    assert navigation_allowlist() != []
    assert navigation_allowlist([""]) != []
    assert navigation_allowlist(["   "]) != []


def test_patterns_are_deduplicated():
    """A declared target must not be appended twice."""
    allowlist = navigation_allowlist(
        ["http://localhost:8000/", "localhost", "http://127.0.0.1:9/"]
    )
    assert len(allowlist) == len(set(allowlist))


def test_the_allowlist_stays_under_the_optimization_threshold(monkeypatch):
    """Past 100 entries browser-use swaps the list for a set and globs stop matching.

    ``*.local`` would silently stop working — a local host would become unreachable
    with no error. The budget is asserted against a realistically loaded list, not
    just the shipped default.
    """
    monkeypatch.setenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "1")
    monkeypatch.setenv(
        "AEGIS_EGRESS_ALLOWED_HOSTS", ",".join(f"h{i}.example.com" for i in range(40))
    )
    allowlist = navigation_allowlist([f"https://h{i}.example.com/" for i in range(40)])

    assert len(allowlist) < _DOMAIN_OPTIMIZATION_THRESHOLD
    assert "*.local" in allowlist, "a glob pattern must still be present"


# ── The wiring ────────────────────────────────────────────────────────────────


def _browser_profile_call() -> ast.Call | None:
    tree = ast.parse((_SRC / "aegis_browser" / "browser_use_agent.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "BrowserProfile":
            return node
    return None


def test_the_profile_passes_the_allowlist_to_browser_use():
    """The gate exists only if the profile carries it.

    Asserted on the AST rather than on prose: a docstring claiming the gate is wired
    is the "reads as a gate" bug class. Dropping this keyword silently restores
    allow-all, because browser-use treats an empty ``allowed_domains`` as permission.
    """
    call = _browser_profile_call()
    assert call is not None, (
        "BrowserProfile(...) is no longer constructed in browser_use_agent.py — "
        "re-point this test at whatever replaced it."
    )
    keywords = {kw.arg: kw.value for kw in call.keywords}
    assert "allowed_domains" in keywords, (
        "BrowserProfile is constructed without allowed_domains, so browser-use will "
        "allow every URL and the per-navigation egress gate disappears."
    )

    value = keywords["allowed_domains"]
    assert isinstance(value, ast.Call) and getattr(value.func, "id", None) == "navigation_allowlist", (
        "allowed_domains must come from navigation_allowlist(), which derives it from "
        "the same predicate the pre-flight check uses. A hand-written list here would "
        "be a second source of truth and would drift."
    )


def test_both_halves_derive_targets_from_one_place():
    """Pre-flight and per-navigation must not compute the target set separately."""
    tree = ast.parse((_SRC / "aegis_browser" / "browser_use_agent.py").read_text(encoding="utf-8"))

    preflight = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_navigation_egress_denied"
    )
    called = {
        node.func.id
        for node in ast.walk(preflight)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "_declared_targets" in called, (
        "_navigation_egress_denied no longer uses _declared_targets(), so the two "
        "halves of the gate may now see different target sets."
    )

    value = {kw.arg: kw.value for kw in _browser_profile_call().keywords}["allowed_domains"]
    nested = {
        node.func.id
        for node in ast.walk(value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "_declared_targets" in nested, (
        "the per-navigation allowlist must be built from _declared_targets(), the same "
        "derivation the pre-flight check uses."
    )
